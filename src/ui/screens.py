import pygame
from src.config.settings import *
from src.ui.button import Button
from src.game.states import GameState
from src.game.hanoi import HanoiGame


# ============================================================
# FONDO DARK-TECH (GRADIENTE)
# ============================================================
def draw_background(surface):
    gradient = pygame.Surface((WIDTH, HEIGHT))
    col1 = (10, 15, 31)
    col2 = (3, 5, 12)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = col1[0] * (1 - ratio) + col2[0] * ratio
        g = col1[1] * (1 - ratio) + col2[1] * ratio
        b = col1[2] * (1 - ratio) + col2[2] * ratio
        pygame.draw.line(gradient, (int(r), int(g), int(b)), (0, y), (WIDTH, y))

    surface.blit(gradient, (0, 0))


# ============================================================
# CLASE BASE
# ============================================================
class Screen:
    def __init__(self, game):
        self.game = game

    def draw(self, surface): pass
    def handle_event(self, event): pass
    def update(self, dt): pass


# ============================================================
# MENÚ PRINCIPAL
# ============================================================
class MenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        cx = WIDTH // 2
        base_y = 250
        w, h = 260, 55

        self.buttons = [
            Button((cx - w // 2, base_y, w, h),
                   "Comenzar Nivel 1",
                   game.font_medium,
                   game.start_game),

            Button((cx - w // 2, base_y + 70, w, h),
                   "Seleccionar Nivel",
                   game.font_medium,
                   lambda: game.transition.start("out", GameState.LEVEL_SELECT)),

            Button((cx - w // 2, base_y + 140, w, h),
                   "Modo Sin Tiempo",
                   game.font_medium,
                   game.start_game_no_time),

            Button((cx - w // 2, base_y + 210, w, h),
                   "Instrucciones",
                   game.font_medium,
                   game.show_instructions),

            Button((cx - w // 2, base_y + 280, w, h),
                   "Salir",
                   game.font_medium,
                   game.exit_game),
        ]

    def draw(self, surface):
        draw_background(surface)

        title = self.game.font_big.render("TORRE DE HANOI", True, (0, 209, 255))
        shadow = self.game.font_big.render("TORRE DE HANOI", True, (0, 80, 100))

        surface.blit(shadow, (WIDTH//2 - title.get_width()//2 + 4, 94))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 90))

        subtitle = self.game.font_small.render("Proyecto Estructuras de Datos", True, (200, 230, 255))
        surface.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 150))

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)


# ============================================================
# INSTRUCCIONES
# ============================================================
class InstructionsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        cx = WIDTH // 2
        self.buttons = [
            Button((cx - 100, HEIGHT - 90, 200, 50),
                   "Volver al menú",
                   game.font_medium,
                   game.back_to_menu)
        ]

        self.lines = [
            "Objetivo: mover toda la torre desde el primer poste al tercero.",
            "",
            "Reglas:",
            "1) Solo puedes mover un disco a la vez.",
            "2) Solo puedes mover el disco superior.",
            "3) Nunca pongas un disco grande sobre uno pequeño.",
            "",
            "Controles:",
            "- Clic y arrastre para mover discos.",
            "- El tiempo y eficiencia afectan la puntuación.",
        ]

    def draw(self, surface):
        draw_background(surface)

        title = self.game.font_big.render("INSTRUCCIONES", True, (0, 209, 255))
        shadow = self.game.font_big.render("INSTRUCCIONES", True, (0, 80, 100))

        surface.blit(shadow, (WIDTH//2 - title.get_width()//2 + 4, 64))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))

        y = 180
        for line in self.lines:
            surf = self.game.font_small.render(line, True, (220, 235, 255))
            surface.blit(surf, (70, y))
            y += 30

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)


# ============================================================
# NIVEL COMPLETADO (ANIMADO)
# ============================================================
class LevelCompleteScreen(Screen):

    def __init__(self, game):
        super().__init__(game)
        self.animation_timer = 0.0
        self.appear_speed = 1.2

        cx = WIDTH // 2
        self.buttons = [
            Button((cx - 130, HEIGHT // 2 + 120, 260, 50),
                   "Siguiente Nivel",
                   game.font_medium,
                   game.next_level),

            Button((cx - 130, HEIGHT // 2 + 190, 260, 50),
                   "Volver al Menú",
                   game.font_medium,
                   game.back_to_menu),
        ]

    def update(self, dt):
        if self.animation_timer < 1:
            self.animation_timer += dt * self.appear_speed
            if self.animation_timer > 1:
                self.animation_timer = 1

    def draw(self, surface):
        progress = self.animation_timer

        # Fade negro
        fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade.set_alpha(int(180 * progress))
        fade.fill((0, 0, 0))
        surface.blit(fade, (0, 0))

        # Zoom panel
        scale = 0.90 + 0.10 * progress
        pw = int(650 * scale)
        ph = int(450 * scale)

        px = WIDTH//2 - pw//2
        py = HEIGHT//2 - ph//2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)

        pygame.draw.rect(panel, (8, 12, 28, 230),
                         (0, 0, pw, ph), border_radius=20)

        pygame.draw.rect(panel, (0, 255, 190),
                         (0, 0, pw, ph), 3, border_radius=20)

        # Glow
        glow = pygame.Surface((pw+40, ph+40), pygame.SRCALPHA)
        pygame.draw.rect(glow, (0, 255, 200, 70),
                         (0, 0, pw+40, ph+40), border_radius=22)
        surface.blit(glow, (px-20, py-20))

        # Texto
        h = self.game.hanoi

        title = self.game.font_big.render("¡NIVEL COMPLETADO!", True, (0, 255, 200))
        s = self.game.font_big.render("¡NIVEL COMPLETADO!", True, (0, 60, 50))

        panel.blit(s, (pw//2 - title.get_width()//2 + 3, 33))
        panel.blit(title, (pw//2 - title.get_width()//2, 30))

        time_info = "Tiempo: N/A" if not h.time_enabled else f"Tiempo restante: {int(h.time_left)}s"

        info = [
            f"Score total: {h.score}",
            f"Movimientos: {h.moves}/{h.min_moves}",
            time_info,
            f"Eficiencia: {round((h.min_moves/max(1,h.moves))*100,1)}%"
        ]

        y = 130
        for line in info:
            t = self.game.font_medium.render(line, True, (210, 240, 255))
            panel.blit(t, (pw//2 - t.get_width()//2, y))
            y += 40

        surface.blit(panel, (px, py))

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)


# ============================================================
# GAME OVER
# ============================================================
class GameOverScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        cx = WIDTH // 2
        self.buttons = [
            Button((cx - 130, HEIGHT // 2, 260, 50),
                   "Reintentar Nivel",
                   game.font_medium,
                   game.restart_level),

            Button((cx - 130, HEIGHT // 2 + 70, 260, 50),
                   "Volver al Menú",
                   game.font_medium,
                   game.back_to_menu),
        ]

    def draw(self, surface):
        self.game.hanoi.draw(surface, self.game.font_small, self.game.font_medium)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        title = self.game.font_big.render("¡TIEMPO AGOTADO!", True, (255, 100, 100))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)


# ============================================================
# PAUSA
# ============================================================
class PauseScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        cx = WIDTH // 2
        cy = HEIGHT // 2

        self.buttons = [
            Button((cx - 130, cy - 40, 260, 50),
                   "Continuar",
                   game.font_medium,
                   self.resume),

            Button((cx - 130, cy + 20, 260, 50),
                   "Reiniciar Nivel",
                   game.font_medium,
                   game.restart_level),

            Button((cx - 130, cy + 80, 260, 50),
                   "Volver al Menú",
                   game.font_medium,
                   game.back_to_menu),

            Button((cx - 130, cy + 140, 260, 50),
                   "Salir",
                   game.font_medium,
                   game.exit_game),
        ]

    def resume(self):
        self.game.state = GameState.PLAYING

    def draw(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = self.game.font_big.render("Pausa", True, TEXT_COLOR)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 120))

        for b in self.buttons:
            b.draw(surface)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)


# ============================================================
# SELECTOR DE NIVELES
# ============================================================
class LevelSelectScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

        self.buttons = []
        self.create_level_buttons()

        self.back_button = Button(
            (50, HEIGHT - 80, 180, 50),
            "Volver",
            game.font_medium,
            game.back_to_menu
        )

    def create_level_buttons(self):
        rows = 2
        cols = 3
        spacing_x = 180
        spacing_y = 120

        start_x = WIDTH // 2 - (cols * spacing_x) // 2 + 40
        start_y = 180

        level = 1
        for r in range(rows):
            for c in range(cols):
                if level > 6:
                    return

                x = start_x + c * spacing_x
                y = start_y + r * spacing_y

                btn = Button(
                    (x, y, 120, 60),
                    f"Nivel {level}",
                    self.game.font_medium,
                    lambda lvl=level: self.start_level(lvl),
                )
                self.buttons.append(btn)
                level += 1

    def start_level(self, level):
        self.game.current_level = level
        self.game.hanoi = HanoiGame(level, self.game, time_enabled=self.game.time_enabled)
        self.game.transition.start("out", GameState.PLAYING)

    def draw(self, surface):
        draw_background(surface)

        title = self.game.font_big.render("SELECCIONAR NIVEL", True, (0, 209, 255))
        shadow = self.game.font_big.render("SELECCIONAR NIVEL", True, (0, 80, 100))

        surface.blit(shadow, (WIDTH//2 - title.get_width()//2 + 4, 84))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        for b in self.buttons:
            b.draw(surface)

        self.back_button.draw(surface)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

        self.back_button.handle_event(event)
