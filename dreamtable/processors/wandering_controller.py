import esper

from ..utils import make_random_vector
from ..components import Velocity, Wandering


class WanderingController(esper.Processor):
    """Kick objects around a bit."""

    def process(self, pyray):
        for _, (vel, jit) in self.world.get_components(Velocity, Wandering):
            jit.tick -= 1
            if jit.tick == 0:
                jit.tick = jit.interval
                vel.x, vel.y = make_random_vector(2)
                vel.x *= jit.force
                vel.y *= jit.force
