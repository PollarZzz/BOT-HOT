import random
from telegram.ext import ContextTypes

def escolher_rotativo(chave: str, lista: list, context: ContextTypes.DEFAULT_TYPE) -> str:
    usados = context.bot_data.get(chave, [])
    restantes = list(set(lista) - set(usados))

    if not restantes:
        usados = []
        restantes = lista

    escolhido = random.choice(restantes)
    usados.append(escolhido)
    context.bot_data[chave] = usados

    return escolhido
