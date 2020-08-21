import esper

from dreamtable import components as c
from dreamtable.hal import HAL


class FinalDeleteController(esper.Processor):
    """
    Delete any deleted Deletable. Immediately before this, other more specific
    deletion processors should run to release any allocated resources. (But don't
    delete the actual entity, that's this thing's job.)
    """

    def process(self, hal: HAL) -> None:
        for ent, del_ in self.world.get_component(c.Deletable):
            if del_.deleted:
                self.world.delete_entity(ent)
