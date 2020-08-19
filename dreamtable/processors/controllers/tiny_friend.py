import esper
import math
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import EPSILON


class TinyFriendController(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        for ent, (friend, vel, spr) in self.world.get_components(
            c.TinyFriend, c.Velocity, c.SpriteRegion
        ):
            base_cell_x = friend.type * 4
            anim_cell_x = 0  # todo
            cell_x = base_cell_x + anim_cell_x

            if abs(vel.x) > EPSILON and abs(vel.y) > EPSILON:
                friend.angle = (math.atan2(vel.y, vel.x) + math.pi) / (2 * math.pi)

            # fmt: off
            cell_y = 1
            if friend.angle < 0.125:   cell_y = 1  # noqa
            elif friend.angle < 0.375: cell_y = 3  # noqa
            elif friend.angle < 0.625: cell_y = 2  # noqa
            elif friend.angle < 0.875: cell_y = 0  # noqa
            # fmt: on

            spr.x = cell_x * 16
            spr.y = cell_y * 16
