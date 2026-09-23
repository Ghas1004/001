from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Static, Input

import random
import os
import threading
from playsound import playsound


# =========================================================
# TOCAR SOM
# =========================================================

def tocar_som(nome_arquivo):

    try:

        caminho_base = os.path.dirname(__file__)

        caminho = os.path.join(
            caminho_base,
            "sons",
            nome_arquivo
        )

        if os.path.exists(caminho):

            threading.Thread(
                target=playsound,
                args=(caminho,),
                daemon=True
            ).start()

        else:

            print(f"❌ Som não encontrado: {caminho}")

    except Exception as erro:

        print(f"❌ Erro ao tocar som: {erro}")


# =========================================================
# PERSONAGENS
# =========================================================

personagens = {

    1: {
        "nome": "Guerreiro ⚔️",
        "vida": 120,

        "armas": {

            "Espada": {
                "dano": 20,
                "descricao": "Ataque rápido",
                "som": "espada.mp3"
            },

            "Machado": {
                "dano": 30,
                "descricao": "Dano pesado",
                "som": "machado.mp3"
            },

            "Martelo": {
                "dano": 40,
                "descricao": "Muito forte",
                "som": "martelo.mp3"
            }
        }
    },

    2: {
        "nome": "Arqueiro 🏹",
        "vida": 90,

        "armas": {

            "Arco": {
                "dano": 25,
                "descricao": "Longa distância",
                "som": "arco.mp3"
            },

            "Besta": {
                "dano": 35,
                "descricao": "Disparo forte",
                "som": "besta.mp3"
            },

            "Adaga": {
                "dano": 15,
                "descricao": "Ataque rápido",
                "som": "adaga.mp3"
            }
        }
    },

    3: {
        "nome": "Mago 🪄",
        "vida": 80,

        "armas": {

            "Fogo": {
                "dano": 45,
                "descricao": "Magia destrutiva",
                "som": "fogo.mp3"
            },

            "Raio": {
                "dano": 35,
                "descricao": "Ataque elétrico",
                "som": "raio.mp3"
            },

            "Cajado": {
                "dano": 20,
                "descricao": "Energia mágica",
                "som": "cajado.mp3"
            }
        }
    }
}


# =========================================================
# MAPAS
# =========================================================

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


# =========================================================
# APP
# =========================================================

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

    # =========================================================
    # TELA
    # =========================================================

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

    # =========================================================
    # MENU PRINCIPAL
    # =========================================================

    def voltar_menu(self):

        self.etapa = "menu"

        texto = self.query_one("#texto")

        texto.update(
            """
🎮 RPG TERMINAL

1 - Avatar
2 - Mapa
3 - Jornada
0 - Sair
"""
        )

    # =========================================================
    # INPUT
    # =========================================================

    def on_input_submitted(self, event: Input.Submitted):

        valor = event.value.strip().upper()

        caixa = self.query_one(Input)
        caixa.value = ""

        texto = self.query_one("#texto")

        # =========================================================
        # MENU
        # =========================================================

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

━━━━━━━━━━━━━━━━
2 - Montanha ⛰️

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

        # =========================================================
        # PERSONAGEM
        # =========================================================

        elif self.etapa == "avatar":

            if not valor.isdigit():
                return

            numero = int(valor)

            if numero == 0:

                self.voltar_menu()
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

        # =========================================================
        # MAPA
        # =========================================================

        elif self.etapa == "mapa":

            if not valor.isdigit():
                return

            numero = int(valor)

            if numero == 0:

                self.voltar_menu()
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

        # =========================================================
        # HISTÓRIA
        # =========================================================

        elif self.etapa == "historia":

            if valor == "Y":

                self.etapa = "batalha"

                self.iniciar_batalha()

        # =========================================================
        # CONTINUAR
        # =========================================================

        elif self.etapa == "continuar":

            if valor == "Y":

                self.etapa = "batalha"

                self.mostrar_batalha()

        # =========================================================
        # BATALHA
        # =========================================================

        elif self.etapa == "batalha":

            if not valor.isdigit():
                return

            inimigo = mapas[self.mapa]["inimigos"][self.inimigo_atual]

            armas = list(
                personagens[self.personagem]["armas"].items()
            )

            escolha = int(valor)

            if escolha < 1 or escolha > len(armas):
                return

            arma_nome, info = armas[escolha - 1]

            # =========================================================
            # TOCAR SOM DA ARMA
            # =========================================================

            tocar_som(info["som"])

            dano = info["dano"]

            inimigo["vida"] -= dano

            mensagem = f"""
⚔️ Você usou {arma_nome}
💥 Causou {dano} dano!

👹 Vida inimigo:
{inimigo['vida']}
"""

            # =========================================================
            # INIMIGO DERROTADO
            # =========================================================

            if inimigo["vida"] <= 0:

                mensagem += (
                    f"\n🏆 {inimigo['nome']} derrotado!\n"
                )

                if self.inimigo_atual == 0:

                    self.vida_jogador += 30

                    mensagem += """
🍎 Você encontrou uma Maçã Dourada!

❤️ Recuperou 30 de vida!

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

            # =========================================================
            # ATAQUE INIMIGO
            # =========================================================

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

    # =========================================================
    # INICIAR BATALHA
    # =========================================================

    def iniciar_batalha(self):

        self.inimigo_atual = 0

        self.mostrar_batalha()

    # =========================================================
    # MOSTRAR BATALHA
    # =========================================================

    def mostrar_batalha(self):

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


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    app = RPG()

    app.run()