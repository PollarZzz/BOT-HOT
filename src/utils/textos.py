import logging
logger = logging.getLogger(__name__)

START_MSG = (
    "🔥 Oi gostosura, <b>{nome}</b> 💋\n\n"
    "Parabéns... você acaba de tropeçar no lugar que vai bagunçar tua cabeça e deixar seu lado safado sem freio.\n\n"
    "Antes da gente se afundar na indecência, preciso de uma coisinha rápida (prometo que não dói 😏):\n\n"
    "👉 Você tem mais de 18 aninhos pra brincar sem medo?"
)

PLANO_MSG = (
    "Aiii, eu sabia que você era dos meus, <b>{nome}</b>... safadinho(a) de primeira viagem 😈🔥\n\n"
    "Aqui não tem censura, não tem frescura — só desejo bruto e conteúdo que deixa qualquer um de joelhos.\n\n"
    "💋 Mas ó... prazer bom tem preço.\n"
    "Escolhe um dos meus planos e vem se lambuzar no conteúdo premium que vai te fazer gemer só de lembrar 😏💦"
)

MENSAGENS_PREVIA = [
    "Aiiiin, só de saber que você quer espiar... já sobe aquele arrepio aqui 😈💦\n\n"
    "Mas tudo bem... vou ser boazinha e deixar. No grupo de prévias você vai provar só a pontinha do que eu tenho pra oferecer... cuidado pra não viciar, hein? 💋",

    "Hmm, você é do tipo 'só a cabecinha', né, safadinho(a)? 😏\n\n"
    "No grupo de prévias eu te deixo sentir o gostinho — mas depois não vem chorar querendo mais... porque a vontade vai te consumir inteiro(a). 🔥🍑",

    "Ai, seu taradinho(a)... já chegou querendo ver o que não devia 😜\n\n"
    "Então vem! No grupo de prévias você pega só um teaser... um aperitivo quente pra deixar tua mente suja borbulhando de vontade. 👅💦",

    "Eu sabia, esses teus olhinhos safados não enganam... 👀\n\n"
    "No grupo de prévias tem só um flash do que te espera... só cuidado pra não se apaixonar — meu conteúdo não é pra amadores. 😘🔥"
]

HELP_MSG = (
    "🥵 Se perdeu, foi, safadinho(a)?\n\n"
    "<b>Calma, bebê...</b> Eu tô aqui pra te guiar — daquele jeitinho que deixa qualquer um de perna bamba. 😈💦\n\n"
    "Olha só o que você pode me pedir:\n\n"
    "✨ <b>/start</b> – Começar do zero... tipo quando a gente finge que é a primeira vez. 🥵\n"
    "🔥 <b>/planos</b> – Ver tudo que eu escondo... sem censura, sem vergonha. 😏\n"
    "👀 <b>/previas</b> – Só uma espiadinha marota... pra ficar querendo mais. 😘\n"
    "🆘 <b>/help</b> – Se perder de novo, é só chamar, neném. 💋\n\n"
    "E se o fogo for grande demais pra aguentar sozinho(a), fala comigo direto aqui: 👉 <a href='{suporte}'>suporte</a>"
)

COLETAR_NOME_MSG = (
    "👅 Hmmm, {nome}... que nome gostoso de falar.\n\n"
    "Agora me diz uma coisa rapidinho... quantos aninhos você tem, hein? "
    "Prometo não te julgar... só me deixar ainda mais animadinha. 😏🔥"
)

IDADE_INVALIDA_MSG = (
    "🙅‍♀️ Ownnn, que peninha...\n\n"
    "Eu até queria brincar contigo, mas só posso me divertir com maiores de idade, viu?\n"
    "Cresce rápido e volta... quem sabe a gente não realiza umas fantasias depois? 💋"
)

FINALIZAR_MSG = (
    "Aiiin, <b>{nome}</b>... Agora que sei teu nomezinho e tua idade, deixa eu confessar uma coisinha? 😏\n\n"
    "<b>Você me deixou doidinha de curiosidade 👀</b>\n"
    "Tô aqui pensando... será que você aguenta ver o que eu tô prestes a liberar? 😈🔥\n"
    "Mas ó, cuidado... depois não adianta implorar pra parar, viu? 😜💦"
)


