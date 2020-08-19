import esper
from raylib.pyray import PyRay

from dreamtable.constants import Tool
from dreamtable.utils import get_outline_rect


class DropperToolRenderer(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        context = self.world.context

        if context.tool != Tool.DROPPER:
            return

        rect_tuple = (
            int(context.mouse_pos_x) + 16,
            int(context.mouse_pos_y) - 50,
            33,
            33,
        )
        rect = pyray.Rectangle(*rect_tuple)
        pyray.draw_rectangle_rec(rect, context.color_dropper)
        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(*get_outline_rect(*rect_tuple)), 1, (255, 255, 255, 255)
        )
