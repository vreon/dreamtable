import esper

from dreamtable import components as c
from dreamtable.hal import HAL, Key


class SelectableDeleteController(esper.Processor):
    """Mark any selected Deletables as deleted when Delete is pressed."""

    def process(self, hal: HAL) -> None:
        if hal.is_key_pressed(Key.DELETE):
            for ent, (sel, del_) in self.world.get_components(
                c.Selectable, c.Deletable
            ):
                if sel.selected:
                    del_.deleted = True
