"""
A "hardware abstraction layer" with a fake implementation.
"""

import logging
import uuid

import esper

from dreamtable.hal.base import HAL
from dreamtable.hal.geom import Rect, Vec2
from dreamtable.hal.types import (
    Camera,
    Color,
    FontHandle,
    ImageHandle,
    Key,
    MouseButton,
    TextureFormat,
    TextureHandle,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class DebugHAL(HAL):
    def init_window(self, width: int, height: int, title: str) -> None:
        logger.debug(f"init_window({width=}, {height=}, {title=})")

    def load_font(self, resource_path: str) -> FontHandle:
        logger.debug(f"load_font({resource_path=})")
        return str(uuid.uuid4())

    def load_image(self, resource_path: str) -> ImageHandle:
        logger.debug(f"load_image({resource_path=})")
        return str(uuid.uuid4())

    def load_texture_from_image(self, image_handle: ImageHandle) -> TextureHandle:
        logger.debug(f"load_texture_from_image({image_handle=})")
        return str(uuid.uuid4())

    def set_image_format(
        self, image_handle: ImageHandle, format: TextureFormat
    ) -> None:
        logger.debug(f"set_image_format({image_handle=}, {format=})")

    def gen_image_from_color(self, size: Vec2, color: Color) -> ImageHandle:
        logger.debug(f"gen_image_from_color({size=}, {color=})")
        return str(uuid.uuid4())

    def draw_image_line(
        self, image_handle: ImageHandle, start: Vec2, end: Vec2, color: Color
    ) -> None:
        logger.debug(f"draw_image_line({image_handle=}, {start=}, {end=}, {color=})")

    def get_image_size(self, image_handle: ImageHandle) -> Vec2:
        logger.debug(f"get_image_size({image_handle=})")
        return Vec2()

    def get_image_color(self, image_handle: ImageHandle, pos: Vec2) -> Color:
        logger.debug(f"get_image_color({image_handle=}, {pos=})")
        return Color()

    def update_texture_from_image(
        self, texture_handle: TextureHandle, image_handle: ImageHandle
    ) -> None:
        logger.debug(f"update_texture_from_image({texture_handle=}, {image_handle=})")

    def export_image(self, image_handle: ImageHandle, filename: str) -> None:
        logger.debug(f"export_image({image_handle=}, {filename=})")

    def unload_image(self, image_handle: ImageHandle) -> None:
        logger.debug(f"unload_image({image_handle=})")

    def unload_texture(self, texture_handle: TextureHandle) -> None:
        logger.debug(f"unload_texture({texture_handle=})")

    def push_camera(self, camera: Camera) -> None:
        logger.debug(f"push_camera({camera=})")

    def pop_camera(self) -> None:
        logger.debug("pop_camera()")

    def get_screen_to_world(self, pos: Vec2, camera: Camera) -> Vec2:
        logger.debug(f"get_screen_to_world({pos=}, {camera=})")
        return Vec2()

    def set_clear_color(self, color: Color) -> None:
        logger.debug(f"set_clear_color({color=})")

    # todo reorder these: text, position, font, color, size=8, spacing=1
    def draw_text(
        self,
        font: FontHandle,
        text: str,
        position: Vec2,
        size: float,
        spacing: float,
        color: Color,
    ) -> None:
        logger.debug(
            f"draw_text({font=}, {text=}, {position=}, {size=}, {spacing=}, {color=}))"
        )

    def draw_rectangle(self, rect: Rect, color: Color) -> None:
        logger.debug(f"draw_rectangle({rect=}, {color=})")

    def draw_rectangle_lines(self, rect: Rect, thickness: int, color: Color) -> None:
        logger.debug(f"draw_rectangle_lines({rect=}, {thickness=}, {color=})")

    def draw_line(self, start: Vec2, end: Vec2, color: Color) -> None:
        logger.debug(f"draw_line({start=}, {end=}, {color=})")

    def draw_line_width(
        self, start: Vec2, end: Vec2, width: float, color: Color
    ) -> None:
        logger.debug(f"draw_line_width({start=}, {end=}, {width=}, {color=})")

    def draw_texture(
        self,
        texture_handle: TextureHandle,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        logger.debug(f"draw_texture({texture_handle=}, {pos=}, {tint=})")

    def draw_texture_rect(
        self,
        texture_handle: TextureHandle,
        source_rect: Rect,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        logger.debug(
            f"draw_texture_rect({texture_handle=}, {source_rect=}, {pos=}, {tint=})"
        )

    def measure_text(
        self, font: FontHandle, text: str, size: int, spacing: int
    ) -> Vec2:
        logger.debug(f"measure_text({font=}, {text=}, {size=}, {spacing=})")
        return Vec2()

    def get_mouse_position(self) -> Vec2:
        logger.debug("get_mouse_position()")
        return Vec2()

    def get_mouse_wheel_move(self) -> float:
        logger.debug("get_mouse_wheel_move()")
        return 0

    def get_screen_size(self) -> Vec2:
        logger.debug("get_screen_size()")
        return Vec2()

    def get_screen_rect(self) -> Rect:
        logger.debug("get_screen_rect()")
        return Rect()

    def is_key_pressed(self, key: Key) -> bool:
        logger.debug(f"is_key_pressed({key=})")
        return False

    def is_key_down(self, key: Key) -> bool:
        logger.debug(f"is_key_down({key=})")
        return False

    def is_mouse_button_down(self, mouse_button: MouseButton) -> bool:
        logger.debug(f"is_mouse_button_down({mouse_button=})")
        return False

    def is_mouse_button_pressed(self, mouse_button: MouseButton) -> bool:
        logger.debug(f"is_mouse_button_pressed({mouse_button=})")
        return False

    def is_mouse_button_released(self, mouse_button: MouseButton) -> bool:
        logger.debug(f"is_mouse_button_released({mouse_button=})")
        return False

    def run(self, world: esper.World) -> None:
        frame = 0
        try:
            while True:
                frame += 1
                logger.debug("-" * 80)
                logger.debug(f"frame {frame}")
                world.process(self)
        except KeyboardInterrupt:
            logger.debug("quit")
