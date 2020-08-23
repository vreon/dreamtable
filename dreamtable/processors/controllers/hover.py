import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class HoverController(esper.Processor):
    def process(self, hal: HAL) -> None:
        for _, (pos, ext, hov) in self.world.get_components(
            c.Position, c.Extent, c.Hoverable
        ):
            camera = self.world.context.cameras[pos.space]
            hover_pos = hal.get_screen_to_world(hal.get_mouse_position(), camera)
            hov.hovered = hover_pos in c.rect(pos.position, ext.extent)
