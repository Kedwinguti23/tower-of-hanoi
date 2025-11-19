import pygame
import sys

from src.config.settings import *
from src.game.states import GameState
from src.game.hanoi import HanoiGame
from src.ui.button import NeonPauseButton, NeonRoundButton

from src.ui.screens import (
    MenuScreen,
    InstructionsScreen,
    LevelCompleteScreen,
    GameOverScreen,
    LevelSelectScreen,
    PauseScreen
)

from src.ui.transition import TransitionManager


class TowerOfHanoiGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Torre de Hanoi - Proyecto Estructuras de Datos")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # ------------------ FUENTES ------------------
        try:
            self.font_big = pygame.font.Font(pygame.font.match_font('bahnschrift'), 40)
            self.font_medium = pygame.font.Font(pygame.font.match_font('bahnschrift'), 28)
            self.font_small = pygame.font.Font(pygame.font.match_font('bahnschrift'), 22)
        except Exception:
            self.font_big = pygame.font.SysFont("arial", 40, bold=True)
            self.font_medium = pygame.font.SysFont("arial", 28)
            self.font_small = pygame.font.SysFont("arial", 22)

        # ------------------ ESTADO INICIAL ------------------
        self.state = GameState.MENU
        self.current_level = 1
        self.hanoi = None
        self.time_enabled = True

        # ------------------ TRANSICIÓN ------------------
        self.transition = TransitionManager(self)
        self.transition.start("in", GameState.MENU)

        # ---------------- BOTÓN DE PAUSA ----------------
        self.pause_button = NeonPauseButton(
            x=WIDTH - 70,
            y=15,
            radius=25,
            label="II",   # <<<<<<<<<<<<<<<<<<<<<<<<<<< CAMBIO IMPORTANTE
            callback=lambda: self.transition.start("out", GameState.PAUSE)
        )

        # ---------------- BOTÓN AUTORRESOLVER ----------------
        self.tutorial_button = NeonRoundButton(
            x=250,
            y=35,
            radius=22,
            text="A",
            callback=self.toggle_tutorial
        )

        # ------------------ PANTALLAS ------------------
        self.screens = {
            GameState.MENU: MenuScreen(self),
            GameState.INSTRUCTIONS: InstructionsScreen(self),
            GameState.LEVEL_COMPLETE: LevelCompleteScreen(self),
            GameState.GAME_OVER: GameOverScreen(self),
            GameState.LEVEL_SELECT: LevelSelectScreen(self),
            GameState.PAUSE: PauseScreen(self),
        }

        # ------------------ AUDIO ------------------
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(MUSIC_PATH)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            self.snd_move = pygame.mixer.Sound(SND_MOVE)
            self.snd_error = pygame.mixer.Sound(SND_ERROR)
            self.snd_win = pygame.mixer.Sound(SND_WIN)
            self.snd_lose = pygame.mixer.Sound(SND_LOSE)
        except Exception:
            print("No se pudo cargar audio.")
            self.snd_move = self.snd_error = self.snd_win = self.snd_lose = None

    # ============================================================
    #                           CALLBACKS
    # ============================================================

    def toggle_tutorial(self):
        if self.hanoi:
            self.hanoi.start_tutorial()

    def start_game(self):
        self.time_enabled = True
        self.current_level = 1
        self.hanoi = HanoiGame(1, self, time_enabled=True)
        self.transition.start("out", GameState.PLAYING)

    def start_game_no_time(self):
        self.time_enabled = False
        self.current_level = 1
        self.hanoi = HanoiGame(1, self, time_enabled=False)
        self.transition.start("out", GameState.PLAYING)

    def start_specific_level(self, level):
        self.current_level = level
        self.hanoi = HanoiGame(level, self, time_enabled=self.time_enabled)
        self.transition.start("out", GameState.PLAYING)

    def back_to_menu(self):
        self.transition.start("out", GameState.MENU)

    def restart_level(self):
        self.hanoi = HanoiGame(self.current_level, self, time_enabled=self.time_enabled)
        self.transition.start("out", GameState.PLAYING)

    def next_level(self):
        if self.current_level < MAX_LEVEL:
            self.current_level += 1
            self.hanoi = HanoiGame(self.current_level, self, time_enabled=self.time_enabled)
            self.transition.start("out", GameState.PLAYING)
        else:
            self.transition.start("out", GameState.MENU)

    def show_instructions(self):
        self.transition.start("out", GameState.INSTRUCTIONS)

    def show_level_select(self):
        self.transition.start("out", GameState.LEVEL_SELECT)

    def exit_game(self):
        pygame.quit()
        sys.exit()

    # ============================================================
    #                            LOOP
    # ============================================================

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()

            if not self.transition.active and self.state == GameState.PLAYING and self.hanoi:
                self.hanoi.update(dt)

                if self.hanoi.finished:
                    next_state = GameState.LEVEL_COMPLETE if self.hanoi.won else GameState.GAME_OVER
                    self.transition.start("out", next_state)

            self.transition.update(dt, self)
            self.draw()
            pygame.display.flip()

    # ============================================================
    #                          EVENTOS
    # ============================================================

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.exit_game()

            if self.transition.active:
                continue

            # ---------------------- GAMEPLAY ----------------------
            if self.state == GameState.PLAYING:

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Botón PAUSA
                    if self.pause_button.is_hover(event.pos):
                        self.transition.start("out", GameState.PAUSE)
                        return

                    # Botón AUTORRESOLVER
                    if not getattr(self.hanoi, "tutorial_mode", False):
                        if self.tutorial_button.is_hover(event.pos):
                            self.toggle_tutorial()
                            return

                    # Si el tutorial está activo → ignorar clics
                    if getattr(self.hanoi, "tutorial_mode", False):
                        return

                    # Drag de discos
                    if self.hanoi:
                        self.hanoi.start_drag(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.hanoi:
                        self.hanoi.end_drag(event.pos)

                continue

            # ---------------------- UI ----------------------
            self.screens[self.state].handle_event(event)

    # ============================================================
    #                             DRAW
    # ============================================================

    def draw(self):
        self.screen.fill((0, 0, 0))

        if self.state == GameState.PLAYING and self.hanoi:
            self.hanoi.draw(self.screen, self.font_small, self.font_medium)

            # Botón de pausa
            self.pause_button.draw(self.screen)

            # Autorresolver solo si no está activo
            if not getattr(self.hanoi, "tutorial_mode", False):
                self.tutorial_button.draw(self.screen)

        else:
            self.screens[self.state].draw(self.screen)

        # Transición encima
        self.transition.draw(self.screen)


if __name__ == "__main__":
    game = TowerOfHanoiGame()
    game.run()
