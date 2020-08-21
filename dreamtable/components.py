from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Iterable, Optional
from typing_extensions import Protocol

from dreamtable.constants import PositionSpace, SelectionType, Tool
from dreamtable.geom import Vec2, Rect
from dreamtable.hal import (
    Camera as HALCamera,
    Color,
    FontHandle,
    ImageHandle,
    TextureHandle,
)


################################################################################
# Global data associated with the entire world
# Can be read or written to by processors


@dataclass
class WorldContext:
    theme: Theme

    # The currently active tool
    tool: Tool = Tool.MOVE

    # Depending on which tool is active, the user may be able to temporarily
    # switch to another tool by holding a key combination (e.g. PENCIL + Alt =
    # DROPPER). This attribute stores which tool we will return to when the key
    # combo is released.
    underlying_tool: Optional[Tool] = None

    color_primary: Color = Color(255, 255, 255, 255)
    color_secondary: Color = Color(0, 0, 0, 255)
    color_dropper: Color = Color(0, 0, 0, 0)

    # Just active cameras; kept in sync by a processor
    cameras: Mapping[PositionSpace, HALCamera] = field(default_factory=dict)

    snap: Vec2 = Vec2(8, 8)

    mouse_pos: Vec2 = field(default_factory=Vec2)
    mouse_delta: Vec2 = field(default_factory=Vec2)
    mouse_wheel: int = 0

    # todo this is janky af
    # it's used to stop propagation of mouse click events
    mouse_reserved: bool = False


@dataclass
class Theme:
    font: FontHandle
    color_background: Color = Color(9, 12, 17, 255)
    color_position_marker: Color = Color(164, 84, 30, 255)
    color_grid_cells_subtle: Color = Color(255, 255, 255, 32)
    color_grid_cells_obvious: Color = Color(255, 255, 255, 64)
    color_grid_minor: Color = Color(68, 93, 144, 16)
    color_grid_major: Color = Color(68, 93, 144, 32)
    color_text_normal: Color = Color(255, 255, 255, 255)
    color_text_error: Color = Color(164, 84, 30, 255)
    color_selection_create_outline: Color = Color(0, 255, 0, 128)
    color_selection_create_fill: Color = Color(0, 255, 0, 32)
    color_selection_normal_outline: Color = Color(68, 93, 144, 128)
    color_selection_normal_fill: Color = Color(68, 93, 144, 32)
    color_thingy_outline: Color = Color(68, 93, 144, 16)
    color_thingy_hovered_outline: Color = Color(68, 93, 144, 48)
    color_thingy_selected_outline: Color = Color(68, 93, 144, 128)
    color_debug_magenta: Color = Color(255, 0, 255, 255)
    color_button_fill: Color = Color(32, 32, 32, 255)
    color_button_border: Color = Color(64, 64, 64, 255)
    color_button_lit_fill: Color = Color(84, 30, 0, 255)
    color_button_lit_border: Color = Color(164, 84, 30, 255)
    color_button_hover_overlay: Color = Color(255, 255, 255, 32)


################################################################################
# Components


class XY(Protocol):
    x: float
    y: float


def rect(xy: XY, wh: XY) -> Rect:
    return Rect(xy.x, xy.y, wh.x, wh.y)


################################################################################
# Components


@dataclass
class Position:
    position: Vec2 = field(default_factory=Vec2)
    space: PositionSpace = PositionSpace.WORLD


@dataclass
class Extent:
    extent: Vec2 = field(default_factory=Vec2)


@dataclass
class Velocity:
    velocity: Vec2 = field(default_factory=Vec2)
    friction: float = 1.0


@dataclass
class Wandering:
    interval: int = 100
    tick: int = 100
    force: float = 5.0


@dataclass
class Name:
    name: str


@dataclass
class PositionMarker:
    size: float = 8.0


@dataclass
class CellGrid:
    x: int = 0
    y: int = 0


@dataclass
class BackgroundGrid:
    color: Color
    line_width: float = 2.0
    min_step: float = 4.0


@dataclass
class Camera:
    camera: HALCamera
    active: bool = False
    zoom_speed: float = 0.025
    zoom_velocity: float = 0
    zoom_friction: float = 0.85


@dataclass
class BoxSelection:
    type: SelectionType = SelectionType.NORMAL
    start_pos: Vec2 = field(default_factory=Vec2)


@dataclass
class Hoverable:
    hovered: bool = False


@dataclass
class Selectable:
    selected: bool = False


@dataclass
class Deletable:
    deleted: bool = False


@dataclass
class Draggable:
    dragging: bool = False
    offset: Optional[Vec2] = None


@dataclass
class Button:
    lit: bool = False


@dataclass
class Pressable:
    pressed: bool = False
    down: bool = False


@dataclass
class ToolSwitcher:
    tool: Tool


@dataclass
class Canvas:
    color: Color = Color(0, 0, 0, 255)
    cell_grid_always_visible: bool = False


@dataclass
class Image:
    image: ImageHandle
    data: Optional[Iterable[Color]] = None
    texture: Optional[TextureHandle] = None
    dirty: bool = False


@dataclass
class SpriteRegion:
    x: int = 0
    y: int = 0
    # todo width height


@dataclass
class EggTimer:
    time_left: int = 0


@dataclass
class TinyFriend:
    # 0: bunny, 1: spider, 2: chick, 3: slime
    type: int = 0
    angle: float = 0


@dataclass
class DebugEntity:
    pass
