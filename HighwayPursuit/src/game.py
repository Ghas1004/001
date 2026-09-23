"""
Classe principal do jogo.

Etapas incluídas nesta versão:
  1) Janela, pista de 4 faixas, troca de faixa suave
  3) Sistema de velocidade: acelerar/frear/nitro de forma suave, com vida
     reduzindo permanentemente a velocidade base e máxima
  4) Trânsito: carros civis nascendo em faixas aleatórias e descendo
  5) Colisão sólida entre jogadores e com o trânsito (sem atravessar)
  6) HUD completo: vida, nitro e tempo de jogo
  7) Spike strip: a polícia solta (tecla Q), com aviso de 2s antes de
     aparecer e cooldown de 1 minuto; fura o pneu por 1 minuto
  8) Barreira: a polícia aciona (tecla E), com o mesmo aviso de 2s;
     ocupa a faixa inteira e machuca quem bater nela
  9) Armas do ladrão: óleo (tecla ., derrapagem temporária na polícia)
     e tiro traseiro (tecla /, dano direto) -- sem aviso, é a surpresa
     do ladrão

Inclui colisão sólida (jogador x jogador e jogador x trânsito) e
inclinação do carro nas curvas. Ainda não incluído: condição de
vitória/derrota e menu.
"""

import random

import pygame

from src import settings
from src.entities.car import Carro
from src.entities.traffic import CarroTrafego
from src.entities.obstacles import FaixaDePregos, Barreira
from src.entities.weapons import OleoDerrapante, Projetil
from src.systems.collision import (
    verificar_colisao_jogadores,
    verificar_colisao_trafego,
    verificar_colisao_spike,
    verificar_colisao_barreira,
    verificar_colisao_oleo,
    verificar_colisao_projetil,
)


