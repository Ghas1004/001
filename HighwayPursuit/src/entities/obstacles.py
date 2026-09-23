"""
Obstáculos acionados pela polícia: spike strip (etapa 7) e barreira (etapa 8).

Os dois se comportam como objetos fixos no chão: nascem perto do topo da
tela e "descem" na mesma velocidade da pista (settings.VELOCIDADE_PISTA),
exatamente como as linhas tracejadas -- isso os mantém visualmente presos
ao mundo, e não a um carro específico.
"""

import pygame
from src import settings


class FaixaDePregos:
    """Spike strip: fica no chão até um carro passar por cima."""

    def __init__(self, faixa):
        self.faixa = faixa
        self.usada = False

        self.x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA + settings.LARGURA_FAIXA / 2
        self.y = -30

        self.rect = pygame.Rect(0, 0, settings.LARGURA_FAIXA - 24, 22)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self):
        self.y += settings.VELOCIDADE_PISTA
        self.rect.center = (int(self.x), int(self.y))

    def fora_da_tela(self):
        return self.rect.top > settings.ALTURA_TELA

    def desenhar(self, tela):
        pygame.draw.rect(tela, settings.COR_SPIKE_BASE, self.rect, border_radius=4)

        num_espinhos = 6
        largura_espinho = self.rect.width / num_espinhos
        for i in range(num_espinhos):
            cx = self.rect.left + largura_espinho * (i + 0.5)
            pontos = [
                (cx, self.rect.top - 6),
                (cx - 5, self.rect.top + 4),
                (cx + 5, self.rect.top + 4),
            ]
            pygame.draw.polygon(tela, settings.COR_SPIKE_PONTA, pontos)


class Barreira:
    """Barreira: ocupa a faixa inteira, obrigando o carro a desviar."""

    def __init__(self, faixa):
        self.faixa = faixa

        self.x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA + settings.LARGURA_FAIXA / 2
        self.y = -50

        self.rect = pygame.Rect(0, 0, settings.LARGURA_FAIXA - 8, 46)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self):
        self.y += settings.VELOCIDADE_PISTA
        self.rect.center = (int(self.x), int(self.y))

    def fora_da_tela(self):
        return self.rect.top > settings.ALTURA_TELA

    def desenhar(self, tela):
        pygame.draw.rect(tela, settings.COR_BARREIRA, self.rect, border_radius=3)

        # Listras diagonais estilo "zebra" de aviso
        largura_listra = 10
        x = self.rect.left - self.rect.height
        while x < self.rect.right:
            p1 = (x, self.rect.bottom)
            p2 = (x + self.rect.height, self.rect.top)
            p3 = (min(x + self.rect.height + largura_listra, self.rect.right), self.rect.top)
            p4 = (min(x + largura_listra, self.rect.right), self.rect.bottom)
            pontos = [p1, p2, p3, p4]
            pontos = [(max(self.rect.left, px), py) for px, py in pontos]
            pygame.draw.polygon(tela, settings.COR_BARREIRA_LISTRA, pontos)
            x += largura_listra * 2

        pygame.draw.rect(tela, settings.COR_BARREIRA_LISTRA, self.rect, 2, border_radius=3)
