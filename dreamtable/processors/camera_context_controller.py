import esper

from ..components import Camera
from ..constants import PositionSpace


class CameraContextController(esper.Processor):
    """Update the context with active cameras."""

    def process(self, pyray):
        for _, cam in self.world.get_component(Camera):
            if cam.active:
                # todo right now all Camera entities are in world space yikes
                self.world.context.cameras[PositionSpace.WORLD] = cam.camera_2d
