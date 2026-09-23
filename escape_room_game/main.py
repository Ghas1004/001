import pygame
import sys
import os
import math

# Garante que a pasta deste arquivo está no caminho de busca de módulos,
# não importa de onde o script seja executado (terminal, VS Code, duplo-clique, etc.)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import GameManager, SCREEN_W, SCREEN_H, SCALE
from scenes_data import SCENES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EFFECTS_DIR = os.path.join(BASE_DIR, "assets", "effects")
SCENES_DIR = os.path.join(BASE_DIR, "assets", "scenes")

# Cache das imagens de tela cheia usadas na sequência final (jumpscare,
# captura e fuga) -- carregadas sob demanda e reaproveitadas depois.
_effect_cache = {}


def load_effect_image(base_name):
    """Carrega uma imagem de efeito pelo nome sem extensão (ex: "escapou").
    Procura em assets/effects/ (lugar certo) e também em assets/scenes/
    (caso o arquivo tenha sido colocado ali por engano), testando as
    extensões .jpeg, .jpg e .png em cada pasta -- assim um arquivo salvo
    com a extensão ou pasta "erradas" ainda funciona."""
    if base_name not in _effect_cache:
        target_size = (SCREEN_W * SCALE, SCREEN_H * SCALE)
        full_path = None
        for folder in (EFFECTS_DIR, SCENES_DIR):
            for ext in (".jpeg", ".jpg", ".png"):
                candidate = os.path.join(folder, base_name + ext)
                if os.path.exists(candidate):
                    full_path = candidate
                    break
            if full_path:
                break

        if full_path:
            img = pygame.image.load(full_path).convert()
            img = pygame.transform.scale(img, target_size)
        else:
            img = pygame.Surface(target_size)
            img.fill((10, 8, 8))
        _effect_cache[base_name] = img
    return _effect_cache[base_name]

# Se existir uma fonte pixelada em assets/fonts/pixel.ttf, o jogo usa ela
# automaticamente. Sem ela, cai na fonte padrão do pygame.
PIXEL_FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "pixel.ttf")


def load_font(size):
    if os.path.exists(PIXEL_FONT_PATH):
        return pygame.font.Font(PIXEL_FONT_PATH, size)
    return pygame.font.Font(None, size)


def draw_hotspot_debug(surface, hotspot, color=(255, 255, 255)):
    """Contorno do hotspot -- só aparece com a tecla D ligada, para calibrar
    posições de clique. Fora do modo debug nada é desenhado."""
    pygame.draw.rect(surface, color, hotspot.rect, width=1)


