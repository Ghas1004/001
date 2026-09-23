export const LARGURA_TELA = 1280;
export const ALTURA_TELA = 720;
export const FPS = 60;
export const TITULO_JANELA = "Highway Pursuit";

export const NUM_FAIXAS = 4;
export const LARGURA_FAIXA = 168;
export const LARGURA_PISTA = NUM_FAIXAS * LARGURA_FAIXA;
export const MARGEM_PISTA = Math.floor((LARGURA_TELA - LARGURA_PISTA) / 2);

export const VELOCIDADE_PISTA = 10;
export const ALTURA_TRACO = 44;
export const ESPACO_TRACO = 32;
export const LARGURA_LINHA = 6;
export const LARGURA_ACOSTAMENTO = 28;
export const ALTURA_JUNTA_ASFALTO = 4;
export const ESPACO_JUNTA_ASFALTO = 240;

export const COR_GRAMA: RGB = [28, 84, 38];
export const COR_ACOSTAMENTO: RGB = [196, 184, 150];
export const COR_ASFALTO: RGB = [48, 48, 54];
export const COR_JUNTA_ASFALTO: RGB = [38, 38, 43];
export const COR_LINHA: RGB = [225, 225, 225];
export const COR_BORDA_PISTA: RGB = [235, 200, 60];
export const COR_POLICIA: RGB = [40, 100, 230];
export const COR_LADRAO: RGB = [220, 60, 50];
export const COR_TEXTO: RGB = [240, 240, 240];
export const COR_NITRO: RGB = [90, 190, 240];
export const COR_SPIKE_BASE: RGB = [60, 60, 65];
export const COR_SPIKE_PONTA: RGB = [222, 222, 228];
export const COR_BARREIRA: RGB = [235, 140, 40];
export const COR_BARREIRA_LISTRA: RGB = [30, 30, 30];
export const COR_ALERTA: RGB = [255, 70, 70];
export const COR_OLEO: RGB = [35, 30, 20];
export const COR_OLEO_BRILHO: RGB = [70, 60, 35];
export const COR_PROJETIL: RGB = [255, 220, 80];

export type RGB = [number, number, number];

export const LARGURA_CARRO = 58;
export const ALTURA_CARRO = 104;
export const VELOCIDADE_TROCA_FAIXA = 16;

export const Y_POLICIA = ALTURA_TELA - 150;
export const Y_LADRAO = ALTURA_TELA - 310;

export const VIDA_INICIAL = 100;
export const VELOCIDADE_BASE_INICIAL = 24;
export const VELOCIDADE_MAXIMA_INICIAL = 40;
export const VELOCIDADE_REFERENCIA = 24;
export const INCREMENTO_ACELERACAO = 0.18;
export const DECREMENTO_DESACELERACAO = 0.28;
export const DECREMENTO_FREIO = 0.75;
export const BONUS_NITRO = 10;
export const INCREMENTO_NITRO = 0.85;
export const NITRO_INICIAL = 100;
export const CONSUMO_NITRO = 0.55;
export const RECARGA_NITRO = 0.3;
export const FATOR_DESLOCAMENTO_Y = 0.32;
export const Y_MIN = 88;
export const Y_MAX = ALTURA_TELA - 48;

export const VELOCIDADE_TRAFEGO_MIN = 4;
export const VELOCIDADE_TRAFEGO_MAX = 8;
export const INTERVALO_SPAWN_MIN = 35;
export const INTERVALO_SPAWN_MAX = 90;
export const CORES_TRAFEGO: RGB[] = [
  [215, 195, 60],
  [170, 170, 178],
  [90, 150, 220],
  [230, 140, 40],
];

export const LIMIAR_COLISAO_LEVE = 3;
export const LIMIAR_COLISAO_MEDIA = 10;
export const DANO_COLISAO_LEVE = 3;
export const DANO_COLISAO_MEDIA = 8;
export const DANO_COLISAO_FORTE = 15;
export const COOLDOWN_COLISAO = 28;
export const DANO_COLISAO_LATERAL = 6;
export const MARGEM_BLOQUEIO_FAIXA = 18;
export const FOLGA_COLISAO = 2;

export const DANO_COLISAO_TRAFEGO_BASE = 6;
export const DANO_COLISAO_TRAFEGO_POR_IMPACTO = 1.2;
export const COOLDOWN_COLISAO_TRAFEGO = 40;

export const ANGULO_CURVA_MAX = 14;
export const FATOR_INCLINACAO = 0.22;
export const FATOR_RETORNO_INCLINACAO = 0.18;

export const DURACAO_ALERTA = 2 * FPS;
export const COOLDOWN_SPIKE = 60 * FPS;
export const DURACAO_PNEU_FURADO = 60 * FPS; // 1 minuto
export const PENALIDADE_VELOCIDADE_PNEU_FURADO = 8;
export const FATOR_CONTROLE_PNEU_FURADO = 0.35;

export const COOLDOWN_BARREIRA = 60 * FPS;
export const DANO_BARREIRA = 12;
export const EMPURRAO_BARREIRA = 40;

export const COOLDOWN_OLEO = 20 * FPS;
export const DURACAO_DERRAPAGEM = 2 * FPS;
export const FORCA_DERRAPAGEM = 3.5;
export const COOLDOWN_TIRO = 12 * FPS;
export const VELOCIDADE_PROJETIL = 11;
export const DANO_TIRO = 10;

export const SNAPSHOT_HZ = 20;

/** Modo Tempo: polícia tem 3 minutos para capturar o ladrão */
export const DURACAO_MODO_TEMPO = 3 * 60 * FPS;

export function rgb(c: RGB, alpha = 1): string {
  if (alpha >= 1) return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
  return `rgba(${c[0]}, ${c[1]}, ${c[2]}, ${alpha})`;
}
