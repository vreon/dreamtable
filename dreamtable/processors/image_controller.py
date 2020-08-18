import esper

from ..components import Image, Canvas, Extent


class ImageController(esper.Processor):
    """Load images, create textures, and keep them in sync."""

    def process(self, pyray):
        for ent, img in self.world.get_component(Image):
            if not img.image and img.filename:
                img.image = pyray.load_image(img.filename)

                image_format = pyray.UNCOMPRESSED_R8G8B8A8  # default apparently
                if img.image.format != image_format:
                    pyray.image_format(pyray.pointer(img.image), image_format)

                img.image_data = pyray.get_image_data(img.image)

                for (_, ext) in self.world.try_components(ent, Canvas, Extent):
                    ext.width = img.image.width
                    ext.height = img.image.height

            if not img.texture:
                img.texture = pyray.load_texture_from_image(img.image)

            if img.texture and img.dirty:
                img.image_data = pyray.get_image_data(img.image)
                pyray.update_texture(img.texture, img.image_data)
                img.dirty = False
