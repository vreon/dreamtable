import esper

from dreamtable import components as c
from dreamtable.constants import SelectionType
from dreamtable.hal import HAL, Rect, Vec2


class BoxSelectionRenderer(esper.Processor):
    """Draws selection regions."""

    def process(self, hal: HAL) -> None:
        theme = self.world.context.theme

        for _, (pos, ext, sel) in self.world.get_components(
            c.Position, c.Extent, c.BoxSelection
        ):
            camera = self.world.context.cameras[pos.space]

            hal.push_camera(camera)

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

            # todo this is just get_aabb
            x, x_max = pos.position.x, pos.position.x + ext.extent.x
            y, y_max = pos.position.y, pos.position.y + ext.extent.y

            if x > x_max:
                x, x_max = x_max, x

            if y > y_max:
                y, y_max = y_max, y

            width = x_max - x
            height = y_max - y

            rect = Rect(x, y, width, height).floored
            hal.draw_rectangle(rect, fill_color)
            hal.draw_rectangle_lines(rect, 1, outline_color)

            if labeled:
                text_pos = Vec2(x, y - 8)
                hal.draw_text(
                    theme.font,
                    f"{int(width)}x{int(height)}",
                    text_pos.floored,
                    size=8,
                    spacing=1,
                    color=theme.color_text_normal,
                )

            hal.pop_camera()
