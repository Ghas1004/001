from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Static, Input

import random
import threading

import os
from nava import play

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SOM = os.path.join(BASE_DIR, "teste.wav")

play(ARQUIVO_SOM, async_mode=True)

# ==========================================
# PERSONAGENS
# ==========================================

personagens = {

    1: {
        "nome": "Guerreiro ⚔️",
        "vida": 120,

        "armas": {

            "Espada": {
                "dano": 20,
                "descricao": "Ataque rápido"
            },

            "Machado": {
                "dano": 30,
                "descricao": "Dano pesado"
            },

            "Martelo": {
                "dano": 40,
                "descricao": "Muito forte"
            }
        }
    },

    2: {
        "nome": "Arqueiro 🏹",
        "vida": 90,

        "armas": {

            "Arco": {
                "dano": 25,
                "descricao": "Longa distância"
            },

            "Besta": {
                "dano": 35,
                "descricao": "Disparo forte"
            },

            "Adaga": {
                "dano": 15,
                "descricao": "Ataque rápido"
            }
        }
    },

    3: {
        "nome": "Mago 🪄",
        "vida": 80,

        "armas": {

            "Fogo": {
                "dano": 45,
                "descricao": "Magia destrutiva"
            },

            "Raio": {
                "dano": 35,
                "descricao": "Ataque elétrico"
            },

            "Cajado": {
                "dano": 20,
                "descricao": "Energia mágica"
            }
        }
    }
}


# ==========================================
# MAPAS
# ==========================================

mapas = {

    1: {

        "nome": "Floresta 🌲",

        "historia": """
🌲 FLORESTA SOMBRIA

A floresta está silenciosa...
O vento sopra entre as árvores.

Algo observa você no escuro.

👹 Um Goblin protege a floresta.

Digite Y para continuar...
""",

        "inimigos": [

            {
                "nome": "Goblin 👹",
                "vida": 70,

                "ataques": [

                    "Golpe de Taco 🪵",
                    "Mordida 🦷",
                    "Arranhão 👋",
                    "Chute 🦶"

                ]
            },

            {
                "nome": "Lobo de Fogo 🔥",
                "vida": 120,

                "ataques": [

                    "Mordida Flamejante 🔥",
                    "Garras Quentes 🐾",
                    "Investida de Fogo ☄️",
                    "Rugido Flamejante 🐺"

                ]
            }
        ]
    },

    2: {

        "nome": "Montanha ⛰️",

        "historia": """
⛰️ MONTANHA CONGELADA

A neve cai lentamente...
Pegadas gigantes aparecem.

🦍 Um Pé Grande vive aqui.

Digite Y para continuar...
""",

        "inimigos": [

            {
                "nome": "Pé Grande 🦍",
                "vida": 90,

                "ataques": [

                    "Soco Gigante 👊",
                    "Pisada Brutal 🦶",
                    "Arremesso de Pedra 🪨",
                    "Rugido Selvagem 😡"

                ]
            },

            {
                "nome": "Tigre Dente de Sabre 🐯",
                "vida": 140,

                "ataques": [

                    "Garras Cortantes 🐾",
                    "Mordida Mortal 🦷",
                    "Salto Selvagem 🐯",
                    "Ataque Feroz ⚡"

                ]
            }
        ]
    }
}

