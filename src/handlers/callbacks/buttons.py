import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from src.utils.textos import RESPOSTAS_BOTOES
from config import GROUP_PREVIAS_LINK

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    resposta = RESPOSTAS_BOTOES.get(data)
    if resposta:
        await asyncio.sleep(1.5)

        if data == "nao_ver_conteudo":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👀 Conhecer a Manu", url=GROUP_PREVIAS_LINK)]
            ])
            await query.message.reply_text(resposta["mensagem"], reply_markup=keyboard)
        else:
            await query.message.reply_text(resposta["mensagem"])

        context.user_data["etapa"] = resposta["etapa"]
    else:
        await query.message.reply_text("❌ Essa opção não é válida. Tenta de novo ou chama o suporte!")

button_handler = CallbackQueryHandler(button, pattern='^(tem_18|nao_tem_18|nao_ver_conteudo)$')
