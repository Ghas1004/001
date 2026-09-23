import * as S from "../settings";
import { Rect } from "../utils/rect";

export interface TrafficSnapshot {
  faixa: number;
  x: number;
  y: number;
  cor: S.RGB;
}

export class CarroTrafego {
  faixa: number;
  velocidade: number;
  cor: S.RGB;
  x: number;
  y: number;
  rect: Rect;

  constructor(faixa: number, y: number, velocidade: number, cor: S.RGB) {
    this.faixa = faixa;
    this.velocidade = velocidade;
    this.cor = cor;
    this.x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA + S.LARGURA_FAIXA / 2;
    this.y = y;
    this.rect = new Rect(0, 0, S.LARGURA_CARRO - 6, S.ALTURA_CARRO - 10);
    this.rect.center = [this.x, this.y];
  }

  atualizar() {
    this.y += this.velocidade;
    this.rect.center = [Math.round(this.x), Math.round(this.y)];
  }

  foraDaTela() {
    return this.rect.top > S.ALTURA_TELA;
  }

  toSnapshot(): TrafficSnapshot {
    return { faixa: this.faixa, x: this.x, y: this.y, cor: this.cor };
  }

  static fromSnapshot(s: TrafficSnapshot) {
    const c = new CarroTrafego(s.faixa, s.y, 0, s.cor);
    c.x = s.x;
    c.rect.center = [Math.round(c.x), Math.round(c.y)];
    return c;
  }

  desenhar(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = S.rgb(this.cor);
    ctx.beginPath();
    const r = 6;
    const x = this.rect.left;
    const y = this.rect.top;
    const w = this.rect.width;
    const h = this.rect.height;
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.fill();
  }
}
