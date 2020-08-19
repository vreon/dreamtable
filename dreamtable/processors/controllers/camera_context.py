import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import PositionSpace


class CameraContextController(esper.Processor):
    """Update the context with active cameras."""

    def process(self, pyray: PyRay) -> None:
        for _, cam in self.world.get_component(c.Camera):
            if cam.active:
                # todo right now all Camera entities are in world space yikes
                self.world.context.cameras[PositionSpace.WORLD] = cam.camera_2d
