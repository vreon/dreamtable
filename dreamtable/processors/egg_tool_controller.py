import esper
from raylib.pyray import PyRay
from pathlib import Path
import random

from ..components import (
    Name,
    Position,
    Extent,
    Draggable,
    Hoverable,
    Selectable,
    Deletable,
    EggTimer,
    Image,
    SpriteRegion,
)
from ..constants import Tool, PositionSpace


pkg_path = Path(__file__).parent.parent


class EggToolController(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        if not self.world.context.tool == Tool.EGG:
            return

        context = self.world.context
        mouse_pos_x = context.mouse_pos_x
        mouse_pos_y = context.mouse_pos_y
        camera = context.cameras[PositionSpace.WORLD]
        click_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)

        if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
            # todo lots of duplicate loading of images/textures
            # should share these somehow / unload them on exit!
            self.world.create_entity(
                Name("Mystery egg"),
                Position(click_pos.x - 8, click_pos.y - 12),
                Extent(16, 16),
                Draggable(),
                Hoverable(),
                Selectable(),
                Deletable(),
                EggTimer(time_left=random.randint(200, 500)),
                Image(filename=str(pkg_path / "resources/sprites/16x16babies.png")),
                SpriteRegion(88, 65),
            )
