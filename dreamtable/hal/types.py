from dataclasses import dataclass, astuple
from typing import Any, Tuple, cast

import esper
from vecrec import Vector as Vector2D, Rect  # noqa


Font = Any
Image = Any


@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 0

    def tuple(self) -> Tuple[int, int, int, int]:
        return cast(Tuple[int, int, int, int], astuple(self))


# todo: Camera should have a Transform2D instead of all this


@dataclass
class Camera:
    position: Vector2D
    offset: Vector2D
    rotation: float
    zoom: float


class HAL:
    def __init__(self) -> None:
        raise NotImplementedError

    def init_window(self, width: int, height: int, title: str) -> None:
        raise NotImplementedError

    def load_font(self, resource_path: Font) -> None:
        raise NotImplementedError

    def load_image(self, resource_path: Image) -> None:
        raise NotImplementedError

    def set_clear_color(self, color: Color) -> None:
        raise NotImplementedError

    def draw_text(
        self,
        font: Font,
        text: str,
        position: Vector2D,
        size: float,
        spacing: float,
        color: Color,
    ) -> None:
        raise NotImplementedError

    def measure_text(self, font: Font, text: str, size: int, spacing: int) -> Vector2D:
        raise NotImplementedError

    def main(self, world: esper.World) -> None:
        raise NotImplementedError