class RPG(App):

    CSS = """

    Screen {
        align: center middle;
    }

    #menu {
        width: 75;
        border: round green;
        padding: 1 2;
    }

    #texto {
        margin-bottom: 1;
    }

    """

    etapa = "menu"

    personagem = None
    mapa = None

    vida_jogador = 0

    inimigo_atual = 0

    def compose(self) -> ComposeResult:

        yield Header()

        yield Vertical(

            Static(
                """
🎮 RPG TERMINAL

1 - Avatar
2 - Mapa
3 - Jornada
0 - Sair
                """,
                id="texto"
            ),

            Input(
                placeholder="Digite aqui..."
            ),

            id="menu"
        )

        yield Footer()

    def on_input_submitted(self, event: Input.Submitted):

        valor = event.value.upper()

        caixa = self.query_one(Input)
        caixa.value = ""

        texto = self.query_one("#texto")

        if self.etapa == "menu":

            if valor == "1":

                self.etapa = "avatar"

                mensagem = "\n🧍 PERSONAGENS\n"

                for numero, dados in personagens.items():

                    mensagem += f"""
━━━━━━━━━━━━━━━━
{numero} - {dados['nome']} ❤️ {dados['vida']}
"""

                    for arma, info in dados["armas"].items():

                        mensagem += (
                            f"• {arma} | "
                            f"💥 {info['dano']} | "
                            f"{info['descricao']}\n"
                        )

                mensagem += "\n0 - Voltar"

                texto.update(mensagem)

            elif valor == "2":

                self.etapa = "mapa"

                texto.update(
                    """
🗺️ MAPAS

━━━━━━━━━━━━━━━━
1 - Floresta 🌲
👹 Goblin
🔥 Lobo de Fogo

━━━━━━━━━━━━━━━━
2 - Montanha ⛰️
🦍 Pé Grande
🐯 Tigre Dente de Sabre

0 - Voltar
"""
                )

            elif valor == "3":

                if self.personagem is None:

                    texto.update(
                        "❌ Escolha um personagem!"
                    )

                    return

                if self.mapa is None:

                    texto.update(
                        "❌ Escolha um mapa!"
                    )

                    return

                self.etapa = "historia"

                texto.update(
                    mapas[self.mapa]["historia"]
                )

            elif valor == "0":

                self.exit()


        elif self.etapa == "avatar":

            numero = int(valor)

            if numero == 0:

                self.etapa = "menu"

                texto.update(
                    """
🎮 RPG TERMINAL

1 - Avatar
2 - Mapa
3 - Jornada
0 - Sair
"""
                )

                return

            if numero in personagens:

                self.personagem = numero

                self.vida_jogador = personagens[numero]["vida"]

                texto.update(
                    f"""
✅ Personagem escolhido

👤 {personagens[numero]['nome']}
❤️ Vida: {self.vida_jogador}

0 - Voltar
"""
                )


        elif self.etapa == "mapa":

            numero = int(valor)

            if numero == 0:

                self.etapa = "menu"

                texto.update(
                    """
🎮 RPG TERMINAL

1 - Avatar
2 - Mapa
3 - Jornada
0 - Sair
"""
                )

                return

            if numero in mapas:

                self.mapa = numero

                texto.update(
                    f"""
✅ Mapa escolhido

🗺️ {mapas[numero]['nome']}

0 - Voltar
"""
                )

        elif self.etapa == "historia":

            if valor == "Y":

                self.etapa = "batalha"

                self.iniciar_batalha()


        elif self.etapa == "continuar":

            if valor == "Y":

                self.etapa = "batalha"

                self.iniciar_batalha()


        elif self.etapa == "batalha":

            inimigo = mapas[self.mapa]["inimigos"][self.inimigo_atual]

            armas = list(
                personagens[self.personagem]["armas"].items()
            )

            try:

                escolha = int(valor)

                if escolha < 1 or escolha > len(armas):
                    return

                arma_nome, info = armas[escolha - 1]

                sons_armas = {

                    "Espada": "sons/espada.mp3",
                    "Machado": "sons/machado.mp3",
                    "Martelo": "sons/martelo.mp3",
                    "Arco": "sons/arco.mp3",
                    "Besta": "sons/besta.mp3",
                    "Adaga": "sons/adaga.mp3",
                    "Fogo": "sons/fogo.mp3",
                    "Raio": "sons/raio.mp3",
                    "Cajado": "sons/cajado.mp3"

                }

                if arma_nome in sons_armas:

                    dano = info["dano"]

                    inimigo["vida"] -= dano

                mensagem = f"""
⚔️ Você usou {arma_nome}
💥 Causou {dano} dano!

👹 Vida inimigo:
{inimigo['vida']}
"""

                if inimigo["vida"] <= 0:

                    mensagem += (
                        f"\n🏆 {inimigo['nome']} derrotado!\n"
                    )

                    if self.inimigo_atual == 0:

                        self.vida_jogador += 30

                        mensagem += """
🍎 Você comeu uma Maçã Dourada!

❤️ Recuperou 30 de vida!

⚠️ Você escuta passos...

Digite Y para continuar.
"""

                        self.inimigo_atual += 1

                        self.etapa = "continuar"

                    else:

                        mensagem += """
💰 Você encontrou um BAÚ!

🏆 PARABÉNS!
Você concluiu a jornada!
"""

                        self.etapa = "fim"

                    texto.update(mensagem)

                    return

                ataque_inimigo = random.choice(
                    inimigo["ataques"]
                )

                dano_inimigo = random.randint(20, 35)

                self.vida_jogador -= dano_inimigo

                mensagem += f"""
👹 {inimigo['nome']} usou:
{ataque_inimigo}

💢 Você recebeu {dano_inimigo} dano!

❤️ Sua vida:
{self.vida_jogador}
"""

                if self.vida_jogador <= 0:

                    mensagem += "\n☠️ VOCÊ MORREU!"

                    self.etapa = "fim"

                mensagem += "\n\nEscolha arma:\n"

                for i, (arma, info) in enumerate(
                    armas,
                    start=1
                ):

                    mensagem += (
                        f"{i} - {arma} "
                        f"💥 {info['dano']}\n"
                    )

                texto.update(mensagem)

            except Exception as erro:

                print(erro)

    def iniciar_batalha(self):

        texto = self.query_one("#texto")

        inimigo = mapas[self.mapa]["inimigos"][self.inimigo_atual]

        armas = list(
            personagens[self.personagem]["armas"].items()
        )

        mensagem = f"""
⚔️ BATALHA INICIADA

🔥 {inimigo['nome']} apareceu!

❤️ Sua vida:
{self.vida_jogador}

👹 Vida inimigo:
{inimigo['vida']}

Escolha arma:
"""

        for i, (arma, info) in enumerate(
            armas,
            start=1
        ):

            mensagem += (
                f"{i} - {arma} "
                f"💥 {info['dano']}\n"
            )

        texto.update(mensagem)
15521
if __name__ == "__main__":

    threading.Thread(
        daemon=True
    ).start()

    app = RPG()
    app.run()