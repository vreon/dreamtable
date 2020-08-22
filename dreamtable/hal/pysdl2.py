"""
A "hardware abstraction layer" that uses PySDL2.
"""

from typing import Dict

import esper

# from dreamtable.hal.base import HAL
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
from dreamtable.hal.debug import DebugHAL

import sdl2
import sdl2.ext
import sdl2.sdlgfx

import uuid


def _sdl2_color(c: Color) -> sdl2.ext.Color:
    return sdl2.ext.Color(c.r, c.g, c.b, c.a)


def _transformed_rect(rect: Rect, camera: Camera) -> Rect:
    rect = rect.copy()
    rect.x = (rect.x - camera.target.x) * camera.zoom + camera.offset.x
    rect.y = (rect.y - camera.target.y) * camera.zoom + camera.offset.y
    rect.width *= camera.zoom
    rect.height *= camera.zoom
    return rect


def _transformed_vec2(vec2: Vec2, camera: Camera) -> Vec2:
    vec2 = vec2.copy()
    vec2.x = (vec2.x - camera.target.x) * camera.zoom + camera.offset.x
    vec2.y = (vec2.y - camera.target.y) * camera.zoom + camera.offset.y
    return vec2


def _untransformed_vec2(vec2: Vec2, camera: Camera) -> Vec2:
    vec2 = vec2.copy()
    vec2.x = (vec2.x - camera.offset.x) / camera.zoom + camera.target.x
    vec2.y = (vec2.y - camera.offset.y) / camera.zoom + camera.target.y
    return vec2


SDL_BUTTON_TO_MOUSEBUTTON = {
    sdl2.SDL_BUTTON_LEFT: MouseButton.LEFT,
    sdl2.SDL_BUTTON_RIGHT: MouseButton.RIGHT,
    sdl2.SDL_BUTTON_MIDDLE: MouseButton.MIDDLE,
}

SDL_KEYCODE_TO_KEY = {
    # todo lots more
    sdl2.SDLK_a: Key.A,
    sdl2.SDLK_b: Key.B,
    sdl2.SDLK_c: Key.C,
    sdl2.SDLK_d: Key.D,
    sdl2.SDLK_e: Key.E,
    sdl2.SDLK_f: Key.F,
    sdl2.SDLK_g: Key.G,
    sdl2.SDLK_h: Key.H,
    sdl2.SDLK_i: Key.I,
    sdl2.SDLK_j: Key.J,
    sdl2.SDLK_k: Key.K,
    sdl2.SDLK_l: Key.L,
    sdl2.SDLK_m: Key.M,
    sdl2.SDLK_n: Key.N,
    sdl2.SDLK_o: Key.O,
    sdl2.SDLK_p: Key.P,
    sdl2.SDLK_q: Key.Q,
    sdl2.SDLK_r: Key.R,
    sdl2.SDLK_s: Key.S,
    sdl2.SDLK_t: Key.T,
    sdl2.SDLK_u: Key.U,
    sdl2.SDLK_v: Key.V,
    sdl2.SDLK_w: Key.W,
    sdl2.SDLK_x: Key.X,
    sdl2.SDLK_y: Key.Y,
    sdl2.SDLK_z: Key.Z,
}


