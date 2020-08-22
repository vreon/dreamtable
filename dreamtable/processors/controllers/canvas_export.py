from datetime import datetime

import esper

from dreamtable import components as c
from dreamtable.hal import HAL, Key


class CanvasExportController(esper.Processor):
    """Export selected Canvas images to a directory"""

    def process(self, hal: HAL) -> None:
        is_control_down = hal.is_key_down(Key.LEFT_CONTROL) or hal.is_key_down(
            Key.RIGHT_CONTROL
        )

        if not (is_control_down and hal.is_key_pressed(Key.S)):
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
            hal.export_image(img.image, filename)
