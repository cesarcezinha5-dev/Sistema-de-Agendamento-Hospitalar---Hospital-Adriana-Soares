import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

LOCAL = "Rua Jacobina, 123 - Centro, Guarulhos - SP"
ARQUIVO_CONSULTAS = Path(__file__).resolve().parent / "consultas.json"

MEDICOS_POR_ESPECIALIDADE = {
    "Cardiologia": ["Dr. João", "Dra. Maria"],
    "Clínica Geral": ["Dr. João", "Dra. Maria"],
    "Dermatologia": ["Dr. Carlos", "Dra. Ana"],
    "Endocrinologia": ["Dr. Pedro", "Dra. Luiza"],
    "Gastroenterologia": ["Dr. Lucas", "Dra. Fernanda"],
    "Ginecologia": ["Dr. Rafael", "Dra. Camila"],
    "Neurologia": ["Dr. Bruno", "Dra. Mariana"],
    "Oftalmologia": ["Dr. Gustavo", "Dra. Juliana"],
    "Ortopedia": ["Dr. Felipe", "Dra. Aline"],
    "Pediatria": ["Dr. Ricardo", "Dra. Gabriela"],
    "Psiquiatria": ["Dr. André", "Dra. Vanessa"],
}

DATAS_POR_MEDICO = {
    "Dr. João": ["01/07/2026", "03/07/2026", "05/07/2026"],
    "Dra. Maria": ["02/07/2026", "04/07/2026", "06/07/2026"],
    "Dr. Carlos": ["01/04/2026", "03/08/2026", "05/08/2026"],
    "Dra. Ana": ["02/07/2026", "04/08/2026", "06/08/2026"],
    "Dr. Pedro": ["25/07/2026", "03/07/2026", "05/07/2026"],
    "Dra. Luiza": ["03/06/2026", "04/06/2026", "06/08/2026"],
    "Dr. Lucas": ["04/05/2026", "03/05/2026", "05/06/2026"],
    "Dra. Fernanda": ["05/05/2026", "04/07/2026", "06/07/2026"],
    "Dr. Rafael": ["03/07/2026", "03/06/2026", "05/06/2026"],
    "Dra. Camila": ["02/07/2026", "04/06/2026", "06/06/2026"],
    "Dr. Bruno": ["01/07/2026", "03/08/2026", "05/07/2026"],
    "Dra. Mariana": ["22/07/2026", "04/04/2026", "06/04/2026"],
    "Dr. Gustavo": ["01/04/2026", "03/06/2026", "05/06/2026"],
    "Dra. Juliana": ["02/06/2026", "04/07/2026", "06/07/2026"],
    "Dr. Felipe": ["11/07/2026", "03/04/2026", "05/09/2026"],
    "Dra. Aline": ["22/08/2026", "04/05/2026", "06/05/2026"],
    "Dr. Ricardo": ["12/05/2026", "03/07/2026", "05/07/2026"],
    "Dra. Gabriela": ["20/07/2026", "04/05/2026", "06/05/2026"],
    "Dr. André": ["21/07/2026", "01/05/2026", "05/05/2026"],
    "Dra. Vanessa": ["02/05/2026", "04/05/2026", "06/05/2026"],
}