class PySDL2HAL(DebugHAL):
    def __init__(self) -> None:
        self._clear_color = Color(0, 0, 0, 255)
        self._camera = Camera()
        self._mouse_position = Vec2()
        self._mouse_wheel_move = 0
        self._is_mouse_button_down: Dict[MouseButton, bool] = {}
        self._is_mouse_button_pressed: Dict[MouseButton, bool] = {}
        self._is_mouse_button_released: Dict[MouseButton, bool] = {}
        self._is_key_down: Dict[Key, bool] = {}
        self._is_key_pressed: Dict[Key, bool] = {}
        self._is_key_released: Dict[Key, bool] = {}

    def init_window(self, width: int, height: int, title: str) -> None:
        sdl2.ext.init()
        self.window = sdl2.ext.Window(title, size=(width, height))
        self.window.show()

        renderflags = (
            sdl2.render.SDL_RENDERER_ACCELERATED | sdl2.render.SDL_RENDERER_PRESENTVSYNC
        )
        self.context = sdl2.ext.Renderer(self.window, flags=renderflags)

    def load_font(self, resource_path: str) -> FontHandle:
        return str(uuid.uuid4())

    def load_image(self, resource_path: str) -> ImageHandle:
        return str(uuid.uuid4())

    def load_texture_from_image(self, image_handle: ImageHandle) -> TextureHandle:
        return str(uuid.uuid4())

    def set_image_format(
        self, image_handle: ImageHandle, format: TextureFormat
    ) -> None:
        pass

    def gen_image_from_color(self, size: Vec2, color: Color) -> ImageHandle:
        return str(uuid.uuid4())

    def draw_image_line(
        self, image_handle: ImageHandle, start: Vec2, end: Vec2, color: Color
    ) -> None:
        pass

    def get_image_size(self, image_handle: ImageHandle) -> Vec2:
        return Vec2()

    def get_image_color(self, image_handle: ImageHandle, pos: Vec2) -> Color:
        return Color()

    def update_texture_from_image(
        self, texture_handle: TextureHandle, image_handle: ImageHandle
    ) -> None:
        pass

    def export_image(self, image_handle: ImageHandle, filename: str) -> None:
        pass

    def unload_image(self, image_handle: ImageHandle) -> None:
        pass

    def unload_texture(self, texture_handle: TextureHandle) -> None:
        pass

    def push_camera(self, camera: Camera) -> None:
        self._camera = camera

    def pop_camera(self) -> None:
        self._camera = Camera()

    def get_screen_to_world(self, pos: Vec2, camera: Camera) -> Vec2:
        return _untransformed_vec2(pos, camera)

    def set_clear_color(self, color: Color) -> None:
        self._clear_color = color

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
        pass

    def draw_rectangle(self, rect: Rect, color: Color) -> None:
        rect = _transformed_rect(rect, self._camera)
        sdl2.sdlgfx.boxRGBA(
            self.context.sdlrenderer,
            int(rect.x),
            int(rect.y),
            int(rect.right),
            int(rect.bottom),
            color.r,
            color.g,
            color.b,
            color.a,
        )

    def draw_rectangle_lines(self, rect: Rect, thickness: int, color: Color) -> None:
        # todo thiccness
        rect = _transformed_rect(rect, self._camera)
        sdl2.sdlgfx.rectangleRGBA(
            self.context.sdlrenderer,
            int(rect.x),
            int(rect.y),
            int(rect.right),
            int(rect.bottom),
            color.r,
            color.g,
            color.b,
            color.a,
        )

    def draw_line(self, start: Vec2, end: Vec2, color: Color) -> None:
        start = _transformed_vec2(start, self._camera)
        end = _transformed_vec2(end, self._camera)
        sdl2.sdlgfx.lineRGBA(
            self.context.sdlrenderer,
            int(start.x),
            int(start.y),
            int(end.x),
            int(end.y),
            color.r,
            color.g,
            color.b,
            color.a,
        )

    def draw_line_width(
        self, start: Vec2, end: Vec2, width: float, color: Color
    ) -> None:
        start = _transformed_vec2(start, self._camera)
        end = _transformed_vec2(end, self._camera)
        sdl2.sdlgfx.thickLineRGBA(
            self.context.sdlrenderer,
            int(start.x),
            int(start.y),
            int(end.x),
            int(end.y),
            int(width),
            color.r,
            color.g,
            color.b,
            color.a,
        )

    def draw_texture(
        self,
        texture_handle: TextureHandle,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        pass

    def draw_texture_rect(
        self,
        texture_handle: TextureHandle,
        source_rect: Rect,
        pos: Vec2,
        tint: Color = Color(255, 255, 255, 255),
    ) -> None:
        pass

    def measure_text(
        self, font: FontHandle, text: str, size: int, spacing: int
    ) -> Vec2:
        return Vec2()

    def get_mouse_position(self) -> Vec2:
        return self._mouse_position.copy()

    def get_mouse_wheel_move(self) -> float:
        return self._mouse_wheel_move

    def get_screen_size(self) -> Vec2:
        return Vec2(self.window.size[0], self.window.size[1])

    def get_screen_rect(self) -> Rect:
        return Rect(0, 0, self.window.size[0], self.window.size[1])

    def is_key_pressed(self, key: Key) -> bool:
        return self._is_key_pressed.get(key, False)

    def is_key_down(self, key: Key) -> bool:
        return self._is_key_down.get(key, False)

    # todo: is_key_released needs to be added to base lol

    def is_mouse_button_down(self, mouse_button: MouseButton) -> bool:
        return self._is_mouse_button_down.get(mouse_button, False)

    def is_mouse_button_pressed(self, mouse_button: MouseButton) -> bool:
        return self._is_mouse_button_pressed.get(mouse_button, False)

    def is_mouse_button_released(self, mouse_button: MouseButton) -> bool:
        return self._is_mouse_button_released.get(mouse_button, False)

    def _reset_frame_inputs(self) -> None:
        self._mouse_wheel_move = 0
        for button in MouseButton:
            self._is_mouse_button_pressed[button] = False
            self._is_mouse_button_released[button] = False
        for key in Key:
            self._is_key_pressed[key] = False
            self._is_key_released[key] = False

    def run(self, world: esper.World) -> None:
        running = True
        while running:
            self._reset_frame_inputs()

            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    self._mouse_position.x = event.motion.x
                    self._mouse_position.y = event.motion.y
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse_button = SDL_BUTTON_TO_MOUSEBUTTON[event.button.button]
                    self._is_mouse_button_down[mouse_button] = True
                    self._is_mouse_button_pressed[mouse_button] = True
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    mouse_button = SDL_BUTTON_TO_MOUSEBUTTON[event.button.button]
                    self._is_mouse_button_down[mouse_button] = False
                    self._is_mouse_button_released[mouse_button] = True
                elif event.type == sdl2.SDL_MOUSEWHEEL:
                    self._mouse_wheel_move = event.wheel.y
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = SDL_KEYCODE_TO_KEY.get(event.key.keysym.sym)
                    if key is None:
                        continue
                    self._is_key_down[key] = True
                    self._is_key_pressed[key] = True
                elif event.type == sdl2.SDL_KEYUP:
                    key = SDL_KEYCODE_TO_KEY.get(event.key.keysym.sym)
                    if key is None:
                        continue
                    self._is_key_down[key] = False
                    self._is_key_released[key] = True

            self.context.clear(_sdl2_color(self._clear_color))
            world.process(self)
            self.context.present()

        sdl2.ext.quit()
