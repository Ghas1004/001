"""
Configurações globais do jogo Highway Pursuit.
Tudo que for "número mágico" deve morar aqui, para facilitar ajustes.
"""

# --- Janela (landscape 16:9 — campo maior) ---
LARGURA_TELA = 1280
ALTURA_TELA = 720
FPS = 60
TITULO_JANELA = "Highway Pursuit"

# --- Pista ---
NUM_FAIXAS = 4
LARGURA_FAIXA = 168
LARGURA_PISTA = NUM_FAIXAS * LARGURA_FAIXA
MARGEM_PISTA = (LARGURA_TELA - LARGURA_PISTA) // 2  # centraliza a pista na tela

VELOCIDADE_PISTA = 10  # velocidade de rolagem das linhas (sensação de movimento)

# Linhas tracejadas entre as faixas
ALTURA_TRACO = 44
ESPACO_TRACO = 32
LARGURA_LINHA = 6

# Acostamento (faixa entre a grama e o asfalto) e "juntas" de asfalto
# (linhas horizontais sutis que dão sensação de textura/segmentos de pista)
LARGURA_ACOSTAMENTO = 28
ALTURA_JUNTA_ASFALTO = 4
ESPACO_JUNTA_ASFALTO = 240

# --- Cores ---
COR_FUNDO = (20, 20, 22)
COR_GRAMA = (28, 84, 38)
COR_ACOSTAMENTO = (196, 184, 150)
COR_ASFALTO = (48, 48, 54)
COR_JUNTA_ASFALTO = (38, 38, 43)
COR_LINHA = (225, 225, 225)
COR_BORDA_PISTA = (235, 200, 60)

COR_POLICIA = (40, 100, 230)
COR_LADRAO = (220, 60, 50)

COR_TEXTO = (240, 240, 240)
COR_NITRO = (90, 190, 240)

# --- Carros ---
LARGURA_CARRO = 58
ALTURA_CARRO = 104

VELOCIDADE_TROCA_FAIXA = 16  # pixels por frame durante a transição lateral

# --- Posição vertical inicial dos jogadores na tela ---
Y_POLICIA = ALTURA_TELA - 150
Y_LADRAO = ALTURA_TELA - 310

# --- Etapa 3: sistema de velocidade ---
VIDA_INICIAL = 100

VELOCIDADE_BASE_INICIAL = 24     # velocidade "de cruzeiro", sem acelerar
VELOCIDADE_MAXIMA_INICIAL = 40   # velocidade máxima segurando o acelerador
VELOCIDADE_REFERENCIA = 24       # velocidade "do mundo" (equivale à pista rolando)

# Aceleração mais responsiva para o jogo não parecer lento
INCREMENTO_ACELERACAO = 0.18     # quanto a velocidade sobe por frame ao acelerar
DECREMENTO_DESACELERACAO = 0.28  # quanto a velocidade cai por frame ao soltar

# Freio: reduz a velocidade bem mais rápido do que simplesmente soltar,
# e pode ir abaixo da velocidade base, até 0
DECREMENTO_FREIO = 0.75

# Nitro: um "extra" temporário acima da velocidade máxima normal,
# limitado por uma barra que se esgota com o uso e recarrega sozinha
BONUS_NITRO = 10                 # quanto o nitro soma acima da velocidade máxima
INCREMENTO_NITRO = 0.85          # quanto a velocidade sobe por frame usando nitro
NITRO_INICIAL = 100
CONSUMO_NITRO = 0.55             # quanto a barra de nitro cai por frame de uso
RECARGA_NITRO = 0.3              # quanto a barra de nitro recupera por frame sem uso

# Quanto o carro sobe/desce na tela por causa da diferença de velocidade
# em relação à VELOCIDADE_REFERENCIA (é isso que cria a sensação de
# "alcançar" ou "se afastar" do outro carro).
FATOR_DESLOCAMENTO_Y = 0.32
Y_MIN = 88                        # não deixa o carro passar por baixo do HUD
Y_MAX = ALTURA_TELA - 48

