import curses
import os
from enum import Enum
from time import sleep
from typing import Any, Callable

from code.game.game_api import GameAPI
from code.tui import TextColor, Rectangle, TextField, Selector, ASCIIImage
from code.game import game_data


# print("▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▉ ▊ ▋ ▌ ▍ ▎ ▏ ▐ ░ ▒ ▓")


class AppState(Enum):
    EXIT = -1
    MAIN_SCREEN = 0
    GAME_SCREEN = 1
    WIN_SCREEN = 2
    LOSE_SCREEN = 3


class BaseScreen:
    def __init__(self, stdscr: curses.window, locale: dict[str, str], images):
        self._stdscr: curses.window = stdscr

        self.locale: dict[str, str] = locale
        self._images: dict[str, tuple[tuple[tuple[str, ...], ...], tuple[tuple[int, ...], ...]]] = images

        self._recalculate_xy()

    def _recalculate_xy(self):
        self._max_y, self._max_x = self._stdscr.getmaxyx()
        # Attempting to write to the lower right corner of a window
        # will cause an exception to be raised after the string is printed.
        # https://docs.python.org/3/library/curses.html
        self._max_x -= 1
        # Число символов всегда нечётное
        if self._max_y % 2 == 0:
            self._max_y -= 1
        # Индекс начинаеться с 0
        self._max_index_y = self._max_y - 1
        self._max_index_x = self._max_x - 1
        self._center_index_y = self._max_index_y // 2


