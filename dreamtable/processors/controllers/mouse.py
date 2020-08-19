import esper
from raylib.pyray import PyRay

from dreamtable.hal import HAL


class MouseController(esper.Processor):
    """Updates Mouse state."""

    def process(self, pyray: PyRay, hal: HAL) -> None:
        context = self.world.context
        context.mouse_wheel = pyray.get_mouse_wheel_move()
        mouse_pos = pyray.get_mouse_position()

        last_x = context.mouse_pos_x
        last_y = context.mouse_pos_y

        if last_x is None:
            last_x = mouse_pos.x
        if last_y is None:
            last_y = mouse_pos.y

        context.mouse_pos_x = mouse_pos.x
        context.mouse_pos_y = mouse_pos.y
        context.mouse_delta_x = context.mouse_pos_x - last_x
        context.mouse_delta_y = context.mouse_pos_y - last_y
