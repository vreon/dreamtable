import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import SelectionType
from dreamtable.hal import HAL


class BoxSelectionRenderer(esper.Processor):
    """Draws selection regions."""

    def process(self, pyray: PyRay, hal: HAL) -> None:
        theme = self.world.context.theme

        for _, (pos, ext, sel) in self.world.get_components(
            c.Position, c.Extent, c.BoxSelection
        ):
            camera = self.world.context.cameras[pos.space]

            pyray.begin_mode_2d(camera)

            if sel.type == SelectionType.NORMAL:
                fill_color = theme.color_selection_normal_fill
                outline_color = theme.color_selection_normal_outline
                labeled = False
            elif sel.type == SelectionType.CREATE:
                fill_color = theme.color_selection_create_fill
                outline_color = theme.color_selection_create_outline
                labeled = True
            else:
                continue

            x, x_max = pos.x, pos.x + ext.width
            y, y_max = pos.y, pos.y + ext.height

            if x > x_max:
                x, x_max = x_max, x

            if y > y_max:
                y, y_max = y_max, y

            width = abs(x_max - x)
            height = abs(y_max - y)

            rect = pyray.Rectangle(int(x), int(y), int(width), int(height))
            pyray.draw_rectangle_rec(rect, fill_color.rgba)
            pyray.draw_rectangle_lines_ex(rect, 1, outline_color.rgba)

            if labeled:
                text_pos = pyray.Vector2(int(x), int(y) - 8)
                pyray.draw_text_ex(
                    theme.font,
                    f"{int(width)}x{int(height)}",
                    text_pos,
                    8,
                    1,
                    theme.color_text_normal.rgba,
                )

            pyray.end_mode_2d()
