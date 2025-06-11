import os
import html
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.utils.textos import PLANO_MSG
from src.utils.helpers import escolher_rotativo  # Importando escolher_rotativo

# Logger
logger = logging.getLogger(__name__)

# Botões dos planos
BOTOES_PLANOS = InlineKeyboardMarkup([
    [InlineKeyboardButton("💖 Plano Básico - R$29,90", url="https://app.pushinpay.com.br/service/pay/9F1CFA95-5837-4A4A-B778-1CAAD275F3D7")],
    [InlineKeyboardButton("💎 Plano Premium - R$69,90", url="https://app.pushinpay.com.br/service/pay/9F207329-CAD9-483F-86E7-223D670343B7")],
    [InlineKeyboardButton("👀 Quero só espiar primeiro", callback_data="espionar")]
])


def carregar_midias():
    pasta = "images"
    return [os.path.join(pasta, f) for f in os.listdir(pasta) if f.startswith("planos")]

async def planos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome_raw = context.user_data.get("nome", "gostoso")
    nome = html.escape(nome_raw)
    texto = PLANO_MSG.format(nome=nome)

    user = update.effective_user
    logger.info(f"Usuário ID={user.id}, Nome={nome} abriu a tela de planos.")

    if update.callback_query:
        query = update.callback_query
        try:
            await query.answer()
            await query.message.delete()
        except Exception as e:
            logger.warning(f"Falha ao tentar deletar mensagem ou responder callback: {e}")
        chat_id = query.message.chat.id
    else:
        chat_id = update.effective_chat.id

    midias_disponiveis = carregar_midias()

    if midias_disponiveis:
        midia_escolhida = escolher_rotativo("midias_planos_usadas", midias_disponiveis, context)
    else:
        midia_escolhida = None

    try:
        if midia_escolhida:
            with open(midia_escolhida, "rb") as midia:
                if midia_escolhida.endswith(".gif"):
                    await context.bot.send_animation(
                        chat_id=chat_id,
                        animation=midia,
                        caption=texto,
                        parse_mode="HTML",
                        reply_markup=BOTOES_PLANOS
                    )
                else:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=midia,
                        caption=texto,
                        parse_mode="HTML",
                        reply_markup=BOTOES_PLANOS
                    )
        else:
            fallback_img_url = "https://via.placeholder.com/600x400?text=Planos+Indispon%C3%ADveis"
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=fallback_img_url,
                caption=texto,
                parse_mode="HTML",
                reply_markup=BOTOES_PLANOS
            )
    except Exception as e:
        logger.error(f"Erro ao enviar mídia dos planos: {e}")