def draw_nav_arrow(surface, hotspot):
    """Desenha uma seta de navegação clicável (triângulo) dentro do rect
    do hotspot, apontando 'left' ou 'right'. Sempre visível (não é debug) --
    é a forma do jogador saber que pode ir naquela direção, mesmo sem asset."""
    r = hotspot.rect
    size = min(r.width, r.height) // 2

    arrow_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
    local_cx, local_cy = r.width // 2, r.height // 2

    if hotspot.arrow == "right":
        points = [
            (local_cx - size // 2, local_cy - size),
            (local_cx - size // 2, local_cy + size),
            (local_cx + size // 2, local_cy),
        ]
    else:  # "left"
        points = [
            (local_cx + size // 2, local_cy - size),
            (local_cx + size // 2, local_cy + size),
            (local_cx - size // 2, local_cy),
        ]

    pygame.draw.polygon(arrow_surf, (255, 255, 255, 160), points)
    pygame.draw.polygon(arrow_surf, (255, 255, 255, 230), points, width=2)
    surface.blit(arrow_surf, (r.x, r.y))


def draw_door_light(surface, hotspot, t):
    """Luz quente vazando por baixo da porta (pulsando devagar). É a marcação
    das portas que realmente abrem -- as trancadas ficam apagadas."""
    r = hotspot.rect
    pulse = 0.72 + 0.28 * math.sin(t * 2.0 + r.x * 0.01)

    # brilho que sobe da soleira em direção ao meio da porta
    glow_h = max(28, r.height // 5)
    glow = pygame.Surface((r.width, glow_h), pygame.SRCALPHA)
    for i in range(glow_h):
        f = ((i + 1) / glow_h) ** 2.6 * pulse
        glow.fill(
            (int(150 * f), int(108 * f), int(42 * f)),
            pygame.Rect(0, i, r.width, 1),
        )
    surface.blit(glow, (r.x, r.bottom - glow_h), special_flags=pygame.BLEND_RGB_ADD)

    # a fresta em si, bem na base da porta
    strip_w = max(6, r.width - 10)
    strip = pygame.Surface((strip_w, 6), pygame.SRCALPHA)
    strip.fill((int(210 * pulse), int(160 * pulse), int(70 * pulse)))
    surface.blit(strip, (r.x + 5, r.bottom - 6), special_flags=pygame.BLEND_RGB_ADD)

    # reflexo curto no chão, logo abaixo da fresta
    spill = pygame.Surface((strip_w, 14), pygame.SRCALPHA)
    for i in range(14):
        f = (1 - i / 14) ** 2 * pulse
        spill.fill((int(90 * f), int(64 * f), int(26 * f)), pygame.Rect(0, i, strip_w, 1))
    surface.blit(spill, (r.x + 5, r.bottom), special_flags=pygame.BLEND_RGB_ADD)


def draw_hover_highlight(surface, hotspot, t):
    """Contorno discreto no objeto sob o cursor -- substitui as linhas
    vermelhas antigas: só aparece quando o mouse está em cima."""
    r = hotspot.rect
    alpha = int(70 + 45 * (0.5 + 0.5 * math.sin(t * 4.0)))
    hi = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
    pygame.draw.rect(hi, (255, 245, 220, alpha), hi.get_rect(), width=2)
    pygame.draw.rect(hi, (255, 245, 220, alpha // 5), hi.get_rect())
    surface.blit(hi, r.topleft)


def draw_hover_label(window, text, font):
    """Nome do objeto sob o cursor, acima da caixa de texto."""
    if not text:
        return
    surf = font.render(text, True, (225, 215, 195))
    rect = surf.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 96))
    bg = pygame.Surface((rect.width + 28, rect.height + 14), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 150))
    window.blit(bg, bg.get_rect(center=rect.center))
    window.blit(surf, rect)


def wrap_text(text, font, max_width):
    """Quebra o texto em várias linhas para caber na largura dada.
    Respeita quebras de linha ("\n") já existentes no texto -- importante
    para falas/cartas com pausas propositais (cada frase numa linha)."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_width or not current:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_bottom_message(window, text, font, color=(235, 225, 210)):
    """Caixa de texto na parte inferior da tela -- é aqui que aparecem
    todas as falas/descrições das interações."""
    max_width = int(SCREEN_W * SCALE * 0.8)
    lines = wrap_text(text, font, max_width)
    line_h = font.get_linesize()

    box_h = line_h * len(lines) + 34
    box_w = max_width + 60
    box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box.fill((0, 0, 0, 185))
    pygame.draw.rect(box, (120, 105, 80, 220), box.get_rect(), width=3)

    box_rect = box.get_rect(midbottom=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 58))
    window.blit(box, box_rect)

    y = box_rect.y + 17
    for line in lines:
        surf = font.render(line, True, color)
        window.blit(surf, surf.get_rect(center=(box_rect.centerx, y + line_h // 2)))
        y += line_h


def draw_overlay(window, overlay, text_font, hint_font):
    """Desenha o close-up de imagem (ex: a carta) por cima da cena.

    Para textos longos que não cabem tudo de uma vez, o texto é paginado:
    calcula quantas linhas cabem no espaço abaixo da imagem e mostra só a
    página atual (overlay.page). Clicar na imagem novamente (tratado em
    game.py) avança pra próxima página; na última página, um aviso indica
    que dá pra fechar clicando fora."""
    dim = pygame.Surface((SCREEN_W * SCALE, SCREEN_H * SCALE), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 205))
    window.blit(dim, (0, 0))

    window.blit(overlay.surface, overlay.rect)

    if not overlay.revealed:
        hint = hint_font.render(overlay.hint, True, (170, 160, 145))
        window.blit(hint, hint.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 70)))
        return

    max_width = int(SCREEN_W * SCALE * 0.7)
    all_lines = wrap_text(overlay.message, text_font, max_width)
    line_h = text_font.get_linesize()

    # Espaço vertical disponível entre o fim da imagem e o rodapé da tela
    # (reservando uma margem para o indicador de página / dica de fechar).
    available_top = overlay.rect.bottom + 26
    available_bottom = SCREEN_H * SCALE - 90
    available_h = max(line_h * 2, available_bottom - available_top)
    lines_per_page = max(1, int(available_h // line_h))
    total_pages = max(1, math.ceil(len(all_lines) / lines_per_page))

    # Trava a página atual dentro do total real (o game.py só incrementa,
    # quem sabe quantas páginas existem de fato é aqui).
    overlay.page = max(0, min(overlay.page, total_pages - 1))
    start = overlay.page * lines_per_page
    page_lines = all_lines[start:start + lines_per_page]

    box_h = line_h * len(page_lines) + 34
    box_w = max_width + 60
    box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    box.fill((0, 0, 0, 195))
    pygame.draw.rect(box, (120, 105, 80, 220), box.get_rect(), width=3)

    box_rect = box.get_rect(midtop=(SCREEN_W * SCALE // 2, available_top))
    window.blit(box, box_rect)

    y = box_rect.y + 17
    for line in page_lines:
        surf = text_font.render(line, True, (235, 225, 210))
        window.blit(surf, surf.get_rect(center=(box_rect.centerx, y + line_h // 2)))
        y += line_h

    if total_pages > 1:
        if overlay.page < total_pages - 1:
            footer_text = f"({overlay.page + 1}/{total_pages}) clique na carta para continuar lendo"
        else:
            footer_text = f"({overlay.page + 1}/{total_pages}) fim da carta -- clique fora para fechar"
        footer = hint_font.render(footer_text, True, (170, 160, 145))
        window.blit(footer, footer.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 40)))


def draw_ending_screen(window, game, text_font, hud_font, qte_font):
    """Desenha a sequência final: jumpscare da diretora, o minigame de teclas
    (QTE) e as telas de captura/fuga -- por cima de tudo, sem desenhar a
    cena normal por trás."""
    stage = game.ending_stage

    if stage == "jumpscare":
        window.blit(load_effect_image("diretora_jumpscare"), (0, 0))

    elif stage == "qte":
        # Fundo: o próprio jumpscare escurecido, pra manter a tensão
        window.blit(load_effect_image("diretora_jumpscare"), (0, 0))
        dim = pygame.Surface((SCREEN_W * SCALE, SCREEN_H * SCALE), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        window.blit(dim, (0, 0))

        current_char = game.qte_sequence[game.qte_index]
        char_surf = qte_font.render(current_char, True, (235, 60, 60))
        window.blit(char_surf, char_surf.get_rect(
            center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE // 2 - 30)
        ))

        # Barra mostrando o tempo restante desta tecla (1 segundo cada)
        bar_w, bar_h = 320, 20
        ratio = max(0.0, game.qte_time_left / game.qte_prompt_duration)
        bar_bg = pygame.Rect(0, 0, bar_w, bar_h)
        bar_bg.center = (SCREEN_W * SCALE // 2, SCREEN_H * SCALE // 2 + 110)
        pygame.draw.rect(window, (60, 55, 50), bar_bg)
        bar_fg = pygame.Rect(bar_bg.x, bar_bg.y, int(bar_w * ratio), bar_h)
        pygame.draw.rect(window, (215, 40, 40), bar_fg)
        pygame.draw.rect(window, (230, 225, 215), bar_bg, width=2)

        progress_surf = hud_font.render(
            f"{game.qte_index}/{len(game.qte_sequence)} -- pressione a tecla mostrada!",
            True, (230, 225, 215),
        )
        window.blit(progress_surf, progress_surf.get_rect(
            center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE // 2 + 150)
        ))

    elif stage == "escape_fade_out":
        # Escurece a partir do clima do jumpscare -- não corta pro preto de
        # repente, vai sumindo aos poucos.
        window.blit(load_effect_image("diretora_jumpscare"), (0, 0))
        progress = 1 - (game.fade_timer / game.fade_duration)
        dim = pygame.Surface((SCREEN_W * SCALE, SCREEN_H * SCALE), pygame.SRCALPHA)
        dim.fill((0, 0, 0, int(255 * max(0.0, min(1.0, progress)))))
        window.blit(dim, (0, 0))

    elif stage == "escape_fade_in":
        # Tela preta some aos poucos revelando a cena final (ele saindo).
        window.fill((0, 0, 0))
        progress = 1 - (game.fade_timer / game.fade_duration)
        img = load_effect_image("escapou").copy()
        img.set_alpha(int(255 * max(0.0, min(1.0, progress))))
        window.blit(img, (0, 0))

    elif stage == "captured":
        window.blit(load_effect_image("diretora_morrendo"), (0, 0))
        msg = text_font.render("Você foi capturado. Pressione R para reiniciar.", True, (220, 40, 40))
        window.blit(msg, msg.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 70)))

    elif stage == "escaped":
        window.blit(load_effect_image("escapou"), (0, 0))
        # Frase sombria em vez de um "você venceu!" comemorativo -- ele
        # escapou da escola, mas o clima continua pesado.
        phrase = hud_font.render(
            "Consegui escapar... mas ainda ouço três batidas atrás de mim: toc, toc, toc.",
            True, (200, 195, 190),
        )
        window.blit(phrase, phrase.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 100)))
        hint = hud_font.render("Pressione R para jogar de novo.", True, (150, 145, 140))
        window.blit(hint, hint.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE - 60)))


def main():
    pygame.init()
    pygame.display.set_caption("Escape Room - Protótipo")
    window = pygame.display.set_mode((SCREEN_W * SCALE, SCREEN_H * SCALE))
    clock = pygame.time.Clock()

    text_font = load_font(34)     # textos de interação (parte inferior da tela)
    hud_font = load_font(26)      # inventário
    small_font = load_font(18)    # rótulos do modo debug
    qte_font = load_font(170)     # letra/número gigante do minigame final

    game = GameManager(SCENES)

    show_debug = False  # tecla D liga/desliga contorno dos hotspots

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    show_debug = not show_debug
                if event.key == pygame.K_ESCAPE and game.overlay:
                    game.overlay = None
                if event.key == pygame.K_r and (game.game_over or game.won):
                    game = GameManager(SCENES)
                # Minigame final: qualquer tecla alfanumérica conta como
                # tentativa de acertar a letra/número mostrado na tela.
                if game.ending_stage == "qte" and event.unicode and len(event.unicode) == 1 and event.unicode.isalnum():
                    game.handle_key_press(event.unicode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)

        game.update(dt)

        # --- Sequência final (jumpscare / minigame / captura / fuga) ---
        # Enquanto isso está ativo, a cena normal nem é desenhada.
        if game.ending_stage is not None:
            draw_ending_screen(window, game, text_font, hud_font, qte_font)
            pygame.display.flip()
            continue

        # --- Renderização da cena ---
        scene_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        scene = game.current_scene
        scene_surface.blit(scene.load_background(), (0, 0))

        if show_debug:
            for hs in scene.hotspots:
                draw_hotspot_debug(scene_surface, hs)
                label_surf = small_font.render(hs.label, True, (255, 255, 0))
                scene_surface.blit(label_surf, (hs.rect.x, hs.rect.y - 16))

        t = pygame.time.get_ticks() / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        hovered = game.hotspot_at(mouse_pos)

        # Luz por baixo das portas que podem ser abertas
        for hs in scene.hotspots:
            if hs.door_light:
                draw_door_light(scene_surface, hs, t)

        # Destaque do objeto sob o cursor
        if hovered is not None:
            draw_hover_highlight(scene_surface, hovered, t)

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if hovered is not None else pygame.SYSTEM_CURSOR_ARROW
        )

        # Setas de navegação sempre visíveis, independente do modo debug
        for hs in scene.hotspots:
            if hs.arrow:
                draw_nav_arrow(scene_surface, hs)

        # Overlay escuro quando há evento de perigo ativo
        if game.danger_active:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            scene_surface.blit(overlay, (0, 0))

        # Escala para a janela final
        scaled = pygame.transform.scale(scene_surface, (SCREEN_W * SCALE, SCREEN_H * SCALE))
        window.blit(scaled, (0, 0))

        # --- Close-up de imagem (carta, etc.) ---
        if game.overlay:
            draw_overlay(window, game.overlay, text_font, hud_font)
        # --- Mensagem de interação na parte inferior ---
        elif game.message:
            draw_bottom_message(window, game.message, text_font)
        elif hovered is not None and hovered.label:
            draw_hover_label(window, hovered.label, hud_font)

        # --- HUD: inventário ---
        inv_text = "Inventário: " + (", ".join(game.inventory) if game.inventory else "(vazio)")
        inv_surf = hud_font.render(inv_text, True, (230, 225, 215))
        window.blit(inv_surf, (18, SCREEN_H * SCALE - 38))

        if game.game_over:
            over_surf = text_font.render("GAME OVER - pressione R para reiniciar", True, (200, 40, 40))
            rect = over_surf.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE // 2))
            window.blit(over_surf, rect)
        elif game.won:
            win_surf = text_font.render("VOCÊ ESCAPOU! pressione R para jogar de novo", True, (0, 255, 100))
            rect = win_surf.get_rect(center=(SCREEN_W * SCALE // 2, SCREEN_H * SCALE // 2))
            window.blit(win_surf, rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


# MELHORIAS GERAIS:
# - Adicionar som de fundo e efeitos sonoros para interações.

# MELHORIAS CENA 2:
# - Fazer com que uma das portas, estejam trancadas, daí na outra porta, fazer interação na imagem, e colocar uma interação na chave, onde, ao pegar a chave, e guardar no inventário, ele poderá acessar a outra porta
