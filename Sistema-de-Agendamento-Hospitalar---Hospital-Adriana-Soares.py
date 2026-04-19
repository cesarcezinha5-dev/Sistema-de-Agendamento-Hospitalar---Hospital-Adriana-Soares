import json
import os

import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()

def enviar_email_confirmacao(destinatario, nome, especialidade, medico, data, horario, local):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")

    msg = EmailMessage()
    msg["Subject"] = "Confirmação de Agendamento - Hospital Adriana Soares"
    msg["From"] = remetente
    msg["To"] = destinatario

    msg.set_content(f"""
Olá {nome}, eu sou a Tayná, assistente inteligente do Hospital Adriana Soares.

Sua consulta foi agendada com sucesso!

Especialidade: {especialidade}
Médico(a): {medico}
Data: {data}
Horário: {horario}
Local: {local}

Agradecemos a preferência!
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remetente, senha_app)
        smtp.send_message(msg)


def salvar_consultas(consultas):
    with open("consultas.json", "w", encoding="utf-8") as arquivo:
        json.dump(consultas, arquivo, ensure_ascii=False, indent=4)


def carregar_consultas():
    if os.path.exists("consultas.json"):
        with open("consultas.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return []



consultas = carregar_consultas()


local = "Rua Jacobina, 123 - Centro, Guarulhos - SP"
def mostrar_datas():
    print("Datas disponíveis para essa especialidade:")
    datas = {
        "Dr. João": ["01/07/2026", "03/07/2026", "05/07/2026"],
        "Dra. Maria": ["02/05/2026", "04/07/2026", "06/05/2026"],
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
        "Dr. Gustavo": ["01/04/2024", "03/06/2026", "05/06/2026"],
        "Dra. Juliana": ["02/06/2026", "04/07/2026", "06/07/2026"],
        "Dr. Felipe": ["11/07/2026", "03/04/2026", "05/09/2026"],
        "Dra. Aline": ["22/08/2026", "04/05/2026", "06/05/2026"],
        "Dr. Ricardo": ["12/05/2026", "03/07/2026", "05/07/2026"],
        "Dra. Gabriela": ["20/07/2026", "04/05/2026", "06/05/2026"],
        "Dr. André": ["21/07/2026", "31/04/2026", "05/05/2026"],
        "Dra. Vanessa": ["02/05/2026", "04/05/2026", "06/05/2026"]
    }
    lista_datas = datas[medico_escolhido]
    return lista_datas
    
    
def horarios_disponiveis():
    print("Horários disponíveis para essa especialidade:")
    horarios = {
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
        "Dra. Vanessa": ["08:30", "12:30", "14:30"]
    }
    lista_horarios = horarios[medico_escolhido]
    return lista_horarios


def mostrar_medicos():
    print("Medicos disponíveis para essa especialidade:")
    medicos ={
        "Cardiologia": ["Dr. João", "Dra. Maria"],
        "Dermatologia": ["Dr. Carlos", "Dra. Ana"],
        "Endocrinologia": ["Dr. Pedro", "Dra. Luiza"],
        "Gastroenterologia": ["Dr. Lucas", "Dra. Fernanda"],
        "Ginecologia": ["Dr. Rafael", "Dra. Camila"],
        "Neurologia": ["Dr. Bruno", "Dra. Mariana"],
        "Oftalmologia": ["Dr. Gustavo", "Dra. Juliana"],
        "Ortopedia": ["Dr. Felipe", "Dra. Aline"],
        "Pediatria": ["Dr. Ricardo", "Dra. Gabriela"],
        "Psiquiatria": ["Dr. André", "Dra. Vanessa"]
    }
    lista_medicos = medicos[especialidade_escolhida]
    return lista_medicos
    
    
def mostrar_especialidades(): 
    print("Especialidades disponíveis:")
    especialidades = [
        "Cardiologia",
        "Dermatologia",
        "Endocrinologia",
        "Gastroenterologia",
        "Ginecologia",
        "Neurologia",
        "Oftalmologia",
        "Ortopedia",
        "Pediatria",
        "Psiquiatria",
    ]
    return especialidades


def escolher_opcao(lista, mensagem):
    while True:
        for i, item in enumerate(lista):
            print(f"{i+1} - {item}")

        try:
            escolha = int(input(mensagem))

            if escolha < 1 or escolha > len(lista):
                print("\nOpção inválida. Tente novamente.\n")
            else:
                return lista[escolha - 1]

        except ValueError:
            print("\nDigite apenas números.\n")


def menu_principal():
    menu = input("1 - Agendar consulta\n2 - Ver agendamentos\n3 - Cancelar consulta\n4 - Sair\n")
    return menu


def resumo_agendamento(nome, especialidade_escolhida, medico_escolhido, escolha_data, escolha_horario, local):
    print("Resumo do agendamento:")
    print(f"Paciente: {nome}")
    print(f"Especialidade: {especialidade_escolhida}")
    print(f"Médico: {medico_escolhido}")
    print(f"Data: {escolha_data}")
    print(f"Horário: {escolha_horario}")
    print(f"Local da consulta: {local}")


print("Bem-vindo ao Hospital Adriana Soares!\n")
print("Olá! Eu sou Tayná, assistente inteligente do Hospital Adriana Soares. Como posso te ajudar hoje? ")
print()

while True:
    menu = menu_principal()

    if menu == "1":
        print("Vamos marcar sua consulta. Por favor me informe algumas informações:")
        nome = input("Nome completo: ")
        numero = input("Numero de telefone: ")
        email = input("E-mail: ")

        especialidades = mostrar_especialidades()
        especialidade_escolhida = escolher_opcao(especialidades, "Digite o número da especialidade desejada: ")
        print(f"Você escolheu: {especialidade_escolhida}")

        lista_medicos = mostrar_medicos()
        medico_escolhido = escolher_opcao(lista_medicos, "Digite o número do médico que deseja: ")

        lista_datas = mostrar_datas()
        escolha_data = escolher_opcao(lista_datas, "Digite o número da data que deseja: ")

        lista_horarios = horarios_disponiveis()
        escolha_horario = escolher_opcao(lista_horarios, "Digite o número do horário que deseja: ")
        print()

        print("Consulta agendada com sucesso!\n")
        resumo_agendamento(nome, especialidade_escolhida, medico_escolhido, escolha_data, escolha_horario, local)
        print()

        consulta = {
        "paciente": nome,
        "especialidade": especialidade_escolhida,
        "medico": medico_escolhido,
        "data": escolha_data,
        "horario": escolha_horario,
        "local": local
        }
        consultas.append(consulta)
        salvar_consultas(consultas)

        try:
            enviar_email_confirmacao(email, nome, especialidade_escolhida, medico_escolhido, escolha_data, escolha_horario, local)
            print("E-mail de confirmação enviado com sucesso!\n")
        except:
            print("Não foi possível enviar o e-mail. Verifique as configurações.\n")

    elif menu == "2":
        if len(consultas) == 0:
            print("Nenhum agendamento encontrado.\n")
        else:
            print("Aqui estão seus agendamentos: \n")
            for c in consultas:
                resumo_agendamento(c["paciente"], c["especialidade"], c["medico"], c["data"], c["horario"], c["local"])
                print()
    
    elif menu == "3":
        if len(consultas) == 0:
            print("Nenhuma consulta cadastrada para cancelar.\n")
        else:
            print("Consultas cadastradas:\n")

            for i, c in enumerate(consultas):
                print(f"{i+1} - {c['paciente']} | {c['especialidade']} | {c['medico']} | {c['data']} às {c['horario']}")

            try:
                escolha_cancelar = int(input("\nDigite o número da consulta que deseja cancelar: "))
            except ValueError:
                print("Digite apenas números.\n")
                continue

            if escolha_cancelar < 1 or escolha_cancelar > len(consultas):
                print("Opção inválida.\n")
            else:
                consulta_cancelada = consultas.pop(escolha_cancelar - 1)
                salvar_consultas(consultas)
                print("\nConsulta cancelada com sucesso!")
                print(f"Paciente: {consulta_cancelada['paciente']}")
                print(f"Médico: {consulta_cancelada['medico']}")
                print(f"Data: {consulta_cancelada['data']} às {consulta_cancelada['horario']}\n")
    elif menu == "4":
        print("Obrigado pela preferência. Tenha um ótimo dia!")
        break
    