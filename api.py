import json
import os
import re
import secrets
import smtplib
import uuid
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

from funcoes import (
    LOCAL,
    HORARIOS_POR_MEDICO,
    MEDICOS_POR_ESPECIALIDADE,
    carregar_consultas,
    enviar_email_confirmacao,
    salvar_consultas,
)


ROOT = Path(__file__).resolve().parent
FRONTEND_DIST = ROOT / "frontend" / "dist"
USERS_FILE = ROOT / "usuarios.json"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = Flask(__name__, static_folder=None)
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "").lower() == "true",
)

if not os.getenv("FLASK_SECRET_KEY"):
    app.logger.warning(
        "FLASK_SECRET_KEY não configurada; as sessões serão invalidadas ao reiniciar a API."
    )


def carregar_usuarios():
    if not USERS_FILE.exists():
        return []

    try:
        with USERS_FILE.open("r", encoding="utf-8") as arquivo:
            usuarios = json.load(arquivo)
    except (json.JSONDecodeError, OSError) as erro:
        raise RuntimeError("Não foi possível carregar as contas de usuário.") from erro
    if not isinstance(usuarios, list):
        raise RuntimeError("O arquivo de contas de usuário tem um formato inválido.")
    return usuarios


def salvar_usuarios(usuarios):
    with USERS_FILE.open("w", encoding="utf-8") as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)


def _usuario_publico(usuario):
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "telefone": usuario["telefone"],
        "email": usuario["email"],
    }


def _consulta_publica(consulta):
    return {campo: valor for campo, valor in consulta.items() if campo != "usuario_id"}


def _usuario_atual():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return None
    return next(
        (usuario for usuario in carregar_usuarios() if usuario.get("id") == usuario_id),
        None,
    )


def _carregar_consultas_com_id():
    consultas = carregar_consultas()
    atualizou = False
    for consulta in consultas:
        if not consulta.get("id"):
            consulta["id"] = uuid.uuid4().hex
            atualizou = True
    if atualizou:
        salvar_consultas(consultas)
    return consultas


def _erro(mensagem, status):
    return jsonify({"erro": mensagem}), status


def _validar_data(valor):
    try:
        data_consulta = datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
    if data_consulta < date.today():
        return None
    return data_consulta


@app.post("/api/auth/register")
def registrar_usuario():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados da conta em formato JSON.", 400)

    nome = dados.get("nome", "").strip() if isinstance(dados.get("nome"), str) else ""
    telefone = (
        dados.get("telefone", "").strip()
        if isinstance(dados.get("telefone"), str)
        else ""
    )
    email = (
        dados.get("email", "").strip().lower()
        if isinstance(dados.get("email"), str)
        else ""
    )
    senha = dados.get("senha")

    if not nome or not telefone or not email or not isinstance(senha, str):
        return _erro("Preencha todos os campos para criar sua conta.", 400)
    if (
        len(nome) > 120
        or len(telefone) > 30
        or len(email) > 254
        or not EMAIL_PATTERN.fullmatch(email)
    ):
        return _erro("Confira o nome, telefone e e-mail informados.", 400)
    if len(senha) < 8 or len(senha) > 128:
        return _erro("A senha deve ter entre 8 e 128 caracteres.", 400)

    usuarios = carregar_usuarios()
    if any(usuario.get("email") == email for usuario in usuarios):
        return _erro("Já existe uma conta com este e-mail.", 409)

    usuario = {
        "id": uuid.uuid4().hex,
        "nome": nome,
        "telefone": telefone,
        "email": email,
        "senha_hash": generate_password_hash(senha),
    }
    usuarios.append(usuario)
    salvar_usuarios(usuarios)
    session.clear()
    session["usuario_id"] = usuario["id"]
    return jsonify({"usuario": _usuario_publico(usuario)}), 201


@app.post("/api/auth/login")
def entrar():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie e-mail e senha em formato JSON.", 400)

    email = (
        dados.get("email", "").strip().lower()
        if isinstance(dados.get("email"), str)
        else ""
    )
    senha = dados.get("senha")
    if len(email) > 254:
        return _erro("E-mail ou senha incorretos.", 401)
    usuario = next(
        (usuario for usuario in carregar_usuarios() if usuario.get("email") == email),
        None,
    )
    if (
        not usuario
        or not isinstance(senha, str)
        or len(senha) > 128
        or not check_password_hash(usuario["senha_hash"], senha)
    ):
        return _erro("E-mail ou senha incorretos.", 401)

    session.clear()
    session["usuario_id"] = usuario["id"]
    return jsonify({"usuario": _usuario_publico(usuario)})


@app.get("/api/auth/me")
def obter_usuario_atual():
    usuario = _usuario_atual()
    if not usuario:
        return _erro("Faça login para continuar.", 401)
    return jsonify({"usuario": _usuario_publico(usuario)})


@app.post("/api/auth/logout")
def sair():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/config")
def obter_configuracao():
    return jsonify(
        {
            "local": LOCAL,
            "medicos_por_especialidade": MEDICOS_POR_ESPECIALIDADE,
        }
    )


