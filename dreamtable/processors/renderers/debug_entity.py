import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.hal import HAL, Color
from dreamtable.geom import Vec2, Rect


class DebugEntityRenderer(esper.Processor):
    """Draws a basic spatial representation of the entity, for debugging."""

    def process(self, pyray: PyRay, hal: HAL) -> None:
        theme = self.world.context.theme

        for ent, (_, pos, ext) in self.world.get_components(
            c.DebugEntity, c.Position, c.Extent
        ):
            camera = self.world.context.cameras[pos.space]
            pyray.begin_mode_2d(camera)

            rect = Rect(pos.x, pos.y, ext.width, ext.height).floored
            color = Color(*theme.color_debug_magenta)

            hal.draw_rectangle_lines(rect, 1, color)

            outline_color = None

            for hov in self.world.try_component(ent, c.Hoverable):
                if hov.hovered:
                    outline_color = Color(*theme.color_thingy_hovered_outline)

            for sel in self.world.try_component(ent, c.Selectable):
                if sel.selected:
                    outline_color = Color(*theme.color_selection_normal_outline)

            if outline_color:
                hal.draw_rectangle_lines(rect.grown(1), 1, outline_color)

            for name in self.world.try_component(ent, c.Name):
                font_size = 8
                spacing = 1
                measurement = hal.measure_text(
                    theme.font, name.name, font_size, spacing
                )
                center = Vec2(pos.x + ext.width / 2, pos.y + ext.height / 2)
                text_pos = (center - measurement / 2).floored
                hal.draw_text(
                    theme.font, name.name, text_pos, font_size, spacing, color,
                )

            pyray.end_mode_2d()
