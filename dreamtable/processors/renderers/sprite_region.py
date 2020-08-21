import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class SpriteRegionRenderer(esper.Processor):
    def process(self, hal: HAL) -> None:
        context = self.world.context
        for ent, (pos, ext, spr, img) in self.world.get_components(
            c.Position, c.Extent, c.SpriteRegion, c.Image
        ):
            camera = context.cameras[pos.space]
            hal.push_camera(camera)
            hal.draw_texture_rect(
                img.texture, c.rect(spr, ext.extent), pos.position.floored
            )
            hal.pop_camera()
