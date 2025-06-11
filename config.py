import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(key: str, required: bool = True, cast_func=str, default=None):
    value = os.getenv(key, default)
    if required and (value is None or value == ""):
        raise ValueError(f"⚠️ Variável de ambiente obrigatória '{key}' não foi definida.")
    try:
        return cast_func(value) if value is not None else None
    except Exception as e:
        raise ValueError(f"❌ Erro ao converter variável '{key}': {e}")

# Variáveis principais
TELEGRAM_TOKEN = get_env_var("TELEGRAM_TOKEN")
MONGO_URI = get_env_var("MONGO_URI")
MONGO_DB_NAME = get_env_var("MONGO_DB_NAME")
LOG_CHANNEL_ID = get_env_var("LOG_CHANNEL_ID", cast_func=int)
CHAVE_PIX = get_env_var("CHAVE_PIX")

# Admins
ADMIN_IDS = get_env_var("ADMIN_IDS", cast_func=lambda x: list(map(int, x.split(","))))

# IDs de grupos
GROUP_WARNINGS_ID = get_env_var("GROUP_WARNINGS_ID", cast_func=int)
GROUP_PREVIAS_ID = get_env_var("GROUP_PREVIAS_ID", cast_func=int)
GROUP_BASIC_ID = get_env_var("GROUP_BASIC_ID", cast_func=int)
GROUP_PREMIUM_ID = get_env_var("GROUP_PREMIUM_ID", cast_func=int)

# Links de convite dos grupos
GROUP_WARNINGS_LINK = get_env_var("GROUP_WARNINGS_LINK")
GROUP_PREVIAS_LINK = get_env_var("GROUP_PREVIAS_LINK")
GROUP_BASIC_LINK = get_env_var("GROUP_BASIC_LINK")
GROUP_PREMIUM_LINK = get_env_var("GROUP_PREMIUM_LINK")

# Contato de suporte
SUPPORT_CONTACT = get_env_var("SUPPORT_CONTACT")
