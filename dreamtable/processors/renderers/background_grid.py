import esper

from dreamtable.constants import PositionSpace
from dreamtable import components as c
from dreamtable.hal import HAL, Vec2


class BackgroundGridRenderer(esper.Processor):
    """Draws BackgroundGrids."""

    def process(self, hal: HAL) -> None:
        camera = self.world.context.cameras[PositionSpace.WORLD]
        screen = hal.get_screen_rect()
        for _, (grid, ext) in self.world.get_components(c.BackgroundGrid, c.Extent):
            step = ext.extent.x * camera.zoom
            if step >= grid.min_step:
                x = -camera.target.x * camera.zoom + screen.width / 2
                x %= step
                while x < screen.width:
                    hal.draw_line_width(
                        Vec2(x, 0).floored,
                        Vec2(x, screen.height).floored,
                        grid.line_width,
                        grid.color,
                    )
                    x += step

            step = ext.extent.y * camera.zoom
            if step >= grid.min_step:
                y = -camera.target.y * camera.zoom + screen.height / 2
                y %= step
                while y < screen.height:
                    hal.draw_line_width(
                        Vec2(0, y).floored,
                        Vec2(screen.width, y).floored,
                        grid.line_width,
                        grid.color,
                    )
                    y += step
