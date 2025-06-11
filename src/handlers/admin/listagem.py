from telegram import Update
from telegram.ext import ContextTypes
from src.database.mongo import get_db
from datetime import datetime
from src.utils.decorators import somente_admins  # importe o decorador

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
    resultados = pedidos.find(query).sort("data", -1).limit(10)

    mensagens = [formatar_pedido(p) for p in resultados]
    if not mensagens:
        await update.message.reply_text("🧐 Nenhum pedido encontrado com esse critério.")
        return

    resposta = "<b>📋 Últimos Pedidos:</b>\n\n" + "\n\n".join(mensagens)
    await update.message.reply_text(resposta, parse_mode="HTML")
