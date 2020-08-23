import esper

from dreamtable.constants import Tool
from dreamtable.hal import HAL, Color, Vec2, Rect


class PencilToolRenderer(esper.Processor):
    def process(self, hal: HAL) -> None:
        context = self.world.context

        if context.tool not in (Tool.PENCIL, Tool.DROPPER):
            return

        mouse_pos = hal.get_mouse_position()

        pos = (mouse_pos + Vec2(16, -16)).floored
        rect = Rect(pos.x, pos.y, 16, 16)
        hal.draw_rectangle(rect, context.color_primary)
        hal.draw_rectangle_lines(rect.grown(1), 1, Color(255, 255, 255, 255))

        pos = (mouse_pos + Vec2(33, -16)).floored
        rect = Rect(pos.x, pos.y, 16, 16)
        hal.draw_rectangle(rect, context.color_secondary)
        hal.draw_rectangle_lines(rect.grown(1), 1, Color(255, 255, 255, 255))
