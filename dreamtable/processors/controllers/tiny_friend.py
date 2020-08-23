import math

import esper

from dreamtable import components as c
from dreamtable.constants import EPSILON
from dreamtable.hal import HAL, Color


# todo lots of vector-y cleanup here
# also the angle calculation is probably wrong
# also also, maybe a helper for angle-to-direction
# also also also, sprite_region needs to have a rect
class TinyFriendController(esper.Processor):
    def process(self, hal: HAL) -> None:
        for ent, (friend, vel, sel, spr) in self.world.get_components(
            c.TinyFriend, c.Velocity, c.Selectable, c.SpriteRegion
        ):
            spr.tint = (
                Color(64, 128, 255, 255) if sel.selected else Color(255, 255, 255, 255)
            )

            base_cell_x = friend.type * 4
            anim_cell_x = 0  # todo
            cell_x = base_cell_x + anim_cell_x

            if vel.velocity.magnitude > EPSILON:
                friend.angle = (
                    math.atan2(vel.velocity.y, vel.velocity.x) + math.pi
                ) / (2 * math.pi)

            # fmt: off
            cell_y = 1
            if friend.angle < 0.125:   cell_y = 1  # noqa
            elif friend.angle < 0.375: cell_y = 3  # noqa
            elif friend.angle < 0.625: cell_y = 2  # noqa
            elif friend.angle < 0.875: cell_y = 0  # noqa
            # fmt: on

            spr.x = cell_x * 16
            spr.y = cell_y * 16
