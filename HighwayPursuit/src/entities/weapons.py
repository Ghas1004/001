"""
Armas do ladrão (etapa 9): óleo e tiro traseiro.

Diferente do spike strip e da barreira, essas armas não têm aviso --
é o ladrão surpreendendo a polícia, não o contrário.
"""

import pygame
from src import settings


class OleoDerrapante:
    """
    Mancha de óleo largada no chão. Comporta-se como um objeto fixo no
    mundo (rola na velocidade da pista), igual ao spike strip e à
    barreira. Só afeta a polícia, e só uma vez (soma usada = True).
    """

    def __init__(self, faixa, y_inicial):
        self.faixa = faixa
        self.usada = False

        self.x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA + settings.LARGURA_FAIXA / 2
        self.y = y_inicial

        self.rect = pygame.Rect(0, 0, settings.LARGURA_FAIXA - 30, 34)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self):
        self.y += settings.VELOCIDADE_PISTA
        self.rect.center = (int(self.x), int(self.y))

    def fora_da_tela(self):
        return self.rect.top > settings.ALTURA_TELA

    def desenhar(self, tela):
        pygame.draw.ellipse(tela, settings.COR_OLEO, self.rect)
        brilho = pygame.Rect(0, 0, self.rect.width * 0.4, self.rect.height * 0.35)
        brilho.center = (self.rect.centerx - 6, self.rect.centery - 4)
        pygame.draw.ellipse(tela, settings.COR_OLEO_BRILHO, brilho)


class Projetil:
    """
    Tiro disparado pelo ladrão para trás. Viaja numa faixa fixa (a
    faixa do ladrão no momento do disparo) e some ao acertar a
    polícia ou sair da tela.
    """

    def __init__(self, faixa, y_inicial):
        self.faixa = faixa
        self.atingiu = False

        self.x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA + settings.LARGURA_FAIXA / 2
        self.y = y_inicial

        self.rect = pygame.Rect(0, 0, 10, 22)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self):
        self.y += settings.VELOCIDADE_PROJETIL
        self.rect.center = (int(self.x), int(self.y))

    def fora_da_tela(self):
        return self.rect.top > settings.ALTURA_TELA

    def desenhar(self, tela):
        pygame.draw.rect(tela, settings.COR_PROJETIL, self.rect, border_radius=4)
