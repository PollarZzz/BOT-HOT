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
from src.handlers.commands.start import start_handler
from src.handlers.commands.planos import planos
from src.handlers.commands.previa import previa
from src.handlers.commands.help import help_handler
from src.handlers.callbacks.buttons import button_handler
from src.handlers.messages.coletar_nome import coletar_nome
from src.utils.broadcast import iniciar_broadcast, tratar_confirmacao_broadcast
from src.utils.decorators import somente_admins
# Importando os handlers necessários

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

    # Mensagens normais
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, coletar_nome))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, iniciar_broadcast))

    # Callbacks
    app.add_handler(CallbackQueryHandler(planos, pattern="^ver_conteudo$"))
    app.add_handler(CallbackQueryHandler(planos, pattern="^planos$"))
    app.add_handler(CallbackQueryHandler(previa, pattern="^espionar$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern="^voltar_menu$"))
    app.add_handler(CallbackQueryHandler(plano_escolhido, pattern="^plano_mensal$"))
    app.add_handler(CallbackQueryHandler(plano_escolhido, pattern="^plano_vitalicio$"))
    app.add_handler(CallbackQueryHandler(plano_escolhido, pattern="^(liberar:|negar:)"))
    app.add_handler(CallbackQueryHandler(tratar_confirmacao_broadcast, pattern="^(confirmar_broadcast|cancelar_broadcast)$"))

    # Handler genérico
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
