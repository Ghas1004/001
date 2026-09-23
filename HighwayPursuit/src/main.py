"""
Ponto de entrada do Highway Pursuit.

Forma recomendada de rodar (a partir da pasta raiz do projeto):

    python -m src.main

Mas este arquivo também funciona se você rodar diretamente:

    python src/main.py

ou até clicando/rodando pelo VSCodium com o botão "Run", graças ao
ajuste de path logo abaixo.
"""

import os
import sys

# Garante que a pasta raiz do projeto (que contém a pasta "src")
# esteja no sys.path, mesmo se este arquivo for executado diretamente
# (e não com "python -m src.main").
PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)

import pygame
from src import settings
from src.game import Game


def main():
    pygame.init()
    pygame.display.set_caption(settings.TITULO_JANELA)
    tela = pygame.display.set_mode((settings.LARGURA_TELA, settings.ALTURA_TELA))

    jogo = Game(tela)
    jogo.executar()

    pygame.quit()


if __name__ == "__main__":
    main()
