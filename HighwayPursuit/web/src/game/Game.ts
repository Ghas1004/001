import * as S from "../settings";
import { Carro } from "../entities/Car";
import { CarroTrafego } from "../entities/Traffic";
import { FaixaDePregos, Barreira } from "../entities/Obstacles";
import { OleoDerrapante, Projetil } from "../entities/Weapons";
import {
  verificarColisaoJogadores,
  verificarColisaoTrafego,
  verificarColisaoSpike,
  verificarColisaoBarreira,
  verificarColisaoOleo,
  verificarColisaoProjetil,
} from "../systems/collision";
import { emptyInput, type PlayerInput } from "../input/controls";
import type { GameSnapshot, MatchType, Winner } from "../net/protocol";
import { AiController } from "../ai/AiController";

export type GameMode = "solo" | "host" | "guest";

export class Game {
  policia = new Carro(1, S.Y_POLICIA, S.COR_POLICIA);
  ladrao = new Carro(2, S.Y_LADRAO, S.COR_LADRAO);
  trafego: CarroTrafego[] = [];
  offsetPista = 0;
  framesTotais = 0;
  mensagemColisao = "";
  timerMensagem = 0;

  spike: FaixaDePregos | null = null;
  cooldownSpike = 0;
  avisoSpike = 0;
  avisoSpikeFaixa: number | null = null;

  barreira: Barreira | null = null;
  cooldownBarreira = 0;
  avisoBarreira = 0;
  avisoBarreiraFaixa: number | null = null;

  oleo: OleoDerrapante | null = null;
  cooldownOleo = 0;
  projetil: Projetil | null = null;
  cooldownTiro = 0;

  matchType: MatchType = "infinite";
  /** Papel do humano no modo solo_ai */
  humanRole: "police" | "thief" = "police";
  tempoRestante: number | null = null;
  terminado = false;
  vencedor: Winner = null;
  motivoFim = "";

  private contadorSpawn = 0;
  private proximoSpawn = 60;
  private remoteInput: PlayerInput = emptyInput();
  private latestSnapshot: GameSnapshot | null = null;
  private ai = new AiController();

  mode: GameMode = "solo";

  configure(opts: {
    mode: GameMode;
    matchType: MatchType;
    humanRole?: "police" | "thief";
  }) {
    this.mode = opts.mode;
    this.matchType = opts.matchType;
    this.humanRole = opts.humanRole ?? "police";
    this.tempoRestante = opts.matchType === "timed" ? S.DURACAO_MODO_TEMPO : null;
    this.terminado = false;
    this.vencedor = null;
    this.motivoFim = "";
  }

  setMode(mode: GameMode) {
    this.mode = mode;
  }

  setRemoteInput(input: PlayerInput) {
    if (input.laneDelta) this.remoteInput.laneDelta = input.laneDelta;
    if (input.ability) this.remoteInput.ability = input.ability;
    this.remoteInput.accel = input.accel;
    this.remoteInput.brake = input.brake;
    this.remoteInput.nitro = input.nitro;
  }

  applySnapshot(snapshot: GameSnapshot) {
    this.latestSnapshot = snapshot;
  }

  private consumirRemote(): PlayerInput {
    const i = { ...this.remoteInput };
    this.remoteInput.laneDelta = 0;
    this.remoteInput.ability = null;
    return i;
  }

  private encerrar(vencedor: Winner, motivo: string) {
    if (this.terminado) return;
    this.terminado = true;
    this.vencedor = vencedor;
    this.motivoFim = motivo;
    this.mensagemColisao = motivo;
    this.timerMensagem = S.FPS * 4;
  }

  private checarFimDeJogo() {
    if (this.terminado) return;

    if (this.ladrao.destruido) {
      this.encerrar("police", "POLICIA CAPTUROU O LADRAO!");
      return;
    }
    if (this.policia.destruido) {
      this.encerrar("thief", "LADRAO ESCAPOU (policia destruida)!");
      return;
    }

    if (this.matchType === "timed" && this.tempoRestante !== null) {
      if (this.tempoRestante <= 0) {
        this.encerrar("thief", "TEMPO ESGOTADO — LADRAO ESCAPOU!");
      }
    }
  }

