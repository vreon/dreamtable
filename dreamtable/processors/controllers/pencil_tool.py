from typing import Optional

import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL, MouseButton, Vec2


class PencilToolController(esper.Processor):
    def __init__(self) -> None:
        self.last_pos: Optional[Vec2] = None
        self.draw_color = None

    def process(self, hal: HAL) -> None:
        context = self.world.context
        if not context.tool == Tool.PENCIL:
            return

        if hal.is_mouse_button_released(
            MouseButton.LEFT
        ) or hal.is_mouse_button_released(MouseButton.RIGHT):
            self.draw_color = None

        any_hovered = False

        for ent, (canvas, pos, ext, img) in self.world.get_components(
            c.Canvas, c.Position, c.Extent, c.Image
        ):
            camera = context.cameras[pos.space]
            rect = c.rect(pos.position, ext.extent)
            pencil_pos = hal.get_screen_to_world(context.mouse_pos, camera)

            if pencil_pos not in rect:
                continue

            any_hovered = True

            if not self.draw_color:
                if hal.is_mouse_button_pressed(MouseButton.LEFT):
                    hal.clear_mouse_button_pressed(MouseButton.LEFT)
                    self.draw_color = context.color_primary
                elif hal.is_mouse_button_pressed(MouseButton.RIGHT):
                    hal.clear_mouse_button_pressed(MouseButton.RIGHT)
                    self.draw_color = context.color_secondary
                else:
                    continue

            if self.last_pos is None:
                self.last_pos = pencil_pos

            assert self.draw_color is not None

            hal.draw_image_line(
                img.image,
                (self.last_pos - pos.position).floored,
                (pencil_pos - pos.position).floored,
                self.draw_color,
            )
            self.last_pos = pencil_pos.copy()
            img.dirty = True

        if not any_hovered:
            self.last_pos = None
