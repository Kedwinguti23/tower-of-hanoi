import pygame
from src.config.settings import WIDTH, HEIGHT

class TransitionManager:
    def __init__(self, game):
        self.game = game
        self.active = False
        self.type = None   # "in" o "out"
        self.next_state = None
        self.alpha = 0
        self.speed = 400   # velocidad del fade

        # Overlay de pantalla del tamaño correcto
        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(self.alpha)

    def start(self, t, next_state):
        self.active = True
        self.type = t
        self.next_state = next_state
        self.alpha = 0 if t == "in" else 255

    def update(self, dt, game):
        if not self.active:
            return

        if self.type == "out":
            self.alpha += self.speed * dt
            if self.alpha >= 255:
                self.alpha = 255
                game.state = self.next_state
                self.type = "in"
        else:
            self.alpha -= self.speed * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.active = False

        self.overlay.set_alpha(self.alpha)

    def draw(self, surface):
        if self.active:
            surface.blit(self.overlay, (0, 0))
