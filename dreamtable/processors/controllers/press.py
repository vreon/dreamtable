import esper

from dreamtable import components as c
from dreamtable.hal import HAL, MouseButton


class PressController(esper.Processor):
    def process(self, hal: HAL) -> None:
        mouse_pos = self.world.context.mouse_pos

        for ent, (pos, ext, press) in self.world.get_components(
            c.Position, c.Extent, c.Pressable
        ):
            camera = self.world.context.cameras[pos.space]
            press_pos = hal.get_screen_to_world(mouse_pos, camera)
            rect = c.rect(pos.position, ext.extent)
            press.pressed = False

            if (
                not self.world.context.mouse_reserved
                and hal.is_mouse_button_pressed(MouseButton.LEFT)
                and press_pos in rect
            ):
                press.pressed = True
                press.down = True

            if hal.is_mouse_button_released(MouseButton.LEFT):
                press.down = False
