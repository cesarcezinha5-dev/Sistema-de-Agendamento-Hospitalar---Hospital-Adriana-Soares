import re
import smtplib
import uuid
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

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
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = Flask(__name__, static_folder=None)


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
    consultas = _carregar_consultas_com_id()
    return jsonify(consultas)


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
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie os dados da consulta em formato JSON.", 400)

    campos = ("paciente", "telefone", "email", "especialidade", "medico", "data", "horario")
    valores = {
        campo: dados.get(campo, "").strip()
        if isinstance(dados.get(campo, ""), str)
        else ""
        for campo in campos
    }
    ausentes = [campo for campo, valor in valores.items() if not valor]
    if ausentes:
        return _erro("Preencha todos os campos obrigatórios.", 400)
    if not EMAIL_PATTERN.fullmatch(valores["email"]):
        return _erro("Digite um endereço de e-mail válido.", 400)
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
        "paciente": valores["paciente"],
        "telefone": valores["telefone"],
        "email": valores["email"],
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
            valores["email"],
            valores["paciente"],
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
                "consulta": consulta,
                "email_enviado": email_enviado,
                "aviso": aviso,
            }
        ),
        201,
    )


@app.delete("/api/appointments/<appointment_id>")
def cancelar_consulta(appointment_id):
    consultas = _carregar_consultas_com_id()
    for indice, consulta in enumerate(consultas):
        if consulta.get("id") == appointment_id:
            cancelada = consultas.pop(indice)
            salvar_consultas(consultas)
            return jsonify({"consulta": cancelada})
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
