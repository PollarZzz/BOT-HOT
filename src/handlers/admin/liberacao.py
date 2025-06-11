import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import CallbackContext
from src.database.mongo import get_db
from datetime import datetime
from src.utils.textos import MENSAGEM_PEDIDO_APROVADO, MENSAGEM_PEDIDO_NEGADO
from config import GROUP_BASIC_LINK, GROUP_PREMIUM_LINK, SUPPORT_CONTACT

logger = logging.getLogger(__name__)

async def decidir_pedido(pedidos, id_produto, user_id, plano, nome_admin, id_admin, data_decisao, context, status):
    try:
        resultado = pedidos.update_one(
            {"id_produto": id_produto},
            {"$set": {
                "status": status,
                "admin": {"nome": nome_admin, "id": id_admin},
                "data_decisao": data_decisao
            }}
        )

        if resultado.modified_count == 0:
            logger.warning(f"[{status.upper()}] Nenhum pedido foi alterado para ID {id_produto}. Pode estar com status repetido.")
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Algo estranho aconteceu. Seu pedido não foi atualizado corretamente. Fale com o suporte.",
                parse_mode="HTML"
            )
            return

        logger.info(f"[{status.upper()}] Pedido {id_produto} {status} por {nome_admin} ({id_admin})")

        if status == "aprovado":
            mensagem = MENSAGEM_PEDIDO_APROVADO.format(plano=plano)

            # Define qual grupo enviar baseado no nome do plano
            if "Vitalício" in plano:
                grupo_link = GROUP_PREMIUM_LINK
            else:
                grupo_link = GROUP_BASIC_LINK

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Entrar no Grupo", url=grupo_link)],
                [InlineKeyboardButton("💬 Falar com o Suporte", url=SUPPORT_CONTACT)]
            ])

            imagem_path = 'images/aprovado.jpg'
            with open(imagem_path, 'rb') as imagem:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=imagem,
                    caption=mensagem,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        else:
            mensagem = MENSAGEM_PEDIDO_NEGADO.format(plano=plano)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Falar com o Suporte", url=SUPPORT_CONTACT)]
            ])
            await context.bot.send_message(
                chat_id=user_id,
                text=mensagem,
                parse_mode="HTML",
                reply_markup=keyboard
            )

    except Exception as e:
        logger.error(f"[ERRO {status.upper()}] ❌ Falha ao processar decisão do pedido {id_produto}: {e}", exc_info=True)
