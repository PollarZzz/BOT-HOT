import random
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database.mongo import collections
from src.utils.textos import COLETAR_NOME_MSG, IDADE_INVALIDA_MSG, FINALIZAR_MSG

# Inicializando o logger
logger = logging.getLogger(__name__)

async def coletar_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if not context.user_data:
        await update.message.reply_text("⚠️ Erro interno: os dados do usuário não puderam ser carregados.")
        return

    etapa = context.user_data.get("etapa")

    if etapa == "coletar_nome":
        nome = update.message.text.strip()
        context.user_data["nome"] = nome
        context.user_data["etapa"] = "coletar_idade"

        logger.info(f"Nome coletado: {nome} | ID={update.effective_user.id}")

        await asyncio.sleep(random.uniform(1.5, 3.5))
        await update.message.reply_text(COLETAR_NOME_MSG.format(nome=nome))

    elif etapa == "coletar_idade":
        idade_input = update.message.text.strip()

        if not idade_input.isdigit() or int(idade_input) < 18:
            await asyncio.sleep(random.uniform(1.5, 3.5))
            await update.message.reply_text(IDADE_INVALIDA_MSG)
            return

        idade = int(idade_input)
        context.user_data["idade"] = idade
        context.user_data["etapa"] = None

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
            logger.error(f"Erro ao salvar dados no banco: {e}")
            await update.message.reply_text("⚠️ Tive um probleminha técnico... tenta novamente mais tarde!")
            return

        await asyncio.sleep(random.uniform(1.5, 3.5))
        await update.message.reply_text(
            FINALIZAR_MSG.format(nome=nome),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Quero ver 😍", callback_data="ver_conteudo")],
                [InlineKeyboardButton("Melhor não 😳", callback_data="nao_ver_conteudo")]
            ])
        )