  update(localInput: PlayerInput) {
    if (this.mode === "guest") {
      if (this.latestSnapshot) this.hydrate(this.latestSnapshot);
      return;
    }

    if (this.terminado) {
      if (this.timerMensagem > 0) this.timerMensagem -= 1;
      return;
    }

    this.framesTotais += 1;
    this.offsetPista = (this.offsetPista + S.VELOCIDADE_PISTA) % (S.ALTURA_TRACO + S.ESPACO_TRACO);

    if (this.matchType === "timed" && this.tempoRestante !== null) {
      this.tempoRestante = Math.max(0, this.tempoRestante - 1);
    }

    let inputPolicia: PlayerInput;
    let inputLadrao: PlayerInput;

    if (this.matchType === "solo_ai") {
      const aiInput = this.ai.update(
        this.humanRole === "police" ? "thief" : "police",
        this.humanRole === "police" ? this.ladrao : this.policia,
        this.humanRole === "police" ? this.policia : this.ladrao,
        this.trafego,
        {
          spike: this.cooldownSpike,
          barrier: this.cooldownBarreira,
          oil: this.cooldownOleo,
          shot: this.cooldownTiro,
        },
      );
      if (this.humanRole === "police") {
        inputPolicia = localInput;
        inputLadrao = aiInput;
      } else {
        inputPolicia = aiInput;
        inputLadrao = localInput;
      }
    } else if (this.mode === "solo") {
      inputPolicia = localInput;
      inputLadrao = localInput;
    } else {
      inputPolicia = localInput;
      inputLadrao = this.consumirRemote();
    }

    this.aplicarInputCarro(this.policia, inputPolicia, "police");
    this.aplicarInputCarro(this.ladrao, inputLadrao, "thief");

    this.atualizarTrafego();
    this.atualizarSpike();
    this.atualizarBarreira();
    this.atualizarOleo();
    this.atualizarProjetil();

    const tipo = verificarColisaoJogadores(this.policia, this.ladrao);
    if (tipo) {
      this.mensagemColisao = `Colisao ${tipo.toUpperCase()}!`;
      this.timerMensagem = S.FPS;
    }

    for (const [jogador, rotulo] of [
      [this.policia, "POLICIA"],
      [this.ladrao, "LADRAO"],
    ] as const) {
      const t = verificarColisaoTrafego(jogador, this.trafego);
      if (t) {
        this.mensagemColisao = `${rotulo} x TRANSITO (${t.toUpperCase()})!`;
        this.timerMensagem = S.FPS;
      }
    }

    this.checarFimDeJogo();

    if (this.timerMensagem > 0) this.timerMensagem -= 1;
  }

  private aplicarInputCarro(carro: Carro, input: PlayerInput, role: "police" | "thief") {
    if (input.laneDelta) carro.trocarFaixa(input.laneDelta, this.trafego);

    if (role === "police") {
      if (input.ability === "spike") this.tentarSpike();
      if (input.ability === "barrier") this.tentarBarreira();
    } else {
      if (input.ability === "oil") this.tentarOleo();
      if (input.ability === "shot") this.tentarTiro();
    }

    carro.atualizar(input.accel, input.brake, input.nitro);
  }

  private atualizarTrafego() {
    this.contadorSpawn += 1;
    if (this.contadorSpawn >= this.proximoSpawn) {
      this.contadorSpawn = 0;
      this.proximoSpawn =
        S.INTERVALO_SPAWN_MIN +
        Math.floor(Math.random() * (S.INTERVALO_SPAWN_MAX - S.INTERVALO_SPAWN_MIN + 1));
      const faixa = Math.floor(Math.random() * S.NUM_FAIXAS);
      const vel =
        S.VELOCIDADE_TRAFEGO_MIN +
        Math.random() * (S.VELOCIDADE_TRAFEGO_MAX - S.VELOCIDADE_TRAFEGO_MIN);
      const cor = S.CORES_TRAFEGO[Math.floor(Math.random() * S.CORES_TRAFEGO.length)];
      this.trafego.push(new CarroTrafego(faixa, -S.ALTURA_CARRO, vel, cor));
    }
    for (const c of this.trafego) c.atualizar();
    this.trafego = this.trafego.filter((c) => !c.foraDaTela());
  }

