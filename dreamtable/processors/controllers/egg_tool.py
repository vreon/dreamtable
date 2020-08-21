import random

import esper

from dreamtable import components as c
from dreamtable.constants import PositionSpace, Tool
from dreamtable.hal import HAL, MouseButton
from dreamtable.geom import Vec2


class EggToolController(esper.Processor):
    def process(self, hal: HAL) -> None:
        if not self.world.context.tool == Tool.EGG:
            return

        context = self.world.context
        camera = context.cameras[PositionSpace.WORLD]
        click_pos = hal.get_screen_to_world(context.mouse_pos, camera)

        if hal.is_mouse_button_pressed(MouseButton.LEFT):
            # todo lots of duplicate loading of images/textures
            # should share these somehow / unload them on exit!
            # can't currently share them because Image component manages lifecycle :|
            image = hal.load_image("res://sprites/16x16babies.png")
            self.world.create_entity(
                c.Name("Mystery egg"),
                c.Position(click_pos - Vec2(8, 12)),
                c.Extent(Vec2(16, 16)),
                c.Draggable(),
                c.Hoverable(),
                c.Selectable(),
                c.Deletable(),
                c.EggTimer(time_left=random.randint(200, 500)),
                c.Image(image),
                c.SpriteRegion(88, 65),
            )
