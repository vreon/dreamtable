import esper
from raylib.pyray import PyRay

from ..constants import Tool
from ..components import Position, Extent, Canvas, Image
from ..utils import point_rect_intersect


class DropperToolController(esper.Processor):
    def __init__(self) -> None:
        self.color = None

    def process(self, pyray: PyRay) -> None:
        context = self.world.context

        if context.tool != Tool.DROPPER:
            return

        mouse_pos_x = context.mouse_pos_x
        mouse_pos_y = context.mouse_pos_y

        context.color_dropper = (0, 0, 0, 0)

        for _, (pos, ext, canvas, img) in self.world.get_components(
            Position, Extent, Canvas, Image
        ):
            camera = self.world.context.cameras[pos.space]
            rect_tuple = (pos.x, pos.y, ext.width, ext.height)
            dropper_pos = pyray.get_screen_to_world_2d(
                (mouse_pos_x, mouse_pos_y), camera
            )

            if point_rect_intersect(dropper_pos.x, dropper_pos.y, *rect_tuple):
                x = int(dropper_pos.x - pos.x)
                y = int(dropper_pos.y - pos.y)
                context.color_dropper = pyray.get_image_data(img.image)[
                    y * img.image.width + x
                ]
                break

        if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
            self.world.context.color_primary = context.color_dropper
        if pyray.is_mouse_button_pressed(pyray.MOUSE_RIGHT_BUTTON):
            self.world.context.color_secondary = context.color_dropper
