import esper

from ..components import Image, Deletable


class ImageDeleteController(esper.Processor):
    """Unloads image (and texture) when the entity is deleted."""

    def process(self, pyray):
        for _, (img, del_) in self.world.get_components(Image, Deletable):
            if not del_.deleted:
                continue

            img.image_data = None

            if img.texture:
                pyray.unload_texture(img.texture)
                img.texture = None

            if img.image:
                pyray.unload_image(img.image)
                img.image = None
