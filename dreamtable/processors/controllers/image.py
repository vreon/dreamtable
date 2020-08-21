import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class ImageController(esper.Processor):
    """Load images, create textures, and keep them in sync."""

    def process(self, hal: HAL) -> None:
        for ent, img in self.world.get_component(c.Image):
            if not img.image and img.filename:
                img.image = hal.load_image(img.filename)
                img.image_data = hal.get_image_data(img.image)

            if not img.texture:
                img.texture = hal.load_texture_from_image(img.image)

            if img.texture and img.dirty:
                img.image_data = hal.get_image_data(img.image)
                hal.update_texture(img.texture, img.image_data)
                img.dirty = False
