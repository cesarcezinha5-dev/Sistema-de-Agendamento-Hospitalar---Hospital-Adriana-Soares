import smtplib

from funcoes import (
    LOCAL,
    carregar_consultas,
    escolher_opcao,
    enviar_email_confirmacao,
    horarios_disponiveis,
    menu_principal,
    mostrar_datas,
    mostrar_especialidades,
    mostrar_medicos,
    resumo_agendamento,
    salvar_consultas,
)


def solicitar_texto(mensagem, nome_campo):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print(f"{nome_campo} não pode ficar vazio.\n")


def solicitar_email():
    while True:
        email = input("E-mail: ").strip()
        if "@" in email and "." in email:
            return email
        print("Digite um e-mail válido.\n")


def iniciar():
    print("Bem-vindo ao Hospital Adriana Soares!\n")
    print("Olá! Eu sou Tayná, assistente inteligente do Hospital Adriana Soares. Como posso te ajudar hoje?")
    print()

    consultas = carregar_consultas()

    while True:
        menu = menu_principal()

        if menu == "1":
            print("Vamos marcar sua consulta. Por favor, informe algumas informações:")
            nome = solicitar_texto("Nome completo: ", "Nome")
            telefone = solicitar_texto("Número de telefone: ", "Número de telefone")
            email = solicitar_email()
            print("Ótimo! Agora vamos escolher a especialidade para sua consulta.\n")

            especialidades = mostrar_especialidades()
            especialidade_escolhida = escolher_opcao(
                especialidades, "Digite o número da especialidade desejada: "
            )
            print(f"Você escolheu: {especialidade_escolhida}")
            print("-" * 40)

            lista_medicos = mostrar_medicos(especialidade_escolhida)
            medico_escolhido = escolher_opcao(
                lista_medicos, "Digite o número do médico que deseja: "
            )
            print("-" * 40)

            lista_datas = mostrar_datas(medico_escolhido)
            escolha_data = escolher_opcao(
                lista_datas, "Digite o número da data que deseja: "
            )
            print("-" * 40)

            lista_horarios = horarios_disponiveis(medico_escolhido)
            escolha_horario = escolher_opcao(
                lista_horarios, "Digite o número do horário que deseja: "
            )
            print("-" * 40)

            consulta = {
                "paciente": nome,
                "telefone": telefone,
                "especialidade": especialidade_escolhida,
                "medico": medico_escolhido,
                "data": escolha_data,
                "horario": escolha_horario,
                "local": LOCAL,
            }

            consultas.append(consulta)
            salvar_consultas(consultas)
            print("Consulta agendada com sucesso!\n")
            resumo_agendamento(
                nome,
                especialidade_escolhida,
                medico_escolhido,
                escolha_data,
                escolha_horario,
                LOCAL,
            )

            try:
                enviar_email_confirmacao(
                    email,
                    nome,
                    especialidade_escolhida,
                    medico_escolhido,
                    escolha_data,
                    escolha_horario,
                    LOCAL,
                )
                print("\nE-mail de confirmação enviado com sucesso!\n")
            except (RuntimeError, smtplib.SMTPException, OSError) as erro:
                print(f"\nNão foi possível enviar o e-mail: {erro}\n")

        elif menu == "2":
            if not consultas:
                print("Nenhum agendamento encontrado.\n")
            else:
                print("Aqui estão seus agendamentos:\n")
                for consulta in consultas:
                    resumo_agendamento(
                        consulta["paciente"],
                        consulta["especialidade"],
                        consulta["medico"],
                        consulta["data"],
                        consulta["horario"],
                        consulta["local"],
                    )
                    print()

        elif menu == "3":
            if not consultas:
                print("Nenhuma consulta cadastrada para cancelar.\n")
            else:
                print("Consultas cadastradas:\n")
                for i, consulta in enumerate(consultas):
                    print(
                        f"{i + 1} - {consulta['paciente']} | "
                        f"{consulta['especialidade']} | {consulta['medico']} | "
                        f"{consulta['data']} às {consulta['horario']}"
                    )

                try:
                    escolha_cancelar = int(
                        input("\nDigite o número da consulta que deseja cancelar: ")
                    )
                except (TypeError, ValueError):
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
                    print(
                        f"Data: {consulta_cancelada['data']} às "
                        f"{consulta_cancelada['horario']}\n"
                    )

        elif menu == "4":
            print("Obrigado pela preferência. Tenha um ótimo dia!")
            break
        else:
            print("Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    iniciar()