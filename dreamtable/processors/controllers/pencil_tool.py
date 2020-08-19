import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.utils import draw_line, point_rect_intersect


class PencilToolController(esper.Processor):
    def __init__(self) -> None:
        self.last_pos_x = None
        self.last_pos_y = None
        self.drawing = False

    def process(self, pyray: PyRay) -> None:
        if not self.world.context.tool == Tool.PENCIL:
            return

        mouse_pos_x = self.world.context.mouse_pos_x
        mouse_pos_y = self.world.context.mouse_pos_y

        for ent, (canvas, pos, ext, img) in self.world.get_components(
            c.Canvas, c.Position, c.Extent, c.Image
        ):
            camera = self.world.context.cameras[pos.space]
            rect_tuple = (pos.x, pos.y, ext.width, ext.height)
            pencil_pos = pyray.get_screen_to_world_2d(
                (mouse_pos_x, mouse_pos_y), camera
            )

            mouse_button_down = False
            if pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON):
                mouse_button_down = True
                color = self.world.context.color_primary
            elif pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
                mouse_button_down = True
                color = self.world.context.color_secondary

            if (
                (self.drawing or not self.world.context.mouse_reserved)
                and mouse_button_down
                and point_rect_intersect(pencil_pos.x, pencil_pos.y, *rect_tuple)
            ):
                self.world.context.mouse_reserved = True
                self.drawing = True

                if self.last_pos_x is None:
                    self.last_pos_x = pencil_pos.x
                if self.last_pos_y is None:
                    self.last_pos_y = pencil_pos.y

                x1 = self.last_pos_x - pos.x
                y1 = self.last_pos_y - pos.y
                x2 = pencil_pos.x - pos.x
                y2 = pencil_pos.y - pos.y

                draw_line(
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2),
                    lambda x, y: pyray.image_draw_pixel(
                        pyray.pointer(img.image), x, y, color
                    ),
                )
                self.last_pos_x = pencil_pos.x
                self.last_pos_y = pencil_pos.y
                img.dirty = True

            if pyray.is_mouse_button_released(
                pyray.MOUSE_LEFT_BUTTON
            ) or pyray.is_mouse_button_released(pyray.MOUSE_RIGHT_BUTTON):
                self.world.context.mouse_reserved = False
                self.drawing = False
                self.last_pos_x = None
                self.last_pos_y = None
