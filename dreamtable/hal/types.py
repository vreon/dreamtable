from dataclasses import dataclass
from typing import Any, Tuple

import esper
from dreamtable.geom import Vec2, Rect


Font = Any
Image = Any


@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 0

    @property
    def rgba(self) -> Tuple[int, int, int, int]:
        return self.r, self.g, self.b, self.a


# todo: Camera should have a Transform2D instead of all this


@dataclass
class Camera:
    position: Vec2
    offset: Vec2
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
        position: Vec2,
        size: float,
        spacing: float,
        color: Color,
    ) -> None:
        raise NotImplementedError

    def draw_rectangle_lines(self, rect: Rect, thickness: int, color: Color) -> None:
        raise NotImplementedError

    def measure_text(self, font: Font, text: str, size: int, spacing: int) -> Vec2:
        raise NotImplementedError

    def main(self, world: esper.World) -> None:
        raise NotImplementedError
