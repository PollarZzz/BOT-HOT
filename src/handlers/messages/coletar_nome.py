import random
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database.mongo import collections
from src.utils.textos import COLETAR_NOME_MSG, IDADE_INVALIDA_MSG, FINALIZAR_MSG, MSG_COMANDO_DESCONHECIDO

# Inicializando o logger
logger = logging.getLogger(__name__)

async def coletar_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        # Ignora mensagens sem texto ou que não são mensagens
        return

    if not context.user_data:
        # Se user_data não existir, inicializa ou trata como erro
        context.user_data["etapa"] = None # Reseta a etapa para evitar loops
        await update.message.reply_text("⚠️ Tive um probleminha técnico e perdi o fio da meada... Por favor, tente novamente usando /start ou /menu.")
        logger.error(f"User data vazio para {update.effective_user.id}. Resetando etapa.")
        return

    etapa = context.user_data.get("etapa")

    if etapa == "coletar_nome":
        # Processa a coleta do nome
        nome = update.message.text.strip()
        if len(nome) < 2: # Adiciona uma pequena validação para o nome
            await update.message.reply_text("🤔 Hmm, seu nome parece um pouco curto. Por favor, digite seu nome completo ou um apelido com pelo menos 2 letras.")
            return

        context.user_data["nome"] = nome
        context.user_data["etapa"] = "coletar_idade"

        logger.info(f"Nome coletado: {nome} | ID={update.effective_user.id}")

        await asyncio.sleep(random.uniform(1.5, 3.5))
        await update.message.reply_text(COLETAR_NOME_MSG.format(nome=nome), parse_mode="HTML")

    elif etapa == "coletar_idade":
        # Processa a coleta da idade
        idade_input = update.message.text.strip()

        if not idade_input.isdigit() or int(idade_input) < 18:
            # Se a idade for inválida ou menor que 18
            await asyncio.sleep(random.uniform(1.5, 3.5))
            await update.message.reply_text(IDADE_INVALIDA_MSG, parse_mode="HTML")
            context.user_data["etapa"] = "aguardando_comando" # Define uma etapa para aguardar um comando explícito
            return

        idade = int(idade_input)
        context.user_data["idade"] = idade
        context.user_data["etapa"] = None # Limpa a etapa após a coleta bem-sucedida

        user = update.effective_user
        telegram_id = user.id
        username = user.username
        first_name = user.first_name
        nome = context.user_data.get("nome")

        logger.info(f"Usuário ID={telegram_id} | Nome={nome} | Idade={idade} salvo no banco.")

        collection = collections["users"]()

        try:
            collection.update_one(
                {"telegram_id": telegram_id},
                {
                    "$set": {
                        "nome": nome,
                        "idade": idade,
                        "username": username,
                        "first_name": first_name,
                        "ultimo_contato": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "data_criacao": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Erro ao salvar dados no banco: {e}", exc_info=True)
            await update.message.reply_text("⚠️ Tive um probleminha técnico... tenta novamente mais tarde! Se o problema persistir, use /help.")
            return

        await asyncio.sleep(random.uniform(1.5, 3.5))
        await update.message.reply_text(
            FINALIZAR_MSG.format(nome=nome),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Quero ver 😍", callback_data="ver_conteudo")],
                [InlineKeyboardButton("Melhor não 😳", callback_data="nao_ver_conteudo")],
                [InlineKeyboardButton("Voltar ao Menu Principal 🏠", callback_data="menu_principal")] # Adiciona botão para o menu
            ])
        )
    else:
        # Se nenhuma etapa de coleta de nome/idade estiver ativa, responde com mensagem de comando desconhecido
        # Isso cobre mensagens que não são comandos nem respostas esperadas
        await update.message.reply_text(MSG_COMANDO_DESCONHECIDO, parse_mode="HTML")
        logger.info(f"Mensagem inesperada de {update.effective_user.id}: '{update.message.text}'. Etapa atual: {etapa}")
