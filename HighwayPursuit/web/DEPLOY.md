# Publicar no GitHub Pages (passo a passo)

O build já está pronto em `web/dist/`. Falta só subir o projeto para o GitHub.

## 1. Criar repositório

No GitHub: **New repository** → nome sugerido `HighwayPursuit` → Create.

## 2. Enviar o código

No PowerShell, na pasta do projeto (`Downloads/HighwayPursuit`):

```bat
git init
git add .
git commit -m "Add Highway Pursuit web multiplayer"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/HighwayPursuit.git
git push -u origin main
```

## 3. Ativar Pages

1. Abra o repositório no GitHub
2. **Settings → Pages**
3. **Source**: GitHub Actions
4. Aguarde o workflow **Deploy Highway Pursuit Web** terminar (aba Actions)

## 4. Link do jogo

```
https://SEU_USUARIO.github.io/HighwayPursuit/
```

- Um cria a sala e manda o link com `?sala=CODIGO`
- O outro abre e joga como Ladrão

## Teste local agora (sem GitHub)

```bat
cd HighwayPursuit\web
npm run dev
```

Abra o endereço no PC e no celular (mesma rede Wi‑Fi), usando o IP que o Vite mostrar.
