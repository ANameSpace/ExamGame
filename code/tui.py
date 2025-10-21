import curses
from abc import ABC, abstractmethod
from enum import Enum
from time import sleep
from typing import Any

debug = True

class TextColor(Enum):
    DEFAULT = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    CYAN = 5
    MAGENTA = 6


class TUIObject(ABC):
    def __init__(self, y: int, x: int, y_size: int, x_size: int, color: TextColor = TextColor.DEFAULT):
        if y < 0 or x < 0:
            raise ValueError()

        self.y = y
        self.x = x
        self.y_size = y_size
        self.x_size = x_size

        self.color: int = 0
        self.set_color(color)

    def set_color(self, color: TextColor) -> None:
        if color is None:
            raise ValueError()
        self.color = curses.color_pair(color.value)

    @abstractmethod
    def pre_render(self, window: curses.window) -> None:
        ...

    def render(self, window: curses.window) -> None:
        self.pre_render(window)
        window.refresh()

    @abstractmethod
    def render_animation(self, window: curses.window, animation_id: int, animation_speed: float) -> None:
        ...


class TUIInteractiveObject(TUIObject, ABC):
    @abstractmethod
    def select(self, window: curses.window) -> Any:
        ...


class TUIModifer(ABC):
    @abstractmethod
    def apply_modifer(self, window: curses.window):
        ...


class Rectangle(TUIObject, TUIModifer):
    class RectangleAnimation(Enum):
        COMPRESS = 1

    def __init__(self, y: int, x: int, y_size: int, x_size: int, color: TextColor = TextColor.DEFAULT,
                 filler: str = "█", background: bool = False):
        if y_size < 3 or x_size < 3:
            raise ValueError()
        super().__init__(y, x, y_size, x_size, color)
        self.y_size -= 1
        self.x_size -= 1
        self.background = background

        self.filler = None
        self.set_filler(filler)

    def set_filler(self, filler: str) -> None:
        if not filler or len(filler) > 1:
            raise ValueError()
        self.filler = filler

    def pre_render(self, window: curses.window) -> None:
        line: str = self.filler * (self.x_size + 1)

        if self.background:
            for i in range(self.y + 1, self.y + self.y_size):
                window.addstr(i, self.x, line, self.color)
        else:
            window.addstr(self.y, self.x, line, self.color)
            window.addstr(self.y + self.y_size, self.x, line, self.color)
            #TODO
            if True:
                line: str = self.filler + (" " * (self.x_size - 1)) + self.filler
                for i in range(self.y + 1, self.y + self.y_size):
                    window.addstr(i, self.x, line, self.color)
            # else:
            #     for i in range(self.y + 1, self.y + self.y_size):
            #         window.addstr(i, self.x, self.filler, self.color)
            #         window.addstr(i, self.x + self.x_size, self.filler, self.color)

    def apply_modifer(self, window: curses.window):
        window.addstr(self.y, self.x, " ", self.color)
        window.addstr(self.y + self.y_size, self.x, " ", self.color)
        window.addstr(self.y, self.x + self.x_size, " ", self.color)
        window.addstr(self.y + self.y_size, self.x + self.x_size, " ", self.color)
        window.addstr(self.y + 1, self.x, self.filler * (self.x_size + 1))

    def render_animation(self, window: curses.window, animation_id: int, animation_speed: float) -> None:
        if animation_speed <= 0.0:
            raise ValueError()

        line: str = self.filler * (self.x_size + 1)
        max_index_y = self.y + self.y_size
        center_index_y = max_index_y // 2

        match animation_id:
            case self.RectangleAnimation.COMPRESS.value:
                if self.background:
                    for i in range(self.y, center_index_y):
                        window.addstr(i, 0, line)
                        window.addstr(max_index_y - i, 0, line)
                        window.refresh()
                        sleep(animation_speed)

                    window.addstr(center_index_y, 0, line)
                    if max_index_y % 2 != 0:
                        window.addstr(center_index_y + 1, 0, line)
                    window.refresh()
                else:
                    pass  # TODO
            case _:
                raise ValueError()


