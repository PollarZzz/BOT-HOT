# src/database/mongo.py

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI, MONGO_DB_NAME
from time import sleep

client = None
db = None

# Logger
logger = logging.getLogger(__name__)

def retry_connection(retries=5, delay=3):
    """
    Tenta conectar ao MongoDB até 'retries' vezes, esperando 'delay' segundos entre tentativas.
    Se não conseguir, lança exceção.
    """
    global client, db
    for i in range(retries):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            db = client[MONGO_DB_NAME]
            client.server_info()  # Força a verificação de conexão
            logger.info("[MONGO] ✅ Conexão com MongoDB estabelecida.")
            return
        except ConnectionFailure as e:
            logger.warning(f"[MONGO] ⚠️ Tentativa {i+1}/{retries} falhou: {e}")
            sleep(delay)

    logger.error("[MONGO] ❌ Falha total ao conectar ao MongoDB.")
    raise Exception("Falha total ao conectar ao MongoDB.")

def get_collection(name):
    """
    Retorna a coleção 'name' do banco. 
    Se ainda não chamou retry_connection(), lança exceção.
    """
    if db is None:
        raise Exception("MongoDB não inicializado. Chame retry_connection() antes.")
    return db[name]

# Mapeamento das coleções fixas (opcional para facilitar uso)
collections = {
    "users": lambda: get_collection("users"),
    "logs": lambda: get_collection("logs"),
    "pagamentos": lambda: get_collection("pagamentos")
}

def create_indexes():
    """
    Cria índices necessários (por enquanto, apenas o 'telegram_id' em users).
    Deve ser chamado após retry_connection().
    """
    users = collections["users"]()
    users.create_index("telegram_id", unique=True)
    logger.info("[MONGO] ✅ Indexação criada para 'users.telegram_id'.")

def get_db():
    """
    Retorna o objeto 'db' (caso precise de algo além de get_collection).
    """
    if db is None:
        raise Exception("MongoDB não inicializado. Chame retry_connection() antes.")
    return db

def close_connection():
    """
    Fecha a conexão com o Mongo (se estiver aberta).
    """
    global client
    if client:
        client.close()
        logger.info("[MONGO] 🔌 Conexão com MongoDB encerrada.")
