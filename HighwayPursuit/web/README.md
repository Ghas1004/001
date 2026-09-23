# Highway Pursuit — Web Multiplayer

Versão para navegador (celular e PC) com multiplayer 2 jogadores via WebRTC (PeerJS).

## Como jogar em 2 (depois de publicado)

1. Abra o link do GitHub Pages no celular/PC
2. Um jogador clica **Criar sala** (será a **Polícia**)
3. Copia o link/código e envia ao amigo
4. O amigo abre o link ou cola o código e clica **Entrar** (será o **Ladrão**)
5. A partida começa automaticamente

### Controles

| Ação | Polícia (Host) | Ladrão (Guest) | Touch |
|------|----------------|----------------|-------|
| Acelerar / Frear / Nitro | W / S / Shift | ↑ / ↓ / Ctrl | ▲ / ▼ / N |
| Trocar faixa | A / D | ← / → | ◀ / ▶ |
| Habilidade 1 | Q (spike) | . (óleo) | botão 1 |
| Habilidade 2 | E (barreira) | / (tiro) | botão 2 |

## Desenvolvimento local

```bash
cd HighwayPursuit/web
npm install
npm run dev
```

Abra o endereço do Vite (ex.: `http://localhost:5173`) em dois navegadores/abas para testar multiplayer. Em celulares na mesma rede, use o IP da máquina (`npm run dev -- --host` já está ativo).

## Build

```bash
npm run build
```

Saída em `web/dist/` — arquivos estáticos prontos para GitHub Pages, Netlify ou Hostinger.

## Publicar no GitHub Pages (grátis)

### Opção A — Actions (recomendado)

1. Envie o repositório para o GitHub
2. Em **Settings → Pages → Source**, escolha **GitHub Actions**
3. O workflow `.github/workflows/deploy-web.yml` publica automaticamente ao push em `main`

O link ficará:

`https://SEU_USUARIO.github.io/NOME_DO_REPO/`

### Opção B — Manual

```bash
cd HighwayPursuit/web
npm run build
```

Envie o conteúdo de `dist/` para a branch `gh-pages`, ou use:

```bash
npx gh-pages -d dist
```

## Notas

- Não precisa de servidor de jogo pago: a partida roda peer-to-peer
- Em redes muito restritas, WebRTC pode falhar; tente 4G/Wi‑Fi residencial
- O modo **Jogar sozinho** serve só para testar a física no mesmo aparelho
