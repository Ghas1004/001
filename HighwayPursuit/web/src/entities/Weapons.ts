import * as S from "../settings";
import { Rect } from "../utils/rect";

export class OleoDerrapante {
  faixa: number;
  usada = false;
  x: number;
  y: number;
  rect: Rect;

  constructor(faixa: number, yInicial: number) {
    this.faixa = faixa;
    this.x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA + S.LARGURA_FAIXA / 2;
    this.y = yInicial;
    this.rect = new Rect(0, 0, S.LARGURA_FAIXA - 30, 34);
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
    ctx.fillStyle = S.rgb(S.COR_OLEO);
    ctx.beginPath();
    ctx.ellipse(this.x, this.y, this.rect.width / 2, this.rect.height / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = S.rgb(S.COR_OLEO_BRILHO);
    ctx.beginPath();
    ctx.ellipse(this.x - 6, this.y - 4, this.rect.width * 0.2, this.rect.height * 0.175, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

export class Projetil {
  faixa: number;
  atingiu = false;
  x: number;
  y: number;
  rect: Rect;

  constructor(faixa: number, yInicial: number) {
    this.faixa = faixa;
    this.x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA + S.LARGURA_FAIXA / 2;
    this.y = yInicial;
    this.rect = new Rect(0, 0, 10, 22);
    this.rect.center = [this.x, this.y];
  }

  atualizar() {
    this.y += S.VELOCIDADE_PROJETIL;
    this.rect.center = [Math.round(this.x), Math.round(this.y)];
  }

  foraDaTela() {
    return this.rect.top > S.ALTURA_TELA;
  }

  desenhar(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = S.rgb(S.COR_PROJETIL);
    ctx.fillRect(this.rect.left, this.rect.top, this.rect.width, this.rect.height);
  }
}
