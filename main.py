import logging
import signal
import sys
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PicklePersistence,
    ContextTypes,
    filters
)
from telegram import Update
from config import TELEGRAM_TOKEN, ADMIN_IDS
from src.database.mongo import retry_connection, create_indexes, close_connection

# Handlers
from src.handlers.admin.decisao import plano_escolhido
from src.handlers.admin.listagem import listar_pedidos, stats_handler # Importar stats_handler
from src.handlers.commands.start import start_handler
from src.handlers.commands.planos import planos
from src.handlers.commands.previa import previa
from src.handlers.commands.help import help_handler
from src.handlers.commands.menu import menu_handler # Importar o novo handler de menu
from src.handlers.callbacks.buttons import button_handler
from src.handlers.messages.coletar_nome import coletar_nome
from src.utils.broadcast import iniciar_broadcast, tratar_confirmacao_broadcast
from src.utils.decorators import somente_admins


# Configuração do logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_handlers(app):
    # Comandos
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("planos", planos))
    app.add_handler(CommandHandler("previa", previa))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("menu", menu_handler)) # Adicionar o comando /menu

    # Comandos de administração
    app.add_handler(CommandHandler("listar", listar_pedidos))
    app.add_handler(CommandHandler("stats", stats_handler)) # Adicionar o comando /stats

    # Mensagens normais
    # O MessageHandler para coletar_nome deve vir antes do iniciar_broadcast
    # para garantir que a coleta de nome/idade tenha prioridade.
    # filters.TEXT & ~filters.COMMAND filtra apenas mensagens de texto que não são comandos.
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, coletar_nome))

    # O iniciar_broadcast deve vir depois, para capturar mensagens de texto ou foto que
    # são comandos de broadcast (ex: /broadcast <texto> ou /broadcast com foto)
    # ou mensagens não tratadas pelos handlers anteriores.
    # No entanto, o decorator @somente_admins em iniciar_broadcast já garante que só admins possam usá-lo.
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, iniciar_broadcast))


    # Callbacks
    app.add_handler(CallbackQueryHandler(planos, pattern="^ver_conteudo$"))
    app.add_handler(CallbackQueryHandler(planos, pattern="^planos$"))
    app.add_handler(CallbackQueryHandler(previa, pattern="^espionar$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern="^voltar_menu$"))
    app.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_principal$")) # Adicionar callback para o menu
    app.add_handler(CallbackQueryHandler(plano_escolhido, pattern="^plano_mensal$"))
    app.add_handler(CallbackQueryHandler(plano_escolhido, pattern="^plano_vitalicio$"))
    app.add_handler(CallbackQueryHandler(plano_escolhido, pattern="^(liberar:|negar:)"))
    app.add_handler(CallbackQueryHandler(tratar_confirmacao_broadcast, pattern="^(confirmar_broadcast|cancelar_broadcast)$"))

    # Handler genérico de botões (deve ser o último para pegar os callbacks que não foram especificados acima)
    # É importante que o button_handler venha DEPOIS dos callbacks mais específicos.
    app.add_handler(button_handler)


def shutdown(signal, frame):
    logger.info("⏳ Encerrando bot...")
    close_connection()
    logger.info("✅ Conexão com Mongo fechada. Bot encerrado com sucesso.")
    sys.exit(0)

def main():
    retry_connection()
    create_indexes()

    persistence = PicklePersistence(filepath="bot_data")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).persistence(persistence).build()
    app.bot_data["admins"] = ADMIN_IDS

    setup_handlers(app)

    # Captura sinais de encerramento
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    app.run_polling()

if __name__ == "__main__":
    main()
