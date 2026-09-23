import { emptyInput, type PlayerInput } from "../input/controls";
import type { Carro } from "../entities/Car";
import type { CarroTrafego } from "../entities/Traffic";
import * as S from "../settings";

/** IA simples para o modo Solo. */
export class AiController {
  private cooldownFaixa = 0;
  private cooldownSkill = 0;

  update(
    role: "police" | "thief",
    me: Carro,
    foe: Carro,
    trafego: CarroTrafego[],
    cooldowns: { spike: number; barrier: number; oil: number; shot: number },
  ): PlayerInput {
    const input = emptyInput();
    if (me.destruido) return input;

    if (this.cooldownFaixa > 0) this.cooldownFaixa -= 1;
    if (this.cooldownSkill > 0) this.cooldownSkill -= 1;

    if (role === "police") {
      this.policeBrain(input, me, foe, trafego, cooldowns);
    } else {
      this.thiefBrain(input, me, foe, trafego, cooldowns);
    }
    return input;
  }

  private policeBrain(
    input: PlayerInput,
    me: Carro,
    foe: Carro,
    trafego: CarroTrafego[],
    cd: { spike: number; barrier: number; oil: number; shot: number },
  ) {
    // Persegue: acelera se estiver atrás (y maior = mais embaixo)
    const atras = me.y > foe.y + 20;
    const longe = me.y - foe.y > 180;
    input.accel = atras || longe;
    input.nitro = atras && longe && me.nitro > 20;
    input.brake = me.y < foe.y - 40; // passou do alvo

    if (this.cooldownFaixa <= 0) {
      const alvo = this.escolherFaixa(me.faixa, foe.faixa, trafego, me.y, true);
      if (alvo !== me.faixa) {
        input.laneDelta = alvo > me.faixa ? 1 : -1;
        this.cooldownFaixa = 28;
      }
    }

    if (this.cooldownSkill <= 0 && Math.abs(me.faixa - foe.faixa) <= 1) {
      if (cd.barrier <= 0 && Math.random() < 0.4) {
        input.ability = "barrier";
        this.cooldownSkill = 90;
      } else if (cd.spike <= 0) {
        input.ability = "spike";
        this.cooldownSkill = 90;
      }
    }
  }

  private thiefBrain(
    input: PlayerInput,
    me: Carro,
    foe: Carro,
    trafego: CarroTrafego[],
    cd: { spike: number; barrier: number; oil: number; shot: number },
  ) {
    // Foge: mantém velocidade alta e evita a faixa da polícia
    input.accel = true;
    input.nitro = foe.y - me.y < 160 && me.nitro > 15;
    input.brake = false;

    if (this.cooldownFaixa <= 0) {
      const alvo = this.escolherFaixa(me.faixa, foe.faixa, trafego, me.y, false);
      if (alvo !== me.faixa) {
        input.laneDelta = alvo > me.faixa ? 1 : -1;
        this.cooldownFaixa = 22;
      }
    }

    const policialAtras = foe.y > me.y && foe.y - me.y < 220;
    if (this.cooldownSkill <= 0 && policialAtras) {
      if (cd.oil <= 0 && Math.abs(me.faixa - foe.faixa) <= 1 && Math.random() < 0.55) {
        input.ability = "oil";
        this.cooldownSkill = 70;
      } else if (cd.shot <= 0 && me.faixa === foe.faixa) {
        input.ability = "shot";
        this.cooldownSkill = 70;
      }
    }
  }

  private escolherFaixa(
    minha: number,
    inimiga: number,
    trafego: CarroTrafego[],
    meuY: number,
    perseguir: boolean,
  ): number {
    let melhor = minha;
    let melhorScore = -Infinity;

    for (let f = 0; f < S.NUM_FAIXAS; f++) {
      if (Math.abs(f - minha) > 1) continue; // só adjacente ou atual
      let score = 0;

      if (perseguir) {
        score -= Math.abs(f - inimiga) * 12;
      } else {
        score += Math.abs(f - inimiga) * 10;
      }

      for (const npc of trafego) {
        if (npc.faixa !== f) continue;
        const dy = Math.abs(npc.y - meuY);
        if (dy < S.ALTURA_CARRO * 2.2) score -= 40;
        else if (dy < S.ALTURA_CARRO * 4) score -= 12;
      }

      score += Math.random() * 3;
      if (score > melhorScore) {
        melhorScore = score;
        melhor = f;
      }
    }
    return melhor;
  }
}
