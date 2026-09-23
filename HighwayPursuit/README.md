# Highway Pursuit

Jogo 2D de perseguição (polícia vs ladrão) numa pista infinita de 4 faixas.

Existem **duas versões**:

| Versão | Onde | Multiplayer online |
|--------|------|--------------------|
| Desktop | Python + Pygame | Não (mesmo PC) |
| Web | Navegador (celular/PC) | Sim — 2 jogadores por link |

## Multiplayer web (celular + PC, gratuito)

Pasta: [`web/`](web/README.md)

```bash
cd web
npm install
npm run dev
```

1. Um jogador clica **Criar sala** (Polícia) e envia o link/código
2. O outro abre o link ou cola o código e clica **Entrar** (Ladrão)
3. A partida começa peer-to-peer (WebRTC / PeerJS) — sem servidor de jogo pago

Para publicar de graça no GitHub Pages, veja [`web/README.md`](web/README.md).
O workflow automático está em [`.github/workflows/deploy-web.yml`](../.github/workflows/deploy-web.yml).

## Como rodar (desktop / Pygame)

```bash
pip install -r requirements.txt
python -m src.main
```

Rode sempre a partir da pasta raiz do projeto (`HighwayPursuit/`), usando
`-m src.main`, para que os imports funcionem.

## Controles (versão atual)

| Ação                  | Polícia (P1)      | Ladrão (P2)        |
|------------------------|--------------------|---------------------|
| Acelerar (segurar)     | W                  | ↑                   |
| Frear (segurar)        | S                  | ↓                   |
| Nitro (segurar)        | Shift              | Ctrl                |
| Trocar de faixa        | A / D              | ← / →               |
| Spike strip            | Q                  | --                  |
| Barreira               | E                  | --                  |
| Óleo                   | --                 | .                   |
| Tiro traseiro          | --                 | /                   |
| Sair do jogo           | ESC                | ESC                 |

- **Acelerar** sobe a velocidade bem devagar até o máximo normal (ligado à vida do carro) -- leva uns 5 segundos pra ir do zero de diferença até o limite do mapa, e soltar derruba rápido de volta pra base (~1s), então o boost é um pico curto, não um patamar sustentável.
- **Frear** reduz a velocidade rapidamente, podendo chegar a 0 -- tem prioridade sobre acelerar e nitro.
- **Nitro** ultrapassa o máximo normal por um tempo, mas gasta a barra de nitro (que recarrega sozinha quando não está em uso).
- **Spike strip (Q)**: a faixa onde vai cair é travada na hora do acionamento (a faixa em que o ladrão está naquele momento). 2 segundos de aviso piscando na faixa antes de aparecer. Fura o pneu de quem passar por cima por **1 minuto** (reduz a velocidade máxima e piora a troca de faixa; depois recupera). Cooldown de 1 minuto.
- **Barreira (E)**: mesmo esquema de aviso de 2s na faixa travada. Ocupa a faixa inteira -- bater nela causa dano e zera a velocidade na hora, além de empurrar o carro pra trás. Ela continua lá, então bater de novo é possível se não trocar de faixa. Cooldown de 1 minuto.
- **Óleo (.)**: o ladrão larga na hora, sem aviso (é a surpresa dele). Se a polícia passar por cima, fica derrapando por alguns segundos (velocidade máxima reduzida e controle pior) -- diferente do spike strip, esse efeito passa sozinho. Cooldown de 20s.
- **Tiro traseiro (/)**: dispara pra trás na faixa em que o ladrão está no momento do disparo. Se acertar a polícia, causa dano direto. Cooldown de 5s.

## Marco 1 — "coração do jogo"

- [x] Janela do Pygame aberta
- [x] Pista de 4 faixas desenhada
- [x] Linhas da pista rolando (sensação de velocidade)
- [x] Dois retângulos representando Polícia e Ladrão
- [x] Troca de faixa suave para os dois jogadores

## Etapa 3 — Sistema de velocidade

- [x] vida, velocidade_base, velocidade_atual, velocidade_maxima por carro
- [x] Acelerar sobe a velocidade suavemente (20 → 30)
- [x] Frear reduz a velocidade rapidamente, podendo chegar a 0
- [x] Soltar desce suavemente de volta à base
- [x] Dano reduz permanentemente a base E o máximo (fórmula: `20/30 - (100 - vida)/10`)
- [x] A diferença entre a velocidade do carro e a velocidade de referência
      do mundo move o carro na tela (é o que cria a sensação de perseguição)

## Etapa 4 — Trânsito

- [x] Carros civis nascem em faixas aleatórias, acima da tela
- [x] Descem em direção aos jogadores com velocidade própria
- [x] São removidos ao saírem da tela

## Etapa 5 — Colisão entre os jogadores

- [x] Detecção de colisão entre Polícia e Ladrão (sobreposição de retângulos)
- [x] Intensidade da batida (leve/média/forte) calculada pela diferença de
      velocidade entre os dois carros no momento do choque
- [x] Perda de vida para os dois carros
- [x] Pequeno empurrão que os separa após a batida
- [x] Cooldown de colisão para não tomar dano repetido enquanto ainda se tocam
- [x] Mensagem na tela mostrando o tipo de colisão

## Etapa 6 — HUD

- [x] Barra superior com vida e nitro de cada jogador
- [x] Tempo de jogo (mm:ss)
- [x] Legenda dos controles

## Etapa 7 — Spike strip

- [x] Polícia solta com Q
- [x] Aviso de 2s (faixa piscando + texto) antes de aparecer
- [x] Cooldown de 1 minuto
- [x] Fica no chão até um carro passar por cima (uso único)
- [x] Efeito por 1 minuto: reduz velocidade máxima e piora o controle na troca de faixa, depois recupera

## Etapa 8 — Barreira

- [x] Polícia aciona com E
- [x] Mesmo aviso de 2s
- [x] Ocupa a faixa inteira
- [x] Bater nela causa dano, zera a velocidade e empurra o carro pra trás
- [x] Continua no lugar (pode bater de novo se não trocar de faixa)

## Etapa 9 — Armas do ladrão

- [x] Óleo (.): sem aviso, dropado na hora atrás do ladrão; derrapagem temporária na polícia (velocidade máxima reduzida + controle pior por alguns segundos); cooldown de 20s
- [x] Tiro traseiro (/): dispara na faixa do ladrão no momento do tiro; dano direto se acertar a polícia; cooldown de 5s

## Visual da pista

- [x] Acostamento (faixa entre a grama e o asfalto)
- [x] "Juntas" de asfalto rolando (textura de segmentos de pavimento)
- [x] Bordas amarelas e linhas tracejadas entre faixas

## Próximos marcos

- Colisão com o trânsito
- Condição de vitória/derrota e tela de fim de jogo
- Menu inicial

## Estrutura do projeto

```
HighwayPursuit/
├── assets/
├── src/
│   ├── main.py
│   ├── settings.py
│   ├── game.py
│   ├── entities/
│   │   ├── car.py
│   │   ├── traffic.py
│   │   ├── obstacles.py
│   │   └── weapons.py
│   ├── systems/
│   │   └── collision.py
│   ├── scenes/        (ainda vazio — menu, game_scene, game_over entram aqui)
│   └── utils/
├── docs/
├── requirements.txt
└── README.md
```
