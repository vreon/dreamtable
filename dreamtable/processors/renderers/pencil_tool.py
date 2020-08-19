import esper
from raylib.pyray import PyRay

from dreamtable.constants import Tool
from dreamtable.utils import get_outline_rect


class PencilToolRenderer(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        context = self.world.context

        if context.tool not in (Tool.PENCIL, Tool.DROPPER):
            return

        mouse_pos_x = context.mouse_pos_x
        mouse_pos_y = context.mouse_pos_y

        rect_tuple = (int(mouse_pos_x) + 16, int(mouse_pos_y) - 16, 16, 16)
        rect = pyray.Rectangle(*rect_tuple)
        pyray.draw_rectangle_rec(rect, context.color_primary)
        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(*get_outline_rect(*rect_tuple)), 1, (255, 255, 255, 255)
        )

        rect_tuple = (int(mouse_pos_x) + 33, int(mouse_pos_y) - 16, 16, 16)
        rect = pyray.Rectangle(*rect_tuple)
        pyray.draw_rectangle_rec(rect, context.color_secondary)
        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(*get_outline_rect(*rect_tuple)), 1, (255, 255, 255, 255)
        )