  private tentarSpike() {
    if (this.cooldownSpike > 0 || this.avisoSpike > 0 || this.spike) return;
    this.avisoSpikeFaixa = this.ladrao.faixa;
    this.avisoSpike = S.DURACAO_ALERTA;
    this.cooldownSpike = S.COOLDOWN_SPIKE;
  }

  private atualizarSpike() {
    if (this.cooldownSpike > 0) this.cooldownSpike -= 1;
    if (this.avisoSpike > 0) {
      this.avisoSpike -= 1;
      if (this.avisoSpike === 0 && this.avisoSpikeFaixa !== null) {
        this.spike = new FaixaDePregos(this.avisoSpikeFaixa);
      }
    }
    if (this.spike) {
      this.spike.atualizar();
      verificarColisaoSpike(this.policia, this.spike);
      verificarColisaoSpike(this.ladrao, this.spike);
      if (this.spike.usada || this.spike.foraDaTela()) this.spike = null;
    }
  }

  private tentarBarreira() {
    if (this.cooldownBarreira > 0 || this.avisoBarreira > 0 || this.barreira) return;
    this.avisoBarreiraFaixa = this.ladrao.faixa;
    this.avisoBarreira = S.DURACAO_ALERTA;
    this.cooldownBarreira = S.COOLDOWN_BARREIRA;
  }

  private atualizarBarreira() {
    if (this.cooldownBarreira > 0) this.cooldownBarreira -= 1;
    if (this.avisoBarreira > 0) {
      this.avisoBarreira -= 1;
      if (this.avisoBarreira === 0 && this.avisoBarreiraFaixa !== null) {
        this.barreira = new Barreira(this.avisoBarreiraFaixa);
      }
    }
    if (this.barreira) {
      this.barreira.atualizar();
      verificarColisaoBarreira(this.policia, this.barreira);
      verificarColisaoBarreira(this.ladrao, this.barreira);
      if (this.barreira.foraDaTela()) this.barreira = null;
    }
  }

  private tentarOleo() {
    if (this.cooldownOleo > 0 || this.oleo) return;
    this.oleo = new OleoDerrapante(this.ladrao.faixa, this.ladrao.y + S.ALTURA_CARRO / 2 + 12);
    this.cooldownOleo = S.COOLDOWN_OLEO;
  }

  private atualizarOleo() {
    if (this.cooldownOleo > 0) this.cooldownOleo -= 1;
    if (this.oleo) {
      this.oleo.atualizar();
      verificarColisaoOleo(this.policia, this.oleo);
      if (this.oleo.usada || this.oleo.foraDaTela()) this.oleo = null;
    }
  }

  private tentarTiro() {
    if (this.cooldownTiro > 0 || this.projetil) return;
    this.projetil = new Projetil(this.ladrao.faixa, this.ladrao.y + S.ALTURA_CARRO / 2 + 4);
    this.cooldownTiro = S.COOLDOWN_TIRO;
  }

  private atualizarProjetil() {
    if (this.cooldownTiro > 0) this.cooldownTiro -= 1;
    if (this.projetil) {
      this.projetil.atualizar();
      verificarColisaoProjetil(this.policia, this.projetil);
      if (this.projetil.atingiu || this.projetil.foraDaTela()) this.projetil = null;
    }
  }

  toSnapshot(): GameSnapshot {
    return {
      frames: this.framesTotais,
      offsetPista: this.offsetPista,
      policia: this.policia.toSnapshot(),
      ladrao: this.ladrao.toSnapshot(),
      trafego: this.trafego.map((t) => t.toSnapshot()),
      mensagemColisao: this.mensagemColisao,
      timerMensagem: this.timerMensagem,
      spike: this.spike
        ? { faixa: this.spike.faixa, x: this.spike.x, y: this.spike.y, usada: this.spike.usada }
        : null,
      barreira: this.barreira
        ? { faixa: this.barreira.faixa, x: this.barreira.x, y: this.barreira.y }
        : null,
      oleo: this.oleo
        ? { faixa: this.oleo.faixa, x: this.oleo.x, y: this.oleo.y, usada: this.oleo.usada }
        : null,
      projetil: this.projetil
        ? {
            faixa: this.projetil.faixa,
            x: this.projetil.x,
            y: this.projetil.y,
            atingiu: this.projetil.atingiu,
          }
        : null,
      avisoSpike: this.avisoSpike,
      avisoSpikeFaixa: this.avisoSpikeFaixa,
      avisoBarreira: this.avisoBarreira,
      avisoBarreiraFaixa: this.avisoBarreiraFaixa,
      cooldownSpike: this.cooldownSpike,
      cooldownBarreira: this.cooldownBarreira,
      cooldownOleo: this.cooldownOleo,
      cooldownTiro: this.cooldownTiro,
      matchType: this.matchType,
      tempoRestante: this.tempoRestante,
      terminado: this.terminado,
      vencedor: this.vencedor,
      motivoFim: this.motivoFim,
    };
  }

