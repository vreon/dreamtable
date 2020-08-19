import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.utils import get_outline_rect


class DebugEntityRenderer(esper.Processor):
    """Draws a basic spatial representation of the entity, for debugging."""

    def process(self, pyray: PyRay) -> None:
        theme = self.world.context.theme

        for ent, (_, pos, ext) in self.world.get_components(
            c.DebugEntity, c.Position, c.Extent
        ):
            camera = self.world.context.cameras[pos.space]
            pyray.begin_mode_2d(camera)

            rect_tuple = int(pos.x), int(pos.y), int(ext.width), int(ext.height)
            rect = pyray.Rectangle(*rect_tuple)
            color = theme.color_debug_magenta

            pyray.draw_rectangle_lines_ex(rect, 1, color)

            outline_color = None
            outline_rect = pyray.Rectangle(*get_outline_rect(*rect_tuple))

            for hov in self.world.try_component(ent, c.Hoverable):
                if hov.hovered:
                    outline_color = theme.color_thingy_hovered_outline

            for sel in self.world.try_component(ent, c.Selectable):
                if sel.selected:
                    outline_color = theme.color_selection_normal_outline

            if outline_color:
                pyray.draw_rectangle_lines_ex(outline_rect, 1, outline_color)

            for name in self.world.try_component(ent, c.Name):
                font_size = 8
                spacing = 1
                measurement = pyray.measure_text_ex(
                    theme.font, name.name, font_size, spacing
                )
                x = (pos.x + ext.width / 2) - measurement.x / 2
                y = (pos.y + ext.height / 2) - measurement.y / 2
                pyray.draw_text_ex(
                    theme.font, name.name, (int(x), int(y)), font_size, spacing, color,
                )

            pyray.end_mode_2d()