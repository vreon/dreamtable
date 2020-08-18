import esper

from ..components import Position, Extent, Pressable
from ..utils import point_rect_intersect


class PressController(esper.Processor):
    def process(self, pyray):
        mouse_pos_x = self.world.context.mouse_pos_x
        mouse_pos_y = self.world.context.mouse_pos_y

        for ent, (pos, ext, press) in self.world.get_components(
            Position, Extent, Pressable
        ):
            camera = self.world.context.cameras[pos.space]
            press_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            press.pressed = False

            if (
                not self.world.context.mouse_reserved
                and pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON)
                and point_rect_intersect(press_pos.x, press_pos.y, rect)
            ):
                press.pressed = True
                press.down = True

            if pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON):
                press.down = False
