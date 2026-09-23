"""
Carro de trânsito (civil).

Os carros civis:
  - nascem numa faixa aleatória, acima da tela;
  - descem em direção aos jogadores numa velocidade fixa (própria de
    cada carro, sorteada dentro de uma faixa de valores);
  - são removidos assim que saem por baixo da tela;
  - colidem com os jogadores (separação física + dano no sistema de colisão).
"""

import pygame
from src import settings


class CarroTrafego:
    def __init__(self, faixa, y, velocidade, cor):
        self.faixa = faixa
        self.velocidade = velocidade
        self.cor = cor

        self.x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA + settings.LARGURA_FAIXA / 2
        self.y = y

        self.rect = pygame.Rect(0, 0, settings.LARGURA_CARRO - 6, settings.ALTURA_CARRO - 10)
        self.rect.center = (int(self.x), int(self.y))

    def atualizar(self):
        self.y += self.velocidade
        self.rect.center = (int(self.x), int(self.y))

    def fora_da_tela(self):
        return self.rect.top > settings.ALTURA_TELA

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect, border_radius=6)
