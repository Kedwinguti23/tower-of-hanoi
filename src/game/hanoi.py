import pygame
from src.config.settings import *

class HanoiGame:
    # -----------------------------------------------------------
    # INIT
    # -----------------------------------------------------------
    def __init__(self, level, game=None, time_enabled=True):
        self.game = game
        self.level = level
        self.time_enabled = time_enabled

        self.num_disks = 2 + level
        self.pegs = [list(range(1, self.num_disks + 1)), [], []]

        self.moves = 0
        self.min_moves = (2 ** self.num_disks) - 1

        # Tiempo
        if self.time_enabled:
            self.time_limit = 30 + int(self.min_moves * 1.5)
            self.time_left = self.time_limit
        else:
            self.time_limit = None
            self.time_left = None

        self.score = 0
        self.finished = False
        self.won = False

        self.dragging_disk = None
        self.drag_from_peg = None

        # Visual
        self.highlight_alpha = 0
        self.shadow_offset = 10
        self.shake_timer = 0
        self.shake_intensity = 0
        self.shake_direction = 1
        self.invalid_target = None

        self.animation = None

        self.peg_positions = self.calculate_peg_positions()

        # Tutorial
        self.tutorial_mode = False
        self.tutorial_moves = []
        self.tutorial_timer = 0

    # -----------------------------------------------------------
    def calculate_peg_positions(self):
        positions = []
        spacing = WIDTH / 3
        base_y = HEIGHT * 0.85

        for i in range(3):
            x = spacing * (i + 0.5)
            positions.append((int(x), int(base_y)))

        return positions

    # -----------------------------------------------------------
    def reset(self):
        # FIX: corregido el typo fatal num_dis_disks → num_disks
        self.pegs = [list(range(1, self.num_disks + 1)), [], []]

        if self.time_enabled:
            self.time_left = self.time_limit
        else:
            self.time_left = None

        self.moves = 0
        self.finished = False
        self.won = False
        self.score = 0
        self.dragging_disk = None
        self.drag_from_peg = None
        self.animation = None

        # Reset visual
        self.shake_timer = 0
        self.shake_intensity = 0
        self.invalid_target = None

        # Reset tutorial
        self.tutorial_mode = False
        self.tutorial_moves = []
        self.tutorial_timer = 0

    # -----------------------------------------------------------
    # ANIMACIÓN
    # -----------------------------------------------------------
    def start_drop_animation(self, disk, from_peg, to_peg):
        mx, my = pygame.mouse.get_pos()
        px, base_y = self.peg_positions[to_peg]
        disk_height = 22
        final_y = base_y - disk_height * (len(self.pegs[to_peg]) + 1)

        self.animation = {
            "disk": disk,
            "from_peg": from_peg,
            "to_peg": to_peg,
            "progress": 0.0,
            "duration": 0.20,
            "start_pos": (mx, my),
            "end_pos": (px, final_y)
        }

    def update_animation(self, dt):
        anim = self.animation
        anim["progress"] += dt / anim["duration"]

        if anim["progress"] >= 1:
            disk = anim["disk"]
            to_peg = anim["to_peg"]
            self.pegs[to_peg].insert(0, disk)
            self.animation = None
            return False

        return True

    # -----------------------------------------------------------
    # INTERACCIÓN
    # -----------------------------------------------------------
    def peg_at_position(self, pos):
        x, y = pos
        for i, (px, py) in enumerate(self.peg_positions):
            if abs(x - px) < 120 and (py - 250) < y < (py + 20):
                return i
        return None

    def start_drag(self, pos):
        if self.finished or self.animation:
            return

        peg = self.peg_at_position(pos)
        if peg is None or not self.pegs[peg]:
            return

        self.dragging_disk = self.pegs[peg].pop(0)
        self.drag_from_peg = peg

    def end_drag(self, pos):
        if self.dragging_disk is None:
            return

        target = self.peg_at_position(pos)

        if target is None or target == self.drag_from_peg:
            self.cancel_drag()
            return

        if self.can_place(self.dragging_disk, target):
            if self.game and self.game.snd_move:
                try: self.game.snd_move.play()
                except: pass

            d = self.dragging_disk
            f = self.drag_from_peg
            self.start_drop_animation(d, f, target)
            self.moves += 1

        else:
            if self.game and self.game.snd_error:
                try: self.game.snd_error.play()
                except: pass

            self.shake_timer = 0.25
            self.shake_intensity = 10
            self.invalid_target = target
            self.cancel_drag()

        self.dragging_disk = None
        self.drag_from_peg = None

    def cancel_drag(self):
        if self.dragging_disk is not None:
            self.pegs[self.drag_from_peg].insert(0, self.dragging_disk)
        self.dragging_disk = None
        self.drag_from_peg = None

    def can_place(self, disk, to_peg):
        if not self.pegs[to_peg]:
            return True
        return disk < self.pegs[to_peg][0]

    # -----------------------------------------------------------
    def get_shake_offset(self, peg_index):
        if peg_index == self.invalid_target and self.shake_timer > 0:
            return int(self.shake_intensity * self.shake_direction)
        return 0

    # -----------------------------------------------------------
    # SCORE
    # -----------------------------------------------------------
    def calculate_score(self):
        if self.time_enabled:
            time_bonus = max(0, int(self.time_left))
        else:
            time_bonus = 0

        efficiency = max(1, self.min_moves / max(1, self.moves))
        self.score = int(1000 * efficiency + time_bonus)

    # ============================================================
    #        MODO TUTORIAL — AUTO RESOLUCIÓN
    # ============================================================
    def start_tutorial(self):
        if self.tutorial_mode:
            return

        self.tutorial_mode = True
        self.tutorial_moves = []
        self.tutorial_timer = 0

        self.generate_solution(self.num_disks, 0, 2, 1)

    def generate_solution(self, n, start, end, aux):
        if n == 1:
            self.tutorial_moves.append((start, end))
            return

        self.generate_solution(n-1, start, aux, end)
        self.tutorial_moves.append((start, end))
        self.generate_solution(n-1, aux, end, start)

    # ============================================================
    # UPDATE
    # ============================================================
    def update(self, dt):
        # 1) Animación
        if self.animation:
            self.update_animation(dt)
            return

        # 2) Tutorial
        if self.tutorial_mode and not self.finished:
            self.tutorial_timer += dt

            if self.tutorial_timer >= 0.45:
                self.tutorial_timer = 0

                if self.tutorial_moves:
                    frm, to = self.tutorial_moves.pop(0)
                    disk = self.pegs[frm].pop(0)
                    self.pegs[to].insert(0, disk)
                else:
                    self.finished = True
                    self.won = True
                    self.calculate_score()

            return

        # 3) Tiempo
        if self.time_enabled and not self.finished:
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.finished = True
                self.won = False

                if self.game and self.game.snd_lose:
                    try: self.game.snd_lose.play()
                    except: pass

        # 4) Victoria normal
        if not self.animation and self.dragging_disk is None:
            if self.pegs[2] == list(range(1, self.num_disks + 1)) and not self.finished:
                self.finished = True
                self.won = True
                self.calculate_score()

                if self.game and self.game.snd_win:
                    try: self.game.snd_win.play()
                    except: pass

        # 5) Shake efecto
        if self.shake_timer > 0:
            self.shake_timer -= dt
        if self.shake_timer <= 0:
            self.shake_intensity = 0
            self.invalid_target = None

        self.shake_direction *= -1

    # ============================================================
    # DRAW
    # ============================================================
    def draw(self, surface, font_small, font_big):
        surface.fill(BACKGROUND_COLOR)

        # HUD
        hud = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 90))
        surface.blit(hud, (0, 0))

        title = font_big.render(f"Nivel {self.level}", True, (0, 255, 180))
        surface.blit(title, (30, 18))

        info = [f"Movs: {self.moves}/{self.min_moves}"]
        if self.time_enabled:
            info.append(f"Tiempo: {int(self.time_left)}s")
        else:
            info.append("Modo: Sin Tiempo")

        y = 18
        for txt in info:
            t = font_small.render(txt, True, (200, 255, 255))
            surface.blit(t, (WIDTH - 260, y))
            y += 22

        # Parámetros de gráficos
        disk_h = 22
        max_w = 180
        min_w = 60

        # Postes
        for i, (px, py) in enumerate(self.peg_positions):
            px_adj = px + self.get_shake_offset(i)
            pygame.draw.rect(surface,
                             PEG_COLOR,
                             (px_adj - 7, py - 200, 14, 200),
                             border_radius=5)

        # Discos en postes
        for peg_i, peg in enumerate(self.pegs):
            px, py = self.peg_positions[peg_i]
            px += self.get_shake_offset(peg_i)

            for level_idx, disk in enumerate(reversed(peg)):
                t = (disk - 1) / max(1, self.num_disks - 1)
                width = int(min_w + (max_w - min_w) * t)
                color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]

                x = px - width // 2
                y = py - disk_h * (level_idx + 1)

                pygame.draw.rect(surface, (0, 0, 0, 60), (x+3, y+3, width, disk_h), border_radius=8)
                pygame.draw.rect(surface, color, (x, y, width, disk_h), border_radius=8)
                pygame.draw.rect(surface, (255, 255, 255, 40), (x, y, width, disk_h), 2, border_radius=8)

        # Disco arrastrado
        if self.dragging_disk:
            mx, my = pygame.mouse.get_pos()
            disk = self.dragging_disk

            t = (disk - 1) / max(1, self.num_disks - 1)
            width = int(min_w + (max_w - min_w) * t)
            color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]

            shadow = pygame.Surface((width, disk_h), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 130),
                             (0, 0, width, disk_h),
                             border_radius=8)
            surface.blit(shadow, (mx - width//2 + 5, my - disk_h//2 + 10))

            glow = pygame.Surface((width+12, disk_h+12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 100),
                             (0, 0, width+12, disk_h+12),
                             border_radius=14)
            surface.blit(glow, (mx - width//2 - 6, my - disk_h//2 - 6))

            pygame.draw.rect(surface, color,
                             (mx - width//2, my - disk_h//2,
                              width, disk_h),
                             border_radius=8)

        # Animación en progreso
        if self.animation:
            anim = self.animation
            prog = anim["progress"]
            prog = 1 - (1 - prog) ** 3  # easing

            x0, y0 = anim["start_pos"]
            x1, y1 = anim["end_pos"]
            x = x0 + (x1 - x0) * prog
            y = y0 + (y1 - y0) * prog

            disk = anim["disk"]
            t = (disk - 1) / max(1, self.num_disks - 1)
            width = int(min_w + (max_w - min_w) * t)
            color = DISK_COLORS[(disk - 1) % len(DISK_COLORS)]

            pygame.draw.rect(surface, color,
                             (x - width//2, y - disk_h//2,
                              width, disk_h),
                             border_radius=8)
