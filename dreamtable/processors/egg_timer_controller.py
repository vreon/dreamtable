import esper
from raylib.pyray import PyRay
import random

from .. import components as c


class EggTimerController(esper.Processor):
    def process(self, pyray: PyRay) -> None:
        for ent, egg in self.world.get_component(c.EggTimer):
            egg.time_left -= 1

            if egg.time_left <= 0:
                # todo spawn an effect
                self.world.remove_component(ent, c.EggTimer)
                self.world.add_component(ent, c.Name("A tiny friend"))
                self.world.add_component(ent, c.Velocity(friction=0.8))
                self.world.add_component(
                    ent, c.Wandering(force=random.random() * 3 + 1)
                )
                self.world.add_component(ent, c.TinyFriend(type=random.randint(0, 3)))
