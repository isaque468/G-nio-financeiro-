# --- PASSO 1: INSTALAR A BIBLIOTECA (Execute esta célula separadamente ou esta linha primeiro) ---
!pip install python-telegram-bot

# --- PASSO 2: CÓDIGO DO SEU GÊNIO FINANCEIRO ---

import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import nest_asyncio
import re

# Permite executar loops asyncio aninhados no Colab
nest_asyncio.apply()

# SEU TOKEN DO BOTFATHER AQUI
TOKEN = 'SEU_TOKEN_DO_BOTFATHER_AQUI'

# --- FUNÇÃO AUXILIAR PARA CRIAR O TECLADO DE COMANDOS ---
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("/resumo"), KeyboardButton("/alterar_renda")],
        [KeyboardButton("/alterar_gasto"), KeyboardButton("/recomecar")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# --- FUNÇÕES HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name_from_telegram = update.effective_user.first_name 
    context.user_data['telegram_name'] = user_name_from_telegram
    
    # Verifica se já tem um nome personalizado salvo para o usuário
    nome_salvo = context.user_data.get('nome_personalizado')

    if nome_salvo:
        # Se o nome já existe, o bot diz uma frase de boas-vindas personalizada
        response = (
            f"Bem-vindo(a) de volta, {nome_salvo}! ✨\n"
            f"Quais das opções você deseja? Use os botões abaixo para interagir ou me diga o que você precisa."
        )
        context.chat_data['state'] = 'idle' # Define um estado ocioso, mas com nome salvo
    else:
        # Se o nome não existe, inicia o fluxo de coleta de nome
        response = (
            f"Olha o que temos aqui!! Um novo amigo em busca de um pouco de mágica financeira! ✨ Qual seu nome, Mestre?"
        )
        context.chat_data['state'] = 'awaiting_name'
    
    await update.message.reply_text(response, reply_markup=get_main_keyboard())


async def coletar_nome_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('state') == 'awaiting_name':
        nome_usuario = update.message.text
        context.user_data['nome_personalizado'] = nome_usuario 
        
        response = (
            f"Que MASSSSSAA, {nome_usuario}! Prazer enorme em te conhecer e em embarcar nessa aventura financeira com você! 😎\n"
            f"Pra gente começar a transformar sua vida financeira de um jeito mágico ✨, preciso conhecer um pouquinho do seu 'mapa do tesouro'. Qual a sua **renda principal** todo mês (apenas o valor, sem R$) e, se puder me contar, em que **dia(s) do mês** ela costuma cair na sua conta? 👇 Essa info é tipo a faísca pra acender nossa jornada! 😉"
        )
        await update.message.reply_text(response, reply_markup=get_main_keyboard()) 
        
        context.chat_data['state'] = 'awaiting_income_and_day'
    else:
        await update.message.reply_text("Hmm, o Gênio está um pouco confuso. Parece que não é a hora de coletar o nome. Vamos tentar de novo? Digite /start ou /recomecar para reiniciar ou me diga o que você precisa! 😉", reply_markup=get_main_keyboard())

async def coletar_renda_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('state') == 'awaiting_income_and_day':
        renda_info = update.message.text 

        renda_valor = None
        renda_match = re.search(r'(?:R\$?\s*)?(\d[\d\.,]*)', renda_info) 
        if renda_match:
            renda_valor_str = renda_match.group(1)
            renda_valor_str = renda_valor_str.replace('.', '').replace(',', '.') 
            try:
                renda_valor = float(renda_valor_str)
            except ValueError:
                renda_valor = None 

        dias_match = re.findall(r'\b(\d{1,2})\b', renda_info) 
        dias_pagamento = ", ".join(dias_match) if dias_match else "não informado(s)"

        if renda_valor is None:
            response = (
                f"Ops, {context.user_data.get('nome_personalizado', 'Mestre')}! Parece que não consegui entender o valor da sua renda. 😕\n"
                f"Por favor, tente digitar **apenas o número** (ex: 3000 ou 1500.50) e os dias se quiser. Assim o Gênio aprende rapidinho! 👇"
            )
            await update.message.reply_text(response, reply_markup=get_main_keyboard()) 
            return 

        context.user_data['renda_principal_valor'] = renda_valor 
        context.user_data['renda_principal_dias'] = dias_pagamento 
        
        response = (
            f"MASSSSSAA, {context.user_data.get('nome_personalizado', 'Mestre')}! Renda principal de R$ {renda_valor:.2f} e dia(s) {dias_pagamento} anotado(s)! 💪\n"
            f"O Gênio já está sentindo a energia da sua grana entrando! Agora que sabemos da sua renda, que tal começarmos a registrar os gastos para ver para onde essa grana está indo? 😉\n"
            f"Me diga seu **primeiro gasto** do mês: o que foi e quanto custou? Por exemplo: 'Comprei pão por 10 reais' ou 'Almoço 35'. Você pode até me dizer **vários gastos em uma única mensagem**, como 'Almoço 35, ração 120, conta de luz 85' 👇"
        )
        await update.message.reply_text(response, reply_markup=get_main_keyboard()) 
        
        context.chat_data['state'] = 'awaiting_first_expense' 

    else:
        # Se chegou aqui de forma inesperada durante o coletar_renda_principal, volta para o início.
        # No cenário de retomar conversa, isso não deveria acontecer se o estado for 'idle' ou None.
        await update.message.reply_text("Hmm, parece que pulamos uma etapa ou eu me perdi. Qual seu nome para eu te dar as boas-vindas novamente?", reply_markup=get_main_keyboard())
        context.chat_data['state'] = 'awaiting_name' 

# --- FUNÇÃO AUXILIAR PARA PARSEAR MÚLTIPLOS GASTOS ---
def parse_multi_gasto_info(gasto_info_string: str):
    gastos_encontrados = []
    
    parts = re.split(r'[,;]\s*| e\s+', gasto_info_string)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue

        descricao = "Item não especificado"
        valor = None
        
        valor_match = re.search(r'(?:R\$?\s*)?(\d[\d\.,]+)', part)
        if valor_match:
            valor_str = valor_match.group(1)
            valor_str = valor_str.replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
            except ValueError:
                valor = None 

            temp_descricao = re.sub(r'(?:R\$?\s*)?(\d[\d\.,]+)', '', part, 1).strip()
            
            if temp_descricao:
                descricao = temp_descricao
            elif valor_match.start() > 0:
                descricao = part[:valor_match.start()].strip()
            elif valor_match.end() < len(part):
                descricao = part[valor_match.end():].strip()
            
            if not descricao or descricao.lower() in ['por', 'de', 'com', 'um', 'uma', 'os', 'as', 'o', 'a']:
                descricao = "Item não especificado" 

        if valor is not None:
            gastos_encontrados.append({'descricao': descricao, 'valor': valor})
            
    return gastos_encontrados

async def coletar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('state') in ['awaiting_first_expense', 'collecting_expenses']:
        gasto_info_string = update.message.text
        
        gastos_detectados = parse_multi_gasto_info(gasto_info_string)

        if not gastos_detectados:
            response = (
                f"Ops, {context.user_data.get('nome_personalizado', 'Mestre')}! Não consegui entender nenhum gasto na sua mensagem. 😕\n"
                f"Por favor, tente digitar no formato 'nome do item X reais' ou 'valor item', como 'Almoço 35' ou 'Cinema 25.50'. "
                f"Você pode tentar vários na mesma linha: 'Almoço 35, ração 120, conta de luz 85'. 👇"
            )
            await update.message.reply_text(response, reply_markup=get_main_keyboard())
            return 

        if 'gastos' not in context.user_data:
            context.user_data['gastos'] = []
        
        registrados_feedback = []
        for gasto in gastos_detectados:
            context.user_data['gastos'].append({
                'descricao': gasto['descricao'],
                'valor': gasto['valor']
            })
            registrados_feedback.append(f"'{gasto['descricao']}' de R$ {gasto['valor']:.2f}")

        if len(registrados_feedback) == 1:
            response = f"Anotado! {registrados_feedback[0]} foi registrado! ✅\n"
        else:
            response = "Anotados! Os seguintes gastos foram registrados: \n" + "\n".join([f"- {g}" for g in registrados_feedback]) + " ✅\n"
        
        response += f"Quer registrar outro gasto agora? Ou quer ver um resumo do que já temos? 😉"
        await update.message.reply_text(response, reply_markup=get_main_keyboard()) 
        
        context.chat_data['state'] = 'collecting_expenses' 

    else:
        # Se chegou aqui de forma inesperada durante o coletar_gasto, volta para o início ou estado ocioso.
        # No cenário de retomar conversa, isso não deveria acontecer se o estado for 'idle' ou None.
        await update.message.reply_text("Hmm, o Gênio está um pouco confuso. Qual seu nome para eu te dar as boas-vindas novamente?", reply_markup=get_main_keyboard())
        context.chat_data['state'] = 'awaiting_name' 

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome = context.user_data.get('nome_personalizado', 'Mestre') # Pega o nome personalizado
    renda = context.user_data.get('renda_principal_valor') 
    gastos = context.user_data.get('gastos', [])
    
    total_gastos = sum([g['valor'] for g in gastos if g['valor'] is not None])
    saldo = renda - total_gastos if renda is not None else -total_gastos 
    
    response = f"📊 **RESUMO FINANCEIRO - {nome.upper()}** 📊\n\n"
    response += f"💰 Renda Principal: R$ {renda:.2f}\n" if renda is not None else "💰 Renda Principal: Não informada\n"
    response += f"💸 Total de Gastos: R$ {total_gastos:.2f}\n"
    response += f"💵 Saldo Atual: R$ {saldo:.2f}\n\n"
    
    if gastos:
        response += "📝 **Seus gastos registrados:**\n"
        for i, gasto in enumerate(gastos, 1):
            valor_str = f"R$ {gasto['valor']:.2f}" if gasto['valor'] is not None else "valor não detectado"
            response += f"{i}. {gasto['descricao']} - {valor_str}\n"
        response += "\nContinue registrando seus gastos ou use os botões abaixo para outras ações! 😉"
    else:
        response += "Você ainda não registrou nenhum gasto. Que tal começar a registrar agora? 😉"
    
    await update.message.reply_text(response, reply_markup=get_main_keyboard()) 
    context.chat_data['state'] = 'collecting_expenses'

async def alterar_renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Certo, Mestre! Qual é o **novo valor da sua renda principal** (apenas o número, sem R$) e, "
        "se quiser, o(s) dia(s) do mês em que ela costuma cair? 👇",
        reply_markup=ReplyKeyboardRemove() 
    )
    context.chat_data['state'] = 'awaiting_income_correction' 

