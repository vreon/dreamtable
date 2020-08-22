import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class ImageController(esper.Processor):
    """Load images, create textures, and keep them in sync."""

    def process(self, hal: HAL) -> None:
        for ent, img in self.world.get_component(c.Image):
            if not img.image and img.filename:
                img.image = hal.load_image(img.filename)

            if not img.texture:
                img.texture = hal.load_texture_from_image(img.image)

            if img.texture and img.dirty:
                hal.update_texture_from_image(img.texture, img.image)
                img.dirty = False