class MainScreen(BaseScreen):
    def __init__(self, stdscr, locale, images):
        super().__init__(stdscr, locale, images)

    def open(self) -> tuple[AppState, dict[Any, Any]]:
        self._stdscr.clear()

        ASCIIImage(self._max_y - 7, 0, self._images["city"]).pre_render(self._stdscr)

        x = (self._max_index_x - 50) // 2
        (Rectangle(self._center_index_y - 5, x, 10, 50, filler="░")
         .pre_render(self._stdscr))
        (TextField(self._center_index_y - 3, x, 1, 50, TextColor.YELLOW, self.locale["main.title"],
                   TextField.TextAlign.CENTER)
         .pre_render(self._stdscr))

        variants = (
            self.locale["main.play"],
            self.locale["main.reload"],
            self.locale["main.exit"]
        )
        selector = Selector(self._center_index_y, (self._max_index_x - 8) // 2, 3, 8, variants, 0)
        selector.pre_render(self._stdscr)
        match selector.select(self._stdscr):
            case 0:
                return AppState.GAME_SCREEN, dict()
            case 1:
                return AppState.MAIN_SCREEN, dict()
            case 2:
                return AppState.EXIT, dict()
            case _:
                raise ValueError()


class GameScreen(BaseScreen, GameAPI):
    def __init__(self, stdscr: curses.window, locale, images):
        super().__init__(stdscr, locale, images)

        self.player: dict = game_data.load_player()
        self.actors: dict[id: str, tuple[str, TextColor]] = game_data.load_actors()
        self.__levels: list[Callable[[GameScreen], None | str]] = game_data.load_levels()

        self._image = None
        self._actor_text = None
        self._actor_name = None
        self._select_border = None
        self._select_text = None
        self._phone_border = None
        self._text_border = None
        self._phone_messages = list()
        self.__is_open = False

    def open(self) -> tuple[AppState, dict[Any, Any]]:
        if self.__is_open:
            raise Exception("Не надо вызывать open()!!!!")
        self.__is_open = True

        (Rectangle(0, 0, self._max_y, self._max_x, filler="█", background=True)
         .render_animation(self._stdscr, Rectangle.RectangleAnimation.COMPRESS.value, 0.05))
        self._stdscr.clear()
        self._stdscr.refresh()

        self._text_border = Rectangle(self._max_y - 9, 0, 9, self._max_x, filler="░")
        self._actor_name = TextField(self._max_y - 7, 2, 1, self._max_x - 2)
        self._actor_text = TextField(self._max_y - 5, 2, 3, self._max_x - 2)

        self._phone_border = Rectangle(0, self._max_x // 2, self._max_y, (self._max_x // 2) - 1, filler="░")

        x = (self._max_index_x - 70) // 2
        y_size = self._max_y - 10
        self._select_border = Rectangle(self._center_index_y - 10, x, y_size, 70, filler="░")
        self._select_text = TextField(self._center_index_y - 8, x, y_size, 68, align=TextField.TextAlign.CENTER)

        for level in self.__levels:
            result = level(self)
            (Rectangle(0, 0, self._max_y, self._max_x, filler="█", background=True)
             .render_animation(self._stdscr, Rectangle.RectangleAnimation.COMPRESS.value, 0.05))
            if result is not None:
                return AppState.LOSE_SCREEN, {"message": result}

        return AppState.WIN_SCREEN, {"message": "Благодарим за прохождение."}

    def get_player(self) -> dict:
        return self.player

    def get_actors(self) -> dict[id: str, tuple[str, TextColor]]:
        return self.actors

    def __wait_interact(self):
        curses.flushinp()
        while self._stdscr.getch() not in [curses.KEY_RIGHT, curses.KEY_ENTER, 10, 13]:
            continue

    def __show_text(self, name: str, name_color: TextColor, text: str) -> None:
        self._phone_messages.clear()
        self._stdscr.clear()
        if self._image:
            self._image.pre_render(self._stdscr)


        self._text_border.pre_render(self._stdscr)

        self._actor_name.set_text(name)
        self._actor_name.set_color(name_color)
        self._actor_name.pre_render(self._stdscr)

        self._actor_text.set_text(text)
        self._actor_text.render_animation(self._stdscr, TextField.TextAnimation.BASE.value, 0.05)
        self._stdscr.refresh()

        self.__wait_interact()

    def look(self, image_name: str):
        self._image = ASCIIImage(0, 0, self._images[image_name])

    def talk(self, actor: tuple[str, TextColor], text: str) -> None:
        self.__show_text(actor[0], actor[1], text)

    def think(self, actor: tuple[str, TextColor], text: str) -> None:
        self.__show_text(actor[0] + self.locale["game.think.suffix"], actor[1], text)

    def do(self, actor: tuple[str, TextColor], text: str) -> None:
        self.__show_text(actor[0], actor[1], "*"+text+"*")

    def phone(self, actor: tuple[str, TextColor], text: str) -> None:
        self._stdscr.clear()

        self._phone_border.pre_render(self._stdscr)
        self._phone_border.apply_modifer(self._stdscr)

        y_start = 2
        if len(self._phone_messages) > 0:
            msg = self._phone_messages[-1]
            new_end = msg.y + msg.text_size
            if new_end >= self._max_index_y - 3:
                self._phone_messages.clear()
            else:
                y_start = new_end

        x_size = (self._max_x // 2) - 3
        al = TextField.TextAlign.RIGHT if actor[0] == self.player["actor"][0] else TextField.TextAlign.LEFT
        self._phone_messages.append(TextField(y_start, x_size + 4, 1, x_size, color=actor[1], text=actor[0], align=al))
        y_start += 1
        self._phone_messages.append(TextField(y_start, x_size + 4, 3, x_size, text=text, align=al))

        for element in self._phone_messages:
            element.pre_render(self._stdscr)
        self._stdscr.refresh()

        self.__wait_interact()

    def select(self, text: str, variants: tuple[str, ...]) -> int:
        self._phone_messages.clear()
        self._stdscr.clear()

        self._select_border.pre_render(self._stdscr)

        self._select_text.set_text(text)
        self._select_text.pre_render(self._stdscr)

        self._stdscr.refresh()

        x = (self._max_index_x - 66) // 2
        y_size = self._max_y - 8
        selector = Selector(self._center_index_y - 6, x, y_size, 68, variants)
        selector.pre_render(self._stdscr)
        return selector.select(self._stdscr)


class GameWinScreen(BaseScreen):
    def __init__(self, stdscr: curses.window, locale, images, message: str):
        super().__init__(stdscr, locale, images)
        self.message = message

    def open(self) -> tuple[AppState, dict[Any, Any]]:
        self._stdscr.clear()

        x = (self._max_index_x - 50) // 2
        (TextField(self._center_index_y - 2, x, 1, 50, TextColor.GREEN, self.locale["win.title"], TextField.TextAlign.CENTER)
         .pre_render(self._stdscr))
        (TextField(self._center_index_y, x, 1, 50, TextColor.DEFAULT, self.message, TextField.TextAlign.CENTER)
         .pre_render(self._stdscr))

        timer: TextField = TextField(self._center_index_y + 1, x, 1, 50, TextColor.DEFAULT, " ",
                                     TextField.TextAlign.CENTER)

        for i in range(5, 0, -1):
            timer.set_text(self.locale["win.timer"] + " " + str(i) + " ...")
            timer.pre_render(self._stdscr)
            self._stdscr.refresh()
            sleep(1)

        return AppState.MAIN_SCREEN, dict()


class GameOverScreen(BaseScreen):
    def __init__(self, stdscr: curses.window, locale, images, message: str):
        super().__init__(stdscr, locale, images)
        self.message = message

    def open(self) -> tuple[AppState, dict[Any, Any]]:
        self._stdscr.clear()

        x = (self._max_index_x - 50) // 2
        (TextField(self._center_index_y - 2, x, 1, 50, TextColor.RED, self.locale["lose.title"], TextField.TextAlign.CENTER)
         .pre_render(self._stdscr))
        (TextField(self._center_index_y, x, 1, 50, TextColor.DEFAULT, self.message, TextField.TextAlign.CENTER)
         .pre_render(self._stdscr))

        timer: TextField = TextField(self._center_index_y + 1, x, 1, 50, TextColor.DEFAULT, " ",
                                     TextField.TextAlign.CENTER)

        for i in range(5, 0, -1):
            timer.set_text(self.locale["lose.timer"] + " " + str(i) + " ...")
            timer.pre_render(self._stdscr)
            self._stdscr.refresh()
            sleep(1)

        return AppState.MAIN_SCREEN, dict()


def load_from_directory(directory: str, extension: str, func) -> None:
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            file_path = (directory + "/" +  filename)
            func(file_path)


class App:
    def __init__(self):
        self.images: dict[str, tuple[tuple[tuple[str, ...], ...], tuple[tuple[int, ...], ...]]] = dict()
        self.locale: dict[str, str] = dict()

        curses.wrapper(self.run)

    def _load_image(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            image: tuple[tuple[str, ...], ...]
            colors: tuple[tuple[int, ...], ...]

            pixels = True
            index = 0
            buffer: list[Any] = list()
            for line in file.readlines():
                line = line.replace("\n", "")
                if line == "IMAGE_END":
                    if pixels:
                        pixels = False

                        temp = list()
                        for l in buffer:
                            temp.append(tuple(l))
                        image = tuple(temp)

                        buffer.clear()
                        continue
                    else:
                        raise Exception()

                buffer.append(line)
                index += 1
            else:
                if pixels:
                    temp = list()
                    for l in buffer:
                        temp.append(tuple(l))
                    image = tuple(temp)

                    # colors = tuple([tuple([0] * len(image[0]))] * len(image))
                    colors = tuple()
                else:
                    temp = list()
                    for l in buffer:
                        l = l.replace(" ", "0")
                        temp.append(tuple(map(curses.color_pair, map(int, list(l)))))
                    colors = tuple(temp)

            self.images[file_path.split("/")[-1].replace(".ascii", "")] = (image, colors)


    def _load_locale(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.locale.clear()
            for line in file.readlines():
                line = line.replace("\n", "")
                if not line or len(line) <= 3:
                    continue
                key, value = line.split("=", 1)
                self.locale[key] = value

    def run(self, stdscr):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

        load_from_directory("assets/image", ".ascii", self._load_image)
        self._load_locale("assets/lang/ru.txt")

        next_screen = MainScreen(stdscr, self.locale, self.images)
        # main loop
        while True:
            result: tuple[AppState, dict[Any, Any]] = next_screen.open()
            match (result[0]):
                case AppState.EXIT:
                    break
                case AppState.MAIN_SCREEN:
                    next_screen = MainScreen(stdscr, self.locale, self.images)
                case AppState.GAME_SCREEN:
                    next_screen = GameScreen(stdscr, self.locale, self.images)
                case AppState.WIN_SCREEN:
                    next_screen = GameWinScreen(stdscr, self.locale, self.images, result[1].get("message", " "))
                case AppState.LOSE_SCREEN:
                    next_screen = GameOverScreen(stdscr, self.locale, self.images, result[1].get("message", " "))
                case _:
                    raise ValueError()
