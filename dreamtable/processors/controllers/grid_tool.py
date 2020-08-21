import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL


class GridToolController(esper.Processor):
    def process(self, hal: HAL) -> None:
        if not self.world.context.tool == Tool.GRID:
            return

        context = self.world.context

        for ent, (canvas, pos, ext, cellgrid) in self.world.get_components(
            c.Canvas, c.Position, c.Extent, c.CellGrid
        ):
            camera = self.world.context.cameras[pos.space]
            rect = c.rect(pos.position, ext.extent)
            mouse_world_pos = hal.get_screen_to_world(context.mouse_pos, camera)

            if mouse_world_pos not in rect:
                continue

            cellgrid.x += context.mouse_wheel
            cellgrid.y += context.mouse_wheel
            cellgrid.x = max(cellgrid.x, 1)
            cellgrid.y = max(cellgrid.y, 1)

            # todo update cellrefs I guess

            context.mouse_wheel = 0
            break
