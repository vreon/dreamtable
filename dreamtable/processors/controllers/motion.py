import esper

from dreamtable import components as c
from dreamtable.constants import EPSILON
from dreamtable.hal import HAL


class MotionController(esper.Processor):
    """Newtonian dynamics."""

    def process(self, hal: HAL) -> None:
        for _, (vel, pos) in self.world.get_components(c.Velocity, c.Position):
            pos.position += vel.velocity
            vel.velocity *= vel.friction
            if abs(vel.velocity.x) < EPSILON:
                vel.velocity.x = 0
            if abs(vel.velocity.y) < EPSILON:
                vel.velocity.y = 0
