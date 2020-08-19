import esper
from raylib.pyray import PyRay

from dreamtable.utils import make_random_vector
from dreamtable import components as c


class WanderingController(esper.Processor):
    """Kick objects around a bit."""

    def process(self, pyray: PyRay) -> None:
        for _, (vel, jit) in self.world.get_components(c.Velocity, c.Wandering):
            jit.tick -= 1
            if jit.tick == 0:
                jit.tick = jit.interval
                vel.x, vel.y = make_random_vector(2)
                vel.x *= jit.force
                vel.y *= jit.force
