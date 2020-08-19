from datetime import datetime

import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.hal import HAL


class CanvasExportController(esper.Processor):
    """Export selected Canvas images to a directory"""

    def process(self, pyray: PyRay, hal: HAL) -> None:
        is_control_down = pyray.is_key_down(
            pyray.KEY_LEFT_CONTROL
        ) or pyray.is_key_down(pyray.KEY_RIGHT_CONTROL)

        if not (is_control_down and pyray.is_key_pressed(pyray.KEY_S)):
            return

        for _, (_, sel, img) in self.world.get_components(
            c.Canvas, c.Selectable, c.Image
        ):
            if not sel.selected:
                continue

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = (
                f"save/thingy_{img.image.width}x{img.image.height}_{timestamp}.png"
            )
            pyray.export_image(img.image, filename)
