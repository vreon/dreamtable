"""
A "hardware abstraction layer" that uses PyRay from python-raylib-cffi.
"""

from pathlib import Path
from typing import Any, Dict

from esper import World
from raylib.pyray import PyRay

from .types import HAL, Color, Font, Image, Vector2D

PACKAGE_PATH = Path(__file__).parents[1]


class PyRayHAL(HAL):
    def __init__(self) -> None:
        self.pyray = PyRay()
        # self.pyray.set_config_flags(pyray.FLAG_WINDOW_RESIZABLE)
        self.pyray.set_target_fps(60)

        self._clear_color = Color(0, 0, 0, 255)
        self._fonts: Dict[Font, Any] = {}
        self._images: Dict[Image, Any] = {}

    def init_window(self, width: int, height: int, title: str) -> None:
        self.pyray.init_window(width, height, title)

    def load_font(self, resource_path: Font) -> None:
        if not resource_path.startswith("res://"):
            raise ValueError("Invalid resource path")
        path = PACKAGE_PATH / "resources" / resource_path[6:]
        self._fonts[resource_path] = self.pyray.load_font(str(path))

    def load_image(self, resource_path: Image) -> None:
        if not resource_path.startswith("res://"):
            raise ValueError("Invalid resource path")
        path = PACKAGE_PATH / "resources" / resource_path[6:]
        self._images[resource_path] = self.pyray.load_image(str(path))

    def set_clear_color(self, color: Color) -> None:
        self._clear_color = color

    def draw_text(
        self,
        font: Font,
        text: str,
        position: Vector2D,
        size: float,
        spacing: float,
        color: Color,
    ) -> None:
        self.pyray.draw_text_ex(
            self._fonts[font], text, position.tuple, size, spacing, color.tuple()
        )

    def measure_text(self, font: Font, text: str, size: int, spacing: int) -> Vector2D:
        m = self.pyray.measure_text_ex(self._fonts[font], text, size, spacing)
        return Vector2D(m.x, m.y)

    def main(self, world: World) -> None:
        while not self.pyray.window_should_close():
            self.pyray.begin_drawing()
            self.pyray.clear_background(self._clear_color.tuple())
            world.process(self.pyray, self)  # todo rm pyray
            self.pyray.end_drawing()

        self.pyray.close_window()
