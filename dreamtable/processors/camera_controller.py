import esper
from raylib.pyray import PyRay

from ..components import Camera
from ..constants import EPSILON


class CameraController(esper.Processor):
    """Update cameras in response to events."""

    def process(self, pyray: PyRay) -> None:
        screen_width = pyray.get_screen_width()
        screen_height = pyray.get_screen_height()

        context = self.world.context
        mouse_delta_x = context.mouse_delta_x
        mouse_delta_y = context.mouse_delta_y

        for _, cam in self.world.get_component(Camera):
            if cam.active:
                # pan
                if pyray.is_mouse_button_down(pyray.MOUSE_MIDDLE_BUTTON):
                    cam.camera_2d.target.x -= mouse_delta_x / cam.camera_2d.zoom
                    cam.camera_2d.target.y -= mouse_delta_y / cam.camera_2d.zoom

                # smooth zoom
                if context.mouse_wheel:
                    cam.zoom_velocity += cam.zoom_speed * context.mouse_wheel
                    context.mouse_wheel = 0

                # global hotkeys
                if pyray.is_key_pressed(pyray.KEY_HOME):
                    cam.camera_2d.target = (0, 0)
                if pyray.is_key_pressed(pyray.KEY_ONE):
                    cam.camera_2d.zoom = 1
                if pyray.is_key_pressed(pyray.KEY_TWO):
                    cam.camera_2d.zoom = 2
                if pyray.is_key_pressed(pyray.KEY_THREE):
                    cam.camera_2d.zoom = 3
                if pyray.is_key_pressed(pyray.KEY_FOUR):
                    cam.camera_2d.zoom = 4

            cam.camera_2d.offset.x = screen_width / 2
            cam.camera_2d.offset.y = screen_height / 2

            cam.camera_2d.zoom += cam.zoom_velocity * cam.camera_2d.zoom
            cam.zoom_velocity *= cam.zoom_friction
            if abs(cam.zoom_velocity) < EPSILON:
                cam.zoom_velocity = 0