  private hydrate(s: GameSnapshot) {
    this.framesTotais = s.frames;
    this.offsetPista = s.offsetPista;
    this.policia.applySnapshot(s.policia);
    this.ladrao.applySnapshot(s.ladrao);
    this.trafego = s.trafego.map((t) => CarroTrafego.fromSnapshot(t));
    this.mensagemColisao = s.mensagemColisao;
    this.timerMensagem = s.timerMensagem;
    this.avisoSpike = s.avisoSpike;
    this.avisoSpikeFaixa = s.avisoSpikeFaixa;
    this.avisoBarreira = s.avisoBarreira;
    this.avisoBarreiraFaixa = s.avisoBarreiraFaixa;
    this.cooldownSpike = s.cooldownSpike;
    this.cooldownBarreira = s.cooldownBarreira;
    this.cooldownOleo = s.cooldownOleo;
    this.cooldownTiro = s.cooldownTiro;
    this.matchType = s.matchType ?? this.matchType;
    this.tempoRestante = s.tempoRestante ?? null;
    this.terminado = s.terminado ?? false;
    this.vencedor = s.vencedor ?? null;
    this.motivoFim = s.motivoFim ?? "";

    if (s.spike) {
      this.spike = new FaixaDePregos(s.spike.faixa);
      this.spike.x = s.spike.x;
      this.spike.y = s.spike.y;
      this.spike.usada = s.spike.usada;
      this.spike.rect.center = [Math.round(this.spike.x), Math.round(this.spike.y)];
    } else this.spike = null;

    if (s.barreira) {
      this.barreira = new Barreira(s.barreira.faixa);
      this.barreira.x = s.barreira.x;
      this.barreira.y = s.barreira.y;
      this.barreira.rect.center = [Math.round(this.barreira.x), Math.round(this.barreira.y)];
    } else this.barreira = null;

    if (s.oleo) {
      this.oleo = new OleoDerrapante(s.oleo.faixa, s.oleo.y);
      this.oleo.x = s.oleo.x;
      this.oleo.usada = s.oleo.usada;
      this.oleo.rect.center = [Math.round(this.oleo.x), Math.round(this.oleo.y)];
    } else this.oleo = null;

    if (s.projetil) {
      this.projetil = new Projetil(s.projetil.faixa, s.projetil.y);
      this.projetil.x = s.projetil.x;
      this.projetil.atingiu = s.projetil.atingiu;
      this.projetil.rect.center = [Math.round(this.projetil.x), Math.round(this.projetil.y)];
    } else this.projetil = null;
  }

  draw(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = S.rgb(S.COR_GRAMA);
    ctx.fillRect(0, 0, S.LARGURA_TELA, S.ALTURA_TELA);
    this.desenharPista(ctx);

    for (const t of this.trafego) t.desenhar(ctx);
    this.spike?.desenhar(ctx);
    this.barreira?.desenhar(ctx);
    this.oleo?.desenhar(ctx);
    this.projetil?.desenhar(ctx);
    this.policia.desenhar(ctx);
    this.ladrao.desenhar(ctx);
    this.desenharAvisos(ctx);
    this.desenharHud(ctx);
    if (this.terminado) this.desenharTelaFim(ctx);
  }

