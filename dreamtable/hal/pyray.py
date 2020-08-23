"""
A "hardware abstraction layer" that uses PyRay from python-raylib-cffi.
"""

from pathlib import Path
from typing import Any, Dict, Set, cast
from typing_extensions import Protocol
import uuid

from esper import World
from raylib.pyray import PyRay

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

PACKAGE_PATH = Path(__file__).parents[1]


def _vec2(v: Any) -> Vec2:
    return Vec2(v.x, v.y)


class PyRayFont(Protocol):
    pass


class PyRayImage(Protocol):
    format: TextureFormat
    width: int
    height: int


class PyRayTexture(Protocol):
    pass


class PyRayHAL(HAL):
    def __init__(self) -> None:
        self.pyray = PyRay()
        # self.pyray.set_config_flags(pyray.FLAG_WINDOW_RESIZABLE)
        self.pyray.set_target_fps(60)

        self._clear_color = Color(0, 0, 0, 255)
        self._fonts: Dict[FontHandle, PyRayFont] = {}
        self._images: Dict[ImageHandle, PyRayImage] = {}
        self._textures: Dict[TextureHandle, PyRayTexture] = {}

        self._cleared_key_presses: Set[Key] = set()
        self._cleared_key_releases: Set[Key] = set()
        self._cleared_mouse_button_presses: Set[MouseButton] = set()
        self._cleared_mouse_button_releases: Set[MouseButton] = set()
        self._is_mouse_wheel_move_cleared = False
        self._mouse_delta = Vec2()
        self._mouse_position = Vec2()

    # Window and screen

    def init_window(self, width: int, height: int, title: str) -> None:
        self.pyray.init_window(width, height, title)

    def get_screen_size(self) -> Vec2:
        return Vec2(self.pyray.get_screen_width(), self.pyray.get_screen_height())

    def get_screen_rect(self) -> Rect:
        return Rect.from_size(
            self.pyray.get_screen_width(), self.pyray.get_screen_height()
        )

    def set_clear_color(self, color: Color) -> None:
        self._clear_color = color

    def push_camera(self, camera: Camera) -> None:
        camera_2d = self.pyray.Camera2D(
            camera.offset.xy, camera.target.xy, camera.rotation, camera.zoom
        )
        self.pyray.begin_mode_2d(camera_2d)

    def pop_camera(self) -> None:
        self.pyray.end_mode_2d()

    def get_screen_to_world(self, pos: Vec2, camera: Camera) -> Vec2:
        camera_2d = self.pyray.Camera2D(
            camera.offset.xy, camera.target.xy, camera.rotation, camera.zoom
        )
        world_pos = self.pyray.get_screen_to_world_2d(pos.xy, camera_2d)
        return Vec2(world_pos.x, world_pos.y)

    # Resource loading / unloading

    # todo: whoops, these aren't idempotent
    # duplicate will clobber already-loaded resources
    # if we share the resmap, how do we know when to free? reference counting?
    def load_font(self, resource_path: str) -> FontHandle:
        if not resource_path.startswith("res://"):
            raise ValueError("Invalid resource path")
        path = PACKAGE_PATH / "resources" / resource_path[6:]
        self._fonts[resource_path] = self.pyray.load_font(str(path))
        return resource_path

    def load_image(self, resource_path: str) -> ImageHandle:
        if not resource_path.startswith("res://"):
            raise ValueError("Invalid resource path")
        path = PACKAGE_PATH / "resources" / resource_path[6:]
        self._images[resource_path] = self.pyray.load_image(str(path))
        self.set_image_format(resource_path, TextureFormat.UNCOMPRESSED_R8G8B8A8)
        return resource_path

    def load_texture_from_image(self, image_handle: ImageHandle) -> TextureHandle:
        self._textures[image_handle] = self.pyray.load_texture_from_image(
            self._images[image_handle]
        )
        return image_handle

    def unload_image(self, image_handle: ImageHandle) -> None:
        self.pyray.unload_image(self._images[image_handle])
        del self._images[image_handle]

    def unload_texture(self, texture_handle: TextureHandle) -> None:
        self.pyray.unload_texture(self._textures[texture_handle])
        del self._textures[texture_handle]

    def gen_image_from_color(self, size: Vec2, color: Color) -> ImageHandle:
        image_handle = str(uuid.uuid4())
        self._images[image_handle] = self.pyray.gen_image_color(
            int(size.x), int(size.y), color.rgba
        )
        return image_handle

    # Resource reading / writing

    def update_texture_from_image(
        self, texture_handle: TextureHandle, image_handle: ImageHandle
    ) -> None:
        self.pyray.update_texture(
            self._textures[texture_handle],
            self.pyray.get_image_data(self._images[image_handle]),
        )

    def set_image_format(
        self, image_handle: ImageHandle, format: TextureFormat
    ) -> None:
        image = self._images[image_handle]
        if image.format != format.value:
            self.pyray.image_format(
                self.pyray.pointer(self._images[image_handle]), format.value
            )

    # NOTE: PyRay.draw_image_line is broken on my machine, so this
    # is a reimplementation
    def draw_image_line(
        self, image_handle: ImageHandle, start: Vec2, end: Vec2, color: Color
    ) -> None:
        image_ptr = self.pyray.pointer(self._images[image_handle])
        x1 = int(start.x)
        y1 = int(start.y)
        x2 = int(end.x)
        y2 = int(end.y)

        dx = abs(x2 - x1)
        sx = 1 if x1 < x2 else -1
        dy = -abs(y2 - y1)
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.pyray.image_draw_pixel(image_ptr, x1, y1, color.rgba)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    def get_image_size(self, image_handle: ImageHandle) -> Vec2:
        image = self._images[image_handle]
        return Vec2(image.width, image.height)

    def get_image_color(self, image_handle: ImageHandle, pos: Vec2) -> Color:
        image = self._images[image_handle]
        color = self.pyray.get_image_data(image)[image.width * int(pos.y) + int(pos.x)]
        return Color(color.r, color.g, color.b, color.a)

    def export_image(self, image_handle: ImageHandle, filename: str) -> None:
        self.pyray.export_image(self._images[image_handle], filename)

    # Screen drawing

    def draw_text(
        self,
        font: FontHandle,
        text: str,
        position: Vec2,
        size: float,
        spacing: float,
        color: Color,
    ) -> None:
        self.pyray.draw_text_ex(
            self._fonts[font], text, position.xy, size, spacing, color.rgba
        )

    def draw_rectangle(self, rect: Rect, color: Color) -> None:
        self.pyray.draw_rectangle_rec(rect.xywh, color.rgba)

    def draw_rectangle_lines(self, rect: Rect, thickness: int, color: Color) -> None:
        self.pyray.draw_rectangle_lines_ex(rect.xywh, thickness, color.rgba)

    def draw_line(self, start: Vec2, end: Vec2, color: Color) -> None:
        self.pyray.draw_line_v(start.xy, end.xy, color.rgba)

    def draw_line_width(
        self, start: Vec2, end: Vec2, width: float, color: Color
    ) -> None:
        self.pyray.draw_line_ex(start.xy, end.xy, width, color.rgba)

    def draw_texture(
        self,
        texture_handle: TextureHandle,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        self.pyray.draw_texture_v(self._textures[texture_handle], pos.xy, tint.rgba)

    def draw_texture_rect(
        self,
        texture_handle: TextureHandle,
        source_rect: Rect,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        self.pyray.draw_texture_rec(
            self._textures[texture_handle], source_rect.xywh, pos.xy, tint.rgba
        )

    def measure_text(
        self, font: FontHandle, text: str, size: int, spacing: int
    ) -> Vec2:
        return _vec2(self.pyray.measure_text_ex(self._fonts[font], text, size, spacing))

    # Keyboard

    def is_key_down(self, key: Key) -> bool:
        return cast(bool, self.pyray.is_key_down(key.value))

    def is_key_pressed(self, key: Key) -> bool:
        if key in self._cleared_key_presses:
            return False
        return cast(bool, self.pyray.is_key_pressed(key.value))

    def is_key_released(self, key: Key) -> bool:
        if key in self._cleared_key_releases:
            return False
        return cast(bool, self.pyray.is_key_released(key.value))

    def clear_key_pressed(self, key: Key) -> None:
        self._cleared_key_presses.add(key)

    def clear_key_releases(self, key: Key) -> None:
        self._cleared_key_releases.add(key)

    # Mouse

    def is_mouse_button_down(self, mouse_button: MouseButton) -> bool:
        return cast(bool, self.pyray.is_mouse_button_down(mouse_button.value))

    def is_mouse_button_pressed(self, mouse_button: MouseButton) -> bool:
        if mouse_button in self._cleared_mouse_button_presses:
            return False
        return cast(bool, self.pyray.is_mouse_button_pressed(mouse_button.value))

    def is_mouse_button_released(self, mouse_button: MouseButton) -> bool:
        if mouse_button in self._cleared_mouse_button_releases:
            return False
        return cast(bool, self.pyray.is_mouse_button_released(mouse_button.value))

    def clear_mouse_button_pressed(self, mouse_button: MouseButton) -> None:
        self._cleared_mouse_button_presses.add(mouse_button)

    def clear_mouse_button_released(self, mouse_button: MouseButton) -> None:
        self._cleared_mouse_button_releases.add(mouse_button)

    def get_mouse_position(self) -> Vec2:
        return self._mouse_position.copy()

    def get_mouse_delta(self) -> Vec2:
        return self._mouse_delta.copy()

    def get_mouse_wheel_move(self) -> float:
        if self._is_mouse_wheel_move_cleared:
            return 0
        return cast(float, self.pyray.get_mouse_wheel_move())

    def clear_mouse_wheel_move(self) -> None:
        self._is_mouse_wheel_move_cleared = True

    def _reset_cleared_inputs(self) -> None:
        self._is_mouse_wheel_move_cleared = False
        self._cleared_key_presses.clear()
        self._cleared_key_releases.clear()
        self._cleared_mouse_button_presses.clear()
        self._cleared_mouse_button_releases.clear()

    def _update_mouse(self) -> None:
        last_mouse_position = self._mouse_position.copy()
        self._mouse_position = _vec2(self.pyray.get_mouse_position())
        self._mouse_delta = self._mouse_position - last_mouse_position

    def run(self, world: World) -> None:
        while not self.pyray.window_should_close():
            self._reset_cleared_inputs()
            self._update_mouse()
            self.pyray.begin_drawing()
            self.pyray.clear_background(self._clear_color.rgba)
            world.process(self)
            self.pyray.end_drawing()
        self.pyray.close_window()
