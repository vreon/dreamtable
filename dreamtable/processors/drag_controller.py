import esper

from ..constants import Tool
from ..components import Position, Extent, Draggable
from ..utils import point_rect_intersect


class DragController(esper.Processor):
    def process(self, pyray):
        if not self.world.context.tool == Tool.MOVE:
            return

        mouse_pos_x = self.world.context.mouse_pos_x
        mouse_pos_y = self.world.context.mouse_pos_y

        for _, (pos, ext, drag) in self.world.get_components(
            Position, Extent, Draggable
        ):
            camera = self.world.context.cameras[pos.space]
            drag_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            if (
                not self.world.context.mouse_reserved
                and pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON)
                and point_rect_intersect(drag_pos.x, drag_pos.y, rect)
            ):
                self.world.context.mouse_reserved = True
                drag.dragging = True
                drag.offset_x = drag_pos.x - pos.x
                drag.offset_y = drag_pos.y - pos.y

            if drag.dragging:
                pos.x = drag_pos.x - drag.offset_x
                pos.y = drag_pos.y - drag.offset_y

                # todo snap to grid

            if pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON):
                self.world.context.mouse_reserved = False
                drag.dragging = False
                drag.offset_x = 0
                drag.offset_y = 0