HORARIOS_POR_MEDICO = {
    "Dr. João": ["10:00", "14:00", "16:00"],
    "Dra. Maria": ["09:30", "13:30", "15:30"],
    "Dr. Carlos": ["09:00", "13:00", "15:00"],
    "Dra. Ana": ["11:00", "15:00", "17:00"],
    "Dr. Pedro": ["08:00", "12:00", "14:00"],
    "Dra. Luiza": ["10:30", "14:30", "16:30"],
    "Dr. Lucas": ["09:30", "13:30", "15:30"],
    "Dra. Fernanda": ["08:30", "12:30", "14:30"],
    "Dr. Rafael": ["10:15", "14:15", "16:15"],
    "Dra. Camila": ["09:15", "13:15", "15:15"],
    "Dr. Bruno": ["08:45", "12:45", "14:45"],
    "Dra. Mariana": ["10:45", "14:45", "16:45"],
    "Dr. Gustavo": ["09:45", "13:45", "15:45"],
    "Dra. Juliana": ["08:15", "12:15", "14:15"],
    "Dr. Felipe": ["10:30", "14:30", "16:30"],
    "Dra. Aline": ["09:30", "13:30", "15:30"],
    "Dr. Ricardo": ["08:00", "12:00", "14:00"],
    "Dra. Gabriela": ["10:00", "14:00", "16:00"],
    "Dr. André": ["09:30", "13:30", "15:30"],
    "Dra. Vanessa": ["08:30", "12:30", "14:30"],
}


def enviar_email_confirmacao(destinatario, nome, especialidade, medico, data, horario, local):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    if not remetente or not senha_app:
        raise RuntimeError("Credenciais de e-mail não configuradas.")

    msg = EmailMessage()
    msg["Subject"] = "Confirmação de Agendamento - Hospital Adriana Soares"
    msg["From"] = remetente
    msg["To"] = destinatario
    msg.set_content(
        f"""Olá {nome}, eu sou a Tayná, assistente inteligente do Hospital Adriana Soares.

Sua consulta foi agendada com sucesso!

Especialidade: {especialidade}
Médico(a): {medico}
Data: {data}
Horário: {horario}
Local: {local}

Agradecemos a preferência!
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remetente, senha_app)
        smtp.send_message(msg)


def salvar_consultas(consultas):
    with ARQUIVO_CONSULTAS.open("w", encoding="utf-8") as arquivo:
        json.dump(consultas, arquivo, ensure_ascii=False, indent=4)


def carregar_consultas():
    if not ARQUIVO_CONSULTAS.exists():
        return []

    try:
        with ARQUIVO_CONSULTAS.open("r", encoding="utf-8") as arquivo:
            consultas = json.load(arquivo)
        return consultas if isinstance(consultas, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def mostrar_datas(medico_escolhido):
    print("Datas disponíveis para esse médico:")
    return DATAS_POR_MEDICO.get(medico_escolhido, [])


def horarios_disponiveis(medico_escolhido):
    print("Horários disponíveis para esse médico:")
    return HORARIOS_POR_MEDICO.get(medico_escolhido, [])


def mostrar_medicos(especialidade_escolhida):
    print("Médicos disponíveis para essa especialidade:")
    return MEDICOS_POR_ESPECIALIDADE.get(especialidade_escolhida, [])


def mostrar_especialidades():
    print("Especialidades disponíveis:")
    return list(MEDICOS_POR_ESPECIALIDADE)


def escolher_opcao(lista, mensagem):
    if not lista:
        raise ValueError("Não há opções disponíveis.")

    while True:
        for i, item in enumerate(lista):
            print(f"{i + 1} - {item}")

        try:
            escolha = int(input(mensagem))
        except (TypeError, ValueError):
            print("\nDigite apenas números.\n")
            continue

        if escolha < 1 or escolha > len(lista):
            print("\nOpção inválida. Tente novamente.\n")
        else:
            return lista[escolha - 1]


def menu_principal():
    return input("1 - Agendar consulta\n2 - Ver agendamentos\n3 - Cancelar consulta\n4 - Sair\nEscolha uma opção: ")


def resumo_agendamento(nome, especialidade_escolhida, medico_escolhido, escolha_data, escolha_horario, local):
    print("Resumo do agendamento:")
    print(f"Paciente: {nome}")
    print(f"Especialidade: {especialidade_escolhida}")
    print(f"Médico: {medico_escolhido}")
    print(f"Data: {escolha_data}")
    print(f"Horário: {escolha_horario}")
    print(f"Local da consulta: {local}")
