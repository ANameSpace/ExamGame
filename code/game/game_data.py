from typing import Callable, Any

from code.game.game import *
from code.tui import TextColor



def load_player() -> dict:
    name = "Я"
    color = TextColor.GREEN

    return {
        "actor": (name, color),
        "inventory": list(),
        "attributes": dict()
    }

def load_actors() -> dict[id: str, tuple[str, TextColor]]:
    actors = dict()

    actors["author"] = (" ", TextColor.RED)
    actors["unknown"] = ("???", TextColor.MAGENTA)

    actors["clock"] = ("Будильник", TextColor.RED)
    actors["aleksandr"] = ("Саня", TextColor.YELLOW)
    actors["bus"] = ("Автобус", TextColor.BLUE)

    actors["controller"] = ("КоНтРоЛёР", TextColor.RED)
    actors["security"] = ("Охранник", TextColor.RED)

    return actors

def load_levels() -> list[Callable[[Any], None | str]]:
    levels = list()

    levels.append(level_0)
    levels.append(level_1)

    return levels