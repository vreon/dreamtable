from typing import Optional

import esper

from dreamtable import components as c
from dreamtable.hal import HAL, Color


class DebugEntityRenderer(esper.Processor):
    """Draws a basic spatial representation of the entity, for debugging."""

    def process(self, hal: HAL) -> None:
        theme = self.world.context.theme

        for ent, (_, pos, ext) in self.world.get_components(
            c.DebugEntity, c.Position, c.Extent
        ):
            camera = self.world.context.cameras[pos.space]
            hal.push_camera(camera)

            rect = c.rect(pos.position, ext.extent)
            color = theme.color_debug_magenta

            hal.draw_rectangle_lines(rect.floored, 1, color)

            outline_color: Optional[Color] = None

            for hov in self.world.try_component(ent, c.Hoverable):
                if hov.hovered:
                    outline_color = theme.color_thingy_hovered_outline

            for sel in self.world.try_component(ent, c.Selectable):
                if sel.selected:
                    outline_color = theme.color_selection_normal_outline

            if outline_color:
                hal.draw_rectangle_lines(rect.grown(1), 1, outline_color)

            for name in self.world.try_component(ent, c.Name):
                size = 8
                spacing = 1
                measurement = hal.measure_text(theme.font, name.name, size, spacing)
                text_pos = rect.center - measurement / 2
                hal.draw_text(
                    theme.font, name.name, text_pos.floored, size, spacing, color,
                )

            hal.pop_camera()
