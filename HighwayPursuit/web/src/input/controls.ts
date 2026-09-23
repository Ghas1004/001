export type AbilityId = "spike" | "barrier" | "oil" | "shot" | null;

export interface PlayerInput {
  accel: boolean;
  brake: boolean;
  nitro: boolean;
  laneDelta: number; // -1 / 0 / +1 (consumido uma vez)
  ability: AbilityId;
}

export function emptyInput(): PlayerInput {
  return {
    accel: false,
    brake: false,
    nitro: false,
    laneDelta: 0,
    ability: null,
  };
}

export class InputManager {
  private held = {
    accel: false,
    brake: false,
    nitro: false,
  };
  private laneQueue = 0;
  private abilityQueue: AbilityId = null;
  private keys = new Set<string>();

  constructor(private role: "police" | "thief" | "local") {
    window.addEventListener("keydown", this.onKeyDown);
    window.addEventListener("keyup", this.onKeyUp);
  }

  setRole(role: "police" | "thief" | "local") {
    this.role = role;
  }

  destroy() {
    window.removeEventListener("keydown", this.onKeyDown);
    window.removeEventListener("keyup", this.onKeyUp);
  }

  bindTouch(root: HTMLElement) {
    const buttons = root.querySelectorAll<HTMLButtonElement>("[data-action]");
    for (const btn of buttons) {
      const action = btn.dataset.action!;
      const start = (e: Event) => {
        e.preventDefault();
        btn.classList.add("active");
        this.touchAction(action, true);
      };
      const end = (e: Event) => {
        e.preventDefault();
        btn.classList.remove("active");
        this.touchAction(action, false);
      };
      btn.addEventListener("pointerdown", start);
      btn.addEventListener("pointerup", end);
      btn.addEventListener("pointerleave", end);
      btn.addEventListener("pointercancel", end);
    }
  }

  private touchAction(action: string, down: boolean) {
    if (action === "accel") this.held.accel = down;
    else if (action === "brake") this.held.brake = down;
    else if (action === "nitro") this.held.nitro = down;
    else if (action === "left" && down) this.laneQueue = -1;
    else if (action === "right" && down) this.laneQueue = 1;
    else if (action === "skill1" && down) {
      this.abilityQueue = this.role === "thief" ? "oil" : "spike";
    } else if (action === "skill2" && down) {
      this.abilityQueue = this.role === "thief" ? "shot" : "barrier";
    }
  }

  private onKeyDown = (e: KeyboardEvent) => {
    if (e.repeat) return;
    this.keys.add(e.code);

    if (this.role === "police" || this.role === "local") {
      if (e.code === "KeyA") this.laneQueue = -1;
      if (e.code === "KeyD") this.laneQueue = 1;
      if (e.code === "KeyQ") this.abilityQueue = "spike";
      if (e.code === "KeyE") this.abilityQueue = "barrier";
    }
    if (this.role === "thief" || this.role === "local") {
      if (e.code === "ArrowLeft") this.laneQueue = -1;
      if (e.code === "ArrowRight") this.laneQueue = 1;
      if (e.code === "Period") this.abilityQueue = "oil";
      if (e.code === "Slash") this.abilityQueue = "shot";
    }
  };

  private onKeyUp = (e: KeyboardEvent) => {
    this.keys.delete(e.code);
  };

  sample(): PlayerInput {
    let accel = this.held.accel;
    let brake = this.held.brake;
    let nitro = this.held.nitro;

    if (this.role === "police" || this.role === "local") {
      accel = accel || this.keys.has("KeyW");
      brake = brake || this.keys.has("KeyS");
      nitro = nitro || this.keys.has("ShiftLeft") || this.keys.has("ShiftRight");
    }
    if (this.role === "thief" || this.role === "local") {
      accel = accel || this.keys.has("ArrowUp");
      brake = brake || this.keys.has("ArrowDown");
      nitro = nitro || this.keys.has("ControlLeft") || this.keys.has("ControlRight");
    }

    const input: PlayerInput = {
      accel,
      brake,
      nitro,
      laneDelta: this.laneQueue,
      ability: this.abilityQueue,
    };
    this.laneQueue = 0;
    this.abilityQueue = null;
    return input;
  }
}
