import esper

from dreamtable.constants import Tool
from dreamtable import components as c
from dreamtable.hal import HAL, MouseButton, Color


class DropperToolController(esper.Processor):
    def process(self, hal: HAL) -> None:
        context = self.world.context

        if context.tool != Tool.DROPPER:
            return

        for _, (pos, ext, canvas, img) in self.world.get_components(
            c.Position, c.Extent, c.Canvas, c.Image
        ):
            camera = self.world.context.cameras[pos.space]
            rect = c.rect(pos.position, ext.extent)
            dropper_pos = hal.get_screen_to_world(hal.get_mouse_position(), camera)

            if dropper_pos in rect:
                context.color_dropper = hal.get_image_color(
                    img.image, dropper_pos - pos.position
                )
                break
        else:
            context.color_dropper = Color(0, 0, 0, 0)

        if hal.is_mouse_button_pressed(MouseButton.LEFT):
            hal.clear_mouse_button_pressed(MouseButton.LEFT)
            context.color_primary = context.color_dropper
        if hal.is_mouse_button_pressed(MouseButton.RIGHT):
            hal.clear_mouse_button_pressed(MouseButton.RIGHT)
            context.color_secondary = context.color_dropper
