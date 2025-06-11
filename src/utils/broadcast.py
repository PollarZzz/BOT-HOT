import os
import asyncio
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest, Forbidden, RetryAfter

from src.utils.decorators import somente_admins
from src.database.mongo import get_collection

logger = logging.getLogger(__name__)

# Carrega RATE_LIMIT via variável de ambiente (se não existir, 0.05s entre envios)
RATE_LIMIT = float(os.getenv("RATE_LIMIT", "0.05"))

@somente_admins
async def iniciar_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id

    # 1) Captura raw (texto ou legenda) e remove o "/broadcast " do início
    if update.message:
        raw = update.message.caption or update.message.text or ""
        partes = raw.split(maxsplit=1)
        texto = partes[1] if len(partes) > 1 else ""
    else:
        texto = ""

    if not texto:
        await update.message.reply_text("❌ Você precisa escrever uma mensagem para o broadcast.")
        return

    # 2) Captura file_id da foto, se existir
    imagem = None
    if update.message and update.message.photo:
        imagem = update.message.photo[-1].file_id

    # 3) Salva rascunho no Mongo (coleção "broadcasts")
    broadcasts_coll = get_collection("broadcasts")
    broadcasts_coll.replace_one(
        {"admin_id": admin_id, "status": "pending"},
        {"admin_id": admin_id, "texto": texto, "imagem": imagem, "status": "pending"},
        upsert=True
    )

    # 4) Monta botão de confirmação/cancelamento
    botoes = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirmar Envio", callback_data="confirmar_broadcast")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_broadcast")]
    ])

    preview_texto = f"🛰️ Prévia do broadcast:\n\n{texto}"

    # 5) Envia a prévia (sem o "/broadcast")
    if imagem:
        await context.bot.send_photo(
            chat_id=admin_id,
            photo=imagem,
            caption=preview_texto,
            reply_markup=botoes
        )
    else:
        await context.bot.send_message(
            chat_id=admin_id,
            text=preview_texto,
            reply_markup=botoes
        )

async def enviar_broadcast_para_usuario(bot, telegram_id, texto, imagem=None):
    try:
        if imagem:
            await bot.send_photo(chat_id=telegram_id, photo=imagem, caption=texto)
        else:
            await bot.send_message(chat_id=telegram_id, text=texto)
        return True

    except RetryAfter as e:
        logger.warning(f"🌊 RetryAfter de {e.retry_after}s para usuário {telegram_id}. Aguardando...")
        await asyncio.sleep(e.retry_after)
        return await enviar_broadcast_para_usuario(bot, telegram_id, texto, imagem)

    except Forbidden as e:
        # Usuário bloqueou o bot ou chat inexistente: remove do DB usando telegram_id
        logger.info(f"🗑️ Removendo telegram_id {telegram_id} (Forbidden: {e}).")
        try:
            get_collection("users").delete_one({"telegram_id": telegram_id})
        except Exception as db_exc:
            logger.error(f"Erro ao remover usuário {telegram_id}: {db_exc}")
        return False

    except TelegramError as e:
        logger.warning(f"❌ Falha ao enviar para {telegram_id}: {e}")
        return False


@somente_admins
async def tratar_confirmacao_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = query.from_user.id
    await query.answer()

    # Valida callback_data
    if query.data == "cancelar_broadcast":
        # Cancela e apaga rascunho no Mongo
        get_collection("broadcasts").delete_many({"admin_id": admin_id, "status": "pending"})
        await query.edit_message_text("🚫 Broadcast cancelado.")
        return

    if query.data != "confirmar_broadcast":
        await query.answer("Opção inválida.", show_alert=True)
        return

    # Busca rascunho no Mongo
    broadcasts_coll = get_collection("broadcasts")
    draft = broadcasts_coll.find_one({"admin_id": admin_id, "status": "pending"})
    if not draft:
        await query.edit_message_text("⚠️ Nada para enviar.")
        return

    texto = draft["texto"]
    imagem = draft.get("imagem")

    users_coll = get_collection("users")
    enviados = 0
    falhas = 0

    # Usa estimated_document_count para grande volume
    try:
        total_users = users_coll.estimated_document_count()
    except Exception:
        total_users = users_coll.count_documents({})

    logger.info(f"📡 Iniciando broadcast. Total aproximado de usuários: {total_users}")

    # Atualiza status do draft para "sending" (caso queira rastrear)
    broadcasts_coll.update_one(
        {"_id": draft["_id"]},
        {"$set": {"status": "sending"}}
    )

    try:
        await query.edit_message_text("📡 Enviando broadcast para todos os usuários...")
    except BadRequest:
        # Se não puder editar (por ex. era mensagem de foto), delete e reenvie aviso
        try:
            await context.bot.delete_message(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id
            )
        except Exception as e:
            logger.warning(f"⚠️ Falha ao deletar mensagem: {e}")
        await context.bot.send_message(chat_id=admin_id, text="📡 Enviando broadcast para todos os usuários...")

    # Obtém todos os usuários de uma vez (cursor síncrono), usando o campo telegram_id
    usuarios = list(users_coll.find({}, {"telegram_id": 1}))
    count = 0

    for user in usuarios:
        telegram_id = user.get("telegram_id")
        if not telegram_id:
            continue

        sucesso = await enviar_broadcast_para_usuario(context.bot, telegram_id, texto, imagem)
        if sucesso:
            enviados += 1
        else:
            falhas += 1

        count += 1
        # Envia feedback parcial a cada 500 mensagens
        if count % 500 == 0:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📊 Progresso: {count}/{total_users} enviados. Falhas até agora: {falhas}."
            )

        await asyncio.sleep(RATE_LIMIT)

    # Remove rascunho
    broadcasts_coll.delete_one({"_id": draft["_id"]})

    summary = (
        f"✅ Broadcast concluído!\n"
        f"👥 Usuários Alvo: {total_users}\n"
        f"📬 Enviados: {enviados}\n"
        f"❌ Falhas: {falhas}"
    )
    logger.info(summary)

    await context.bot.send_message(chat_id=admin_id, text=summary)
