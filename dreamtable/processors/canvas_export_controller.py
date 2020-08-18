from datetime import datetime
import esper

from ..components import Canvas, Selectable, Image


class CanvasExportController(esper.Processor):
    """Export selected Canvas images to a directory"""

    def process(self, pyray):
        is_control_down = pyray.is_key_down(
            pyray.KEY_LEFT_CONTROL
        ) or pyray.is_key_down(pyray.KEY_RIGHT_CONTROL)

        if not (is_control_down and pyray.is_key_pressed(pyray.KEY_S)):
            return

        for _, (_, sel, img) in self.world.get_components(Canvas, Selectable, Image):
            if not sel.selected:
                continue

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = (
                f"save/thingy_{img.image.width}x{img.image.height}_{timestamp}.png"
            )
            pyray.export_image(img.image, filename)