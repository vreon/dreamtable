import esper

from ..components import Selectable, Deletable


class SelectableDeleteController(esper.Processor):
    """Mark any selected Deletables as deleted when Delete is pressed."""

    def process(self, pyray):
        if pyray.is_key_pressed(pyray.KEY_DELETE):
            for ent, (sel, del_) in self.world.get_components(Selectable, Deletable):
                if sel.selected:
                    del_.deleted = True
