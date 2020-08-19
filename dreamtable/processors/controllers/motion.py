import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import EPSILON


class MotionController(esper.Processor):
    """Newtonian dynamics."""

    def process(self, pyray: PyRay) -> None:
        for _, (vel, pos) in self.world.get_components(c.Velocity, c.Position):
            pos.x += vel.x
            pos.y += vel.y
            vel.x *= vel.friction
            vel.y *= vel.friction
            if abs(vel.x) < EPSILON:
                vel.x = 0
            if abs(vel.y) < EPSILON:
                vel.y = 0
