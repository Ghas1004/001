import Peer, { type DataConnection } from "peerjs";
import { decode, encode, type NetMessage } from "./protocol";

export type SessionRole = "host" | "guest";

function randomCode(len = 6): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let out = "";
  for (let i = 0; i < len; i++) out += alphabet[Math.floor(Math.random() * alphabet.length)];
  return out;
}

export class PeerSession {
  peer: Peer | null = null;
  conn: DataConnection | null = null;
  role: SessionRole;
  roomCode = "";
  onMessage: ((msg: NetMessage) => void) | null = null;
  onConnected: (() => void) | null = null;
  onDisconnected: (() => void) | null = null;
  onError: ((err: string) => void) | null = null;
  onReady: ((code: string) => void) | null = null;

  constructor(role: SessionRole) {
    this.role = role;
  }

  async createRoom(): Promise<string> {
    this.role = "host";
    this.roomCode = randomCode();
    const peerId = `hp-${this.roomCode}`;
    await this.openPeer(peerId);
    this.peer!.on("connection", (conn) => {
      this.attachConn(conn);
    });
    this.onReady?.(this.roomCode);
    return this.roomCode;
  }

  async joinRoom(code: string): Promise<void> {
    this.role = "guest";
    this.roomCode = code.trim().toUpperCase();
    await this.openPeer();
    const conn = this.peer!.connect(`hp-${this.roomCode}`, { reliable: true });
    this.attachConn(conn);
  }

  private openPeer(id?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.peer = id ? new Peer(id) : new Peer();
      const timer = window.setTimeout(() => reject(new Error("Timeout ao conectar no PeerJS")), 15000);
      this.peer.on("open", () => {
        window.clearTimeout(timer);
        resolve();
      });
      this.peer.on("error", (err) => {
        window.clearTimeout(timer);
        this.onError?.(String(err));
        reject(err);
      });
    });
  }

  private attachConn(conn: DataConnection) {
    this.conn = conn;
    conn.on("open", () => this.onConnected?.());
    conn.on("data", (data) => {
      const msg = typeof data === "string" ? decode(data) : decode(JSON.stringify(data));
      if (msg) this.onMessage?.(msg);
    });
    conn.on("close", () => this.onDisconnected?.());
    conn.on("error", (err) => this.onError?.(String(err)));
  }

  send(msg: NetMessage) {
    if (!this.conn || !this.conn.open) return;
    this.conn.send(encode(msg));
  }

  destroy() {
    try {
      this.conn?.close();
    } catch {
      /* ignore */
    }
    try {
      this.peer?.destroy();
    } catch {
      /* ignore */
    }
    this.conn = null;
    this.peer = null;
  }
}

export function roomLink(code: string): string {
  const url = new URL(window.location.href);
  url.searchParams.set("sala", code);
  return url.toString();
}
