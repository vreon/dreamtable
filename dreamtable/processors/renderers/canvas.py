import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.utils import get_outline_rect
from dreamtable.hal import HAL


class CanvasRenderer(esper.Processor):
    """Draws Canvases and their images."""

    def process(self, pyray: PyRay, hal: HAL) -> None:
        theme = self.world.context.theme

        for ent, (canvas, pos, ext) in self.world.get_components(
            c.Canvas, c.Position, c.Extent
        ):
            camera = self.world.context.cameras[pos.space]

            pyray.begin_mode_2d(camera)

            # draw texture if it has an image
            # it always should, but who knows.
            for img in self.world.try_component(ent, c.Image):
                if not img.texture:
                    continue
                pyray.draw_texture(
                    img.texture, int(pos.x), int(pos.y), (255, 255, 255, 255)
                )

            outline_color = theme.color_thingy_outline
            for hov in self.world.try_component(ent, c.Hoverable):
                if hov.hovered:
                    outline_color = theme.color_thingy_hovered_outline
            for sel in self.world.try_component(ent, c.Selectable):
                if sel.selected:
                    outline_color = theme.color_thingy_selected_outline

            rect_tuple = (int(pos.x), int(pos.y), int(ext.width), int(ext.height))
            outline_rect = pyray.Rectangle(*get_outline_rect(*rect_tuple))
            pyray.draw_rectangle_lines_ex(outline_rect, 1, outline_color)

            # todo: draw ref'd cells
            # for cell_y, cell_ref_row in enumerate(self.cell_refs):
            #     for cell_x, cell_ref in enumerate(cell_ref_row):
            #         if not cell_ref:
            #             continue

            #         source, source_cell_x, source_cell_y = cell_ref

            #         # draw refs as samples from source
            #         pyray.draw_texture_pro(
            #             source.texture,
            #             pyray.Rectangle(
            #                 int(source.w * source_cell_x / source.cells_x),
            #                 int(source.h * source_cell_y / source.cells_y),
            #                 int(source.w / source.cells_x),
            #                 int(source.h / source.cells_y),
            #             ),
            #             pyray.Rectangle(
            #                 self.x + int(self.w * cell_x / self.cells_x),
            #                 self.y + int(self.h * cell_y / self.cells_y),
            #                 int(self.w / self.cells_x),
            #                 int(self.h / self.cells_y),
            #             ),
            #             pyray.Vector2(0, 0),
            #             0,
            #             (255, 255, 255, 255),
            #         )

            # Draw the c.CellGrid, if this c.Canvas has one
            for cells in self.world.try_component(ent, c.CellGrid):
                if (
                    self.world.context.tool != Tool.GRID
                    and not canvas.cell_grid_always_visible
                ):
                    continue

                cell_grid_color = theme.color_grid_cells_subtle
                if (
                    self.world.context.tool == Tool.GRID
                    and canvas.cell_grid_always_visible
                ):
                    cell_grid_color = theme.color_grid_cells_obvious

                if cells.x > 1:
                    for ix in range(1, cells.x):
                        x = pos.x + ix / cells.x * ext.width
                        pyray.draw_line(
                            int(x),
                            int(pos.y),
                            int(x),
                            int(pos.y + ext.height),
                            cell_grid_color,
                        )

                if cells.y > 1:
                    for iy in range(1, cells.y):
                        y = pos.y + iy / cells.y * ext.height
                        pyray.draw_line(
                            int(pos.x),
                            int(y),
                            int(pos.x + ext.width),
                            int(y),
                            cell_grid_color,
                        )

            pyray.end_mode_2d()
