import * as S from "../settings";
import type { Carro } from "../entities/Car";
import type { CarroTrafego } from "../entities/Traffic";
import type { FaixaDePregos, Barreira } from "../entities/Obstacles";
import type { OleoDerrapante, Projetil } from "../entities/Weapons";
import type { Rect } from "../utils/rect";

export function verificarColisaoJogadores(policia: Carro, ladrao: Carro): string | null {
  if (policia.destruido || ladrao.destruido) return null;
  if (!policia.rect.colliderect(ladrao.rect)) return null;

  const overlapX =
    Math.min(policia.rect.right, ladrao.rect.right) - Math.max(policia.rect.left, ladrao.rect.left);
  const overlapY =
    Math.min(policia.rect.bottom, ladrao.rect.bottom) - Math.max(policia.rect.top, ladrao.rect.top);
  const batidaLateral = overlapX < overlapY && policia.faixa !== ladrao.faixa;

  separarCarros(policia, ladrao);
  igualarVelocidade(policia, ladrao);

  if (policia.cooldown_colisao > 0 || ladrao.cooldown_colisao > 0) return null;

  const diff = Math.abs(policia.velocidade_atual - ladrao.velocidade_atual);
  let tipo: string;
  let dano: number;
  if (diff < S.LIMIAR_COLISAO_LEVE) {
    tipo = "leve";
    dano = S.DANO_COLISAO_LEVE;
  } else if (diff < S.LIMIAR_COLISAO_MEDIA) {
    tipo = "media";
    dano = S.DANO_COLISAO_MEDIA;
  } else {
    tipo = "forte";
    dano = S.DANO_COLISAO_FORTE;
  }

  if (batidaLateral) {
    dano = Math.max(dano, S.DANO_COLISAO_LATERAL);
    if (dano >= S.DANO_COLISAO_FORTE) tipo = "forte";
    else if (dano >= S.DANO_COLISAO_MEDIA) tipo = "media";
  }

  policia.aplicarDano(dano);
  ladrao.aplicarDano(dano);
  policia.cooldown_colisao = S.COOLDOWN_COLISAO;
  ladrao.cooldown_colisao = S.COOLDOWN_COLISAO;
  return tipo;
}

export function verificarColisaoTrafego(jogador: Carro, trafego: CarroTrafego[]): string | null {
  if (jogador.destruido) return null;
  let tipoMsg: string | null = null;

  for (const npc of trafego) {
    if (!jogador.rect.colliderect(npc.rect)) continue;
    separarJogadorNpc(jogador, npc);
    if (jogador.cooldown_colisao > 0) continue;

    const impacto = Math.abs(jogador.velocidade_atual - S.VELOCIDADE_REFERENCIA);
    let dano = Math.floor(S.DANO_COLISAO_TRAFEGO_BASE + impacto * S.DANO_COLISAO_TRAFEGO_POR_IMPACTO);
    dano = Math.max(S.DANO_COLISAO_LEVE, Math.min(S.DANO_COLISAO_FORTE, dano));
    jogador.aplicarDano(dano);
    jogador.velocidade_atual = Math.max(0, jogador.velocidade_atual - impacto * 0.35);
    jogador.cooldown_colisao = S.COOLDOWN_COLISAO_TRAFEGO;

    if (dano >= S.DANO_COLISAO_FORTE) tipoMsg = "forte";
    else if (dano >= S.DANO_COLISAO_MEDIA) tipoMsg = "media";
    else tipoMsg = "leve";
  }
  return tipoMsg;
}

function eixoSeparacao(a: Rect, b: Rect, mesmaFaixa: boolean): "x" | "y" | null {
  const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
  const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
  if (ox <= 0 || oy <= 0) return null;
  if (mesmaFaixa || oy <= ox) return "y";
  return "x";
}

function separarCarros(a: Carro, b: Carro) {
  const eixo = eixoSeparacao(a.rect, b.rect, a.faixa === b.faixa);
  if (!eixo) return;
  const folga = S.FOLGA_COLISAO;

  if (eixo === "y") {
    const ox = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.top, b.rect.top);
    const d = ox / 2 + folga;
    if (a.y <= b.y) {
      a.y = Math.max(S.Y_MIN, a.y - d);
      b.y = Math.min(S.Y_MAX, b.y + d);
    } else {
      a.y = Math.min(S.Y_MAX, a.y + d);
      b.y = Math.max(S.Y_MIN, b.y - d);
    }
  } else {
    const ox = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.left, b.rect.left);
    const d = ox / 2 + folga;
    if (a.x <= b.x) {
      a.x -= d;
      b.x += d;
    } else {
      a.x += d;
      b.x -= d;
    }
    a.cancelarTrocaFaixa();
    b.cancelarTrocaFaixa();
  }
  a.rect.center = [Math.round(a.x), Math.round(a.y)];
  b.rect.center = [Math.round(b.x), Math.round(b.y)];
}

