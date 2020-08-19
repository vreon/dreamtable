import esper
from raylib.pyray import PyRay

from ..constants import PositionSpace
from .. import components as c


class BackgroundGridRenderer(esper.Processor):
    """Draws BackgroundGrids."""

    def process(self, pyray: PyRay) -> None:
        camera = self.world.context.cameras[PositionSpace.WORLD]
        screen_width = pyray.get_screen_width()
        screen_height = pyray.get_screen_height()
        for _, (grid, ext) in self.world.get_components(c.BackgroundGrid, c.Extent):
            step = ext.width * camera.zoom
            if step >= grid.min_step:
                x = -camera.target.x * camera.zoom + screen_width / 2
                x %= step
                while x < screen_width:
                    pyray.draw_line_ex(
                        (int(x), 0),
                        (int(x), int(screen_height)),
                        grid.line_width,
                        grid.color,
                    )
                    x += step

            step = ext.height * camera.zoom
            if step >= grid.min_step:
                y = -camera.target.y * camera.zoom + screen_height / 2
                y %= step
                while y < screen_height:
                    pyray.draw_line_ex(
                        (0, int(y)),
                        (int(screen_width), int(y)),
                        grid.line_width,
                        grid.color,
                    )
                    y += step
