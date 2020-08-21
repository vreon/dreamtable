import random

import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class EggTimerController(esper.Processor):
    def process(self, hal: HAL) -> None:
        for ent, egg in self.world.get_component(c.EggTimer):
            egg.time_left -= 1

            if egg.time_left <= 0:
                # todo spawn an effect
                self.world.remove_component(ent, c.EggTimer)
                for component in [
                    c.Name("A tiny friend"),
                    c.Velocity(friction=0.8),
                    c.Wandering(force=random.uniform(1, 4)),
                    c.TinyFriend(type=random.randint(0, 3)),
                ]:
                    self.world.add_component(ent, component)
