import esper
from ..components import Position, PositionMarker


class PositionMarkerRenderer(esper.Processor):
    """Draws PositionMarkers."""

    def process(self, pyray):
        theme = self.world.context.theme

        for _, (pos, mark) in self.world.get_components(Position, PositionMarker):
            camera = self.world.context.cameras[pos.space]
            pyray.begin_mode_2d(camera)

            pyray.draw_line_v(
                (int(pos.x - mark.size), int(pos.y)),
                (int(pos.x + mark.size), int(pos.y)),
                theme.color_position_marker,
            )
            pyray.draw_line_v(
                (int(pos.x), int(pos.y - mark.size)),
                (int(pos.x), int(pos.y + mark.size)),
                theme.color_position_marker,
            )

            pyray.end_mode_2d()