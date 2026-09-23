import * as S from "../settings";
import { Rect } from "../utils/rect";

export interface CarSnapshot {
  faixa: number;
  x: number;
  y: number;
  angulo: number;
  vida: number;
  nitro: number;
  velocidade: number;
  destruido: boolean;
  pneuFurado: boolean;
  timerPneuFurado: number;
}

export class Carro {
  faixa: number;
  y: number;
  cor: S.RGB;
  vida = S.VIDA_INICIAL;
  velocidade_atual = S.VELOCIDADE_BASE_INICIAL;
  nitro = S.NITRO_INICIAL;
  destruido = false;
  cooldown_colisao = 0;
  pneu_furado = false;
  timer_pneu_furado = 0;
  timer_derrapagem = 0;
  angulo = 0;
  x: number;
  x_alvo: number;
  rect: Rect;

  constructor(faixa_inicial: number, y: number, cor: S.RGB) {
    this.faixa = faixa_inicial;
    this.y = y;
    this.cor = cor;
    this.x = this.xDaFaixa(this.faixa);
    this.x_alvo = this.x;
    this.rect = new Rect(0, 0, S.LARGURA_CARRO, S.ALTURA_CARRO);
    this.rect.center = [this.x, this.y];
  }

  xDaFaixa(faixa: number) {
    return S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA + S.LARGURA_FAIXA / 2;
  }

  trocarFaixa(direcao: number, ocupantes: Array<{ faixa: number; y: number; destruido?: boolean }> = []) {
    if (this.destruido || this.timer_derrapagem > 0) return false;
    const nova = this.faixa + direcao;
    if (nova < 0 || nova >= S.NUM_FAIXAS) return false;
    if (this.faixaOcupada(nova, ocupantes)) return false;
    this.faixa = nova;
    this.x_alvo = this.xDaFaixa(this.faixa);
    return true;
  }

  private faixaOcupada(
    faixa: number,
    ocupantes: Array<{ faixa: number; y: number; destruido?: boolean }>,
  ) {
    const margem = S.ALTURA_CARRO + S.MARGEM_BLOQUEIO_FAIXA;
    for (const outro of ocupantes) {
      if (outro === (this as unknown) || outro.destruido) continue;
      if (outro.faixa !== faixa) continue;
      if (Math.abs(outro.y - this.y) < margem) return true;
    }
    return false;
  }

  cancelarTrocaFaixa() {
    this.x_alvo = this.xDaFaixa(this.faixa);
  }

  velocidadeBaseAtual() {
    const reducao = (S.VIDA_INICIAL - this.vida) / 10;
    return Math.max(0, S.VELOCIDADE_BASE_INICIAL - reducao);
  }

  velocidadeMaximaAtual() {
    const reducao = (S.VIDA_INICIAL - this.vida) / 10;
    let maximo = Math.max(0, S.VELOCIDADE_MAXIMA_INICIAL - reducao);
    if (this.pneu_furado) maximo = Math.max(0, maximo - S.PENALIDADE_VELOCIDADE_PNEU_FURADO);
    return maximo;
  }

  aplicarPneuFurado() {
    this.pneu_furado = true;
    this.timer_pneu_furado = S.DURACAO_PNEU_FURADO;
  }

  aplicarDerrapagem() {
    this.timer_derrapagem = S.DURACAO_DERRAPAGEM;
  }

  aplicarDano(quantidade: number) {
    if (this.destruido) return;
    this.vida = Math.max(0, this.vida - quantidade);
    if (this.vida <= 0) {
      this.destruido = true;
      this.velocidade_atual = 0;
    }
  }

  private atualizarVelocidade(acelerando: boolean, freando: boolean, usandoNitro: boolean) {
    if (this.destruido) {
      this.velocidade_atual = 0;
      this.nitro = Math.min(S.NITRO_INICIAL, this.nitro + S.RECARGA_NITRO);
      return;
    }

    const base = this.velocidadeBaseAtual();
    const maximo = this.velocidadeMaximaAtual();
    const tetoNitro = maximo + S.BONUS_NITRO;
    usandoNitro = usandoNitro && this.nitro > 0 && !freando;

    if (freando) {
      this.velocidade_atual = Math.max(this.velocidade_atual - S.DECREMENTO_FREIO, 0);
    } else if (usandoNitro) {
      this.velocidade_atual = Math.min(this.velocidade_atual + S.INCREMENTO_NITRO, tetoNitro);
    } else if (acelerando) {
      this.velocidade_atual = Math.min(this.velocidade_atual + S.INCREMENTO_ACELERACAO, maximo);
    } else if (this.velocidade_atual > base) {
      this.velocidade_atual = Math.max(this.velocidade_atual - S.DECREMENTO_DESACELERACAO, base);
    } else {
      this.velocidade_atual = base;
    }

    if (usandoNitro) this.nitro = Math.max(0, this.nitro - S.CONSUMO_NITRO);
    else this.nitro = Math.min(S.NITRO_INICIAL, this.nitro + S.RECARGA_NITRO);

    const teto = usandoNitro ? tetoNitro : maximo;
    this.velocidade_atual = Math.min(this.velocidade_atual, teto);
  }

