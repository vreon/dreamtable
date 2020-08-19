import esper
from raylib.pyray import PyRay

from dreamtable import components as c


class SpriteRegionRenderer(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        context = self.world.context
        for ent, (pos, ext, spr, img) in self.world.get_components(
            c.Position, c.Extent, c.SpriteRegion, c.Image
        ):
            camera = context.cameras[pos.space]
            pyray.begin_mode_2d(camera)
            source_rect = pyray.Rectangle(
                int(spr.x), int(spr.y), int(ext.width), int(ext.height)
            )
            dest_pos = (int(pos.x), int(pos.y))
            pyray.draw_texture_rec(img.texture, source_rect, dest_pos, spr.tint)
            pyray.end_mode_2d()
