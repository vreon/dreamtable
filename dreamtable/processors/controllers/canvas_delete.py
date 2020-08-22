import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class CanvasDeleteController(esper.Processor):
    """Unloads canvas image (and texture) when the entity is deleted."""

    def process(self, hal: HAL) -> None:
        for _, (_, img, del_) in self.world.get_components(
            c.Canvas, c.Image, c.Deletable
        ):
            if not del_.deleted:
                continue

            img.image_data = None

            if img.texture:
                hal.unload_texture(img.texture)
                img.texture = None

            if img.image:
                hal.unload_image(img.image)
                img.image = None
