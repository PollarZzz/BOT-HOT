import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import SUPPORT_CONTACT
from src.utils.textos import HELP_MSG

# Inicializando o logger
logger = logging.getLogger(__name__)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Usuário ID={user.id}, Nome={user.first_name} pediu ajuda.")

    texto = HELP_MSG.format(suporte=SUPPORT_CONTACT)

    botoes = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ver Planos 🔥", callback_data="ver_conteudo")],
        [InlineKeyboardButton("Espiar Prévias 👀", callback_data="espionar")]
    ])

    try:
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.edit_text(
                text=texto,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=botoes
            )
        else:
            await update.message.reply_text(
                text=texto,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=botoes
            )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem de help: {e}")
