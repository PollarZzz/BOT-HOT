from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

def somente_admins(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            if update.message:
                await update.message.reply_text("⚠️ Usuário não identificado.")
            elif update.callback_query:
                await update.callback_query.answer("⚠️ Usuário não identificado.", show_alert=True)
            logger.warning("⚠️ Ação bloqueada: usuário não identificado.")
            return

        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            logger.warning(f"🚫 Acesso negado para user_id={user_id}. Não é admin.")
            if update.message:
                await update.message.reply_text(
                    "🚫 Este comando é restrito aos administradores.\n"
                    "Se você acha que houve algum engano, fale com o suporte."
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "🚫 Acesso restrito a administradores.", show_alert=True
                )
            return  # Bloqueia execução do método protegido

        return await func(update, context, *args, **kwargs)

    return wrapper