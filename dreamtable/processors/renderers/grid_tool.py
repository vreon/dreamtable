import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL, Vec2


class GridToolRenderer(esper.Processor):
    def process(self, hal: HAL) -> None:
        context = self.world.context

        if not context.tool == Tool.GRID:
            return

        theme = context.theme

        for ent, (canvas, pos, ext, cellgrid) in self.world.get_components(
            c.Canvas, c.Position, c.Extent, c.CellGrid
        ):
            camera = context.cameras[pos.space]
            hal.push_camera(camera)

            cell_w = ext.extent.x / cellgrid.x
            cell_h = ext.extent.y / cellgrid.y

            if cell_w.is_integer() and cell_h.is_integer():
                text_color = theme.color_text_normal
                cell_dimensions = f"{int(cell_w)}x{int(cell_h)}"
            else:
                text_color = theme.color_text_error
                cell_dimensions = f"{cell_w:.2f}x{cell_h:.2f}"

            hal.draw_text(
                theme.font,
                str(f"{cellgrid.x}x{cellgrid.y} @ {cell_dimensions}"),
                pos.position + Vec2(0, -8),
                8,
                1,
                text_color,
            )

            hal.pop_camera()