  private moverNoMundo() {
    const diferenca = this.velocidade_atual - S.VELOCIDADE_REFERENCIA;
    this.y -= diferenca * S.FATOR_DESLOCAMENTO_Y;
    this.y = Math.max(S.Y_MIN, Math.min(S.Y_MAX, this.y));
  }

  private atualizarInclinacao(movendoLateral: number) {
    let alvo = 0;
    let fator = S.FATOR_RETORNO_INCLINACAO;
    if (movendoLateral < 0) {
      alvo = S.ANGULO_CURVA_MAX;
      fator = S.FATOR_INCLINACAO;
    } else if (movendoLateral > 0) {
      alvo = -S.ANGULO_CURVA_MAX;
      fator = S.FATOR_INCLINACAO;
    }
    this.angulo += (alvo - this.angulo) * fator;
    if (Math.abs(this.angulo) < 0.05) this.angulo = 0;
  }

  atualizar(acelerando = false, freando = false, usandoNitro = false) {
    this.atualizarVelocidade(acelerando, freando, usandoNitro);
    this.moverNoMundo();

    if (this.timer_pneu_furado > 0) {
      this.timer_pneu_furado -= 1;
      if (this.timer_pneu_furado <= 0) {
        this.pneu_furado = false;
        this.timer_pneu_furado = 0;
      }
    }

    let velocidadeTroca = S.VELOCIDADE_TROCA_FAIXA;
    if (this.pneu_furado) velocidadeTroca *= S.FATOR_CONTROLE_PNEU_FURADO;

    let movendoLateral = 0;
    if (this.timer_derrapagem > 0) {
      this.timer_derrapagem -= 1;
      this.x += (Math.random() * 2 - 1) * S.FORCA_DERRAPAGEM;
      this.x = Math.max(
        S.MARGEM_PISTA + S.LARGURA_CARRO / 2,
        Math.min(S.MARGEM_PISTA + S.LARGURA_PISTA - S.LARGURA_CARRO / 2, this.x),
      );
      const faixaEstimada = Math.floor((this.x - S.MARGEM_PISTA) / S.LARGURA_FAIXA);
      this.faixa = Math.max(0, Math.min(S.NUM_FAIXAS - 1, faixaEstimada));
      this.x_alvo = this.xDaFaixa(this.faixa);
      movendoLateral = Math.random() > 0.5 ? 1 : -1;
    } else if (this.x < this.x_alvo) {
      this.x = Math.min(this.x + velocidadeTroca, this.x_alvo);
      movendoLateral = 1;
    } else if (this.x > this.x_alvo) {
      this.x = Math.max(this.x - velocidadeTroca, this.x_alvo);
      movendoLateral = -1;
    }

    this.atualizarInclinacao(movendoLateral);
    if (this.cooldown_colisao > 0) this.cooldown_colisao -= 1;
    this.rect.center = [Math.round(this.x), Math.round(this.y)];
  }

  toSnapshot(): CarSnapshot {
    return {
      faixa: this.faixa,
      x: this.x,
      y: this.y,
      angulo: this.angulo,
      vida: this.vida,
      nitro: this.nitro,
      velocidade: this.velocidade_atual,
      destruido: this.destruido,
      pneuFurado: this.pneu_furado,
      timerPneuFurado: this.timer_pneu_furado,
    };
  }

  applySnapshot(s: CarSnapshot) {
    this.faixa = s.faixa;
    this.x = s.x;
    this.y = s.y;
    this.x_alvo = this.xDaFaixa(this.faixa);
    this.angulo = s.angulo;
    this.vida = s.vida;
    this.nitro = s.nitro;
    this.velocidade_atual = s.velocidade;
    this.destruido = s.destruido;
    this.pneu_furado = s.pneuFurado;
    this.timer_pneu_furado = s.timerPneuFurado ?? 0;
    this.rect.center = [Math.round(this.x), Math.round(this.y)];
  }

  desenhar(ctx: CanvasRenderingContext2D) {
    const cor = this.destruido ? ([90, 90, 90] as S.RGB) : this.cor;
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate((-this.angulo * Math.PI) / 180);

    roundRect(ctx, -S.LARGURA_CARRO / 2, -S.ALTURA_CARRO / 2, S.LARGURA_CARRO, S.ALTURA_CARRO, 8);
    ctx.fillStyle = S.rgb(cor);
    ctx.fill();

    roundRect(ctx, -S.LARGURA_CARRO / 2 + 8, -S.ALTURA_CARRO / 2 + 8, S.LARGURA_CARRO - 16, 10, 3);
    ctx.fillStyle = "#fff";
    ctx.fill();

    if (this.pneu_furado) {
      roundRect(ctx, -S.LARGURA_CARRO / 2, -S.ALTURA_CARRO / 2, S.LARGURA_CARRO, S.ALTURA_CARRO, 8);
      ctx.strokeStyle = "rgb(235,140,40)";
      ctx.lineWidth = 3;
      ctx.stroke();
    }
    ctx.restore();

    const bx = this.rect.left;
    const by = this.rect.top - 12;
    ctx.fillStyle = "rgb(40,40,40)";
    ctx.fillRect(bx, by, S.LARGURA_CARRO, 6);
    ctx.fillStyle = this.vida > 40 ? "rgb(60,200,80)" : "rgb(220,80,50)";
    ctx.fillRect(bx, by, (S.LARGURA_CARRO * this.vida) / S.VIDA_INICIAL, 6);
  }
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
