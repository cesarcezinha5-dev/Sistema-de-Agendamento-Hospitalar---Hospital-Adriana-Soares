Sistema de Agendamento Hospitalar - Hospital Adriana Soares

Desenvolvi um sistema em Python para simular o agendamento de consultas médicas em um hospital, 
permitindo que o usuário selecione a especialidade, médico disponível, data e horário da consulta através de um menu interativo.

O sistema possui funcionalidades completas de CRUD, permitindo:

Agendar consultas
Visualizar todos os agendamentos realizados
Cancelar consultas já cadastradas
Armazenar os dados em arquivo JSON para manter o histórico salvo

Além disso, implementei envio automático de e-mail de confirmação utilizando SMTP (Gmail), 
garantindo uma experiência mais realista e próxima de sistemas utilizados no mercado.

Projeto desenvolvido com foco em praticar lógica de programação, listas, dicionários, funções, tratamento de erros, 
manipulação de arquivos e integração com envio de e-mails.

## Interface web em React

A aplicação também possui uma interface responsiva em React. Ela permite visualizar os agendamentos, pesquisar e cancelar consultas, além de agendar uma nova consulta com horários ocupados atualizados. Os dados continuam salvos em `consultas.json`, e o envio de confirmação por e-mail usa as credenciais configuradas no arquivo `.env`.

### Contas e privacidade

Cada paciente cria uma conta com e-mail e senha para acessar a área de agendamentos. A API associa as consultas à conta autenticada e só permite que o próprio paciente as visualize ou cancele. As senhas são armazenadas como hashes em `usuarios.json`, arquivo ignorado pelo Git.

Configure `FLASK_SECRET_KEY` no `.env` para manter as sessões válidas após reiniciar a API. Gere uma chave com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Em produção, use HTTPS e configure `SESSION_COOKIE_SECURE=true`. Agendamentos antigos, sem conta associada, não são exibidos na área do paciente.

### Executar em desenvolvimento

1. Instale as dependências Python na raiz do projeto:

   ```bash
   pip install -r requirements.txt
   ```

2. Em um terminal, inicie a API:

   ```bash
   python api.py
   ```

3. Em outro terminal, inicie o React:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Abra o endereço exibido pelo Vite, normalmente `http://localhost:5173`.

### Executar a versão compilada

Na pasta `frontend`, execute `npm run build`. Depois, na raiz do projeto, execute `python api.py` e acesse `http://127.0.0.1:5000`.
