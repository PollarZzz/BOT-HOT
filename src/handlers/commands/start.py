import os
import html
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

from src.database.mongo import get_collection  # <— Importa get_collection para Mongo
from src.utils.textos import START_MSG  # <- Importando o texto

# Inicializando o logger
logger = logging.getLogger(__name__)

IMAGE_PATH = "Images/start.jpg"

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    telegram_id = user.id
    nome = html.escape(user.first_name or "Anônimo")

    # 1) Registra/atualiza usuário no Mongo
    try:
        users_coll = get_collection("users")
        users_coll.update_one(
            {"telegram_id": telegram_id},
            {
                "$set": {
                    "telegram_id": telegram_id,
                    "first_name": nome,
                    "username": user.username or "",
                    "registered_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        logger.info(f"📥 Usuário {telegram_id} registrado/atualizado no Mongo.")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar usuário {telegram_id} no Mongo: {e}")

    # 2) Monta teclado de confirmação de idade
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim, tenho 18 anos", callback_data="tem_18"),
            InlineKeyboardButton("❌ Não tenho 18 anos", callback_data="nao_tem_18"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = START_MSG.format(nome=nome)

    # 3) Envia imagem (se existir) ou só texto
    try:
        if os.path.exists(IMAGE_PATH):
            with open(IMAGE_PATH, "rb") as img:
                await update.message.reply_photo(
                    photo=img,
                    caption=msg,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text(
                text=msg + "\n\n⚠️ (Imagem não encontrada, mas a diversão continua...)",
                parse_mode="HTML",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem de start a {telegram_id}: {e}")

start_command = CommandHandler("start", start_handler)
