from enum import Enum, auto

EPSILON = 1e-5


# todo: these are really more like layers
# consider moving Position.space to Layer.layer
class PositionSpace(Enum):
    WORLD = auto()
    SCREEN = auto()


class SelectionType(Enum):
    NORMAL = auto()
    CREATE = auto()


class Tool(Enum):
    MOVE = auto()
    PENCIL = auto()
    DROPPER = auto()
    GRID = auto()
    CELLREF = auto()
    CELLREF_DROPPER = auto()
    EGG = auto()
