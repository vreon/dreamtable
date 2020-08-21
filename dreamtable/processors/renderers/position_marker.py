import esper

from dreamtable import components as c
from dreamtable.hal import HAL
from dreamtable.geom import Vec2


class PositionMarkerRenderer(esper.Processor):
    """Draws PositionMarkers."""

    def process(self, hal: HAL) -> None:
        theme = self.world.context.theme

        for _, (pos, mark) in self.world.get_components(c.Position, c.PositionMarker):
            camera = self.world.context.cameras[pos.space]
            hal.push_camera(camera)

            hal.draw_line(
                Vec2(pos.position.x - mark.size, pos.position.y).floored,
                Vec2(pos.position.x + mark.size, pos.position.y).floored,
                theme.color_position_marker,
            )
            hal.draw_line(
                Vec2(pos.position.x, pos.position.y - mark.size).floored,
                Vec2(pos.position.x, pos.position.y + mark.size).floored,
                theme.color_position_marker,
            )

            hal.pop_camera()