MENSAGEM_USUARIO_PEDIDO = (
    "😏 <b>Hmm... Pedido recebido com sucesso!</b>\n\n"
    "👤 <b>Nome:</b> {nome_usuario}\n"
    "📦 <b>Delícia escolhida:</b> {nome_plano}\n"
    "💸 <b>Valor da tentação:</b> {valor}\n"
    "🆔 <b>ID do Pecado:</b> <code>{id_produto}</code>\n\n"
    "📌 <b>Para concluir o seu pedido, envie o comprovante de pagamento para nossa garotinha perversa:</b> <a href=\"{suporte}\">Manuzinha</a>\n"
    "📱 <b>Chave PIX:</b> <code>{chave_pix}</code>\n\n"
    "⚠️ <b>Importante:</b> O pagamento deve ser feito em até 24 horas, senão o pedido será cancelado.\n"
    "🔒 <b>Fique tranquilo(a), sua privacidade é sagrada!</b>\n\n"
    "⏳ Agora senta aí e espera, que a aprovação tá vindo com gosto...\n"
    "Assim que for liberado, eu mesma vou te dar aquela notificação gostosa, aqui no privado. 😌\n\n"
    "💋 Enquanto isso, clica nos botõezinhos abaixo — tem coisa boa te esperando...")

MENSAGEM_ADMIN_PEDIDO = (
    "📅 <b>Novo Pedido Recebido!</b>\n\n"
    "👤 <b>Usuário:</b> {nome_usuario} (<code>{user_id}</code>)\n"
    "📦 <b>Produto:</b> {nome_plano}\n"
    "💰 <b>Valor:</b> {valor}\n"
    "🆔 <b>ID do Produto:</b> <code>{id_produto}</code>\n"
    "🕒 <b>Data:</b> {data}")

RESPOSTAS_BOTOES = {
    "tem_18": {
        "mensagem": (
            "😏 Hmmm, maior de idade e cheio(a) de más intenções, né? "
            "Adoro... Agora me conta, como eu posso te chamar enquanto te deixo sem ar? 🥵💬"
        ),
        "etapa": "coletar_nome"
    },
    "nao_tem_18": {
        "mensagem": (
            "🚫 Tão novinho assim? Que peninha... "
            "Aqui é só pros grandinhos que aguentam o tranco, bebê.\n\n"
            "Vai crescer e volta logo... Quem sabe um dia você não aguenta a pressão? 😈"
        ),
        "etapa": "nao_tem_18"
    },
    "nao_ver_conteudo": {
        "mensagem": (
            "🙈 Awnnn, tímido(a) desse jeito? "
            "Tudo bem, eu entendo... Nem todo mundo tá pronto pra tanta ousadia.\n\n"
            "Mas ó, quando bater aquela vontade de brincar sem vergonha, é só me chamar, tá? 🔥😉"
        ),
        "etapa": "nao_ver_conteudo"
    }
}


MENSAGEM_PEDIDO_APROVADO = (
    "💋 OHHH YES! Tua inscrição no <b>{plano}</b> foi <b>liberada</b> com sucesso, delícia.\n\n"
    "Agora que a porteira abriu, tá na hora de você se jogar nesse mundinho sujo que a gente adora. "
    "Vai ter conteúdo quente, provocação sem censura e diversão pra fazer até santo se benzer.\n\n"
    "👀 Clica no botão, entra pro grupo e mostra que tu não é de ficar só olhando. "
    "E se bater aquela dúvida, chama no suporte — mas vem preparado, porque aqui a gente não passa a mão na cabeça. ❤️‍🔥"
)

MENSAGEM_PEDIDO_NEGADO = (
    "😈 Vixe... deu ruim, safadinho(a)! Seu pedido no <b>{plano}</b> foi <b>negado</b>.\n\n"
    "Mas relaxa, ninguém vai te deixar na seca por muito tempo... ainda tem jeito de virar esse jogo. "
    "Dá aquela choradinha básica no suporte — talvez com jeitinho (ou uma promessa indecente), a gente libera sua entrada.\n\n"
    "💬 Clica no botão, corre lá e mostra que você sabe jogar o jogo. A vida é pros ousados, bebê."
)