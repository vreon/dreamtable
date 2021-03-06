import esper

from dreamtable import components as c
from dreamtable.constants import EPSILON
from dreamtable.hal import HAL, Key, MouseButton


class CameraController(esper.Processor):
    """Update cameras in response to events."""

    def process(self, hal: HAL) -> None:
        screen_size = hal.get_screen_size()
        mouse_delta = hal.get_mouse_delta()

        for _, cam in self.world.get_component(c.Camera):
            if cam.active:
                # pan
                if hal.is_mouse_button_down(MouseButton.MIDDLE):
                    cam.camera.target -= mouse_delta / cam.camera.zoom

                # smooth zoom
                if wheel_move := hal.get_mouse_wheel_move():
                    cam.zoom_velocity += cam.zoom_speed * wheel_move
                    hal.clear_mouse_wheel_move()

                # global hotkeys
                if hal.is_key_pressed(Key.HOME):
                    cam.camera.target.zero()
                if hal.is_key_pressed(Key.ONE):
                    cam.camera.zoom = 1
                if hal.is_key_pressed(Key.TWO):
                    cam.camera.zoom = 2
                if hal.is_key_pressed(Key.THREE):
                    cam.camera.zoom = 3
                if hal.is_key_pressed(Key.FOUR):
                    cam.camera.zoom = 4

            cam.camera.offset = screen_size / 2
            cam.camera.zoom += cam.zoom_velocity * cam.camera.zoom

            cam.zoom_velocity *= cam.zoom_friction
            if abs(cam.zoom_velocity) < EPSILON:
                cam.zoom_velocity = 0
