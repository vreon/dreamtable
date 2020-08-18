import esper

from ..components import Position, Extent, Button, Hoverable, Image


class ButtonRenderer(esper.Processor):
    def process(self, pyray):
        theme = self.world.context.theme

        for ent, (pos, ext, btn) in self.world.get_components(Position, Extent, Button):
            camera = self.world.context.cameras[pos.space]

            pyray.begin_mode_2d(camera)

            rect = pyray.Rectangle(
                int(pos.x), int(pos.y), int(ext.width), int(ext.height),
            )

            fill_color = theme.color_button_fill
            border_color = theme.color_button_border

            if btn.lit:
                fill_color = theme.color_button_lit_fill
                border_color = theme.color_button_lit_border

            pyray.draw_rectangle_rec(rect, fill_color)
            pyray.draw_rectangle_lines_ex(rect, 1, border_color)

            for hov in self.world.try_component(ent, Hoverable):
                if hov.hovered:
                    pyray.draw_rectangle_rec(rect, theme.color_button_hover_overlay)

            for img in self.world.try_component(ent, Image):
                if img.texture:
                    pyray.draw_texture(
                        img.texture, int(pos.x), int(pos.y), (255, 255, 255, 255)
                    )

            pyray.end_mode_2d()