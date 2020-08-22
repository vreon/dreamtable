import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL, MouseButton


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

            if hal.is_mouse_button_pressed(MouseButton.LEFT):
                canvas.cell_grid_always_visible = not canvas.cell_grid_always_visible

            cellgrid.x += context.mouse_wheel
            cellgrid.y += context.mouse_wheel
            cellgrid.x = max(cellgrid.x, 1)
            cellgrid.y = max(cellgrid.y, 1)

            # todo update cellrefs I guess

            hal.clear_mouse_wheel_move()
            context.mouse_wheel = 0
            break