async def processar_nova_renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('state') == 'awaiting_income_correction':
        nova_renda_info = update.message.text

        renda_valor = None
        renda_match = re.search(r'(?:R\$?\s*)?(\d[\d\.,]*)', nova_renda_info) 
        if renda_match:
            renda_valor_str = renda_match.group(1)
            renda_valor_str = renda_valor_str.replace('.', '').replace(',', '.') 
            try:
                renda_valor = float(renda_valor_str)
            except ValueError:
                renda_valor = None 
        
        dias_match = re.findall(r'\b(\d{1,2})\b', nova_renda_info) 
        dias_pagamento = ", ".join(dias_match) if dias_match else "não informado(s)"

        if renda_valor is None:
            await update.message.reply_text(
                "Ops! Não consegui entender o novo valor da sua renda. Por favor, digite **apenas o número** "
                "e os dias (ex: 3500 ou 2800.75 dia 10). 🤔",
                reply_markup=ReplyKeyboardRemove() 
            )
            return 

        context.user_data['renda_principal_valor'] = renda_valor
        context.user_data['renda_principal_dias'] = dias_pagamento

        nome_usuario = context.user_data.get('nome_personalizado', 'Mestre')
        await update.message.reply_text(
            f"Maravilha, {nome_usuario}! Sua renda principal foi atualizada para R$ {renda_valor:.2f} "
            f"e dias de pagamento para {dias_pagamento}! ✅\n"
            f"Agora você pode continuar registrando gastos ou usar os botões abaixo."
        )
        context.chat_data['state'] = 'collecting_expenses'
        await update.message.reply_text("Escolha uma opção:", reply_markup=get_main_keyboard()) 
    else:
        # Se chegou aqui de forma inesperada, volta para o início ou estado ocioso.
        await update.message.reply_text("Hmm, o Gênio está um pouco confuso. Qual seu nome para eu te dar as boas-vindas novamente?", reply_markup=get_main_keyboard())
        context.chat_data['state'] = 'awaiting_name'

