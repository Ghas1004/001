import "./style.css";
import * as S from "./settings";
import { Game } from "./game/Game";
import { InputManager } from "./input/controls";
import { PeerSession, roomLink } from "./net/PeerSession";
import type { MatchType, NetMessage } from "./net/protocol";

const menuEl = document.getElementById("menu")!;
const soloRoleEl = document.getElementById("solo-role")!;
const lobbyEl = document.getElementById("lobby")!;
const gameWrap = document.getElementById("game-wrap")!;
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
const statusEl = document.getElementById("lobby-status")!;
const shareBox = document.getElementById("share-box")!;
const roomCodeEl = document.getElementById("room-code")!;
const roomInput = document.getElementById("room-input") as HTMLInputElement;
const touchUi = document.getElementById("touch-ui")!;
const lobbyTitle = document.getElementById("lobby-title")!;
const lobbySub = document.getElementById("lobby-sub")!;

const btnModeInfinite = document.getElementById("btn-mode-infinite")!;
const btnModeTimed = document.getElementById("btn-mode-timed")!;
const btnModeSolo = document.getElementById("btn-mode-solo")!;
const btnRolePolice = document.getElementById("btn-role-police")!;
const btnRoleThief = document.getElementById("btn-role-thief")!;
const btnSoloBack = document.getElementById("btn-solo-back")!;
const btnCreate = document.getElementById("btn-create")!;
const btnJoin = document.getElementById("btn-join")!;
const btnLobbyBack = document.getElementById("btn-lobby-back")!;
const btnCopy = document.getElementById("btn-copy")!;
const btnExit = document.getElementById("btn-exit")!;

let game: Game | null = null;
let input: InputManager | null = null;
let session: PeerSession | null = null;
let selectedMatch: MatchType = "infinite";
let raf = 0;
let lastTs = 0;
let acc = 0;
const step = 1000 / S.FPS;
let snapshotAcc = 0;
const snapshotStep = 1000 / S.SNAPSHOT_HZ;
let running = false;

function setStatus(msg: string) {
  statusEl.textContent = msg;
}

type ViewName = "menu" | "solo" | "lobby";

function showView(view: ViewName) {
  menuEl.classList.toggle("hidden", view !== "menu");
  soloRoleEl.classList.toggle("hidden", view !== "solo");
  lobbyEl.classList.toggle("hidden", view !== "lobby");
}

function showLobbyMenu() {
  stopGame();
  gameWrap.classList.add("hidden");
  shareBox.classList.add("hidden");
  showView("menu");
  setStatus("");
}

async function lockLandscape() {
  try {
    const orientation = screen.orientation as ScreenOrientation & {
      lock?: (mode: string) => Promise<void>;
    };
    if (orientation?.lock) await orientation.lock("landscape");
  } catch {
    /* ok */
  }
}

function showGame() {
  menuEl.classList.add("hidden");
  soloRoleEl.classList.add("hidden");
  lobbyEl.classList.add("hidden");
  gameWrap.classList.remove("hidden");
  void lockLandscape();
}

function stopGame() {
  running = false;
  cancelAnimationFrame(raf);
  input?.destroy();
  input = null;
  game = null;
  session?.destroy();
  session = null;
}

function startGame(opts: {
  netMode: "solo" | "host" | "guest";
  matchType: MatchType;
  humanRole: "police" | "thief";
}) {
  canvas.width = S.LARGURA_TELA;
  canvas.height = S.ALTURA_TELA;
  game = new Game();
  game.configure({
    mode: opts.netMode,
    matchType: opts.matchType,
    humanRole: opts.humanRole,
  });

  input = new InputManager(opts.humanRole);
  input.bindTouch(touchUi);
  updateSkillLabels(opts.humanRole);
  showGame();
  running = true;
  lastTs = performance.now();
  acc = 0;
  snapshotAcc = 0;
  raf = requestAnimationFrame(loop);
}

function updateSkillLabels(role: "police" | "thief") {
  const s1 = touchUi.querySelector<HTMLButtonElement>('[data-action="skill1"]');
  const s2 = touchUi.querySelector<HTMLButtonElement>('[data-action="skill2"]');
  if (!s1 || !s2) return;
  if (role === "thief") {
    s1.textContent = "Óleo";
    s2.textContent = "Tiro";
  } else {
    s1.textContent = "Spike";
    s2.textContent = "Barreira";
  }
}

function loop(ts: number) {
  if (!running || !game || !input) return;
  const dt = Math.min(50, ts - lastTs);
  lastTs = ts;
  acc += dt;
  snapshotAcc += dt;

  while (acc >= step) {
    const local = input.sample();
    if (game.mode === "guest" && session && !game.terminado) {
      session.send({ type: "input", input: local });
    }
    game.update(local);
    acc -= step;
  }

  if (game.mode === "host" && session && snapshotAcc >= snapshotStep) {
    session.send({ type: "snapshot", snapshot: game.toSnapshot() });
    snapshotAcc = 0;
  }

  game.draw(ctx);
  raf = requestAnimationFrame(loop);
}

