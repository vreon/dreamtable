from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Tuple

from .constants import PositionSpace, SelectionType, Tool

Color = Tuple[int, int, int, int]


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

    color_primary: Color = (255, 255, 255, 255)
    color_secondary: Color = (0, 0, 0, 255)
    color_dropper: Color = (0, 0, 0, 0)

    # Just active cameras; kept in sync by a processor
    cameras: Mapping[PositionSpace, Any] = field(default_factory=dict)

    snap_x: int = 8
    snap_y: int = 8

    mouse_pos_x: Optional[int] = None
    mouse_pos_y: Optional[int] = None
    mouse_delta_x: int = 0
    mouse_delta_y: int = 0
    mouse_wheel: int = 0

    # todo this is janky af
    # it's used to stop propagation of mouse click events
    mouse_reserved: bool = False


@dataclass
class Theme:
    color_background: Color = (9, 12, 17, 255)
    color_position_marker: Color = (164, 84, 30, 255)
    color_grid_cells_subtle: Color = (255, 255, 255, 32)
    color_grid_cells_obvious: Color = (255, 255, 255, 64)
    color_grid_minor: Color = (68, 93, 144, 16)
    color_grid_major: Color = (68, 93, 144, 32)
    color_text_normal: Color = (255, 255, 255, 255)
    color_text_error: Color = (164, 84, 30, 255)
    color_selection_create_outline: Color = (0, 255, 0, 128)
    color_selection_create_fill: Color = (0, 255, 0, 32)
    color_selection_normal_outline: Color = (68, 93, 144, 128)
    color_selection_normal_fill: Color = (68, 93, 144, 32)
    color_thingy_outline: Color = (68, 93, 144, 16)
    color_thingy_hovered_outline: Color = (68, 93, 144, 48)
    color_thingy_selected_outline: Color = (68, 93, 144, 128)
    color_debug_magenta: Color = (255, 0, 255, 255)
    color_button_fill: Color = (32, 32, 32, 255)
    color_button_border: Color = (64, 64, 64, 255)
    color_button_lit_fill: Color = (84, 30, 0, 255)
    color_button_lit_border: Color = (164, 84, 30, 255)
    color_button_hover_overlay: Color = (255, 255, 255, 32)
    font: Any = None  # TODO


################################################################################
# Components


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0
    space: PositionSpace = PositionSpace.WORLD


@dataclass
class Extent:
    width: float = 0.0
    height: float = 0.0


@dataclass
class Velocity:
    x: float = 0
    y: float = 0
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
    camera_2d: Any = None
    active: bool = False
    zoom_speed: float = 0.025
    zoom_velocity: float = 0
    zoom_friction: float = 0.85


@dataclass
class BoxSelection:
    type: SelectionType = SelectionType.NORMAL
    start_x: float = 0.0
    start_y: float = 0.0


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
    offset_x: float = 0.0
    offset_y: float = 0.0


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
    color: Color = (0, 0, 0, 255)
    cell_grid_always_visible: bool = False


@dataclass
class Image:
    image: Any = None
    texture: Any = None
    image_data: Any = None
    filename: Optional[str] = None
    dirty: bool = False


@dataclass
class SpriteRegion:
    x: int = 0
    y: int = 0
    tint: Color = (255, 255, 255, 255)


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
