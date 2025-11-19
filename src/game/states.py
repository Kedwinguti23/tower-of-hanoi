from enum import Enum

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4
    INSTRUCTIONS = 5
    LEVEL_SELECT = 6
    PAUSE = 7     # <-- NUEVO
