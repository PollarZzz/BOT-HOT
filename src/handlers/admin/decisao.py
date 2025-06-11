from html import escape
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from datetime import datetime
from config import SUPPORT_CONTACT, LOG_CHANNEL_ID, GROUP_WARNINGS_LINK, CHAVE_PIX
from src.database.mongo import get_db
from src.utils.textos import MENSAGEM_USUARIO_PEDIDO, MENSAGEM_ADMIN_PEDIDO
from src.handlers.admin.liberacao import decidir_pedido  # <- IMPORTANDO DECIDIR_PEDIDO
import random
import string

logger = logging.getLogger(__name__)

PLANOS = {
    "plano_mensal": {"nome": "Plano Mensal 💖", "valor": "R$29,90"},
    "plano_vitalicio": {"nome": "Plano Vitalício 💎", "valor": "R$69,90"}
}

def gerar_id_produto():
    return f"PROD-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def registrar_pedido(user_id, nome_usuario, nome_plano, valor, id_produto):
    try:
        db = get_db()
        pedidos = db["pedidos"]
        resultado = pedidos.insert_one({
            "user_id": user_id,
            "nome_usuario": nome_usuario,
            "plano": nome_plano,
            "valor": valor,
            "id_produto": id_produto,
            "data": datetime.utcnow(),
            "status": "pendente"
        })
        if not resultado.acknowledged:
            raise Exception("❌ Falha ao registrar pedido no MongoDB.")
    except Exception as e:
        logger.error(f"[MONGO] ❌ Falha ao registrar pedido no banco:", exc_info=True)

def montar_botoes_usuario():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Entrar no Grupo de Avisos", url=GROUP_WARNINGS_LINK)],
        [InlineKeyboardButton("💬 Falar com o Suporte", url=SUPPORT_CONTACT)],
    ])

def montar_botoes_admin(id_produto):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Liberar", callback_data=f"liberar:{id_produto}"),
            InlineKeyboardButton("❌ Negar", callback_data=f"negar:{id_produto}")
        ]
    ])

async def plano_escolhido(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        user = query.from_user
        await query.answer()

        if not query or not query.data:
            return await query.message.reply_text("❌ Não foi possível processar sua escolha.")

        if query.data.startswith("liberar:") or query.data.startswith("negar:"):
            action, id_produto = query.data.split(":")
            db = get_db()
            pedidos = db["pedidos"]
            pedido = pedidos.find_one({"id_produto": id_produto})

            if not pedido:
                return await query.message.reply_text("❌ Pedido não encontrado no banco.")

            user_id = pedido["user_id"]
            nome_admin = user.full_name or user.username or "Admin Desconhecido"
            id_admin = user.id
            data_decisao = datetime.utcnow()

            if action == "liberar":
                await decidir_pedido(pedidos, id_produto, user_id, pedido["plano"], nome_admin, id_admin, data_decisao, context, status="aprovado")
                await query.message.reply_text(f"✅ Pedido {id_produto} liberado com sucesso.")
            else:
                await decidir_pedido(pedidos, id_produto, user_id, pedido["plano"], nome_admin, id_admin, data_decisao, context, status="negado")
                await query.message.reply_text(f"❌ Pedido {id_produto} negado.")
            return

        if query.message.chat.type != "private":
            return await query.message.reply_text(
                "⚠️ Por favor, finalize seu pedido no privado com o bot."
            )

        plano = query.data
        if plano not in PLANOS:
            return await query.message.reply_text("❌ Eita! Plano inválido.")

        nome_plano = PLANOS[plano]["nome"]
        valor = PLANOS[plano]["valor"]
        id_produto = gerar_id_produto()
        nome_usuario = user.full_name or user.username or "Usuário Desconhecido"
        nome_usuario = nome_usuario.strip()
        user_id = user.id

        logger.info(f"[PEDIDO] {nome_usuario} ({user_id}) escolheu {nome_plano} - {id_produto}")

        mensagem_usuario = MENSAGEM_USUARIO_PEDIDO.format(
            nome_usuario=escape(nome_usuario),
            nome_plano=nome_plano,
            valor=valor,
            id_produto=id_produto,
            suporte=SUPPORT_CONTACT,
            chave_pix=CHAVE_PIX
        )

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=mensagem_usuario,
            parse_mode="HTML",
            reply_markup=montar_botoes_usuario()
        )

        registrar_pedido(user_id, nome_usuario, nome_plano, valor, id_produto)

        log_mensagem = MENSAGEM_ADMIN_PEDIDO.format(
            nome_usuario=escape(nome_usuario),
            user_id=user_id,
            nome_plano=nome_plano,
            valor=valor,
            id_produto=id_produto,
            data=datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S') + " UTC"
        )

        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=log_mensagem,
            parse_mode="HTML",
            reply_markup=montar_botoes_admin(id_produto)
        )

    except Exception as e:
        logger.error(f"[ERRO PLANO] ❌ Falha ao processar escolha do plano: {e}", exc_info=True)
