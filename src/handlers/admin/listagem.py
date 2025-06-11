from telegram import Update
from telegram.ext import ContextTypes
from src.database.mongo import get_db, collections # Importar collections para acesso direto
from datetime import datetime
from src.utils.decorators import somente_admins
import logging

logger = logging.getLogger(__name__)

STATUS_ICONS = {
    "pendente": "🟡",
    "aprovado": "✅",
    "negado": "❌"
}

def formatar_pedido(pedido):
    icon = STATUS_ICONS.get(pedido["status"], "❔")
    data = pedido.get("data", datetime.utcnow()).strftime('%d/%m/%Y %H:%M')
    return (
        f"{icon} <b>{pedido['plano']}</b>\n"
        f"👤 {pedido['nome_usuario']} (<code>{pedido['user_id']}</code>)\n"
        f"🆔 <code>{pedido['id_produto']}</code>\n"
        f"📅 {data}\n"
        f"<b>Status:</b> {pedido['status'].capitalize()}\n"
        f"{'—'*25}"
    )

@somente_admins
async def listar_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Lista os últimos pedidos, opcionalmente filtrando por status.
    Ex: /listar pendente, /listar aprovado, /listar negado, /listar
    """
    db = get_db()
    pedidos = db["pedidos"]

    status = None
    if context.args:
        status = context.args[0].lower()
        if status not in STATUS_ICONS:
            await update.message.reply_text(
                "❌ Status inválido.\n"
                "Use: <code>/listar pendente</code>, <code>/listar aprovado</code> ou <code>/listar negado</code>.",
                parse_mode="HTML"
            )
            return

    query = {"status": status} if status else {}
    # Limita a 10 resultados para não sobrecarregar a mensagem
    resultados = pedidos.find(query).sort("data", -1).limit(10)

    mensagens = [formatar_pedido(p) for p in resultados]
    if not mensagens:
        await update.message.reply_text(f"🧐 Nenhum pedido encontrado com o status '{status}'." if status else "🧐 Nenhum pedido encontrado.")
        return

    resposta = "<b>📋 Últimos Pedidos:</b>\n\n" + "\n\n".join(mensagens)
    await update.message.reply_text(resposta, parse_mode="HTML")

@somente_admins
async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Mostra estatísticas rápidas do bot: total de usuários e pedidos pendentes.
    Comando: /stats
    """
    users_coll = collections["users"]()
    pedidos_coll = collections["pedidos"]()

    try:
        # Conta o total de usuários
        total_users = users_coll.count_documents({})

        # Conta os pedidos pendentes
        pedidos_pendentes = pedidos_coll.count_documents({"status": "pendente"})

        # Conta os pedidos aprovados
        pedidos_aprovados = pedidos_coll.count_documents({"status": "aprovado"})

        # Conta os pedidos negados
        pedidos_negados = pedidos_coll.count_documents({"status": "negado"})

        mensagem = (
            "📊 <b>Estatísticas do Bot:</b>\n\n"
            f"👥 Total de Usuários: <b>{total_users}</b>\n"
            f"🟡 Pedidos Pendentes: <b>{pedidos_pendentes}</b>\n"
            f"✅ Pedidos Aprovados: <b>{pedidos_aprovados}</b>\n"
            f"❌ Pedidos Negados: <b>{pedidos_negados}</b>\n\n"
            "<i>(Os dados são aproximados e atualizados na hora da consulta.)</i>"
        )
        await update.message.reply_text(mensagem, parse_mode="HTML")
        logger.info(f"Admin {update.effective_user.id} consultou estatísticas.")

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do bot: {e}", exc_info=True)
        await update.message.reply_text("❌ Ocorreu um erro ao buscar as estatísticas. Tente novamente mais tarde.")