class Game:
    def __init__(self, tela):
        self.tela = tela
        self.relogio = pygame.time.Clock()
        self.rodando = True

        # Offset usado para "rolar" as linhas tracejadas da pista
        self.offset_pista = 0

        # Carro da polícia começa na faixa 1 (segunda faixa da esquerda)
        self.policia = Carro(faixa_inicial=1, y=settings.Y_POLICIA, cor=settings.COR_POLICIA)

        # Carro do ladrão começa na faixa 2
        self.ladrao = Carro(faixa_inicial=2, y=settings.Y_LADRAO, cor=settings.COR_LADRAO)

        # --- Trânsito (etapa 4) ---
        self.trafego = []
        self.contador_spawn = 0
        self.proximo_spawn = random.randint(settings.INTERVALO_SPAWN_MIN, settings.INTERVALO_SPAWN_MAX)

        # --- Mensagem de colisão na tela (etapa 5) ---
        self.mensagem_colisao = ""
        self.timer_mensagem_colisao = 0

        # --- Tempo de jogo (etapa 6) ---
        self.frames_totais = 0

        # --- Spike strip (etapa 7) ---
        self.spike = None
        self.cooldown_spike = 0
        self.aviso_spike = 0
        self.aviso_spike_faixa = None

        # --- Barreira (etapa 8) ---
        self.barreira = None
        self.cooldown_barreira = 0
        self.aviso_barreira = 0
        self.aviso_barreira_faixa = None

        # --- Armas do ladrão (etapa 9) ---
        self.oleo = None
        self.cooldown_oleo = 0

        self.projetil = None
        self.cooldown_tiro = 0

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def executar(self):
        while self.rodando:
            self._tratar_eventos()
            self._atualizar()
            self._desenhar()
            self.relogio.tick(settings.FPS)

    # ------------------------------------------------------------------
    # Eventos / input
    # ------------------------------------------------------------------
    def _tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False

                # Controles da Polícia (Player 1): A / D trocam de faixa
                elif evento.key == pygame.K_a:
                    self.policia.trocar_faixa(-1, self._ocupantes_para(self.policia))
                elif evento.key == pygame.K_d:
                    self.policia.trocar_faixa(1, self._ocupantes_para(self.policia))

                # Habilidades da Polícia: Q = spike strip, E = barreira
                elif evento.key == pygame.K_q:
                    self._tentar_ativar_spike()
                elif evento.key == pygame.K_e:
                    self._tentar_ativar_barreira()

                # Controles do Ladrão (Player 2): setas esquerda / direita
                elif evento.key == pygame.K_LEFT:
                    self.ladrao.trocar_faixa(-1, self._ocupantes_para(self.ladrao))
                elif evento.key == pygame.K_RIGHT:
                    self.ladrao.trocar_faixa(1, self._ocupantes_para(self.ladrao))

                # Armas do Ladrão: . = óleo, / = tiro traseiro
                elif evento.key == pygame.K_PERIOD:
                    self._tentar_soltar_oleo()
                elif evento.key == pygame.K_SLASH:
                    self._tentar_atirar()

    # ------------------------------------------------------------------
    # Atualização de estado
    # ------------------------------------------------------------------
    def _atualizar(self):
        self.frames_totais += 1

        self.offset_pista = (self.offset_pista + settings.VELOCIDADE_PISTA) % (
            settings.ALTURA_TRACO + settings.ESPACO_TRACO
        )

        teclas = pygame.key.get_pressed()

        acelerando_policia = teclas[pygame.K_w]
        freando_policia = teclas[pygame.K_s]
        nitro_policia = teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]

        acelerando_ladrao = teclas[pygame.K_UP]
        freando_ladrao = teclas[pygame.K_DOWN]
        nitro_ladrao = teclas[pygame.K_RCTRL] or teclas[pygame.K_LCTRL]

        self.policia.atualizar(
            acelerando=acelerando_policia, freando=freando_policia, usando_nitro=nitro_policia
        )
        self.ladrao.atualizar(
            acelerando=acelerando_ladrao, freando=freando_ladrao, usando_nitro=nitro_ladrao
        )

        self._atualizar_trafego()
        self._atualizar_spike()
        self._atualizar_barreira()
        self._atualizar_oleo()
        self._atualizar_projetil()

        tipo_colisao = verificar_colisao_jogadores(self.policia, self.ladrao)
        if tipo_colisao is not None:
            self.mensagem_colisao = f"Colisao {tipo_colisao.upper()}!"
            self.timer_mensagem_colisao = settings.FPS  # ~1 segundo

        for jogador, rotulo in ((self.policia, "POLICIA"), (self.ladrao, "LADRAO")):
            tipo_npc = verificar_colisao_trafego(jogador, self.trafego)
            if tipo_npc is not None:
                self.mensagem_colisao = f"{rotulo} x TRANSITO ({tipo_npc.upper()})!"
                self.timer_mensagem_colisao = settings.FPS

        if self.timer_mensagem_colisao > 0:
            self.timer_mensagem_colisao -= 1

    def _ocupantes_para(self, _jogador=None):
        """Só NPCs bloqueiam faixa — jogadores podem se bater de propósito."""
        return list(self.trafego)

    def _atualizar_trafego(self):
        self.contador_spawn += 1
        if self.contador_spawn >= self.proximo_spawn:
            self.contador_spawn = 0
            self.proximo_spawn = random.randint(
                settings.INTERVALO_SPAWN_MIN, settings.INTERVALO_SPAWN_MAX
            )
            self._spawnar_carro_trafego()

        for carro in self.trafego:
            carro.atualizar()

        self.trafego = [carro for carro in self.trafego if not carro.fora_da_tela()]

    def _spawnar_carro_trafego(self):
        faixa = random.randint(0, settings.NUM_FAIXAS - 1)
        velocidade = random.uniform(settings.VELOCIDADE_TRAFEGO_MIN, settings.VELOCIDADE_TRAFEGO_MAX)
        cor = random.choice(settings.CORES_TRAFEGO)
        y_inicial = -settings.ALTURA_CARRO
        self.trafego.append(CarroTrafego(faixa, y_inicial, velocidade, cor))

    # ------------------------------------------------------------------
    # Etapa 7 — Spike strip
    # ------------------------------------------------------------------
    def _tentar_ativar_spike(self):
        pode_ativar = self.cooldown_spike <= 0 and self.aviso_spike <= 0 and self.spike is None
        if not pode_ativar:
            return
        # A faixa-alvo é travada AGORA, no momento do acionamento, para
        # que o aviso de 10s sirva de verdade para o ladrão reagir.
        self.aviso_spike_faixa = self.ladrao.faixa
        self.aviso_spike = settings.DURACAO_ALERTA
        self.cooldown_spike = settings.COOLDOWN_SPIKE

    def _atualizar_spike(self):
        if self.cooldown_spike > 0:
            self.cooldown_spike -= 1

        if self.aviso_spike > 0:
            self.aviso_spike -= 1
            if self.aviso_spike == 0:
                self.spike = FaixaDePregos(self.aviso_spike_faixa)

        if self.spike is not None:
            self.spike.atualizar()
            verificar_colisao_spike(self.policia, self.spike)
            verificar_colisao_spike(self.ladrao, self.spike)

            if self.spike.usada or self.spike.fora_da_tela():
                self.spike = None

    # ------------------------------------------------------------------
    # Etapa 8 — Barreira
    # ------------------------------------------------------------------
    def _tentar_ativar_barreira(self):
        pode_ativar = self.cooldown_barreira <= 0 and self.aviso_barreira <= 0 and self.barreira is None
        if not pode_ativar:
            return
        self.aviso_barreira_faixa = self.ladrao.faixa
        self.aviso_barreira = settings.DURACAO_ALERTA
        self.cooldown_barreira = settings.COOLDOWN_BARREIRA

    def _atualizar_barreira(self):
        if self.cooldown_barreira > 0:
            self.cooldown_barreira -= 1

        if self.aviso_barreira > 0:
            self.aviso_barreira -= 1
            if self.aviso_barreira == 0:
                self.barreira = Barreira(self.aviso_barreira_faixa)

        if self.barreira is not None:
            self.barreira.atualizar()
            verificar_colisao_barreira(self.policia, self.barreira)
            verificar_colisao_barreira(self.ladrao, self.barreira)

            if self.barreira.fora_da_tela():
                self.barreira = None

    # ------------------------------------------------------------------
    # Etapa 9 — Óleo (arma do ladrão)
    # ------------------------------------------------------------------
    def _tentar_soltar_oleo(self):
        if self.cooldown_oleo > 0 or self.oleo is not None:
            return
        # Sem aviso -- larga na hora, logo atrás do ladrão
        y_inicial = self.ladrao.y + settings.ALTURA_CARRO / 2 + 12
        self.oleo = OleoDerrapante(self.ladrao.faixa, y_inicial)
        self.cooldown_oleo = settings.COOLDOWN_OLEO

    def _atualizar_oleo(self):
        if self.cooldown_oleo > 0:
            self.cooldown_oleo -= 1

        if self.oleo is not None:
            self.oleo.atualizar()
            verificar_colisao_oleo(self.policia, self.oleo)

            if self.oleo.usada or self.oleo.fora_da_tela():
                self.oleo = None

    # ------------------------------------------------------------------
    # Etapa 9 — Tiro traseiro (arma do ladrão)
    # ------------------------------------------------------------------
    def _tentar_atirar(self):
        if self.cooldown_tiro > 0 or self.projetil is not None:
            return
        y_inicial = self.ladrao.y + settings.ALTURA_CARRO / 2 + 4
        self.projetil = Projetil(self.ladrao.faixa, y_inicial)
        self.cooldown_tiro = settings.COOLDOWN_TIRO

    def _atualizar_projetil(self):
        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

        if self.projetil is not None:
            self.projetil.atualizar()
            verificar_colisao_projetil(self.policia, self.projetil)

            if self.projetil.atingiu or self.projetil.fora_da_tela():
                self.projetil = None

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def _desenhar(self):
        self.tela.fill(settings.COR_GRAMA)

        self._desenhar_pista()

        for carro in self.trafego:
            carro.desenhar(self.tela)

        if self.spike is not None:
            self.spike.desenhar(self.tela)
        if self.barreira is not None:
            self.barreira.desenhar(self.tela)
        if self.oleo is not None:
            self.oleo.desenhar(self.tela)
        if self.projetil is not None:
            self.projetil.desenhar(self.tela)

        self.policia.desenhar(self.tela)
        self.ladrao.desenhar(self.tela)

        self._desenhar_avisos()
        self._desenhar_hud()

        pygame.display.flip()

    def _desenhar_pista(self):
        pygame.draw.rect(
            self.tela, settings.COR_ACOSTAMENTO,
            (settings.MARGEM_PISTA - settings.LARGURA_ACOSTAMENTO, 0,
             settings.LARGURA_ACOSTAMENTO, settings.ALTURA_TELA)
        )
        pygame.draw.rect(
            self.tela, settings.COR_ACOSTAMENTO,
            (settings.MARGEM_PISTA + settings.LARGURA_PISTA, 0,
             settings.LARGURA_ACOSTAMENTO, settings.ALTURA_TELA)
        )

        pista_rect = pygame.Rect(
            settings.MARGEM_PISTA, 0, settings.LARGURA_PISTA, settings.ALTURA_TELA
        )
        pygame.draw.rect(self.tela, settings.COR_ASFALTO, pista_rect)

        passo_junta = settings.ESPACO_JUNTA_ASFALTO
        y_junta = -passo_junta + (self.offset_pista % passo_junta)
        while y_junta < settings.ALTURA_TELA:
            pygame.draw.rect(
                self.tela, settings.COR_JUNTA_ASFALTO,
                (settings.MARGEM_PISTA, y_junta, settings.LARGURA_PISTA, settings.ALTURA_JUNTA_ASFALTO)
            )
            y_junta += passo_junta

        pygame.draw.rect(
            self.tela, settings.COR_BORDA_PISTA,
            (settings.MARGEM_PISTA - 4, 0, 4, settings.ALTURA_TELA)
        )
        pygame.draw.rect(
            self.tela, settings.COR_BORDA_PISTA,
            (settings.MARGEM_PISTA + settings.LARGURA_PISTA, 0, 4, settings.ALTURA_TELA)
        )

        passo = settings.ALTURA_TRACO + settings.ESPACO_TRACO
        for faixa in range(1, settings.NUM_FAIXAS):
            x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA
            y = -passo + self.offset_pista
            while y < settings.ALTURA_TELA:
                pygame.draw.rect(
                    self.tela, settings.COR_LINHA,
                    (x - settings.LARGURA_LINHA // 2, y, settings.LARGURA_LINHA, settings.ALTURA_TRACO)
                )
                y += passo

        self._desenhar_marcadores_alerta()

    def _desenhar_marcadores_alerta(self):
        """Realça a faixa onde o spike strip / barreira vai aparecer."""
        avisos = []
        if self.aviso_spike > 0:
            avisos.append((self.aviso_spike_faixa, settings.COR_SPIKE_PONTA))
        if self.aviso_barreira > 0:
            avisos.append((self.aviso_barreira_faixa, settings.COR_BARREIRA))

        # Pisca (visível na metade dos frames) para chamar atenção
        if (self.frames_totais // 15) % 2 != 0:
            return

        for faixa, cor in avisos:
            x = settings.MARGEM_PISTA + faixa * settings.LARGURA_FAIXA
            faixa_rect = pygame.Rect(x, 0, settings.LARGURA_FAIXA, settings.ALTURA_TELA)
            marcador = pygame.Surface((faixa_rect.width, faixa_rect.height), pygame.SRCALPHA)
            marcador.fill((*cor, 60))
            self.tela.blit(marcador, faixa_rect.topleft)

    # ------------------------------------------------------------------
    # HUD e avisos
    # ------------------------------------------------------------------
    def _desenhar_avisos(self):
        fonte = pygame.font.SysFont("consolas", 22, bold=True)
        y = 100

        if self.aviso_spike > 0:
            segundos = self.aviso_spike // settings.FPS + 1
            texto = fonte.render(f"SPIKE STRIP em {segundos}s -- atencao, ladrao!", True, settings.COR_ALERTA)
            rect = texto.get_rect(center=(settings.LARGURA_TELA // 2, y))
            self.tela.blit(texto, rect)
            y += 30

        if self.aviso_barreira > 0:
            segundos = self.aviso_barreira // settings.FPS + 1
            texto = fonte.render(f"BARREIRA em {segundos}s -- troque de faixa!", True, settings.COR_BARREIRA)
            rect = texto.get_rect(center=(settings.LARGURA_TELA // 2, y))
            self.tela.blit(texto, rect)

    def _desenhar_hud(self):
        largura_faixa_hud = settings.LARGURA_TELA
        altura_hud = 96
        fundo_hud = pygame.Surface((largura_faixa_hud, altura_hud), pygame.SRCALPHA)
        fundo_hud.fill((0, 0, 0, 140))
        self.tela.blit(fundo_hud, (0, 0))

        fonte = pygame.font.SysFont("consolas", 20, bold=True)
        fonte_pequena = pygame.font.SysFont("consolas", 14)

        self._desenhar_linha_hud(fonte, "POLICIA", self.policia, y=8, cor=settings.COR_POLICIA)
        self._desenhar_linha_hud(fonte, "LADRAO ", self.ladrao, y=38, cor=settings.COR_LADRAO)

        segundos_totais = self.frames_totais // settings.FPS
        minutos = segundos_totais // 60
        segundos = segundos_totais % 60
        texto_tempo = fonte.render(f"Tempo {minutos:02d}:{segundos:02d}", True, settings.COR_TEXTO)
        self.tela.blit(texto_tempo, (settings.LARGURA_TELA - texto_tempo.get_width() - 16, 6))

        cooldown_spike_s = max(0, self.cooldown_spike // settings.FPS)
        cooldown_barreira_s = max(0, self.cooldown_barreira // settings.FPS)
        texto_habilidades_policia = fonte_pequena.render(
            f"Spike (Q): {'pronto' if cooldown_spike_s == 0 else str(cooldown_spike_s) + 's'}   "
            f"Barreira (E): {'pronta' if cooldown_barreira_s == 0 else str(cooldown_barreira_s) + 's'}",
            True, settings.COR_TEXTO
        )
        self.tela.blit(
            texto_habilidades_policia,
            (settings.LARGURA_TELA - texto_habilidades_policia.get_width() - 16, 30)
        )

        cooldown_oleo_s = max(0, self.cooldown_oleo // settings.FPS)
        cooldown_tiro_s = max(0, self.cooldown_tiro // settings.FPS)
        texto_armas_ladrao = fonte_pequena.render(
            f"Oleo (.): {'pronto' if cooldown_oleo_s == 0 else str(cooldown_oleo_s) + 's'}   "
            f"Tiro (/): {'pronto' if cooldown_tiro_s == 0 else str(cooldown_tiro_s) + 's'}",
            True, settings.COR_TEXTO
        )
        self.tela.blit(
            texto_armas_ladrao,
            (settings.LARGURA_TELA - texto_armas_ladrao.get_width() - 16, 50)
        )

        controles = fonte_pequena.render(
            "Policia: W/S/Shift, A/D faixa, Q spike, E barreira  |  "
            "Ladrao: seta cima/baixo/Ctrl, </> faixa, . oleo, / tiro",
            True, settings.COR_TEXTO
        )
        self.tela.blit(controles, (16, altura_hud - 16))

        if self.timer_mensagem_colisao > 0:
            fonte_grande = pygame.font.SysFont("consolas", 30, bold=True)
            texto_colisao = fonte_grande.render(self.mensagem_colisao, True, (255, 210, 40))
            rect_texto = texto_colisao.get_rect(center=(settings.LARGURA_TELA // 2, altura_hud + 30))
            self.tela.blit(texto_colisao, rect_texto)

    def _desenhar_linha_hud(self, fonte, rotulo, carro, y, cor):
        x = 16
        texto_vida = fonte.render(f"{rotulo}  Vida {carro.vida:3d}", True, cor)
        self.tela.blit(texto_vida, (x, y))

        x_barra = x + texto_vida.get_width() + 20
        self._desenhar_barra(
            x_barra, y + 4, largura=140, altura=16,
            valor=carro.nitro, valor_maximo=settings.NITRO_INICIAL,
            cor_preenchida=settings.COR_NITRO, rotulo="Nitro"
        )

    def _desenhar_barra(self, x, y, largura, altura, valor, valor_maximo, cor_preenchida, rotulo):
        pygame.draw.rect(self.tela, (40, 40, 40), (x, y, largura, altura))
        largura_preenchida = int(largura * max(0.0, valor) / valor_maximo)
        pygame.draw.rect(self.tela, cor_preenchida, (x, y, largura_preenchida, altura))
        pygame.draw.rect(self.tela, (10, 10, 10), (x, y, largura, altura), 1)

        fonte_rotulo = pygame.font.SysFont("consolas", 12)
        texto = fonte_rotulo.render(rotulo, True, (255, 255, 255))
        self.tela.blit(texto, (x + largura + 8, y + 1))
