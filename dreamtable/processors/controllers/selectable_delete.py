import esper
from raylib.pyray import PyRay

from dreamtable import components as c


class SelectableDeleteController(esper.Processor):
    """Mark any selected Deletables as deleted when Delete is pressed."""

    def process(self, pyray: PyRay) -> None:
        if pyray.is_key_pressed(pyray.KEY_DELETE):
            for ent, (sel, del_) in self.world.get_components(
                c.Selectable, c.Deletable
            ):
                if sel.selected:
                    del_.deleted = True