# --- Etapa 4: trânsito ---
VELOCIDADE_TRAFEGO_MIN = 4
VELOCIDADE_TRAFEGO_MAX = 8
INTERVALO_SPAWN_MIN = 35
INTERVALO_SPAWN_MAX = 90
CORES_TRAFEGO = [
    (215, 195, 60),
    (170, 170, 178),
    (90, 150, 220),
    (230, 140, 40),
]

# --- Etapa 5: colisão entre os jogadores ---
LIMIAR_COLISAO_LEVE = 3    # diferença de velocidade abaixo disso = leve
LIMIAR_COLISAO_MEDIA = 10  # abaixo disso = média; acima = forte

DANO_COLISAO_LEVE = 3
DANO_COLISAO_MEDIA = 8
DANO_COLISAO_FORTE = 15

EMPURRAO_COLISAO = 28       # pixels de separação vertical após a batida
COOLDOWN_COLISAO = 28       # frames de "imunidade" após bater (evita dano repetido)
DANO_COLISAO_LATERAL = 6    # dano mínimo ao bater de lado (troca de faixa)

# Separação física contínua (impede um carro atravessar o outro)
# Bloqueio de faixa vale só para NPCs — jogadores podem se bater de propósito
MARGEM_BLOQUEIO_FAIXA = 18  # folga vertical para considerar a faixa "ocupada"
FOLGA_COLISAO = 2           # pixels mínimos mantidos entre retângulos

# --- Colisão com trânsito (NPC) ---
DANO_COLISAO_TRAFEGO_BASE = 6
DANO_COLISAO_TRAFEGO_POR_IMPACTO = 1.2  # escala com a intensidade do impacto
EMPURRAO_TRAFEGO = 22
COOLDOWN_COLISAO_TRAFEGO = 40

# --- Inclinação visual nas curvas (troca de faixa) ---
ANGULO_CURVA_MAX = 14       # graus máximos de inclinação da frente do carro
FATOR_INCLINACAO = 0.22     # quão rápido o ângulo acompanha a curva
FATOR_RETORNO_INCLINACAO = 0.18  # quão rápido volta ao centro ao terminar a curva

# --- Etapa 7: spike strip ---
DURACAO_ALERTA = 2 * FPS          # aviso antes do obstáculo aparecer (2s)
COOLDOWN_SPIKE = 60 * FPS         # a polícia só pode soltar de novo a cada 1 minuto

# Pneu furado: reduz a velocidade máxima e piora a troca de faixa,
# mas recupera sozinho após DURACAO_PNEU_FURADO.
DURACAO_PNEU_FURADO = 60 * FPS                # 1 minuto
PENALIDADE_VELOCIDADE_PNEU_FURADO = 8         # reduz ainda mais a velocidade máxima
FATOR_CONTROLE_PNEU_FURADO = 0.35             # troca de faixa fica bem mais lenta

COR_SPIKE_BASE = (60, 60, 65)
COR_SPIKE_PONTA = (222, 222, 228)

# --- Etapa 8: barreiras ---
# Mesmo padrão de aviso/cooldown do spike strip (não foi detalhado um
# valor diferente, então assumi o mesmo por consistência)
COOLDOWN_BARREIRA = 60 * FPS

DANO_BARREIRA = 12
EMPURRAO_BARREIRA = 40      # empurra o carro pra trás ao bater na barreira

COR_BARREIRA = (235, 140, 40)
COR_BARREIRA_LISTRA = (30, 30, 30)

COR_ALERTA = (255, 70, 70)

# --- Etapa 9: armas do ladrão ---
COOLDOWN_OLEO = 20 * FPS
DURACAO_DERRAPAGEM = 2 * FPS
FORCA_DERRAPAGEM = 3.5
COR_OLEO = (35, 30, 20)
COR_OLEO_BRILHO = (70, 60, 35)

COOLDOWN_TIRO = 12 * FPS
VELOCIDADE_PROJETIL = 11
DANO_TIRO = 10
COR_PROJETIL = (255, 220, 80)