@app.get("/api/appointments")
def listar_consultas():
    usuario = _usuario_atual()
    if not usuario:
        return _erro("Faça login para ver seus agendamentos.", 401)
    consultas = _carregar_consultas_com_id()
    return jsonify(
        [
            _consulta_publica(consulta)
            for consulta in consultas
            if consulta.get("usuario_id") == usuario["id"]
        ]
    )


@app.get("/api/availability")
def consultar_horarios_disponiveis():
    especialidade = request.args.get("especialidade", "").strip()
    medico = request.args.get("medico", "").strip()
    valor_data = request.args.get("data", "").strip()
    data_consulta = _validar_data(valor_data)

    if medico not in MEDICOS_POR_ESPECIALIDADE.get(especialidade, []):
        return _erro("Selecione uma especialidade e um médico válidos.", 400)
    if data_consulta is None:
        return _erro("Selecione uma data válida, igual ou posterior a hoje.", 400)

    data_salva = data_consulta.strftime("%d/%m/%Y")
    consultas = _carregar_consultas_com_id()
    ocupados = {
        consulta.get("horario")
        for consulta in consultas
        if consulta.get("medico") == medico and consulta.get("data") == data_salva
    }
    horarios = [
        horario
        for horario in HORARIOS_POR_MEDICO.get(medico, [])
        if horario not in ocupados
    ]
    return jsonify({"data": valor_data, "horarios": horarios})


@app.post("/api/appointments")
def criar_consulta():
    usuario = _usuario_atual()
    if not usuario:
        return _erro("Faça login para agendar uma consulta.", 401)

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados da consulta em formato JSON.", 400)

    campos = ("especialidade", "medico", "data", "horario")
    valores = {
        campo: dados.get(campo, "").strip()
        if isinstance(dados.get(campo, ""), str)
        else ""
        for campo in campos
    }
    ausentes = [campo for campo, valor in valores.items() if not valor]
    if ausentes:
        return _erro("Preencha todos os campos obrigatórios.", 400)
    if valores["medico"] not in MEDICOS_POR_ESPECIALIDADE.get(valores["especialidade"], []):
        return _erro("O médico não pertence à especialidade selecionada.", 400)

    data_consulta = _validar_data(valores["data"])
    if data_consulta is None:
        return _erro("Selecione uma data válida, igual ou posterior a hoje.", 400)

    horarios = HORARIOS_POR_MEDICO.get(valores["medico"], [])
    if valores["horario"] not in horarios:
        return _erro("O horário selecionado não está disponível para esse médico.", 400)

    consultas = _carregar_consultas_com_id()
    data_salva = data_consulta.strftime("%d/%m/%Y")
    conflito = any(
        consulta.get("medico") == valores["medico"]
        and consulta.get("data") == data_salva
        and consulta.get("horario") == valores["horario"]
        for consulta in consultas
    )
    if conflito:
        return _erro("Esse horário acabou de ser reservado. Escolha outro.", 409)

    consulta = {
        "id": uuid.uuid4().hex,
        "usuario_id": usuario["id"],
        "paciente": usuario["nome"],
        "telefone": usuario["telefone"],
        "email": usuario["email"],
        "especialidade": valores["especialidade"],
        "medico": valores["medico"],
        "data": data_salva,
        "horario": valores["horario"],
        "local": LOCAL,
    }
    consultas.append(consulta)
    salvar_consultas(consultas)

    email_enviado = True
    aviso = None
    try:
        enviar_email_confirmacao(
            usuario["email"],
            usuario["nome"],
            valores["especialidade"],
            valores["medico"],
            data_salva,
            valores["horario"],
            LOCAL,
        )
    except (RuntimeError, smtplib.SMTPException, OSError) as erro:
        email_enviado = False
        aviso = str(erro)
        app.logger.warning("Falha ao enviar confirmação de consulta: %s", erro)

    return (
        jsonify(
            {
                "consulta": _consulta_publica(consulta),
                "email_enviado": email_enviado,
                "aviso": aviso,
            }
        ),
        201,
    )


@app.delete("/api/appointments/<appointment_id>")
def cancelar_consulta(appointment_id):
    usuario = _usuario_atual()
    if not usuario:
        return _erro("Faça login para cancelar uma consulta.", 401)

    consultas = _carregar_consultas_com_id()
    for indice, consulta in enumerate(consultas):
        if (
            consulta.get("id") == appointment_id
            and consulta.get("usuario_id") == usuario["id"]
        ):
            cancelada = consultas.pop(indice)
            salvar_consultas(consultas)
            return jsonify({"consulta": _consulta_publica(cancelada)})
    return _erro("Agendamento não encontrado.", 404)


@app.get("/")
def servir_frontend():
    if not (FRONTEND_DIST / "index.html").is_file():
        return _erro(
            "A interface ainda não foi compilada. Execute npm install e npm run build na pasta frontend.",
            404,
        )
    return send_from_directory(FRONTEND_DIST, "index.html")


@app.get("/<path:arquivo>")
def servir_arquivo_frontend(arquivo):
    caminho = FRONTEND_DIST / arquivo
    if caminho.is_file():
        return send_from_directory(FRONTEND_DIST, arquivo)
    if (FRONTEND_DIST / "index.html").is_file():
        return send_from_directory(FRONTEND_DIST, "index.html")
    return _erro("Arquivo não encontrado.", 404)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
