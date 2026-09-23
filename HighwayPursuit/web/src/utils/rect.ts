export class Rect {
  constructor(
    public x: number,
    public y: number,
    public width: number,
    public height: number,
  ) {}

  get left() {
    return this.x;
  }
  get right() {
    return this.x + this.width;
  }
  get top() {
    return this.y;
  }
  get bottom() {
    return this.y + this.height;
  }
  get centerx() {
    return this.x + this.width / 2;
  }
  get centery() {
    return this.y + this.height / 2;
  }

  set center(value: [number, number]) {
    this.x = value[0] - this.width / 2;
    this.y = value[1] - this.height / 2;
  }

  colliderect(other: Rect): boolean {
    return (
      this.left < other.right &&
      this.right > other.left &&
      this.top < other.bottom &&
      this.bottom > other.top
    );
  }
}
