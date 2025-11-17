from dataclasses import dataclass
import pygame


@dataclass
class InputState:
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False
    start: bool = False


class InputManager:
    def __init__(self):
        # mapping from player id (0,1,...) to assigned key map or device
        self.keymaps = {
            0: {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'start': pygame.K_SPACE},
            1: {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'start': pygame.K_RETURN},
        }

    def poll(self) -> dict[int, InputState]:
        # handle discrete events if needed (KEYDOWN/KEYUP)
        events = pygame.event.get()   # call once per frame
        # keep or forward events for menu handling, quit, etc.
        keydown = {e.key: e.type == pygame.KEYDOWN for e in events if e.type in (
            pygame.KEYDOWN, pygame.KEYUP)}

        # continuous state via get_pressed (good for movement)
        keys = pygame.key.get_pressed()

        states = {}
        for pid, km in self.keymaps.items():
            st = InputState(
                up=bool(keys[km['up']]),
                down=bool(keys[km['down']]),
                left=bool(keys[km['left']]),
                right=bool(keys[km['right']]),
                start=bool(keys[km.get('start')]) if km.get(
                    'start') else False,
            )
            states[pid] = st

        # also return events if Game wants them:
        return states, events
