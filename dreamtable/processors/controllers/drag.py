import esper

from dreamtable import components as c
from dreamtable.constants import Tool
from dreamtable.hal import HAL, MouseButton


class DragController(esper.Processor):
    def process(self, hal: HAL) -> None:
        if not self.world.context.tool == Tool.MOVE:
            return

        mouse_pos = self.world.context.mouse_pos

        for _, (pos, ext, drag) in self.world.get_components(
            c.Position, c.Extent, c.Draggable
        ):
            camera = self.world.context.cameras[pos.space]
            drag_pos = hal.get_screen_to_world(mouse_pos, camera)
            rect = c.rect(pos.position, ext.extent)
            if hal.is_mouse_button_pressed(MouseButton.LEFT) and drag_pos in rect:
                drag.dragging = True
                drag.offset = drag_pos - pos.position

            if drag.dragging:
                pos.position.assign((drag_pos - drag.offset).floored)

                # todo snap to grid

            if hal.is_mouse_button_released(MouseButton.LEFT):
                drag.dragging = False
                drag.offset = None
