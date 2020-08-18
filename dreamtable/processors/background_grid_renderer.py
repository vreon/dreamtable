import esper

from ..constants import PositionSpace
from ..components import BackgroundGrid, Extent


class BackgroundGridRenderer(esper.Processor):
    """Draws BackgroundGrids."""

    def _draw_x(self, pyray, grid, camera, step, width, height):
        if step < grid.min_step:
            return

        x = -camera.target.x * camera.zoom + width / 2
        x %= step
        while x < width:
            pyray.draw_line_ex(
                (int(x), 0), (int(x), int(height)), grid.line_width, grid.color,
            )
            x += step

    def _draw_y(self, pyray, grid, camera, step, width, height):
        if step < grid.min_step:
            return

        y = -camera.target.y * camera.zoom + height / 2
        y %= step
        while y < height:
            pyray.draw_line_ex(
                (0, int(y)), (int(width), int(y)), grid.line_width, grid.color,
            )
            y += step

    def process(self, pyray):
        camera = self.world.context.cameras[PositionSpace.WORLD]
        screen_width = pyray.get_screen_width()
        screen_height = pyray.get_screen_height()
        for _, (grid, ext) in self.world.get_components(BackgroundGrid, Extent):
            self._draw_x(
                pyray,
                grid,
                camera,
                ext.width * camera.zoom,
                screen_width,
                screen_height,
            )
            self._draw_y(
                pyray,
                grid,
                camera,
                ext.height * camera.zoom,
                screen_width,
                screen_height,
            )
