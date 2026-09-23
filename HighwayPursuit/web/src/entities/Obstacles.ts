import * as S from "../settings";
import { Rect } from "../utils/rect";

export class FaixaDePregos {
  faixa: number;
  usada = false;
  x: number;
  y: number;
  rect: Rect;

  constructor(faixa: number) {
    this.faixa = faixa;
    this.x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA + S.LARGURA_FAIXA / 2;
    this.y = -30;
    this.rect = new Rect(0, 0, S.LARGURA_FAIXA - 24, 22);
    this.rect.center = [this.x, this.y];
  }

  atualizar() {
    this.y += S.VELOCIDADE_PISTA;
    this.rect.center = [Math.round(this.x), Math.round(this.y)];
  }

  foraDaTela() {
    return this.rect.top > S.ALTURA_TELA;
  }

  desenhar(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = S.rgb(S.COR_SPIKE_BASE);
    ctx.fillRect(this.rect.left, this.rect.top, this.rect.width, this.rect.height);
    const n = 6;
    const w = this.rect.width / n;
    for (let i = 0; i < n; i++) {
      const cx = this.rect.left + w * (i + 0.5);
      ctx.fillStyle = S.rgb(S.COR_SPIKE_PONTA);
      ctx.beginPath();
      ctx.moveTo(cx, this.rect.top - 6);
      ctx.lineTo(cx - 5, this.rect.top + 4);
      ctx.lineTo(cx + 5, this.rect.top + 4);
      ctx.fill();
    }
  }
}

export class Barreira {
  faixa: number;
  x: number;
  y: number;
  rect: Rect;

  constructor(faixa: number) {
    this.faixa = faixa;
    this.x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA + S.LARGURA_FAIXA / 2;
    this.y = -50;
    this.rect = new Rect(0, 0, S.LARGURA_FAIXA - 8, 46);
    this.rect.center = [this.x, this.y];
  }

  atualizar() {
    this.y += S.VELOCIDADE_PISTA;
    this.rect.center = [Math.round(this.x), Math.round(this.y)];
  }

  foraDaTela() {
    return this.rect.top > S.ALTURA_TELA;
  }

  desenhar(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = S.rgb(S.COR_BARREIRA);
    ctx.fillRect(this.rect.left, this.rect.top, this.rect.width, this.rect.height);
    ctx.strokeStyle = S.rgb(S.COR_BARREIRA_LISTRA);
    ctx.lineWidth = 2;
    ctx.strokeRect(this.rect.left, this.rect.top, this.rect.width, this.rect.height);
  }
}
