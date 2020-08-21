import esper

from dreamtable import components as c
from dreamtable.hal import HAL
from dreamtable.geom import Vec2


class WanderingController(esper.Processor):
    """Kick objects around a bit."""

    def process(self, hal: HAL) -> None:
        for _, (vel, jit) in self.world.get_components(c.Velocity, c.Wandering):
            jit.tick -= 1
            if jit.tick == 0:
                jit.tick = jit.interval
                vel.x, vel.y = Vec2.random().xy
                vel.x *= jit.force
                vel.y *= jit.force
