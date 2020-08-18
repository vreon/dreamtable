import esper

from ..constants import Tool
from ..components import Canvas, Position, Extent, CellGrid
from ..utils import point_rect_intersect


class GridToolController(esper.Processor):
    def process(self, pyray):
        if not self.world.context.tool == Tool.GRID:
            return

        context = self.world.context
        mouse_pos_x = context.mouse_pos_x
        mouse_pos_y = context.mouse_pos_y

        for ent, (canvas, pos, ext, cellgrid) in self.world.get_components(
            Canvas, Position, Extent, CellGrid
        ):
            camera = self.world.context.cameras[pos.space]
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            mouse_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)

            if not point_rect_intersect(mouse_pos.x, mouse_pos.y, rect):
                continue

            cellgrid.x += context.mouse_wheel
            cellgrid.y += context.mouse_wheel
            cellgrid.x = max(cellgrid.x, 1)
            cellgrid.y = max(cellgrid.y, 1)

            # todo update cellrefs I guess

            context.mouse_wheel = 0
            break
