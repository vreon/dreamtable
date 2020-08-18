import esper

from ..components import Canvas, Position, Extent, CellGrid
from ..constants import Tool


class GridToolRenderer(esper.Processor):
    def process(self, pyray):
        context = self.world.context

        if not context.tool == Tool.GRID:
            return

        theme = context.theme

        for ent, (canvas, pos, ext, cellgrid) in self.world.get_components(
            Canvas, Position, Extent, CellGrid
        ):
            camera = context.cameras[pos.space]

            pyray.begin_mode_2d(camera)

            cell_w = ext.width / cellgrid.x
            cell_h = ext.height / cellgrid.y

            if cell_w.is_integer() and cell_h.is_integer():
                text_color = theme.color_text_normal
                cell_dimensions = f"{int(cell_w)}x{int(cell_h)}"
            else:
                text_color = theme.color_text_error
                cell_dimensions = f"{cell_w:.2f}x{cell_h:.2f}"

            text_offset_x = 0
            text_offset_y = -8

            pyray.draw_text_ex(
                theme.font,
                str(f"{cellgrid.x}x{cellgrid.y} @ {cell_dimensions}"),
                (pos.x + text_offset_x, pos.y + text_offset_y),
                8,
                1,
                text_color,
            )

            pyray.end_mode_2d()
