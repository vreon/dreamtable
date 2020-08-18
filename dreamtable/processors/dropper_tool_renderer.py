import esper

from ..constants import Tool
from ..utils import get_outline_rect


class DropperToolRenderer(esper.Processor):
    def process(self, pyray):
        context = self.world.context

        if context.tool != Tool.DROPPER:
            return

        rect = pyray.Rectangle(
            int(context.mouse_pos_x) + 16, int(context.mouse_pos_y) - 50, 33, 33
        )
        pyray.draw_rectangle_rec(rect, context.color_dropper)
        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(*get_outline_rect(rect)), 1, (255, 255, 255, 255)
        )
