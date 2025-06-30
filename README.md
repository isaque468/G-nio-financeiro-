# 🧞‍♂️ Bot do Gênio Financeiro

Um bot do Telegram inteligente para controle financeiro pessoal, desenvolvido em Python com integração ao Google Gemini AI.

## 🚀 Funcionalidades

- ✨ Controle de renda e gastos pessoais
- 📊 Resumos financeiros automáticos
- 🤖 Integração com Google Gemini AI
- 💬 Interface amigável via Telegram
- 🔄 Atualizações em tempo real

## 📋 Pré-requisitos

### 1. Token do Bot do Telegram
1. Acesse [@BotFather](https://t.me/BotFather) no Telegram
2. Digite `/newbot` e siga as instruções
3. Guarde o token fornecido

### 2. API Key do Google Gemini
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma nova API Key
3. Guarde a chave fornecida

## 🛠️ Instalação Local

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com seus tokens
```

## ⚙️ Configuração

1. Copie o arquivo `.env.example` para `.env`
2. Edite o arquivo `.env` e adicione:
   - `TELEGRAM_BOT_TOKEN`: Token do seu bot
   - `GEMINI_API_KEY`: Sua API key do Gemini

```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GEMINI_API_KEY=AIzaSyABC123...
```

## 🚀 Deploy no Render.com

### Método 1: Via GitHub (Recomendado)

1. **Fork/Clone** este repositório para sua conta GitHub
2. Acesse [Render.com](https://render.com) e faça login
3. Clique em **"New +"** → **"Web Service"**
4. Conecte seu repositório GitHub
5. Configure:
   - **Name**: `telegram-bot-genio-financeiro`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: Free
6. Adicione as variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN`: Seu token do Telegram
   - `GEMINI_API_KEY`: Sua API key do Gemini
   - `PORT`: 10000
7. Clique em **"Create Web Service"**

### Método 2: Via render.yaml

1. Certifique-se que o arquivo `render.yaml` está no seu repositório
2. No Render, use **"New +"** → **"Blueprint"**
3. Conecte seu repositório
4. Configure as variáveis de ambiente no painel

## 🔧 Execução Local

```bash
# Execute o bot
python main.py
```

O bot estará disponível no Telegram e o health check em `http://localhost:10000/health`

## 📁 Estrutura do Projeto

```
├── main.py              # Código principal do bot
├── requirements.txt     # Dependências Python
├── .env.example         # Exemplo de variáveis de ambiente
├── render.yaml          # Configuração para deploy no Render
├── README.md           # Este arquivo
└── .gitignore          # Arquivos ignorados pelo Git
```

## 🔍 Health Check

O bot inclui um servidor HTTP para health check, essencial para o Render:
- URL: `https://seu-app.onrender.com/health`
- Resposta: `{"status": "healthy", "service": "telegram-bot"}`

## 🐛 Solução de Problemas

### Bot não responde
- Verifique se o `TELEGRAM_BOT_TOKEN` está correto
- Confirme se o bot foi iniciado via `/start`

### Erro de API Gemini
- Verifique se `GEMINI_API_KEY` está correto
- Confirme se a API está habilitada no Google Cloud

### Deploy falhando no Render
- Verifique se todas as variáveis de ambiente estão configuradas
- Confirme se o `requirements.txt` está presente
- Verifique os logs do deploy no painel do Render

## 📝 Comandos do Bot

- `/start` - Inicia o bot e configuração inicial
- `/resumo` - Mostra resumo financeiro atual
- `/alterar_renda` - Modifica a renda principal
- `/alterar_gasto` - Altera gastos registrados
- `/recomecar` - Reinicia a configuração

## 🔒 Segurança

- ⚠️ **NUNCA** commiteu arquivos `.env` no Git
- 🔑 Mantenha seus tokens seguros
- 🔄 Regenere tokens se comprometidos

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs no painel do Render
2. Confirme todas as configurações
3. Teste localmente primeiro

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.