async def alterar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gastos = context.user_data.get('gastos', [])
    if not gastos:
        await update.message.reply_text("Você ainda não registrou nenhum gasto para alterar. Comece registrando alguns! 😉", reply_markup=get_main_keyboard())
        context.chat_data['state'] = 'collecting_expenses'
        return
    
    response = "📝 **Seus gastos registrados:**\n"
    for i, gasto in enumerate(gastos, 1):
        valor_str = f"R$ {gasto['valor']:.2f}" if gasto['valor'] is not None else "valor não detectado"
        response += f"{i}. {gasto['descricao']} - {valor_str}\n"
    
    response += "\nQual o **número do gasto** que você deseja alterar? (Digite apenas o número, ex: 1)"
    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove()) 
    context.chat_data['state'] = 'awaiting_expense_index_for_alteration' 

async def processar_indice_gasto_alteracao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('state') == 'awaiting_expense_index_for_alteration':
        try:
            indice_str = update.message.text.strip()
            indice = int(indice_str) - 1 

            gastos = context.user_data.get('gastos', [])
            if 0 <= indice < len(gastos):
                context.user_data['temp_expense_index_to_alter'] = indice
                gasto_selecionado = gastos[indice]
                await update.message.reply_text(
                    f"Certo! Você quer alterar o gasto '{gasto_selecionado['descricao']}' de R$ {gasto_selecionado['valor']:.2f}.\n"
                    f"Qual o **novo valor** para este gasto? Se quiser, pode incluir uma nova descrição. "
                    f"(Ex: 'Novo almoço 40' ou 'Só 38.50')",
                    reply_markup=ReplyKeyboardRemove() 
                )
                context.chat_data['state'] = 'awaiting_new_expense_value_for_alteration' 
            else:
                await update.message.reply_text(
                    f"Ops! O número '{indice_str}' não corresponde a nenhum gasto na sua lista. "
                    f"Por favor, digite um número válido na lista de gastos. 😉",
                    reply_markup=ReplyKeyboardRemove() 
                )
        except ValueError:
            await update.message.reply_text(
                "Por favor, digite apenas o **número** do gasto que você quer alterar. 🤔",
                reply_markup=ReplyKeyboardRemove() 
            )
    else:
        # Se chegou aqui de forma inesperada, volta para o início ou estado ocioso.
        await update.message.reply_text("Hmm, o Gênio está um pouco confuso. Qual seu nome para eu te dar as boas-vindas novamente?", reply_markup=get_main_keyboard())
        context.chat_data['state'] = 'awaiting_name'

