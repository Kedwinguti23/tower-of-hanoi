import pygame
import sys
import math
from enum import Enum

# ----------------- CONFIGURACIÓN GENERAL -----------------

WIDTH, HEIGHT = 900, 600
FPS = 60

BACKGROUND_COLOR = (15, 15, 25)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (50, 90, 180)
BUTTON_HOVER = (80, 120, 220)
PEG_COLOR = (200, 200, 210)
DISK_COLORS = [
    (255, 99, 71),
    (255, 165, 0),
    (255, 215, 0),
    (50, 205, 50),
    (64, 224, 208),
    (65, 105, 225),
    (186, 85, 211),
    (238, 130, 238),
]

MAX_LEVEL = 5   # nivel 1 = 3 discos, nivel 2 = 4, etc.


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4
    INSTRUCTIONS = 5


# ----------------- CLASES DE UI -----------------

class Button:
    def __init__(self, rect, text, font, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        color = BUTTON_HOVER if is_hover else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()


# ----------------- LÓGICA DEL HANOI -----------------

class HanoiGame:
    def __init__(self, level):
        # level 1 -> 3 discos, level 2 -> 4 discos...
        self.level = level
        self.num_disks = 2 + level  # empiezas en 3 discos
        self.pegs = [list(reversed(range(1, self.num_disks + 1))), [], []]  # 1 pequeño, N grande
        self.selected_peg = None
        self.moves = 0
        self.min_moves = (2 ** self.num_disks) - 1

        # tiempo límite (segundos): base + factor por movimiento mínimo
        self.time_limit = 40 + int(self.min_moves * 1.5)
        self.time_left = self.time_limit

        self.score = 0
        self.finished = False
        self.won = False

        # para animar el arrastre
        self.dragging_disk = None
        self.drag_offset_y = 0
        self.drag_from_peg = None

        # geometría
        self.peg_positions = self.calculate_peg_positions()

    def calculate_peg_positions(self):
        positions = []
        spacing = WIDTH // 3
        for i in range(3):
            x = spacing * (i + 0.5)
            y = HEIGHT * 0.75
            positions.append((int(x), int(y)))
        return positions

    def reset(self):
        self.pegs = [list(reversed(range(1, self.num_disks + 1))), [], []]
        self.selected_peg = None
        self.moves = 0
        self.time_left = self.time_limit
        self.score = 0
        self.finished = False
        self.won = False
        self.dragging_disk = None
        self.drag_from_peg = None

    def update(self, dt):
        if not self.finished:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.finished = True
                self.won = False

        # verificar victoria
        if self.pegs[2] == list(reversed(range(1, self.num_disks + 1))) and not self.finished:
            self.finished = True
            self.won = True
            self.calculate_score()

    def calculate_score(self):
        # simple: puntos base por nivel + extra por tiempo y eficiencia
        if not self.won:
            self.score = 0
            return
        efficiency = max(0, (self.min_moves / max(self.moves, self.min_moves)))
        time_factor = self.time_left / self.time_limit
        base = 100 * self.level
        self.score = int(base + 200 * efficiency * time_factor)

    # ------------- manejo de clics y jugadas -------------

    def peg_at_position(self, pos):
        x, y = pos
        for i, (px, py) in enumerate(self.peg_positions):
            # simple hitbox alrededor del poste
            if abs(x - px) < 80 and y > HEIGHT * 0.3:
                return i
        return None

    def start_drag(self, mouse_pos):
        peg_index = self.peg_at_position(mouse_pos)
        if peg_index is None:
            return
        if not self.pegs[peg_index]:
            return

        # solo el disco superior
        disk = self.pegs[peg_index][-1]
        self.dragging_disk = disk
        self.drag_from_peg = peg_index
        # offset para que no salte
        self.drag_offset_y = 0

    def end_drag(self, mouse_pos):
        if self.dragging_disk is None:
            return

        target_peg = self.peg_at_position(mouse_pos)
        if target_peg is None:
            # cancelar
            self.cancel_drag()
            return

        # validar movimiento
        if self.can_move(self.drag_from_peg, target_peg):
            self.move_disk(self.drag_from_peg, target_peg)
        # si no se puede, se devuelve solo
        self.dragging_disk = None
        self.drag_from_peg = None

    def cancel_drag(self):
        self.dragging_disk = None
        self.drag_from_peg = None

    def can_move(self, from_peg, to_peg):
        if from_peg == to_peg:
            return False
        if not self.pegs[from_peg]:
            return False
        disk = self.pegs[from_peg][-1]
        if not self.pegs[to_peg]:
            return True
        top_to = self.pegs[to_peg][-1]
        return disk < top_to

    def move_disk(self, from_peg, to_peg):
        disk = self.pegs[from_peg].pop()
        self.pegs[to_peg].append(disk)
        self.moves += 1

    # ------------- dibujo -------------

    def draw(self, surface, font_small, font_big):
        # fondo
        surface.fill(BACKGROUND_COLOR)

        # título nivel
        title = font_big.render(f"Nivel {self.level} - {self.num_disks} discos", True, TEXT_COLOR)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 15))

        # info HUD
        hud_y = 70
        info_texts = [
            f"Movimientos: {self.moves}",
            f"Mínimos: {self.min_moves}",
            f"Tiempo: {int(self.time_left)}s",
        ]
        for i, txt in enumerate(info_texts):
            surf = font_small.render(txt, True, TEXT_COLOR)
            surface.blit(surf, (30, hud_y + i * 25))

        # postes
        base_y = int(HEIGHT * 0.8)
        for (px, py) in self.peg_positions:
            # base
            pygame.draw.rect(surface, PEG_COLOR, (px - 100, base_y, 200, 15))
            # poste
            pygame.draw.rect(surface, PEG_COLOR, (px - 7, base_y - 200, 14, 200), border_radius=5)

        # discos
        max_width = 180
        min_width = 60
        disk_height = 22

        for peg_index, peg in enumerate(self.pegs):
            px, _ = self.peg_positions[peg_index]
            for level_index, disk in enumerate(peg):
                # si este disco está siendo arrastrado, lo dibujará luego
                if disk == self.dragging_disk:
                    continue

                t = (disk - 1) / max(1, self.num_disks - 1)
                width = int(min_width + (max_width - min_width) * (1 - t))
                color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]

                # el nivel 0 es el más abajo
                x = px - width // 2
                y = base_y - disk_height * (len(peg) - level_index)
                pygame.draw.rect(surface, color, (x, y, width, disk_height), border_radius=8)

        # disco en arrastre
        if self.dragging_disk is not None:
            mx, my = pygame.mouse.get_pos()
            disk = self.dragging_disk
            t = (disk - 1) / max(1, self.num_disks - 1)
            width = int(min_width + (max_width - min_width) * (1 - t))
            color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]
            x = mx - width // 2
            y = my - disk_height // 2
            pygame.draw.rect(surface, color, (x, y, width, disk_height), border_radius=8)

        # mensaje final
        if self.finished:
            msg = "¡Nivel completado!" if self.won else "Tiempo agotado"
            msg_surf = font_big.render(msg, True, (255, 215, 0) if self.won else (255, 80, 80))
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT * 0.18))
            surface.blit(msg_surf, msg_rect)

            if self.won:
                score_surf = font_small.render(f"Puntuación: {self.score}", True, TEXT_COLOR)
                surface.blit(score_surf, (WIDTH // 2 - score_surf.get_width() // 2, msg_rect.bottom + 5))


# ----------------- JUEGO PRINCIPAL -----------------

class TowerOfHanoiGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Torre de Hanoi - Videojuego")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("arial", 40, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 28)
        self.font_small = pygame.font.SysFont("arial", 22)

        self.state = GameState.MENU
        self.current_level = 1
        self.hanoi = None

        # botones
        self.menu_buttons = []
        self.play_buttons = []
        self.level_complete_buttons = []
        self.game_over_buttons = []
        self.instructions_buttons = []

        self.create_menu_buttons()
        self.create_play_buttons()
        self.create_end_buttons()

        # música de fondo (opcional)
        # try:
        #     pygame.mixer.music.load("music.mp3")
        #     pygame.mixer.music.play(-1)
        # except:
        #     print("No se encontró music.mp3, sigue sin música de fondo.")

    # ---------- creación de botones ----------

    def create_menu_buttons(self):
        cx = WIDTH // 2
        base_y = 250
        w, h = 260, 55

        self.menu_buttons = [
            Button((cx - w // 2, base_y, w, h), "Jugar", self.font_medium, self.start_game),
            Button((cx - w // 2, base_y + 80, w, h), "Instrucciones", self.font_medium, self.show_instructions),
            Button((cx - w // 2, base_y + 160, w, h), "Salir", self.font_medium, self.exit_game),
        ]

    def create_play_buttons(self):
        # botones en pantalla de juego: Reiniciar, Menú
        self.play_buttons = [
            Button((WIDTH - 180, 80, 150, 40), "Reiniciar", self.font_small, self.restart_level),
            Button((WIDTH - 180, 130, 150, 40), "Menú", self.font_small, self.back_to_menu),
        ]

    def create_end_buttons(self):
        # nivel completado
        cx = WIDTH // 2
        self.level_complete_buttons = [
            Button((cx - 130, HEIGHT // 2, 260, 50), "Siguiente nivel", self.font_medium, self.next_level),
            Button((cx - 130, HEIGHT // 2 + 70, 260, 50), "Volver al menú", self.font_medium, self.back_to_menu),
        ]
        # game over
        self.game_over_buttons = [
            Button((cx - 130, HEIGHT // 2, 260, 50), "Reintentar nivel", self.font_medium, self.restart_level),
            Button((cx - 130, HEIGHT // 2 + 70, 260, 50), "Volver al menú", self.font_medium, self.back_to_menu),
        ]
        # instrucciones
        self.instructions_buttons = [
            Button((cx - 100, HEIGHT - 90, 200, 50), "Volver al menú", self.font_medium, self.back_to_menu),
        ]

    # ---------- callbacks de botones ----------

    def start_game(self):
        self.current_level = 1
        self.hanoi = HanoiGame(self.current_level)
        self.state = GameState.PLAYING

    def back_to_menu(self):
        self.state = GameState.MENU

    def restart_level(self):
        if self.hanoi:
            self.hanoi.reset()
        self.state = GameState.PLAYING

    def next_level(self):
        if self.current_level < MAX_LEVEL:
            self.current_level += 1
            self.hanoi = HanoiGame(self.current_level)
            self.state = GameState.PLAYING
        else:
            # si ya no hay más niveles, regresa al menú
            self.state = GameState.MENU

    def show_instructions(self):
        self.state = GameState.INSTRUCTIONS

    def exit_game(self):
        pygame.quit()
        sys.exit()

    # ---------- bucle principal ----------

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()

    # ---------- manejo de eventos ----------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game()

            if self.state == GameState.MENU:
                for b in self.menu_buttons:
                    b.handle_event(event)

            elif self.state == GameState.PLAYING:
                for b in self.play_buttons:
                    b.handle_event(event)

                if self.hanoi and not self.hanoi.finished:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.hanoi.start_drag(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.hanoi.end_drag(event.pos)

            elif self.state == GameState.LEVEL_COMPLETE:
                for b in self.level_complete_buttons:
                    b.handle_event(event)

            elif self.state == GameState.GAME_OVER:
                for b in self.game_over_buttons:
                    b.handle_event(event)

            elif self.state == GameState.INSTRUCTIONS:
                for b in self.instructions_buttons:
                    b.handle_event(event)

    # ---------- actualización ----------

    def update(self, dt):
        if self.state == GameState.PLAYING and self.hanoi:
            self.hanoi.update(dt)
            if self.hanoi.finished:
                if self.hanoi.won:
                    self.state = GameState.LEVEL_COMPLETE
                else:
                    self.state = GameState.GAME_OVER

    # ---------- dibujo de pantallas ----------

    def draw_menu(self):
        self.screen.fill(BACKGROUND_COLOR)

        title = self.font_big.render("Torre de Hanoi", True, TEXT_COLOR)
        subtitle = self.font_small.render("Proyecto Estructuras de Datos - Python", True, TEXT_COLOR)

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 90))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 140))

        for b in self.menu_buttons:
            b.draw(self.screen)

    def draw_instructions(self):
        self.screen.fill(BACKGROUND_COLOR)
        title = self.font_big.render("Instrucciones", True, TEXT_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        lines = [
            "Objetivo: mover toda la torre desde el primer poste al tercero,",
            "cumpliendo estas reglas:",
            "1) Solo puedes mover un disco a la vez.",
            "2) Solo puedes mover el disco superior de un poste.",
            "3) Nunca puedes poner un disco grande sobre uno más pequeño.",
            "",
            "Controles:",
            "- Haz clic sobre la torre (poste) que tiene el disco que quieres mover,",
            "  mantén el clic y arrastra el disco hacia el poste destino.",
            "- Suelta el mouse sobre el poste donde quieres dejar el disco.",
            "",
            "Cada nivel aumenta la cantidad de discos y el tiempo límite.",
            "Tu puntuación depende del tiempo restante y de qué tan cerca estás",
            "del número mínimo de movimientos teóricos.",
        ]

        y = 130
        for line in lines:
            surf = self.font_small.render(line, True, TEXT_COLOR)
            self.screen.blit(surf, (70, y))
            y += 26

        for b in self.instructions_buttons:
            b.draw(self.screen)

    def draw_playing(self):
        if not self.hanoi:
            return
        self.hanoi.draw(self.screen, self.font_small, self.font_medium)
        for b in self.play_buttons:
            b.draw(self.screen)

    def draw_level_complete(self):
        self.draw_playing()
        # sombreado
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        msg = self.font_big.render("¡Nivel completado!", True, (255, 215, 0))
        self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 3))

        score_msg = self.font_medium.render(f"Puntuación: {self.hanoi.score}", True, TEXT_COLOR)
        self.screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 3 + 60))

        for b in self.level_complete_buttons:
            b.draw(self.screen)

    def draw_game_over(self):
        self.draw_playing()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        msg = self.font_big.render("Tiempo agotado", True, (255, 80, 80))
        self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 3))

        for b in self.game_over_buttons:
            b.draw(self.screen)

    def draw(self):
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_playing()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.INSTRUCTIONS:
            self.draw_instructions()


if __name__ == "__main__":
    game = TowerOfHanoiGame()
    game.run()
