import pygame
from src.config.settings import BUTTON_COLOR, BUTTON_HOVER, TEXT_COLOR


# ============================================================
# BOTÓN RECTANGULAR (normal)
# ============================================================
class Button:
    def __init__(self, rect, text, font, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.callback = callback

        # Animación de hover
        self.hover_scale = 0
        self.max_scale = 6

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)

        # Animación
        if is_hover:
            self.hover_scale = min(self.hover_scale + 1, self.max_scale)
        else:
            self.hover_scale = max(self.hover_scale - 1, 0)

        scaled_rect = self.rect.inflate(self.hover_scale, self.hover_scale)

        # Sombra
        shadow = scaled_rect.copy()
        shadow.y += 5
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=14)

        # Cuerpo del botón (glass)
        glass = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            glass,
            (30, 45, 70, 120),
            (0, 0, scaled_rect.width, scaled_rect.height),
            border_radius=14
        )
        surface.blit(glass, scaled_rect.topleft)

        # Borde
        border_color = (0, 200, 255) if is_hover else (0, 130, 160)
        pygame.draw.rect(surface, border_color, scaled_rect, 2, border_radius=14)

        # Glow suave
        if is_hover:
            glow = pygame.Surface((scaled_rect.width + 14, scaled_rect.height + 14), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 200, 255, 70),
                             (0, 0, glow.get_width(), glow.get_height()),
                             border_radius=18)
            surface.blit(glow, (scaled_rect.x - 7, scaled_rect.y - 7))

        # Texto
        text_surf = self.font.render(self.text, True, (220, 240, 255))
        surface.blit(text_surf, text_surf.get_rect(center=scaled_rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()


# ============================================================
# BOTÓN CIRCULAR PARA PAUSA
# ============================================================
class NeonPauseButton:
    def __init__(self, x, y, radius=25, label=None, callback=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.callback = callback
        self.label = label  # texto opcional ("A" / "II")

        # Colores
        self.base_color = (0, 220, 255)
        self.glow_color = (0, 180, 255, 140)

        # Fuente para texto dentro del botón
        self.font = pygame.font.SysFont("bahnschrift", radius)

    def is_hover(self, pos):
        mx, my = pos
        return (mx - self.x)**2 + (my - self.y)**2 <= self.radius**2

    def draw(self, surface):
        # Glow externo
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, self.glow_color,
                           (self.radius * 2, self.radius * 2),
                           self.radius * 2)
        surface.blit(glow, (self.x - self.radius * 2, self.y - self.radius * 2))

        # Círculo principal
        pygame.draw.circle(surface, self.base_color, (self.x, self.y), self.radius, width=3)

        # Si tiene label → texto
        if self.label:
            text_surf = self.font.render(self.label, True, (255, 255, 255))
            rect = text_surf.get_rect(center=(self.x, self.y))
            surface.blit(text_surf, rect)

        else:
            # Icono pausa
            bar_w = 6
            bar_h = self.radius + 5

            pygame.draw.rect(surface, self.base_color,
                             (self.x - 10, self.y - bar_h // 2, bar_w, bar_h),
                             border_radius=3)

            pygame.draw.rect(surface, self.base_color,
                             (self.x + 4, self.y - bar_h // 2, bar_w, bar_h),
                             border_radius=3)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hover(event.pos):
                if self.callback:
                    self.callback()


# ============================================================
# BOTÓN REDONDO CON TEXTO (no pausa)
# ============================================================
class NeonRoundButton:
    def __init__(self, x, y, radius=25, text="", callback=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.text = text
        self.callback = callback

        self.base_color = (0, 220, 255)
        self.glow_color = (0, 180, 255, 140)

    def is_hover(self, pos):
        mx, my = pos
        return (mx - self.x)**2 + (my - self.y)**2 <= self.radius**2

    def draw(self, surface):
        # Glow externo
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, self.glow_color,
                           (self.radius * 2, self.radius * 2),
                           self.radius * 2)
        surface.blit(glow, (self.x - self.radius * 2, self.y - self.radius * 2))

        # Círculo principal
        pygame.draw.circle(surface, self.base_color, (self.x, self.y), self.radius, width=3)

        # Texto interno
        font = pygame.font.SysFont("bahnschrift", 24)
        text_surf = font.render(self.text, True, (255, 255, 255))
        rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hover(event.pos):
                if self.callback:
                    self.callback()