async def processar_novo_valor_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.chat_data.get('state') == 'awaiting_new_expense_value_for_alteration':
        indice = context.user_data.get('temp_expense_index_to_alter')
        if indice is None:
            await update.message.reply_text(
                "Parece que perdi qual gasto você queria alterar. Por favor, comece de novo com /alterar_gasto.",
                reply_markup=get_main_keyboard() 
            )
            context.chat_data['state'] = 'collecting_expenses'
            return

        novo_gasto_info = update.message.text
        gastos_detectados = parse_multi_gasto_info(novo_gasto_info) 

        if not gastos_detectados or len(gastos_detectados) > 1 or gastos_detectados[0]['valor'] is None:
            await update.message.reply_text(
                f"Ops! Não consegui entender o novo valor para este gasto. Por favor, digite o valor (e descrição) novamente (Ex: '45.00' ou 'Gasolina 80.50'). Tente focar em um item por vez aqui. 🤔",
                reply_markup=ReplyKeyboardRemove() 
            )
            return 

        nova_descricao = gastos_detectados[0]['descricao']
        novo_valor = gastos_detectados[0]['valor']

        gastos = context.user_data.get('gastos', [])
        if 0 <= indice < len(gastos):
            gastos[indice]['descricao'] = nova_descricao
            gastos[indice]['valor'] = novo_valor
            
            await update.message.reply_text(
                f"Gasto '{nova_descricao}' atualizado para R$ {novo_valor:.2f}! ✅\n"
                f"Você pode registrar mais gastos ou usar os botões abaixo."
            )
        else:
            await update.message.reply_text(
                "Parece que o gasto que você estava alterando sumiu. Por favor, tente novamente com /alterar_gasto.",
                reply_markup=get_main_keyboard() 
            )
        
        if 'temp_expense_index_to_alter' in context.user_data:
            del context.user_data['temp_expense_index_to_alter']
        context.chat_data['state'] = 'collecting_expenses'
        await update.message.reply_text("Escolha uma opção:", reply_markup=get_main_keyboard()) 
    else:
        # Se chegou aqui de forma inesperada, volta para o início ou estado ocioso.
        await update.message.reply_text("Hmm, o Gênio está um pouco confuso. Qual seu nome para eu te dar as boas-vindas novamente?", reply_markup=get_main_keyboard())
        context.chat_data['state'] = 'awaiting_name'

