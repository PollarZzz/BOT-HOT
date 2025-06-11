import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import GROUP_PREVIAS_LINK

# Lista fixa de mensagens provocantes
MENSAGENS = [
    "Aiiin, só de saber que você quer espiar... já me dá um arrepio aqui 😏\n\n"
    "Mas tudo bem, vou deixar... só um pouquinho, viu? Nada de exagerar. No grupo de prévias você vai ver só o comecinho do que te espera 💋",

    "Você é daquele tipo que diz 'só a cabecinha', né? 😈\n\n"
    "Pois bem... no grupo de prévias eu deixo você ver só um gostinho. Mas cuidado... depois não diga que eu não avisei, porque o vício é certo 🔥",

    "Ai, seu safadinho... já chegou todo curioso querendo espiar 😜\n\n"
    "Então toma! No grupo de prévias tem um aperitivo do que eu preparo pra quem se joga de verdade comigo... e olha, é de deixar molhadinh-- digo... curioso 😳",

    "Hmm, eu sabia que você ia querer espiar... esses olhinhos denunciam tudo 👀\n\n"
    "No grupo de prévias, eu libero só um teaser... mas já é o suficiente pra te deixar querendo mais. Tá pronto pra isso? 😘"
]

# Carrega os arquivos de mídia da pasta /images
def carregar_midias():
    pasta = "images"
    return [os.path.join(pasta, f) for f in os.listdir(pasta) if f.startswith("previa")]

# Função auxiliar para escolher uma entrada sem repetir até esgotar
def escolher_rotativo(chave: str, lista: list, context: ContextTypes.DEFAULT_TYPE):
    usados = context.bot_data.get(chave, [])
    restantes = list(set(lista) - set(usados))

    if not restantes:
        usados = []
        restantes = lista

    escolhido = random.choice(restantes)
    usados.append(escolhido)
    context.bot_data[chave] = usados
    return escolhido

async def previa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = escolher_rotativo("mensagens_usadas", MENSAGENS, context)
    midia_escolhida = escolher_rotativo("midias_usadas", carregar_midias(), context)

    botoes = InlineKeyboardMarkup([
        [InlineKeyboardButton("Entrar no Grupo de Prévias 🔥", url=GROUP_PREVIAS_LINK)],
        [InlineKeyboardButton("Voltar 🔙", callback_data="planos")]
    ])

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.delete()

    if midia_escolhida.endswith(".gif"):
        await context.bot.send_animation(
            chat_id=update.effective_chat.id,
            animation=open(midia_escolhida, "rb"),
            caption=texto,
            parse_mode="HTML",
            reply_markup=botoes
        )
    else:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=open(midia_escolhida, "rb"),
            caption=texto,
            parse_mode="HTML",
            reply_markup=botoes
        )
