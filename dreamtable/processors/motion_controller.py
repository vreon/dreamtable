import esper

from ..constants import EPSILON
from ..components import Velocity, Position


class MotionController(esper.Processor):
    """Newtonian dynamics."""

    def process(self, pyray):
        for _, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            vel.x *= vel.friction
            vel.y *= vel.friction
            if abs(vel.x) < EPSILON:
                vel.x = 0
            if abs(vel.y) < EPSILON:
                vel.y = 0