function separarJogadorNpc(jogador: Carro, npc: CarroTrafego) {
  const eixo = eixoSeparacao(jogador.rect, npc.rect, jogador.faixa === npc.faixa);
  if (!eixo) return;
  const folga = S.FOLGA_COLISAO;

  if (eixo === "y") {
    const minimo = (jogador.rect.height + npc.rect.height) / 2 + folga;
    if (
      jogador.y < npc.y ||
      (jogador.y === npc.y && jogador.velocidade_atual >= S.VELOCIDADE_REFERENCIA)
    ) {
      npc.y = jogador.y + minimo;
    } else {
      jogador.y = Math.min(S.Y_MAX, npc.y + minimo);
      if (jogador.velocidade_atual > S.VELOCIDADE_REFERENCIA) {
        jogador.velocidade_atual = S.VELOCIDADE_REFERENCIA;
      }
    }
  } else {
    const ox = Math.min(jogador.rect.right, npc.rect.right) - Math.max(jogador.rect.left, npc.rect.left);
    const d = ox + folga;
    if (jogador.x <= npc.x) jogador.x -= d;
    else jogador.x += d;
    jogador.cancelarTrocaFaixa();
  }

  jogador.rect.center = [Math.round(jogador.x), Math.round(jogador.y)];
  npc.rect.center = [Math.round(npc.x), Math.round(npc.y)];

  if (jogador.rect.colliderect(npc.rect)) {
    if (eixo === "y") {
      if (jogador.y <= npc.y) {
        npc.y = jogador.y + (jogador.rect.height + npc.rect.height) / 2 + folga + 1;
      } else {
        jogador.y = Math.min(
          S.Y_MAX,
          npc.y + (jogador.rect.height + npc.rect.height) / 2 + folga + 1,
        );
      }
      jogador.rect.center = [Math.round(jogador.x), Math.round(jogador.y)];
      npc.rect.center = [Math.round(npc.x), Math.round(npc.y)];
    } else {
      jogador.x += jogador.x <= npc.x ? -(folga + 1) : folga + 1;
      jogador.rect.center = [Math.round(jogador.x), Math.round(jogador.y)];
    }
  }
}

function igualarVelocidade(a: Carro, b: Carro) {
  const [frente, tras] = a.y < b.y ? [a, b] : [b, a];
  if (tras.velocidade_atual > frente.velocidade_atual) {
    tras.velocidade_atual = frente.velocidade_atual;
  }
}

export function verificarColisaoSpike(carro: Carro, spike: FaixaDePregos | null) {
  if (!spike || spike.usada || carro.destruido) return false;
  if (!carro.rect.colliderect(spike.rect)) return false;
  spike.usada = true;
  carro.aplicarPneuFurado();
  return true;
}

export function verificarColisaoBarreira(carro: Carro, barreira: Barreira | null) {
  if (!barreira || carro.destruido || carro.cooldown_colisao > 0) return false;
  if (!carro.rect.colliderect(barreira.rect)) return false;
  carro.aplicarDano(S.DANO_BARREIRA);
  carro.velocidade_atual = 0;
  carro.cooldown_colisao = S.COOLDOWN_COLISAO;
  carro.y = Math.min(S.Y_MAX, carro.y + S.EMPURRAO_BARREIRA);
  carro.rect.center = [Math.round(carro.x), Math.round(carro.y)];
  return true;
}

export function verificarColisaoOleo(carro: Carro, oleo: OleoDerrapante | null) {
  if (!oleo || oleo.usada || carro.destruido) return false;
  if (!carro.rect.colliderect(oleo.rect)) return false;
  oleo.usada = true;
  carro.aplicarDerrapagem();
  return true;
}

export function verificarColisaoProjetil(carro: Carro, projetil: Projetil | null) {
  if (!projetil || projetil.atingiu || carro.destruido) return false;
  if (!carro.rect.colliderect(projetil.rect)) return false;
  projetil.atingiu = true;
  carro.aplicarDano(S.DANO_TIRO);
  return true;
}
