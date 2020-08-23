import esper

from dreamtable.constants import Tool
from dreamtable.hal import HAL, Color, Vec2, Rect


class DropperToolRenderer(esper.Processor):
    def process(self, hal: HAL) -> None:
        context = self.world.context

        if context.tool != Tool.DROPPER:
            return

        pos = hal.get_mouse_position() + Vec2(16, -50)
        rect = Rect(pos.x, pos.y, 33, 33)
        hal.draw_rectangle(rect, context.color_dropper)
        hal.draw_rectangle_lines(rect.grown(1), 1, Color(255, 255, 255, 255))
