"""
Entidade Carro (versão com vida, velocidade, freio e nitro).

Regras principais:
  - vida começa em 100 e nunca é recuperada nesta versão;
  - quanto menor a vida, menor a velocidade base E a velocidade máxima
    (o carro danificado nunca volta a ter o desempenho original);
  - segurando o acelerador, a velocidade sobe suavemente até o máximo;
  - soltando, ela cai suavemente até a base;
  - segurando o freio, a velocidade cai rapidamente, podendo chegar a 0
    (tem prioridade sobre acelerar e nitro);
  - segurando o nitro (com barra de nitro disponível), a velocidade sobe
    mais rápido e pode ultrapassar o máximo normal por um tempo; a barra
    se esgota com o uso e recarrega sozinha quando não está em uso;
  - a diferença entre a velocidade atual do carro e a "velocidade de
    referência" (velocidade do mundo/pista) empurra o carro para cima
    ou para baixo na tela -- é isso que simula alcançar ou se afastar
    do outro carro, e é a base para a detecção de colisão;
  - se o pneu for furado (spike strip), a velocidade máxima fica
    reduzida e a troca de faixa mais lenta por 1 minuto, depois recupera;
  - nas trocas de faixa, o carro inclina a frente para o lado da curva.
"""

import random

import pygame
from src import settings


