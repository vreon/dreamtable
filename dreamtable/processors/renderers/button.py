import esper
from raylib.pyray import PyRay

from dreamtable import components as c


class ButtonRenderer(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        theme = self.world.context.theme

        for ent, (pos, ext, btn) in self.world.get_components(
            c.Position, c.Extent, c.Button
        ):
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

            for hov in self.world.try_component(ent, c.Hoverable):
                if hov.hovered:
                    pyray.draw_rectangle_rec(rect, theme.color_button_hover_overlay)

            for img in self.world.try_component(ent, c.Image):
                if img.texture:
                    pyray.draw_texture(
                        img.texture, int(pos.x), int(pos.y), (255, 255, 255, 255)
                    )

            pyray.end_mode_2d()
