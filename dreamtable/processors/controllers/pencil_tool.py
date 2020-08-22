from typing import Optional

import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL, MouseButton, Vec2


class PencilToolController(esper.Processor):
    def __init__(self) -> None:
        self.last_pos: Optional[Vec2] = None
        self.drawing = False

    def process(self, hal: HAL) -> None:
        context = self.world.context
        if not context.tool == Tool.PENCIL:
            return

        for ent, (canvas, pos, ext, img) in self.world.get_components(
            c.Canvas, c.Position, c.Extent, c.Image
        ):
            camera = context.cameras[pos.space]
            rect = c.rect(pos.position, ext.extent)
            pencil_pos = hal.get_screen_to_world(context.mouse_pos, camera)

            mouse_button_down = False
            if hal.is_mouse_button_down(MouseButton.LEFT):
                mouse_button_down = True
                color = context.color_primary
            elif hal.is_mouse_button_down(MouseButton.RIGHT):
                mouse_button_down = True
                color = context.color_secondary

            if (
                (self.drawing or not context.mouse_reserved)
                and mouse_button_down
                and pencil_pos in rect
            ):
                context.mouse_reserved = True
                self.drawing = True

                if self.last_pos is None:
                    self.last_pos = pencil_pos

                hal.draw_image_line(
                    img.image,
                    (self.last_pos - pos.position).floored,
                    (pencil_pos - pos.position).floored,
                    color,
                )
                self.last_pos = pencil_pos.copy()
                img.dirty = True

            if hal.is_mouse_button_released(
                MouseButton.LEFT
            ) or hal.is_mouse_button_released(MouseButton.RIGHT):
                context.mouse_reserved = False
                self.drawing = False
                self.last_pos = None
