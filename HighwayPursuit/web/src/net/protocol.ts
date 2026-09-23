import type { PlayerInput } from "../input/controls";
import type { CarSnapshot } from "../entities/Car";
import type { TrafficSnapshot } from "../entities/Traffic";

export type MatchType = "infinite" | "timed" | "solo_ai";
export type Winner = "police" | "thief" | null;

export type NetMessage =
  | { type: "hello"; role: "police" | "thief"; name?: string }
  | { type: "ready" }
  | { type: "start"; matchType: MatchType }
  | { type: "input"; input: PlayerInput }
  | { type: "snapshot"; snapshot: GameSnapshot }
  | { type: "ping"; t: number }
  | { type: "disconnect" };

export interface GameSnapshot {
  frames: number;
  offsetPista: number;
  policia: CarSnapshot;
  ladrao: CarSnapshot;
  trafego: TrafficSnapshot[];
  mensagemColisao: string;
  timerMensagem: number;
  spike: { faixa: number; x: number; y: number; usada: boolean } | null;
  barreira: { faixa: number; x: number; y: number } | null;
  oleo: { faixa: number; x: number; y: number; usada: boolean } | null;
  projetil: { faixa: number; x: number; y: number; atingiu: boolean } | null;
  avisoSpike: number;
  avisoSpikeFaixa: number | null;
  avisoBarreira: number;
  avisoBarreiraFaixa: number | null;
  cooldownSpike: number;
  cooldownBarreira: number;
  cooldownOleo: number;
  cooldownTiro: number;
  matchType: MatchType;
  tempoRestante: number | null;
  terminado: boolean;
  vencedor: Winner;
  motivoFim: string;
}

export function encode(msg: NetMessage): string {
  return JSON.stringify(msg);
}

export function decode(raw: string): NetMessage | null {
  try {
    return JSON.parse(raw) as NetMessage;
  } catch {
    return null;
  }
}
