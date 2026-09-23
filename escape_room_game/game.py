import os
import random
import pygame

SCREEN_W, SCREEN_H = 1600, 900  # resolução nativa das artes (imagens já vêm nesse tamanho)
SCALE = 1  # já é tamanho de tela; aumente se quiser ampliar mais

# Pasta onde este arquivo (game.py) está -- usada como base para resolver
# caminhos de imagens e do scenes.json, não importa de qual pasta o jogo é executado.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Hotspot:
    def __init__(self, data):
        self.id = data["id"]
        self.rect = pygame.Rect(data["rect"])
        self.type = data["type"]  # navigate | examine | pickup | message | image | win | sequence_item | climax_door
        self.target = data.get("target")
        self.item = data.get("item")
        self.once = data.get("once", False)
        self.requires_item = data.get("requires_item")
        self.locked_message = data.get("locked_message", "Não é possível agora.")
        self.message = data.get("message", "")
        self.label = data.get("label", "")
        self.arrow = data.get("arrow")  # "left" | "right" | None -- desenha seta clicável no lugar do rect
        # Usados pelo tipo "image": mostra uma imagem em close-up na tela e,
        # ao clicar nela, revela um texto (campo "image_message").
        self.image = data.get("image")
        self.image_message = data.get("image_message", "")
        # Marca visual: luz quente vazando por baixo da porta. Serve para o
        # jogador identificar, sem texto, quais portas realmente abrem.
        self.door_light = data.get("door_light", False)
        self.consumed = False  # usado para itens "once"

        # --- Puzzles de sequência (ex: frascos de química) ---
        # Um hotspot "sequence_item" representa uma peça clicável de um puzzle
        # (ex: um frasco). "puzzle_id" identifica a qual puzzle da cena ele
        # pertence (ver Scene.puzzle) e "value" é o identificador dessa peça
        # dentro da sequência esperada (ex: "triangulo").
        self.puzzle_id = data.get("puzzle_id")
        self.sequence_value = data.get("value")
        # Qualquer hotspot (pickup, navigate, etc.) pode exigir que um puzzle
        # já tenha sido resolvido, da mesma forma que "requires_item" exige
        # um item no inventário.
        self.requires_puzzle = data.get("requires_puzzle")


class ImageOverlay:
    """Close-up de um objeto (ex: a carta) desenhado por cima da cena, no
    topo da tela. Clicar em cima da imagem avança a leitura do texto
    (página por página, para textos longos); clicar fora fecha o close-up.

    A imagem fica menor e no topo (em vez de ocupar quase a tela toda)
    para sobrar espaço embaixo dela onde o texto é desenhado -- importante
    para mensagens longas como a carta, que não cabem de uma vez só."""

    def __init__(self, image_path, message, hint="(clique na carta para começar a ler)"):
        self.message = message
        self.hint = hint
        # -1 = ainda não começou a ler (mostra só a dica).
        # 0, 1, 2... = página atual do texto sendo lida.
        # Quem decide quantas páginas existem e desenha o texto é o main.py
        # (que tem acesso à fonte pra calcular a quebra de linha); aqui só
        # guardamos em qual página o jogador está.
        self.page = -1

        img = None
        if image_path:
            full_path = os.path.join(BASE_DIR, image_path)
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()

        if img is None:
            # Placeholder enquanto a arte não existe
            img = pygame.Surface((84, 116), pygame.SRCALPHA)
            img.fill((198, 182, 148))

        # Amplia em múltiplo inteiro para manter o visual pixelado (nearest
        # neighbor). Tamanho reduzido (30% da altura da tela) de propósito:
        # sobra bastante espaço abaixo da imagem para o texto, mesmo em
        # cartas longas com várias páginas.
        factor = max(1, int((SCREEN_H * 0.30) // img.get_height()))
        self.surface = pygame.transform.scale(
            img, (img.get_width() * factor, img.get_height() * factor)
        )
        self.rect = self.surface.get_rect(center=(SCREEN_W // 2, int(SCREEN_H * 0.22)))

    @property
    def revealed(self):
        return self.page >= 0

    def advance(self):
        """Avança para a próxima página do texto (chamado ao clicar na
        imagem). O main.py trava (clamp) esse valor no total de páginas
        real ao desenhar, então não precisa se preocupar em passar do fim."""
        self.page += 1


class Scene:
    def __init__(self, scene_id, data):
        self.id = scene_id
        self.background_path = data["background"]
        self.hotspots = [Hotspot(h) for h in data["hotspots"]]
        self.danger_event = data.get("danger_event")
        # Definição opcional de puzzle de sequência da cena, no formato:
        # {
        #   "id": "quimica_frascos",
        #   "sequence": ["triangulo", "hexagono", "circulo", "quadrado"],
        #   "progress_message": "...", "wrong_message": "...", "solved_message": "...",
        # }
        self.puzzle = data.get("puzzle")
        self.background_surface = None  # carregado sob demanda

    def load_background(self):
        if self.background_surface is None:
            full_path = os.path.join(BASE_DIR, self.background_path)
            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert()
                self.background_surface = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
            else:
                # Placeholder enquanto a arte real não existe: fundo escuro com
                # o nome da cena e o arquivo esperado, para facilitar o teste.
                surf = pygame.Surface((SCREEN_W, SCREEN_H))
                surf.fill((26, 26, 30))
                try:
                    font = pygame.font.Font(None, 46)
                    small = pygame.font.Font(None, 30)
                    t1 = font.render(f"[ cena: {self.id} ]", True, (150, 145, 135))
                    t2 = small.render(f"arte ainda não criada -> {self.background_path}", True, (95, 92, 86))
                    surf.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))
                    surf.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20)))
                except pygame.error:
                    pass
                self.background_surface = surf
        return self.background_surface


