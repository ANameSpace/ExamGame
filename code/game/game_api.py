from abc import ABC, abstractmethod

from code.tui import TextColor


class GameAPI(ABC):
    @abstractmethod
    def get_player(self) -> dict:
        ...

    @abstractmethod
    def get_actors(self) -> dict[id: str, tuple[str, TextColor]]:
        ...

    @abstractmethod
    def look(self, image_name: str) -> None:
        ...

    @abstractmethod
    def talk(self, actor: tuple[str, TextColor], text: str) -> None:
        ...

    @abstractmethod
    def think(self, actor: tuple[str, TextColor], text: str) -> None:
        ...

    @abstractmethod
    def do(self, actor: tuple[str, TextColor], text: str) -> None:
        ...

    @abstractmethod
    def phone(self, actor: tuple[str, TextColor], text: str) -> None:
        ...

    @abstractmethod
    def select(self, text: str, variants: tuple[str, ...]) -> int:
        ...