class Carro:
    def __init__(self, faixa_inicial, y, cor):
        self.faixa = faixa_inicial
        self.y = y
        self.cor = cor

        # --- Vida e velocidade (etapa 3) ---
        self.vida = settings.VIDA_INICIAL
        self.velocidade_atual = settings.VELOCIDADE_BASE_INICIAL
        self.nitro = settings.NITRO_INICIAL
        self.destruido = False

        # Cooldown usado pelo sistema de colisão (etapa 5) para não
        # aplicar dano em todo frame enquanto os carros ainda se tocam
        self.cooldown_colisao = 0

        # Efeito do spike strip (etapa 7): dura DURACAO_PNEU_FURADO e
        # depois o pneu volta ao normal.
        self.pneu_furado = False
        self.timer_pneu_furado = 0

        # Derrapagem temporária (óleo do ladrão)
        self.timer_derrapagem = 0

        # Inclinação visual na curva (graus; positivo = nariz à esquerda)
        self.angulo = 0.0

        self.x = self._x_da_faixa(self.faixa)
        self.x_alvo = self.x

        self.rect = pygame.Rect(0, 0, settings.LARGURA_CARRO, settings.ALTURA_CARRO)
        self.rect.center = (int(self.x), int(self.y))

    # ------------------------------------------------------------------
    # Faixa / posição horizontal
    # ------------------------------------------------------------------
    def _x_da_faixa(self, faixa):
        return settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA + settings.LARGURA_FAIXA / 2

    def trocar_faixa(self, direcao, ocupantes=None):
        """direcao = -1 (esquerda) ou +1 (direita). Bloqueia se a faixa estiver ocupada."""
        if self.destruido or self.timer_derrapagem > 0:
            return False

        nova_faixa = self.faixa + direcao
        if not (0 <= nova_faixa < settings.NUM_FAIXAS):
            return False

        if ocupantes and self._faixa_ocupada(nova_faixa, ocupantes):
            return False

        self.faixa = nova_faixa
        self.x_alvo = self._x_da_faixa(self.faixa)
        return True

    def _faixa_ocupada(self, faixa, ocupantes):
        margem = settings.ALTURA_CARRO + settings.MARGEM_BLOQUEIO_FAIXA
        for outro in ocupantes:
            if outro is self or getattr(outro, "destruido", False):
                continue
            faixa_outro = getattr(outro, "faixa", None)
            if faixa_outro != faixa:
                continue
            if abs(outro.y - self.y) < margem:
                return True
        return False

    def cancelar_troca_faixa(self):
        """Volta o alvo horizontal para a faixa atual (bateu de lado ao mudar)."""
        self.x_alvo = self._x_da_faixa(self.faixa)

    # ------------------------------------------------------------------
    # Vida e dano
    # ------------------------------------------------------------------
    def velocidade_base_atual(self):
        """Velocidade de cruzeiro, reduzida permanentemente pelo dano."""
        reducao = (settings.VIDA_INICIAL - self.vida) / 10
        return max(0.0, settings.VELOCIDADE_BASE_INICIAL - reducao)

    def velocidade_maxima_atual(self):
        """Velocidade máxima possível (acelerando), reduzida pelo dano
        e temporariamente se o pneu estiver furado."""
        reducao = (settings.VIDA_INICIAL - self.vida) / 10
        maximo = max(0.0, settings.VELOCIDADE_MAXIMA_INICIAL - reducao)
        if self.pneu_furado:
            maximo = max(0.0, maximo - settings.PENALIDADE_VELOCIDADE_PNEU_FURADO)
        return maximo

    def aplicar_pneu_furado(self):
        """Efeito do spike strip: fura por 1 minuto e depois recupera."""
        self.pneu_furado = True
        self.timer_pneu_furado = settings.DURACAO_PNEU_FURADO

    def aplicar_derrapagem(self):
        """Efeito temporário do óleo: perde o controle lateral por alguns frames."""
        self.timer_derrapagem = settings.DURACAO_DERRAPAGEM

    def aplicar_dano(self, quantidade):
        if self.destruido:
            return
        self.vida = max(0, self.vida - quantidade)
        if self.vida <= 0:
            self.destruido = True
            self.velocidade_atual = 0

    # ------------------------------------------------------------------
    # Velocidade (acelerar / frear / nitro / soltar)
    # ------------------------------------------------------------------
    def _atualizar_velocidade(self, acelerando, freando, usando_nitro):
        if self.destruido:
            self.velocidade_atual = 0
            self.nitro = min(settings.NITRO_INICIAL, self.nitro + settings.RECARGA_NITRO)
            return

        base = self.velocidade_base_atual()
        maximo = self.velocidade_maxima_atual()
        teto_com_nitro = maximo + settings.BONUS_NITRO

        usando_nitro = usando_nitro and self.nitro > 0 and not freando

        if freando:
            # Frear tem prioridade: reduz a velocidade rapidamente,
            # podendo ir abaixo da base, até zero.
            self.velocidade_atual = max(self.velocidade_atual - settings.DECREMENTO_FREIO, 0)
        elif usando_nitro:
            self.velocidade_atual = min(self.velocidade_atual + settings.INCREMENTO_NITRO, teto_com_nitro)
        elif acelerando:
            self.velocidade_atual = min(self.velocidade_atual + settings.INCREMENTO_ACELERACAO, maximo)
        else:
            if self.velocidade_atual > base:
                self.velocidade_atual = max(self.velocidade_atual - settings.DECREMENTO_DESACELERACAO, base)
            else:
                self.velocidade_atual = base

        # Nitro consome enquanto usado, e recarrega sozinho no resto do tempo
        if usando_nitro:
            self.nitro = max(0, self.nitro - settings.CONSUMO_NITRO)
        else:
            self.nitro = min(settings.NITRO_INICIAL, self.nitro + settings.RECARGA_NITRO)

        # Garante que a velocidade nunca ultrapasse o teto válido no momento
        # (importante quando um dano recente reduz o máximo de repente)
        teto_valido = teto_com_nitro if usando_nitro else maximo
        self.velocidade_atual = min(self.velocidade_atual, teto_valido)

    def _mover_no_mundo(self):
        """
        Desloca o carro verticalmente na tela de acordo com a diferença
        entre sua velocidade e a velocidade de referência do mundo.
        Mais rápido que a referência = sobe na tela (se aproxima da frente).
        """
        diferenca = self.velocidade_atual - settings.VELOCIDADE_REFERENCIA
        self.y -= diferenca * settings.FATOR_DESLOCAMENTO_Y
        self.y = max(settings.Y_MIN, min(settings.Y_MAX, self.y))

    def _atualizar_inclinacao(self, movendo_lateral):
        """Inclina a frente do carro para o lado da curva e volta ao centro depois."""
        if movendo_lateral < 0:
            alvo = settings.ANGULO_CURVA_MAX
            fator = settings.FATOR_INCLINACAO
        elif movendo_lateral > 0:
            alvo = -settings.ANGULO_CURVA_MAX
            fator = settings.FATOR_INCLINACAO
        else:
            alvo = 0.0
            fator = settings.FATOR_RETORNO_INCLINACAO

        self.angulo += (alvo - self.angulo) * fator
        if abs(self.angulo) < 0.05:
            self.angulo = 0.0

    # ------------------------------------------------------------------
    # Atualização geral (chamada uma vez por frame)
    # ------------------------------------------------------------------
    def atualizar(self, acelerando=False, freando=False, usando_nitro=False):
        self._atualizar_velocidade(acelerando, freando, usando_nitro)
        self._mover_no_mundo()

        if self.timer_pneu_furado > 0:
            self.timer_pneu_furado -= 1
            if self.timer_pneu_furado <= 0:
                self.pneu_furado = False
                self.timer_pneu_furado = 0

        # Troca de faixa suave (interpolação simples). Com o pneu furado,
        # essa transição fica bem mais lenta -- é o "controle pior nas curvas".
        velocidade_troca = settings.VELOCIDADE_TROCA_FAIXA
        if self.pneu_furado:
            velocidade_troca *= settings.FATOR_CONTROLE_PNEU_FURADO

        movendo_lateral = 0
        if self.timer_derrapagem > 0:
            self.timer_derrapagem -= 1
            self.x += random.uniform(-settings.FORCA_DERRAPAGEM, settings.FORCA_DERRAPAGEM)
            self.x = max(
                settings.MARGEM_PISTA + settings.LARGURA_CARRO / 2,
                min(settings.MARGEM_PISTA + settings.LARGURA_PISTA - settings.LARGURA_CARRO / 2, self.x),
            )
            # Mantém a faixa coerente com a posição enquanto escorrega
            faixa_estimada = int((self.x - settings.MARGEM_PISTA) // settings.LARGURA_FAIXA)
            self.faixa = max(0, min(settings.NUM_FAIXAS - 1, faixa_estimada))
            self.x_alvo = self._x_da_faixa(self.faixa)
            movendo_lateral = 1 if random.random() > 0.5 else -1
        elif self.x < self.x_alvo:
            self.x = min(self.x + velocidade_troca, self.x_alvo)
            movendo_lateral = 1
        elif self.x > self.x_alvo:
            self.x = max(self.x - velocidade_troca, self.x_alvo)
            movendo_lateral = -1

        self._atualizar_inclinacao(movendo_lateral)

        if self.cooldown_colisao > 0:
            self.cooldown_colisao -= 1

        self.rect.center = (int(self.x), int(self.y))

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def desenhar(self, tela):
        cor = (90, 90, 90) if self.destruido else self.cor

        corpo = pygame.Surface((settings.LARGURA_CARRO, settings.ALTURA_CARRO), pygame.SRCALPHA)
        pygame.draw.rect(corpo, cor, corpo.get_rect(), border_radius=8)

        farol = pygame.Rect(8, 8, settings.LARGURA_CARRO - 16, 10)
        pygame.draw.rect(corpo, (255, 255, 255), farol, border_radius=3)

        if self.pneu_furado:
            pygame.draw.rect(corpo, (235, 140, 40), corpo.get_rect(), 3, border_radius=8)

        if abs(self.angulo) > 0.1:
            corpo = pygame.transform.rotate(corpo, self.angulo)

        dest = corpo.get_rect(center=(int(self.x), int(self.y)))
        tela.blit(corpo, dest)

        # Rect de colisão permanece alinhado ao eixo (mais estável no gameplay)
        self.rect.center = (int(self.x), int(self.y))
        self._desenhar_barra_de_vida(tela)

    def _desenhar_barra_de_vida(self, tela):
        largura_total = settings.LARGURA_CARRO
        altura_barra = 6
        x = self.rect.left
        y = self.rect.top - altura_barra - 6

        pygame.draw.rect(tela, (40, 40, 40), (x, y, largura_total, altura_barra))
        largura_vida = int(largura_total * (self.vida / settings.VIDA_INICIAL))
        cor_vida = (60, 200, 80) if self.vida > 40 else (220, 80, 50)
        pygame.draw.rect(tela, cor_vida, (x, y, largura_vida, altura_barra))
