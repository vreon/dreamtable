import esper
from raylib.pyray import PyRay

from ..components import Position, Extent, Hoverable
from ..utils import point_rect_intersect


class HoverController(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        mouse_pos_x = self.world.context.mouse_pos_x
        mouse_pos_y = self.world.context.mouse_pos_y
        for _, (pos, ext, hov) in self.world.get_components(
            Position, Extent, Hoverable
        ):
            camera = self.world.context.cameras[pos.space]
            hover_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)
            hov.hovered = point_rect_intersect(
                hover_pos.x, hover_pos.y, pos.x, pos.y, ext.width, ext.height
            )