  private desenharPista(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = S.rgb(S.COR_ACOSTAMENTO);
    ctx.fillRect(S.MARGEM_PISTA - S.LARGURA_ACOSTAMENTO, 0, S.LARGURA_ACOSTAMENTO, S.ALTURA_TELA);
    ctx.fillRect(S.MARGEM_PISTA + S.LARGURA_PISTA, 0, S.LARGURA_ACOSTAMENTO, S.ALTURA_TELA);

    ctx.fillStyle = S.rgb(S.COR_ASFALTO);
    ctx.fillRect(S.MARGEM_PISTA, 0, S.LARGURA_PISTA, S.ALTURA_TELA);

    const passoJunta = S.ESPACO_JUNTA_ASFALTO;
    let yJunta = -passoJunta + (this.offsetPista % passoJunta);
    ctx.fillStyle = S.rgb(S.COR_JUNTA_ASFALTO);
    while (yJunta < S.ALTURA_TELA) {
      ctx.fillRect(S.MARGEM_PISTA, yJunta, S.LARGURA_PISTA, S.ALTURA_JUNTA_ASFALTO);
      yJunta += passoJunta;
    }

    ctx.fillStyle = S.rgb(S.COR_BORDA_PISTA);
    ctx.fillRect(S.MARGEM_PISTA - 4, 0, 4, S.ALTURA_TELA);
    ctx.fillRect(S.MARGEM_PISTA + S.LARGURA_PISTA, 0, 4, S.ALTURA_TELA);

    const passo = S.ALTURA_TRACO + S.ESPACO_TRACO;
    ctx.fillStyle = S.rgb(S.COR_LINHA);
    for (let faixa = 1; faixa < S.NUM_FAIXAS; faixa++) {
      const x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA;
      let y = -passo + this.offsetPista;
      while (y < S.ALTURA_TELA) {
        ctx.fillRect(x - S.LARGURA_LINHA / 2, y, S.LARGURA_LINHA, S.ALTURA_TRACO);
        y += passo;
      }
    }

    if (Math.floor(this.framesTotais / 15) % 2 === 0) {
      const avisos: Array<[number | null, S.RGB]> = [
        [this.avisoSpike > 0 ? this.avisoSpikeFaixa : null, S.COR_SPIKE_PONTA],
        [this.avisoBarreira > 0 ? this.avisoBarreiraFaixa : null, S.COR_BARREIRA],
      ];
      for (const [faixa, cor] of avisos) {
        if (faixa === null) continue;
        const x = S.MARGEM_PISTA + faixa * S.LARGURA_FAIXA;
        ctx.fillStyle = S.rgb(cor, 0.25);
        ctx.fillRect(x, 0, S.LARGURA_FAIXA, S.ALTURA_TELA);
      }
    }
  }

  private desenharAvisos(ctx: CanvasRenderingContext2D) {
    ctx.font = "bold 22px Consolas, monospace";
    ctx.textAlign = "center";
    let y = 100;
    if (this.avisoSpike > 0) {
      const s = Math.floor(this.avisoSpike / S.FPS) + 1;
      ctx.fillStyle = S.rgb(S.COR_ALERTA);
      ctx.fillText(`SPIKE STRIP em ${s}s`, S.LARGURA_TELA / 2, y);
      y += 30;
    }
    if (this.avisoBarreira > 0) {
      const s = Math.floor(this.avisoBarreira / S.FPS) + 1;
      ctx.fillStyle = S.rgb(S.COR_BARREIRA);
      ctx.fillText(`BARREIRA em ${s}s`, S.LARGURA_TELA / 2, y);
    }
  }