class TextField(TUIObject):
    class TextAlign(Enum):
        LEFT = -1
        CENTER = 0
        RIGHT = 1

    class TextAnimation(Enum):
        BASE = 1

    def __init__(self, y: int, x: int, y_size: int, x_size: int, color: TextColor = TextColor.DEFAULT, text: str = " ",
                 align: TextAlign = TextAlign.LEFT):
        super().__init__(y, x, y_size, x_size, color)
        self.text: str = ""
        self.set_text(text)
        self.align = None
        self.set_align(align)

        self.text_size = 0

    def set_text(self, text: str) -> None:
        if not text:
            raise ValueError()
        self.text = text

    def set_align(self, align: TextAlign) -> None:
        if not align:
            raise ValueError()
        self.align = align

    def _format_text(self) -> list[str]:
        lines: list[str] = list()
        text = self.text
        while len(text) > self.x_size and len(lines) <= self.y_size:
            for i in range(self.x_size - 1, 0, -1):
                symbol = text[i]
                if symbol == " ":
                    end_index = i
                    break
            else:
                end_index = self.x_size - 1
            lines.append(text[:end_index])
            text = text[end_index + 1:]
        else:
            lines.append(text)
        return lines

    def pre_render(self, window: curses.window) -> None:
        lines: list[str] = self._format_text()
        if len(lines) > self.y_size:
            lines = lines[:self.y_size]
        self.text_size = len(lines)

        match self.align:
            case self.TextAlign.LEFT:
                for i, line in enumerate(lines):
                    window.addstr(self.y + i, self.x, line, self.color)
            case self.TextAlign.CENTER:
                for i, line in enumerate(lines):
                    window.addstr(self.y + i, self.x + ((self.x_size - len(line)) // 2), line, self.color)
            case self.TextAlign.RIGHT:
                for i, line in enumerate(lines):
                    window.addstr(self.y + i, self.x + (self.x_size - len(line)), line, self.color)

    def render_animation(self, window: curses.window, animation_id: int, animation_speed: float) -> None:
        lines: list[str] = self._format_text()
        if len(lines) > self.y_size:
            lines = lines[:self.y_size]

        if debug:
            self.pre_render(window)
            window.refresh()
            return

        match animation_id:
            case self.TextAnimation.BASE.value:
                for i, line in enumerate(lines):
                    x_offset = 0
                    match self.align:
                        case self.TextAlign.CENTER:
                            x_offset = (self.x_size - len(line)) // 2
                        case self.TextAlign.RIGHT:
                            x_offset = self.x_size - len(line)
                    for j, symbol in enumerate(line):
                        window.addstr(self.y + i, self.x + x_offset + j, symbol, self.color)
                        window.refresh()
                        sleep(animation_speed)
            case _:
                raise ValueError()


class CheckBox(TUIObject):
    def __init__(self, y: int, x: int, y_size: int, x_size: int, status: bool = False
                 , true: str = "[x]", true_color: TextColor = TextColor.DEFAULT
                 , false: str = "[ ]", false_color: TextColor = TextColor.DEFAULT):
        if x_size > 1:
            raise ValueError()
        super().__init__(y, x, y_size, x_size)
        self.true: tuple[str, int] = ("", 0)
        self.false: tuple[str, int] = ("", 0)
        self.set_text(True, true, true_color)
        self.set_text(False, false, false_color)
        self.status = status

    def set_text(self, status: bool, text: str, color: TextColor = TextColor.DEFAULT) -> None:
        if not text or len(text) != self.x_size:
            raise ValueError()
        if status:
            self.true = (text, color.value)
        else:
            self.false = (text, color.value)

    def pre_render(self, window: curses.window) -> None:
        window.addstr(self.y, self.x, *(self.true if self.status else self.false))

    def render_animation(self, window: curses.window, animation_id: int, animation_speed: float) -> None:
        raise ValueError()


class Selector(TUIInteractiveObject):
    def __init__(self, y: int, x: int, y_size: int, x_size: int, variants: tuple[str, ...], step: int = 1,
                 color: TextColor = TextColor.DEFAULT, active_color: TextColor = TextColor.YELLOW):
        super().__init__(y, x, y_size, x_size, color)
        if variants is None or len(variants) == 0:
            raise ValueError()
        if step < 0:
            raise ValueError()
        self.variants: tuple[str, ...] = variants
        self.items: list[(CheckBox, TextField)] = list()
        self.step = step
        self.active_color_code: int = curses.color_pair(active_color.value)

    def pre_render(self, window: curses.window) -> None:
        self.items.clear()
        y_offset = 0
        for i, variant in enumerate(self.variants):
            checkbox = CheckBox(self.y + y_offset, self.x, 1, 1, true=">", false=" ")
            checkbox.pre_render(window)
            textfield = TextField(self.y + y_offset, self.x + 1, self.y_size - y_offset, self.x_size - 1, text=variant)
            textfield.pre_render(window)
            y_offset += textfield.text_size + self.step
            self.items.append((checkbox, textfield))

    def render_animation(self, window: curses.window, animation_id: int, animation_speed: float) -> None:
        raise ValueError()

    def select(self, window: curses.window) -> Any:
        current_index = 0
        max_index = len(self.items) - 1
        self.__set_active(0, True, window)
        window.refresh()
        curses.flushinp()
        while True:
            ch = window.getch()
            match ch:
                case curses.KEY_DOWN:
                    if current_index == max_index:
                        continue
                    self.__set_active(current_index, False, window)
                    current_index += 1
                    self.__set_active(current_index, True, window)
                    window.refresh()
                case curses.KEY_UP:
                    if current_index == 0:
                        continue
                    self.__set_active(current_index, False, window)
                    current_index -= 1
                    self.__set_active(current_index, True, window)
                    window.refresh()
                case curses.KEY_RIGHT | curses.KEY_ENTER | 10 | 13:
                    break

        return current_index

    def __set_active(self, index: int, status: bool, window: curses.window) -> None:
        checkbox: CheckBox = self.items[index][0]
        checkbox.status = status
        checkbox.pre_render(window)
        textfield: TextField = self.items[index][1]
        textfield.color = self.active_color_code if status else self.color
        textfield.pre_render(window)


class ASCIIImage(TUIObject):
    def __init__(self, y: int, x: int, data):
        super().__init__(y, x, 1, 1)
        self.pixels: tuple[tuple[str, ...], ...] = data[0]
        self.colors: tuple[tuple[int, ...], ...] = data[1]

    def pre_render(self, window: curses.window) -> None:
        for i, line in enumerate(self.pixels):
            for j, symbol in enumerate(line):
                try:
                    color = self.colors[i][j]
                except IndexError:
                    color = 0
                window.addstr(self.y + i, self.x + j, symbol, color)

    def render_animation(self, window: curses.window, animation_id: int, animation_speed: float) -> None:
        raise ValueError()