# --- Lidar com Respostas Negativas ---
async def handle_negative_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    negative_keywords = ["não", "nao", "no", "parar", "fim", "chega"]
    
    if update.message.text.lower() in negative_keywords:
        if context.chat_data.get('state') in ['awaiting_first_expense', 'collecting_expenses']:
            nome_personalizado = context.user_data.get('nome_personalizado', 'Mestre')
            await update.message.reply_text(
                f"Ok, investidor {nome_personalizado}! Se precisar de algo, é só dizer 'Oi' ou usar os comandos. 😉",
                reply_markup=get_main_keyboard()
            )
            context.chat_data['state'] = 'idle' # Define o estado como 'idle' em vez de None
            return True
    return False


async def handle_general_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Primeiro, tenta lidar com respostas negativas (antes de tentar parsear como gasto)
    if await handle_negative_response(update, context):
        return 

    state = context.chat_data.get('state')
    
    if state == 'awaiting_name':
        await coletar_nome_usuario(update, context)
    elif state == 'awaiting_income_and_day':
        await coletar_renda_principal(update, context)
    elif state in ['awaiting_first_expense', 'collecting_expenses']:
        await coletar_gasto(update, context)
    elif state == 'awaiting_income_correction':
        await processar_nova_renda(update, context)
    elif state == 'awaiting_expense_index_for_alteration':
        await processar_indice_gasto_alteracao(update, context)
    elif state == 'awaiting_new_expense_value_for_alteration':
        await processar_novo_valor_gasto(update, context)
    elif state == 'idle' or state is None: # Se o estado for 'idle' ou 'None' (estado inicial/resetado)
        nome_personalizado = context.user_data.get('nome_personalizado')
        
        if update.message.text and update.message.text.lower() == 'oi':
            if nome_personalizado:
                await update.message.reply_text(
                    f"Oi, {nome_personalizado}! Quais das opções você deseja? ✨",
                    reply_markup=get_main_keyboard()
                )
                context.chat_data['state'] = 'idle' # Mantém no estado ocioso
            else:
                # Se disse 'Oi' mas não tem nome salvo, inicia o fluxo de start
                await start(update, context)
        else: # Mensagem não reconhecida em estado ocioso
            if nome_personalizado:
                await update.message.reply_text(
                    f"Olá, {nome_personalizado}! Não entendi o que você disse. 😕\n"
                    f"Use os botões abaixo para interagir, digite um comando como /resumo, "
                    f"ou diga 'Oi' para me chamar novamente! ✨",
                    reply_markup=get_main_keyboard()
                )
            else:
                await update.message.reply_text(
                    "Olá! Sou o Gênio Financeiro! 🧞‍♂️\n"
                    "Use os botões abaixo para interagir, digite um comando como /resumo, "
                    "ou diga 'Oi' para recomeçar! ✨",
                    reply_markup=get_main_keyboard() 
                )
            context.chat_data['state'] = 'idle' # Garante que o estado seja 'idle' se não for um comando
    else: # Catch-all para estados não tratados explicitamente
        await update.message.reply_text(
            f"Desculpe, {context.user_data.get('nome_personalizado', 'Mestre')}, parece que estou em um estado inesperado. 😅\n"
            "Por favor, use os botões abaixo ou digite /start ou /recomecar para reiniciar nossa magia!",
            reply_markup=get_main_keyboard()
        )
        context.chat_data['state'] = 'idle' # Volta para um estado seguro


async def main():
    print("🚀 Iniciando o Bot do Gênio Financeiro...")
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recomecar", start)) 
    application.add_handler(CommandHandler("resumo", resumo))
    application.add_handler(CommandHandler("alterar_renda", alterar_renda))
    application.add_handler(CommandHandler("alterar_gasto", alterar_gasto))
    
    # Este MessageHandler captura todas as mensagens de texto que não são comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_general_message))
    
    print("✅ Bot configurado! Iniciando polling...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("🎉 Bot do Gênio Financeiro está rodando!")
    print("💡 Para parar o bot, interrompa a execução da célula (Runtime > Interrupt execution)")
    
    try:
        await asyncio.Event().wait()  
    except KeyboardInterrupt:
        print("🛑 Parando o bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("👋 Bot parado com sucesso!")

if __name__ == '__main__':
    if TOKEN == 'SEU_TOKEN_DO_BOTFATHER_AQUI':
        print("❌ ERRO: Você precisa substituir 'SEU_TOKEN_DO_BOTFATHER_AQUI' pelo seu token real do BotFather!")
        print("📱 Como obter o token:")
        print("1. Abra o Telegram e procure por @BotFather")
        print("2. Digite /newbot e siga as instruções")
        print("3. Copie o token que ele te der e cole na variável TOKEN")
    else:
        asyncio.run(main())

