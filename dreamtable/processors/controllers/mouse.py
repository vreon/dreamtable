import esper

from dreamtable.hal import HAL


class MouseController(esper.Processor):
    """Updates global mouse state."""

    def process(self, hal: HAL) -> None:
        context = self.world.context

        mouse_pos = hal.get_mouse_position()
        last = context.mouse_pos
        context.mouse_pos = mouse_pos
        context.mouse_delta = mouse_pos - last

        context.mouse_wheel = hal.get_mouse_wheel_move()
