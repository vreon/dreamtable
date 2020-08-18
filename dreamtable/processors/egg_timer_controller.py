import esper
import random

from ..components import EggTimer, Name, Velocity, Wandering, TinyFriend


class EggTimerController(esper.Processor):
    def process(self, pyray):
        for ent, egg in self.world.get_component(EggTimer):
            egg.time_left -= 1

            if egg.time_left <= 0:
                # todo spawn an effect
                self.world.remove_component(ent, EggTimer)
                self.world.add_component(ent, Name("A tiny friend"))
                self.world.add_component(ent, Velocity(friction=0.8))
                self.world.add_component(ent, Wandering(force=random.random() * 3 + 1))
                self.world.add_component(ent, TinyFriend(type=random.randint(0, 3)))
