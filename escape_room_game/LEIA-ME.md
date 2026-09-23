# Protótipo - Escape Room 1ª Pessoa (Pygame)

## Como rodar
1. Instale o Python 3.10+ 
2. Instale a dependência:
   ```
   pip install pygame
   ```
3. Rode:
   ```
   python main.py
   ```

## Controles
- **Clique esquerdo**: interage com o hotspot (porta, objeto, item)
- **D**: liga/desliga os contornos vermelhos de debug (mostra onde estão os hotspots)
- **R**: reinicia o jogo após vitória ou game over

## Estrutura do projeto
```
escape_room_game/
  main.py          -> loop principal, desenho na tela, input
  game.py           -> lógica: Scene, Hotspot, GameManager
  data/
    scenes.json      -> TODAS as cenas, hotspots, itens e eventos de perigo
  assets/
    scenes/          -> imagens de fundo (384x216 px) de cada cômodo
    items/            -> ícones de itens do inventário
    enemies/          -> sprites de fantasmas/jumpscare
    sfx/ e music/      -> sons
```

## Como adicionar uma cena nova (sem programar)
Basta editar `data/scenes.json` e adicionar um novo bloco, por exemplo:

```json
"nome_da_cena": {
  "background": "assets/scenes/arquivo.png",
  "hotspots": [
    {
      "id": "algum_id",
      "rect": [x, y, largura, altura],
      "type": "navigate",
      "target": "outra_cena",
      "label": "Descrição"
    }
  ]
}
```

Tipos de hotspot disponíveis:
- `navigate` -> muda para outra cena (`target`)
- `examine` -> abre uma "sub-cena" de close-up (também usa `target`)
- `pickup` -> adiciona um item ao inventário (`item`, `once: true` pra sumir depois de pego)
- `win` -> termina o jogo com vitória

Um hotspot pode exigir item para funcionar:
```json
"requires_item": "lanterna",
"locked_message": "Está escuro demais para ver essa porta."
```

## Como adicionar um evento de perigo/jumpscare numa cena
Adicione isso dentro do bloco da cena:
```json
"danger_event": {
  "duration": 4.0,
  "message": "Você ouve passos se aproximando... não se mexa."
}
```
Enquanto esse evento está ativo, qualquer clique em porta/item/saída
causa jumpscare (fim de jogo). O jogador precisa esperar o tempo passar
sem clicar em nada de "ação".

## Sobre as imagens (para quem for desenhar)
- Tamanho: **384 x 216 px**, PNG
- Todas as cenas de fundo vão em `assets/scenes/`
- Sem arte ainda? Sem problema — o jogo mostra um retângulo cinza no
  lugar, então dá pra testar toda a lógica antes das imagens ficarem
  prontas. Assim que o arquivo existir com o nome certo no JSON, ele
  aparece automaticamente.

## Próximos passos sugeridos
1. Trocar os placeholders cinzas pelas primeiras imagens reais
2. Adicionar sons (passos, ambiente, jumpscare) com `pygame.mixer`
3. Adicionar tela de menu inicial e tela de créditos/conquistas
4. Criar um sistema de "save" em JSON (progresso, conquistas, dinheiro)
5. Adicionar mais cenas seguindo o mesmo padrão do `scenes.json`
