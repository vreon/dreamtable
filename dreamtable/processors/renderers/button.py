import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class ButtonRenderer(esper.Processor):
    def process(self, hal: HAL) -> None:
        theme = self.world.context.theme

        for ent, (pos, ext, btn) in self.world.get_components(
            c.Position, c.Extent, c.Button
        ):
            camera = self.world.context.cameras[pos.space]

            hal.push_camera(camera)

            rect = c.rect(pos.position, ext.extent)

            fill_color = theme.color_button_fill
            border_color = theme.color_button_border

            if btn.lit:
                fill_color = theme.color_button_lit_fill
                border_color = theme.color_button_lit_border

            hal.draw_rectangle(rect, fill_color)
            hal.draw_rectangle_lines(rect, 1, border_color)

            for hov in self.world.try_component(ent, c.Hoverable):
                if hov.hovered:
                    hal.draw_rectangle(rect, theme.color_button_hover_overlay)

            for img in self.world.try_component(ent, c.Image):
                if img.texture:
                    hal.draw_texture(img.texture, pos.position)

            hal.pop_camera()
