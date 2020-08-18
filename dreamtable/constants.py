from enum import Enum


EPSILON = 1e-5


# todo: these are really more like layers
# consider moving Position.space to Layer.layer
class PositionSpace(Enum):
    WORLD = 1
    SCREEN = 2


class SelectionType(Enum):
    NORMAL = 1
    CREATE = 2


class Tool(Enum):
    MOVE = 1
    PENCIL = 2
    DROPPER = 3
    GRID = 4
    CELLREF = 5
    CELLREF_DROPPER = 6
    EGG = 7
