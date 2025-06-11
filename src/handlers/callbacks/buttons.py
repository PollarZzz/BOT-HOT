import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from src.utils.textos import RESPOSTAS_BOTOES # Importa os textos atualizados
from config import GROUP_PREVIAS_LINK

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    resposta = RESPOSTAS_BOTOES.get(data)
    if resposta:
        await asyncio.sleep(1.5)

        # Atualiza a etapa do usuário no user_data
        context.user_data["etapa"] = resposta["etapa"]

        if data == "nao_ver_conteudo":
            # Para 'nao_ver_conteudo', mostra o botão para o grupo de prévias e o menu/start
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👀 Conhecer a Manu", url=GROUP_PREVIAS_LINK)],
                [InlineKeyboardButton("Voltar ao Menu Principal 🏠", callback_data="menu_principal")] # Novo botão para o menu
            ])
            await query.message.reply_text(resposta["mensagem"], reply_markup=keyboard, parse_mode="HTML")
        elif data == "nao_tem_18":
            # Para 'nao_tem_18', não oferece opções adicionais além da mensagem
            # A mensagem já orienta o usuário a usar /start ou /help
            await query.message.reply_text(resposta["mensagem"], parse_mode="HTML")
        else:
            # Para outras respostas, como 'tem_18', apenas envia a mensagem
            await query.message.reply_text(resposta["mensagem"], parse_mode="HTML")
    else:
        # Mensagem de fallback se a opção do botão não for encontrada
        await query.message.reply_text("❌ Essa opção não é válida. Por favor, tente novamente ou use /help para ver os comandos disponíveis.")

# Define o CallbackQueryHandler para os padrões específicos
# Adiciona "menu_principal" ao padrão para ser tratado pelo button handler ou um novo handler
button_handler = CallbackQueryHandler(button, pattern='^(tem_18|nao_tem_18|nao_ver_conteudo)$')
