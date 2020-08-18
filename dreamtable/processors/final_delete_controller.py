import esper

from ..components import Deletable


class FinalDeleteController(esper.Processor):
    """
    Delete any deleted Deletable. Immediately before this, other more specific
    deletion processors should run to release any allocated resources. (But don't
    delete the actual entity, that's this thing's job.)
    """

    def process(self, pyray):
        for ent, del_ in self.world.get_component(Deletable):
            if del_.deleted:
                self.world.delete_entity(ent)