  private desenharHud(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = "rgba(0,0,0,0.55)";
    ctx.fillRect(0, 0, S.LARGURA_TELA, 96);

    ctx.textAlign = "left";
    ctx.font = "bold 18px Consolas, monospace";
    this.linhaHud(ctx, "POLICIA", this.policia, 18, S.COR_POLICIA);
    this.linhaHud(ctx, "LADRAO", this.ladrao, 48, S.COR_LADRAO);

    ctx.fillStyle = S.rgb(S.COR_TEXTO);
    ctx.textAlign = "right";
    if (this.matchType === "timed" && this.tempoRestante !== null) {
      const segs = Math.ceil(this.tempoRestante / S.FPS);
      const mm = String(Math.floor(segs / 60)).padStart(2, "0");
      const ss = String(segs % 60).padStart(2, "0");
      ctx.fillStyle = segs <= 30 ? S.rgb(S.COR_ALERTA) : S.rgb(S.COR_TEXTO);
      ctx.fillText(`Restante ${mm}:${ss}`, S.LARGURA_TELA - 16, 24);
    } else {
      const segs = Math.floor(this.framesTotais / S.FPS);
      const mm = String(Math.floor(segs / 60)).padStart(2, "0");
      const ss = String(segs % 60).padStart(2, "0");
      ctx.fillText(`Tempo ${mm}:${ss}`, S.LARGURA_TELA - 16, 24);
    }

    const modoLabel =
      this.matchType === "timed" ? "MODO TEMPO" : this.matchType === "solo_ai" ? "MODO SOLO IA" : "MODO INFINITO";
    ctx.font = "12px Consolas, monospace";
    ctx.fillStyle = S.rgb(S.COR_TEXTO);
    ctx.fillText(modoLabel, S.LARGURA_TELA - 16, 44);

    ctx.font = "12px Consolas, monospace";
    let roleHint: string;
    if (this.matchType === "solo_ai") {
      roleHint =
        this.humanRole === "police"
          ? "Voce: POLICIA (IA = ladrao) | ◀▶ ▲▼ N | 1 spike 2 barreira"
          : "Voce: LADRAO (IA = policia) | ◀▶ ▲▼ N | 1 oleo 2 tiro";
    } else if (this.mode === "guest") roleHint = "Voce: LADRAO | ◀▶ faixa | ▲▼ N | 1 oleo 2 tiro";
    else if (this.mode === "host") roleHint = "Voce: POLICIA | ◀▶ faixa | ▲▼ N | 1 spike 2 barreira";
    else roleHint = "Solo local: W/A/S/D + setas";
    ctx.textAlign = "left";
    ctx.fillText(roleHint, 16, 84);

    if (this.timerMensagem > 0 && !this.terminado) {
      ctx.font = "bold 28px Consolas, monospace";
      ctx.fillStyle = "rgb(255,210,40)";
      ctx.textAlign = "center";
      ctx.fillText(this.mensagemColisao, S.LARGURA_TELA / 2, 130);
    }
  }

  private desenharTelaFim(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = "rgba(0,0,0,0.65)";
    ctx.fillRect(0, 0, S.LARGURA_TELA, S.ALTURA_TELA);
    ctx.textAlign = "center";
    ctx.fillStyle = this.vencedor === "police" ? S.rgb(S.COR_POLICIA) : S.rgb(S.COR_LADRAO);
    ctx.font = "bold 48px Consolas, monospace";
    ctx.fillText(this.vencedor === "police" ? "POLICIA VENCEU" : "LADRAO VENCEU", S.LARGURA_TELA / 2, S.ALTURA_TELA / 2 - 20);
    ctx.fillStyle = S.rgb(S.COR_TEXTO);
    ctx.font = "22px Consolas, monospace";
    ctx.fillText(this.motivoFim, S.LARGURA_TELA / 2, S.ALTURA_TELA / 2 + 30);
    ctx.font = "16px Consolas, monospace";
    ctx.fillStyle = S.rgb(S.COR_TEXTO, 0.85);
    ctx.fillText("Toque em Sair para voltar ao menu", S.LARGURA_TELA / 2, S.ALTURA_TELA / 2 + 70);
  }

  private linhaHud(ctx: CanvasRenderingContext2D, rotulo: string, carro: Carro, y: number, cor: S.RGB) {
    ctx.fillStyle = S.rgb(cor);
    ctx.fillText(`${rotulo}  Vida ${String(carro.vida).padStart(3, " ")}`, 16, y);
    const bx = 220;
    ctx.fillStyle = "rgb(40,40,40)";
    ctx.fillRect(bx, y - 12, 140, 14);
    ctx.fillStyle = S.rgb(S.COR_NITRO);
    ctx.fillRect(bx, y - 12, (140 * carro.nitro) / S.NITRO_INICIAL, 14);
    ctx.strokeStyle = "#111";
    ctx.strokeRect(bx, y - 12, 140, 14);
    ctx.fillStyle = "#fff";
    ctx.font = "12px Consolas, monospace";
    ctx.fillText("Nitro", bx + 148, y - 1);
    ctx.font = "bold 18px Consolas, monospace";
  }
}
