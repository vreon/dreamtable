import random
from pathlib import Path

import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import PositionSpace, Tool
from dreamtable.hal import HAL

pkg_path = Path(__file__).parent.parent.parent  # todo lol


class EggToolController(esper.Processor):
    def process(self, pyray: PyRay, hal: HAL) -> None:
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
                c.Name("Mystery egg"),
                c.Position(click_pos.x - 8, click_pos.y - 12),
                c.Extent(16, 16),
                c.Draggable(),
                c.Hoverable(),
                c.Selectable(),
                c.Deletable(),
                c.EggTimer(time_left=random.randint(200, 500)),
                c.Image(filename=str(pkg_path / "resources/sprites/16x16babies.png")),
                c.SpriteRegion(88, 65),
            )