class GameManager:
    def __init__(self, scenes_data):
        # scenes_data agora é um dict Python puro (ver scenes_data.py),
        # não é mais lido de arquivo JSON -- a lógica de montagem é a mesma.
        self.scenes = {sid: Scene(sid, sdata) for sid, sdata in scenes_data.items()}
        self.current_scene_id = "hall_entrada"
        self.inventory = []
        self.message = ""
        self.message_timer = 0.0

        # Close-up de imagem aberto no momento (ou None)
        self.overlay = None

        # Estado do evento de perigo (jumpscare) da cena atual
        self.danger_active = False
        self.danger_timer = 0.0
        self.danger_locked = False
        self.game_over = False
        self.won = False

        # --- Estado dos puzzles de sequência ---
        # puzzle_progress: puzzle_id -> lista de valores já clicados nesta tentativa
        # solved_puzzles: conjunto de puzzle_id já resolvidos (permanece resolvido)
        self.puzzle_progress = {}
        self.solved_puzzles = set()

        # --- Sequência final: jumpscare da diretora + minigame de teclas ---
        # ending_stage vai passando por: None -> "jumpscare" -> "qte" -> "captured" | "escaped"
        # Enquanto ending_stage não é None, a cena normal para de responder a
        # cliques (ver hotspot_at/handle_click) e quem desenha a tela é o
        # main.py (draw_ending_screen), não o desenho normal da cena.
        self.ending_stage = None
        self.jumpscare_duration = 1.6  # segundos mostrando o jumpscare antes do minigame começar
        self.jumpscare_timer = 0.0

        self.qte_prompt_duration = 1.5  # segundos que cada tecla fica na tela
        self.qte_length = 20            # total de teclas na sequência (~20 segundos)
        self.qte_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.qte_sequence = []
        self.qte_index = 0
        self.qte_time_left = 0.0

        # Transição de fuga: depois de acertar todas as teclas, a tela
        # escurece (fade out) e então some pra imagem final (fade in),
        # em vez de aparecer de repente.
        self.fade_duration = 1.3  # segundos de cada metade da transição
        self.fade_timer = 0.0

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_id]

    def go_to(self, scene_id):
        self.overlay = None
        self.current_scene_id = scene_id
        scene = self.current_scene
        if scene.danger_event:
            self.danger_active = True
            self.danger_timer = scene.danger_event["duration"]
            self.danger_locked = True
            self.set_message(scene.danger_event.get("message", "Não se mexa!"))
        else:
            self.danger_active = False

    def set_message(self, text, duration=3.5):
        self.message = text
        self.message_timer = duration

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

        if self.danger_active and self.danger_timer > 0:
            self.danger_timer -= dt
            if self.danger_timer <= 0:
                self.danger_active = False
                self.danger_locked = False
                self.set_message("Tudo calmo agora.")

        # --- Sequência final (jumpscare + minigame de teclas) ---
        if self.ending_stage == "jumpscare":
            self.jumpscare_timer -= dt
            if self.jumpscare_timer <= 0:
                self._start_qte()
        elif self.ending_stage == "qte":
            self.qte_time_left -= dt
            if self.qte_time_left <= 0:
                self._fail_qte()
        elif self.ending_stage == "escape_fade_out":
            self.fade_timer -= dt
            if self.fade_timer <= 0:
                self.ending_stage = "escape_fade_in"
                self.fade_timer = self.fade_duration
        elif self.ending_stage == "escape_fade_in":
            self.fade_timer -= dt
            if self.fade_timer <= 0:
                self.ending_stage = "escaped"
                self.won = True  # só agora, pra não dar pra reiniciar no meio do fade

    def start_ending_sequence(self):
        """Chamado ao abrir a porta final (hotspot tipo 'climax_door') já com
        a chave certa no inventário: mostra o jumpscare da diretora e, em
        seguida, o minigame de digitar teclas aleatórias pra escapar."""
        self.overlay = None
        self.message = ""
        self.ending_stage = "jumpscare"
        self.jumpscare_timer = self.jumpscare_duration

    def _start_qte(self):
        self.qte_sequence = [random.choice(self.qte_chars) for _ in range(self.qte_length)]
        self.qte_index = 0
        self.qte_time_left = self.qte_prompt_duration
        self.ending_stage = "qte"

    def handle_key_press(self, char):
        """Chamado pelo main.py a cada tecla alfanumérica pressionada durante
        o minigame. Acertar a tecla mostrada avança pra próxima; errar ou
        estourar o tempo (1s por tecla, ver update()) resulta em captura."""
        if self.ending_stage != "qte":
            return

        expected = self.qte_sequence[self.qte_index]
        if char.upper() == expected:
            self.qte_index += 1
            if self.qte_index >= len(self.qte_sequence):
                self._succeed_qte()
            else:
                self.qte_time_left = self.qte_prompt_duration
        else:
            self._fail_qte()

    def _fail_qte(self):
        self.ending_stage = "captured"
        self.game_over = True  # reaproveita a tecla R de reiniciar já existente

    def _succeed_qte(self):
        # Não vai direto pra tela final: primeiro escurece (fade out),
        # depois some pra imagem de fuga (fade in) -- ver update().
        self.ending_stage = "escape_fade_out"
        self.fade_timer = self.fade_duration

    def trigger_jumpscare(self):
        self.overlay = None
        self.game_over = True
        self.set_message("Você foi pego! Fim de jogo.", duration=5)

    def hotspot_at(self, pos):
        """Hotspot sob o cursor (usado para destacar o objeto e mostrar o nome
        dele na tela). Retorna None se o mouse não está sobre nada."""
        if self.overlay is not None or self.game_over or self.won or self.ending_stage is not None:
            return None
        scene_pos = (pos[0] // SCALE, pos[1] // SCALE)
        for hs in self.current_scene.hotspots:
            if hs.rect.collidepoint(scene_pos):
                if hs.once and hs.consumed:
                    return None
                return hs
        return None

    def handle_click(self, pos, sound_manager=None):
        if self.game_over or self.won or self.ending_stage is not None:
            return

        scene_pos = (pos[0] // SCALE, pos[1] // SCALE)

        # Com um close-up aberto, o clique só interage com ele
        if self.overlay is not None:
            if self.overlay.rect.collidepoint(scene_pos):
                self.overlay.advance()
            else:
                self.overlay = None
            return

        # Se está no evento de perigo travado, qualquer clique de navegação = jumpscare
        for hs in self.current_scene.hotspots:
            if hs.rect.collidepoint(scene_pos):
                if self.danger_locked and hs.type in ("navigate", "pickup", "win"):
                    self.trigger_jumpscare()
                    return
                self._activate_hotspot(hs, sound_manager)
                return

    def _activate_hotspot(self, hs: Hotspot, sound_manager):
        if hs.once and hs.consumed:
            return

        if hs.requires_item and hs.requires_item not in self.inventory:
            self.set_message(hs.locked_message)
            return

        if hs.requires_puzzle and hs.requires_puzzle not in self.solved_puzzles:
            self.set_message(hs.locked_message)
            return

        if hs.type == "navigate":
            self.go_to(hs.target)
        elif hs.type == "examine":
            self.go_to(hs.target)
        elif hs.type == "pickup":
            if hs.item not in self.inventory:
                self.inventory.append(hs.item)
                self.set_message(hs.message or f"Você pegou: {hs.item}")
            hs.consumed = True
        elif hs.type == "message":
            # Objeto que só mostra um texto (flavor text / pista), não muda de cena
            self.set_message(hs.message, duration=4)
        elif hs.type == "image":
            # Abre o close-up da imagem (ex: a carta rasgada do quadro de avisos)
            self.overlay = ImageOverlay(hs.image, hs.image_message)
        elif hs.type == "sequence_item":
            self._handle_sequence_click(hs)
        elif hs.type == "climax_door":
            # Porta final: já passou pelo requires_item acima (a chave certa
            # já está garantida aqui), então dispara jumpscare + minigame.
            self.start_ending_sequence()
        elif hs.type == "win":
            self.won = True
            self.set_message("Você escapou! Vitória!", duration=999)

    def _handle_sequence_click(self, hs: Hotspot):
        """Trata o clique numa peça de puzzle de sequência (ex: um frasco).
        Compara com a sequência esperada definida em Scene.puzzle; se o
        jogador errar a ordem, o progresso reseta; se acertar tudo, o
        puzzle é marcado como resolvido (destrava hotspots com
        requires_puzzle == puzzle_id)."""
        puzzle = self.current_scene.puzzle
        if not puzzle:
            return

        puzzle_id = hs.puzzle_id or puzzle.get("id")
        if puzzle_id in self.solved_puzzles:
            self.set_message(puzzle.get("solved_message", "Já está resolvido."))
            return

        expected = puzzle["sequence"]
        progress = self.puzzle_progress.setdefault(puzzle_id, [])
        progress.append(hs.sequence_value)
        idx = len(progress) - 1

        if progress[idx] != expected[idx]:
            self.puzzle_progress[puzzle_id] = []
            self.set_message(puzzle.get("wrong_message", "Ordem errada -- tente de novo."))
        elif len(progress) == len(expected):
            self.solved_puzzles.add(puzzle_id)
            self.puzzle_progress[puzzle_id] = []
            self.set_message(puzzle.get("solved_message", "Resolvido!"), duration=4.5)
        else:
            self.set_message(puzzle.get("progress_message", "Até agora, certo..."))
