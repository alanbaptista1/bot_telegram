from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters
from telegram import KeyboardButton, ReplyKeyboardMarkup
from datetime import datetime
import json
import requests

# Telegram Bot Token
BOT_TOKEN = "7396724622:AAE8uo61UlXybp__AWZO6KSSq7GSBWbXEJc"

# Configurações da API Secullum
AUTH_URL = "https://autenticador.secullum.com.br/token"
BANKS_URL = "https://autenticador.secullum.com.br/ContasSecullumExterno/ListarBancos"
FUNCIONARIOS_URL = "https://pontowebintegracaoexterna.secullum.com.br/IntegracaoExterna/Funcionarios"
USERNAME = "alan.111@hotmail.com"
PASSWORD = "Escola@12"
CLIENT_ID = "3"

#Configurações para incluir ponto
INCLUIR_PONTO_URL = "https://pontowebintegracaoexterna.secullum.com.br/IntegracaoExterna/InclusaoPonto/Incluir"
BANCO_ID = 58785
CPF_FIXO = "239.146.990-00"
PIS_FIXO = "823914699008"
PRECISAO_FIXA = 7


# Autenticar e obter token
def obter_access_token():
    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "client_id": CLIENT_ID
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(AUTH_URL, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get("access_token")
    return None

# Buscar funcionários
def buscar_funcionarios_visiveis(token, banco_id):
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "secullumidbancoselecionado": str(banco_id)
    })

    response = session.get(FUNCIONARIOS_URL)
    if response.status_code == 200:
        funcionarios = response.json()
        visiveis = [f for f in funcionarios if f.get("Invisivel") is False]
        return visiveis
    else:
        return None
    
"""# Autorizar a localização
async def enviarlocalizacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botao = KeyboardButton(text="📍 Enviar minha localização", request_location=True)
    teclado = ReplyKeyboardMarkup([[botao]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Clique no botão abaixo para enviar sua localização:",
        reply_markup=teclado
    )"""
    
""" # Comando /enviarlocalizacao
from telegram.ext import MessageHandler, filters

async def tratar_localizacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    local = update.message.location
    if local:
        latitude = local.latitude
        longitude = local.longitude
        await update.message.reply_text(f"📌 Sua localização:\nLatitude: {latitude}\nLongitude: {longitude}")
    else:
        await update.message.reply_text("❌ Não consegui pegar a localização.") """


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie o comando /funcionarios <id_do_banco> para listar os funcionários visíveis.")

# Comando /funcionarios
async def funcionarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Por favor, informe o ID do banco. Exemplo: /funcionarios 123")
        return

    banco_id = context.args[0]
    token = obter_access_token()
    if not token:
        await update.message.reply_text("❌ Erro ao autenticar com a API da Secullum.")
        return

    lista = buscar_funcionarios_visiveis(token, banco_id)
    if lista is None:
        await update.message.reply_text("❌ Erro ao buscar funcionários.")
        return

    if not lista:
        await update.message.reply_text("⚠️ Nenhum funcionário visível encontrado.")
        return

    for func in lista:
        texto = (
            f"👤 *{func.get('Nome')}*\n"
            f"📧 Email: {func.get('Email', 'Não informado')}\n"
            f"📱 Celular: {func.get('Celular', 'Não informado')}\n"
            f"📄 CPF: {func.get('Cpf', 'Não informado')}\n"
            f"🏢 Empresa: {func['Empresa'].get('Nome') if func.get('Empresa') else 'Não informado'}\n"
            f"💼 Cargo: {func['Funcao'].get('Descricao') if func.get('Funcao') else 'Não informado'}\n"
            f"🗂 Departamento: {func['Departamento'].get('Descricao') if func.get('Departamento') else 'Não informado'}\n"
            f"🕒 Horário: {func['Horario'].get('Descricao') if func.get('Horario') else 'Não informado'}\n"
            f"📆 Admissão: {func.get('Admissao', 'Não informado')}\n"
            f"🟢 Permite Ponto Manual: {func.get('PermiteInclusaoPontoManual')}\n"
        )
        await update.message.reply_text(texto, parse_mode="Markdown")
        
# /Listarbancos
async def listarbancos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_token = obter_access_token()
    if not access_token:
        await update.message.reply_text("❌ Erro ao autenticar com a API da Secullum.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(BANKS_URL, headers=headers)

    if response.status_code == 200:
        bancos = response.json()
        if not bancos:
            await update.message.reply_text("⚠️ Nenhum banco encontrado.")
            return

        resposta = "🏦 *Lista de Bancos Disponíveis:*\n"
        for banco in bancos:
            resposta += f"➡️ *ID:* {banco.get('id')} - *Nome:* {banco.get('nome')}\n"

        await update.message.reply_text(resposta, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Erro ao listar bancos: {response.status_code}")

# Registrar ponto /incluirponto
async def incluirponto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botao = KeyboardButton("📍 Enviar localização para bater ponto", request_location=True)
    teclado = ReplyKeyboardMarkup([[botao]], resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Clique no botão abaixo para enviar sua localização atual e registrar o ponto:",
        reply_markup=teclado
    )
# Mensagem sobre incluir ponto

async def tratar_localizacao_para_ponto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    local = update.message.location
    print("🛰️ Função de localização iniciada")
    if not local:
        await update.message.reply_text("❌ Localização não recebida.")
        return

    latitude = local.latitude
    longitude = local.longitude
    data_hora = datetime.now().isoformat()

    token = obter_access_token()
    if not token:
        await update.message.reply_text("❌ Falha ao autenticar com a API da Secullum.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "secullumidbancoselecionado": str(BANCO_ID),
        "Content-Type": "application/json-patch+json"
    }

    payload = {
        "pis": PIS_FIXO,
        "cpf": CPF_FIXO,
        "endereco": "",  # Podemos preencher usando API de geolocalização se quiser
        "latitude": latitude,
        "longitude": longitude,
        "precisao": PRECISAO_FIXA,
        "dataHora": data_hora,
        "justificativa": "Ponto registrado via Telegram",
        "foto": "",
        "identificacaoDispositivo": "TelegramBot",
        "marcacaoOffline": True
    }

    response = requests.post(INCLUIR_PONTO_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        await update.message.reply_text("✅ Ponto registrado com sucesso!")
    else:
        await update.message.reply_text(f"❌ Erro ao registrar ponto: {response.status_code}\n{response.text}")



# Rodar o bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("funcionarios", funcionarios))
app.add_handler(CommandHandler("listarbancos", listarbancos))
#app.add_handler(CommandHandler("enviarlocalizacao", enviarlocalizacao))
#app.add_handler(MessageHandler(filters.LOCATION, tratar_localizacao))
app.add_handler(CommandHandler("incluirponto", incluirponto))
app.add_handler(MessageHandler(filters.LOCATION, tratar_localizacao_para_ponto))

print("🤖 Bot rodando no Telegram...")
app.run_polling()
