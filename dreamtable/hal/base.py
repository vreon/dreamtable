import esper
from dreamtable.hal.types import (
    FontHandle,
    ImageHandle,
    TextureHandle,
    Camera,
    Color,
    Key,
    MouseButton,
    TextureFormat,
)
from dreamtable.hal.geom import Vec2, Rect


class HAL:
    # Window and screen

    def init_window(self, width: int, height: int, title: str) -> None:
        raise NotImplementedError

    def get_screen_size(self) -> Vec2:
        raise NotImplementedError

    def get_screen_rect(self) -> Rect:
        raise NotImplementedError

    def set_clear_color(self, color: Color) -> None:
        raise NotImplementedError

    def push_camera(self, camera: Camera) -> None:
        raise NotImplementedError

    def pop_camera(self) -> None:
        raise NotImplementedError

    def get_screen_to_world(self, pos: Vec2, camera: Camera) -> Vec2:
        raise NotImplementedError

    # Resource loading / unloading

    def load_font(self, resource_path: str) -> FontHandle:
        raise NotImplementedError

    def load_image(self, resource_path: str) -> ImageHandle:
        raise NotImplementedError

    def load_texture_from_image(self, image_handle: ImageHandle) -> TextureHandle:
        raise NotImplementedError

    def unload_image(self, image_handle: ImageHandle) -> None:
        raise NotImplementedError

    def unload_texture(self, texture_handle: TextureHandle) -> None:
        raise NotImplementedError

    def gen_image_from_color(self, size: Vec2, color: Color) -> ImageHandle:
        raise NotImplementedError

    # Resource reading / writing

    def update_texture_from_image(
        self, texture_handle: TextureHandle, image_handle: ImageHandle
    ) -> None:
        raise NotImplementedError

    def set_image_format(
        self, image_handle: ImageHandle, format: TextureFormat
    ) -> None:
        raise NotImplementedError

    def draw_image_line(
        self, image_handle: ImageHandle, start: Vec2, end: Vec2, color: Color
    ) -> None:
        raise NotImplementedError

    def get_image_size(self, image_handle: ImageHandle) -> Vec2:
        raise NotImplementedError

    def get_image_color(self, image_handle: ImageHandle, pos: Vec2) -> Color:
        raise NotImplementedError

    def export_image(self, image_handle: ImageHandle, filename: str) -> None:
        raise NotImplementedError

    # Screen drawing

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
        raise NotImplementedError

    def draw_rectangle(self, rect: Rect, color: Color) -> None:
        raise NotImplementedError

    def draw_rectangle_lines(self, rect: Rect, thickness: int, color: Color) -> None:
        raise NotImplementedError

    def draw_line(self, start: Vec2, end: Vec2, color: Color) -> None:
        raise NotImplementedError

    def draw_line_width(
        self, start: Vec2, end: Vec2, width: float, color: Color
    ) -> None:
        raise NotImplementedError

    def draw_texture(
        self,
        texture_handle: TextureHandle,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        raise NotImplementedError

    def draw_texture_rect(
        self,
        texture_handle: TextureHandle,
        source_rect: Rect,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        raise NotImplementedError

    def measure_text(
        self, font: FontHandle, text: str, size: int, spacing: int
    ) -> Vec2:
        raise NotImplementedError

    # Keyboard

    def is_key_down(self, key: Key) -> bool:
        raise NotImplementedError

    def is_key_pressed(self, key: Key) -> bool:
        raise NotImplementedError

    def is_key_released(self, key: Key) -> bool:
        raise NotImplementedError

    def clear_key_pressed(self, key: Key) -> None:
        raise NotImplementedError

    def clear_key_released(self, key: Key) -> None:
        raise NotImplementedError

    # Mouse

    def is_mouse_button_down(self, mouse_button: MouseButton) -> bool:
        raise NotImplementedError

    def is_mouse_button_pressed(self, mouse_button: MouseButton) -> bool:
        raise NotImplementedError

    def is_mouse_button_released(self, mouse_button: MouseButton) -> bool:
        raise NotImplementedError

    def clear_mouse_button_pressed(self, mouse_button: MouseButton) -> None:
        raise NotImplementedError

    def clear_mouse_button_released(self, mouse_button: MouseButton) -> None:
        raise NotImplementedError

    def get_mouse_position(self) -> Vec2:
        raise NotImplementedError

    def get_mouse_wheel_move(self) -> float:
        raise NotImplementedError

    def clear_mouse_wheel_move(self) -> None:
        raise NotImplementedError

    # Main loop

    def run(self, world: esper.World) -> None:
        raise NotImplementedError
