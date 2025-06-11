import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.textos import MENU_PRINCIPAL_MSG # Importa o texto para o menu principal

# Inicializando o logger
logger = logging.getLogger(__name__)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    nome_usuario = context.user_data.get("nome", user.first_name or "gostosura") # Usa o nome coletado, ou o primeiro nome, ou um fallback
    logger.info(f"Usuário ID={user.id}, Nome={nome_usuario} acessou o menu principal.")

    texto = MENU_PRINCIPAL_MSG.format(nome=nome_usuario)

    botoes = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ver Planos 🔥", callback_data="ver_conteudo")],
        [InlineKeyboardButton("Espiar Prévias 👀", callback_data="espionar")],
        [InlineKeyboardButton("Preciso de Ajuda 🆘", callback_data="voltar_menu")] # Reutiliza callback do help
    ])

    try:
        # Se for um callback_query, tenta editar a mensagem anterior
        if update.callback_query:
            query = update.callback_query
            await query.answer() # Responde ao callback para remover o estado de "carregando"
            # Tenta editar a mensagem original, se possível, para evitar poluir o chat
            try:
                await query.edit_message_text(
                    text=texto,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=botoes
                )
            except Exception as e:
                # Se não puder editar (ex: mensagem muito antiga ou de tipo diferente), envia uma nova
                logger.warning(f"Falha ao editar mensagem do menu via callback, enviando nova: {e}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=texto,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=botoes
                )
        else:
            # Se for um comando direto, envia uma nova mensagem
            await update.message.reply_text(
                text=texto,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=botoes
            )
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem do menu principal: {e}", exc_info=True)