function openLobby(matchType: MatchType) {
  selectedMatch = matchType;
  if (matchType === "timed") {
    lobbyTitle.textContent = "Multiplayer — Tempo";
    lobbySub.textContent = "Host = Polícia · Convidado = Ladrão · 3 minutos para capturar";
  } else {
    lobbyTitle.textContent = "Multiplayer — Infinito";
    lobbySub.textContent = "Host = Polícia · Convidado = Ladrão · sem limite de tempo";
  }
  shareBox.classList.add("hidden");
  setStatus("");
  showView("lobby");
}

btnModeInfinite.addEventListener("click", () => openLobby("infinite"));
btnModeTimed.addEventListener("click", () => openLobby("timed"));
btnModeSolo.addEventListener("click", () => showView("solo"));
btnSoloBack.addEventListener("click", () => showView("menu"));
btnLobbyBack.addEventListener("click", () => showView("menu"));

btnRolePolice.addEventListener("click", () => {
  startGame({ netMode: "solo", matchType: "solo_ai", humanRole: "police" });
});
btnRoleThief.addEventListener("click", () => {
  startGame({ netMode: "solo", matchType: "solo_ai", humanRole: "thief" });
});

btnCreate.addEventListener("click", async () => {
  setStatus("Criando sala...");
  btnCreate.setAttribute("disabled", "true");
  try {
    session = new PeerSession("host");
    session.onError = (e) => setStatus(`Erro: ${e}`);
    session.onDisconnected = () => setStatus("Convidado desconectou.");
    session.onMessage = onNetMessage;
    session.onConnected = () => {
      setStatus("Jogador conectou! Iniciando...");
      session?.send({ type: "start", matchType: selectedMatch });
      startGame({ netMode: "host", matchType: selectedMatch, humanRole: "police" });
    };
    const code = await session.createRoom();
    roomCodeEl.textContent = code;
    shareBox.classList.remove("hidden");
    setStatus("Sala pronta. Envie o link/código e aguarde.");
    const url = new URL(window.location.href);
    url.searchParams.set("sala", code);
    url.searchParams.set("modo", selectedMatch);
    history.replaceState({}, "", url.toString());
  } catch (err) {
    setStatus(`Falha ao criar sala: ${String(err)}`);
  } finally {
    btnCreate.removeAttribute("disabled");
  }
});

btnJoin.addEventListener("click", () => joinWithCode(roomInput.value));

btnCopy.addEventListener("click", async () => {
  const code = roomCodeEl.textContent || "";
  const link = roomLink(code);
  const withMode = new URL(link);
  withMode.searchParams.set("modo", selectedMatch);
  try {
    await navigator.clipboard.writeText(withMode.toString());
    setStatus("Link copiado!");
  } catch {
    setStatus(withMode.toString());
  }
});

btnExit.addEventListener("click", () => {
  showLobbyMenu();
  history.replaceState({}, "", window.location.pathname);
});

function onNetMessage(msg: NetMessage) {
  if (!game && msg.type === "start") {
    const matchType = msg.matchType || selectedMatch;
    selectedMatch = matchType;
    startGame({ netMode: "guest", matchType, humanRole: "thief" });
    return;
  }
  if (!game) return;
  if (msg.type === "input" && game.mode === "host") game.setRemoteInput(msg.input);
  if (msg.type === "snapshot" && game.mode === "guest") game.applySnapshot(msg.snapshot);
}

async function joinWithCode(code: string) {
  const clean = code.trim().toUpperCase();
  if (clean.length < 4) {
    setStatus("Digite um código válido.");
    return;
  }
  setStatus("Entrando na sala...");
  btnJoin.setAttribute("disabled", "true");
  try {
    session = new PeerSession("guest");
    session.onError = (e) => setStatus(`Erro: ${e}`);
    session.onDisconnected = () => setStatus("Host desconectou.");
    session.onMessage = onNetMessage;
    session.onConnected = () => {
      setStatus("Conectado! Aguardando início...");
      session?.send({ type: "hello", role: "thief" });
    };
    await session.joinRoom(clean);
  } catch (err) {
    setStatus(`Falha ao entrar: ${String(err)}`);
  } finally {
    btnJoin.removeAttribute("disabled");
  }
}

const params = new URLSearchParams(window.location.search);
const sala = params.get("sala");
const modo = params.get("modo");
if (modo === "timed" || modo === "infinite") selectedMatch = modo;
if (sala) {
  openLobby(selectedMatch === "timed" ? "timed" : "infinite");
  roomInput.value = sala.toUpperCase();
  setStatus(`Sala detectada: ${sala.toUpperCase()}. Entrando...`);
  window.setTimeout(() => joinWithCode(sala), 400);
} else {
  showView("menu");
}
