#!/usr/bin/env python

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Tuple

# import raylib.static as rl
from raylib.pyray import PyRay
import esper

# todo move to package
from drawing import draw_line

pyray = PyRay()

################################################################################
# Constants, enums, types

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
    CELL_REF = 5
    CELL_REF_DROPPER = 6


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
    underlying_tool: Tool = None

    color_primary: Color = (255, 255, 255, 255)
    color_secondary: Color = (0, 0, 0, 255)

    # Just active cameras; kept in sync by a processor
    cameras: Mapping[PositionSpace, Any] = field(default_factory=dict)

    snap_x: int = 8
    snap_y: int = 8


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
class DeltaPosition:
    x: float = 0.0
    y: float = 0.0
    last_x: float = 0.0
    last_y: float = 0.0


@dataclass
class Jitter:
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


# todo dataclass this
class Camera:
    def __init__(self, *, active=False, zoom=1):
        self.camera_2d = pyray.Camera2D((0, 0), (0, 0), 0, zoom)
        self.active = active
        self.zoom_speed = 0.025
        self.zoom_velocity = 0
        self.zoom_friction = 0.85


@dataclass
class Mouse:
    reserved: bool = False


@dataclass
class RectangularSelection:
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
class Resizable:
    resizing: bool = False


@dataclass
class Scalable:
    scale: float = 1.0


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
    filename: str = None
    dirty: bool = False


@dataclass
class DebugEntity:
    pass


################################################################################
# Processors


class MotionController(esper.Processor):
    """Newtonian dynamics."""

    def process(self):
        for _, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            vel.x *= vel.friction
            vel.y *= vel.friction
            if abs(vel.x) < EPSILON:
                vel.x = 0
            if abs(vel.y) < EPSILON:
                vel.y = 0


# debug
class JitterController(esper.Processor):
    """Kick objects around a bit."""

    def process(self):
        for _, (vel, jit) in self.world.get_components(Velocity, Jitter):
            jit.tick -= 1
            if jit.tick == 0:
                jit.tick = jit.interval
                vel.x = random.randint(-jit.force, jit.force)
                vel.y = random.randint(-jit.force, jit.force)


class DeltaPositionController(esper.Processor):
    """Updates DeltaPositions."""

    def process(self):
        for _, (pos, delta) in self.world.get_components(Position, DeltaPosition):
            delta.x = delta.last_x - pos.x
            delta.y = delta.last_y - pos.y
            delta.last_x = pos.x
            delta.last_y = pos.y


class DebugEntityRenderer(esper.Processor):
    """Draws a basic spatial representation of the entity, for debugging."""

    def process(self):
        theme = self.world.context.theme

        for ent, (_, pos, ext) in self.world.get_components(
            DebugEntity, Position, Extent
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            pyray.begin_mode_2d(camera)

            rect = pyray.Rectangle(
                int(pos.x), int(pos.y), int(ext.width), int(ext.height)
            )
            color = theme.color_debug_magenta

            pyray.draw_rectangle_lines_ex(rect, 1, color)

            outline_color = None
            outline_rect = get_outline_rect(rect)

            for hov in self.world.try_component(ent, Hoverable):
                if hov.hovered:
                    outline_color = theme.color_thingy_hovered_outline

            for sel in self.world.try_component(ent, Selectable):
                if sel.selected:
                    outline_color = theme.color_selection_normal_outline

            if outline_color:
                pyray.draw_rectangle_lines_ex(outline_rect, 1, outline_color)

            for name in self.world.try_component(ent, Name):
                font_size = 8
                spacing = 1
                measurement = pyray.measure_text_ex(
                    theme.font, name.name, font_size, spacing
                )
                x = (pos.x + ext.width / 2) - measurement.x / 2
                y = (pos.y + ext.height / 2) - measurement.y / 2
                pyray.draw_text_ex(
                    theme.font, name.name, (int(x), int(y)), font_size, spacing, color,
                )

            pyray.end_mode_2d()


class BackgroundGridRenderer(esper.Processor):
    """Draws BackgroundGrids."""

    def _draw_x(self, grid, camera, step, width, height):
        if step < grid.min_step:
            return

        x = -camera.target.x * camera.zoom + width / 2
        x %= step
        while x < width:
            pyray.draw_line_ex(
                (int(x), 0), (int(x), int(height)), grid.line_width, grid.color,
            )
            x += step

    def _draw_y(self, grid, camera, step, width, height):
        if step < grid.min_step:
            return

        y = -camera.target.y * camera.zoom + height / 2
        y %= step
        while y < height:
            pyray.draw_line_ex(
                (0, int(y)), (int(width), int(y)), grid.line_width, grid.color,
            )
            y += step

    def process(self):
        if not (camera := self.world.context.cameras.get(PositionSpace.WORLD)):
            return

        screen_width = pyray.get_screen_width()
        screen_height = pyray.get_screen_height()
        for _, (grid, ext) in self.world.get_components(BackgroundGrid, Extent):
            self._draw_x(
                grid, camera, ext.width * camera.zoom, screen_width, screen_height,
            )
            self._draw_y(
                grid, camera, ext.height * camera.zoom, screen_width, screen_height,
            )


class PositionMarkerRenderer(esper.Processor):
    """Draws PositionMarkers."""

    def process(self):
        theme = self.world.context.theme

        for _, (pos, mark) in self.world.get_components(Position, PositionMarker):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            pyray.begin_mode_2d(camera)

            pyray.draw_line_v(
                (int(pos.x - mark.size), int(pos.y)),
                (int(pos.x + mark.size), int(pos.y)),
                theme.color_position_marker,
            )
            pyray.draw_line_v(
                (int(pos.x), int(pos.y - mark.size)),
                (int(pos.x), int(pos.y + mark.size)),
                theme.color_position_marker,
            )

            pyray.end_mode_2d()


class CameraController(esper.Processor):
    """Update cameras in response to events."""

    def process(self):
        screen_width = pyray.get_screen_width()
        screen_height = pyray.get_screen_height()

        mouse_delta = None
        for _, (_, mouse_delta) in self.world.get_components(Mouse, DeltaPosition):
            break

        for _, cam in self.world.get_component(Camera):
            if cam.active:
                # todo right now all Camera entities are in world space yikes
                self.world.context.cameras[PositionSpace.WORLD] = cam.camera_2d

                # pan
                if mouse_delta and pyray.is_mouse_button_down(
                    pyray.MOUSE_MIDDLE_BUTTON
                ):
                    cam.camera_2d.target.x += mouse_delta.x / cam.camera_2d.zoom
                    cam.camera_2d.target.y += mouse_delta.y / cam.camera_2d.zoom

                # smooth zoom
                if wheel := pyray.get_mouse_wheel_move():
                    cam.zoom_velocity += cam.zoom_speed * wheel

                # global hotkeys
                if pyray.is_key_pressed(pyray.KEY_HOME):
                    cam.camera_2d.target = (0, 0)
                if pyray.is_key_pressed(pyray.KEY_ONE):
                    cam.camera_2d.zoom = 1
                if pyray.is_key_pressed(pyray.KEY_TWO):
                    cam.camera_2d.zoom = 2
                if pyray.is_key_pressed(pyray.KEY_THREE):
                    cam.camera_2d.zoom = 3
                if pyray.is_key_pressed(pyray.KEY_FOUR):
                    cam.camera_2d.zoom = 4

            cam.camera_2d.offset.x = screen_width / 2
            cam.camera_2d.offset.y = screen_height / 2

            cam.camera_2d.zoom += cam.zoom_velocity * cam.camera_2d.zoom
            cam.zoom_velocity *= cam.zoom_friction
            if abs(cam.zoom_velocity) < EPSILON:
                cam.zoom_velocity = 0


class MouseController(esper.Processor):
    """Updates Mouse state."""

    def process(self):
        for _, (pos, mouse) in self.world.get_components(Position, Mouse):
            mouse_pos = pyray.get_mouse_position()
            pos.x = mouse_pos.x
            pos.y = mouse_pos.y


class RectangularSelectionController(esper.Processor):
    """Updates selection regions."""

    def process(self):
        if not (mouse_comps := get_mouse_and_pos(self.world)):
            return
        mouse, mouse_pos = mouse_comps

        # Are we hovering over anything? If so, we can't create selections
        hovering_any = False
        for ent, hover in self.world.get_component(Hoverable):
            if hover.hovered:
                hovering_any = True

                # If we just clicked, select only this.
                # todo if we're holding shift, don't deselect other stuff
                if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
                    for sel_ent, sel in self.world.get_component(Selectable):
                        sel.selected = ent == sel_ent

                break

        # Create new selections
        if not hovering_any and not mouse.reserved:
            # New selections always go into world space
            # Maybe change this someday? idk
            space = PositionSpace.WORLD
            start_pos = pyray.get_screen_to_world_2d(
                (mouse_pos.x, mouse_pos.y), self.world.context.cameras[space]
            )
            if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
                mouse.reserved = True
                self.world.create_entity(
                    Name("Selection region"),
                    Position(space=space),
                    Extent(),
                    RectangularSelection(start_x=start_pos.x, start_y=start_pos.y),
                )
            elif pyray.is_mouse_button_pressed(pyray.MOUSE_RIGHT_BUTTON):
                mouse.reserved = True
                self.world.create_entity(
                    Name("Create thingy region"),
                    Position(space=space),
                    Extent(),
                    RectangularSelection(
                        type=SelectionType.CREATE,
                        start_x=start_pos.x,
                        start_y=start_pos.y,
                    ),
                )

        # Identify selectables
        selectables_by_space = {
            PositionSpace.WORLD: [],
            PositionSpace.SCREEN: [],
        }
        for ent, (pos, ext, selectable) in self.world.get_components(
            Position, Extent, Selectable
        ):
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            selectables_by_space[pos.space].append((selectable, rect))

        # Update pos/ext, selectables, and handle release actions
        for ent, (pos, ext, selection) in self.world.get_components(
            Position, Extent, RectangularSelection
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            end_pos = pyray.get_screen_to_world_2d((mouse_pos.x, mouse_pos.y), camera)

            selection_rect = aabb(
                selection.start_x,
                selection.start_y,
                end_pos.x,
                end_pos.y,
                self.world.context.snap_x,
                self.world.context.snap_y,
            )

            pos.x = selection_rect.x
            pos.y = selection_rect.y
            ext.width = selection_rect.width
            ext.height = selection_rect.height

            # todo Squarify region
            # if pyray.is_key_down(pyray.KEY_LEFT_CONTROL) or pyray.is_key_down(
            #     pyray.KEY_RIGHT_CONTROL
            # ):
            #     if abs(width) > abs(height):
            #         height = abs(width) * height_sign
            #     else:
            #         width = abs(height) * width_sign

            # Update selectable entities
            if selection.type == SelectionType.NORMAL:
                for selectable, selectable_rect in selectables_by_space[pos.space]:
                    selectable.selected = rect_rect_intersect(
                        selectable_rect, selection_rect
                    )

            # Handle selection complete
            if (
                selection.type == SelectionType.NORMAL
                and pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON)
            ):
                mouse.reserved = False
                self.world.delete_entity(ent)
                continue
            elif (
                selection.type == SelectionType.CREATE
                and pyray.is_mouse_button_released(pyray.MOUSE_RIGHT_BUTTON)
            ):
                mouse.reserved = False
                self.world.create_entity(
                    Name("Canvas"),
                    Position(selection_rect.x, selection_rect.y),
                    Extent(selection_rect.width, selection_rect.height),
                    Canvas(),
                    Image(
                        image=pyray.gen_image_color(
                            int(selection_rect.width),
                            int(selection_rect.height),
                            draw_tool.color_secondary,
                        )
                    ),
                    CellGrid(3, 3),
                    Draggable(),
                    Hoverable(),
                    Selectable(),
                    Deletable(),
                )
                self.world.delete_entity(ent)
                continue


class RectangularSelectionRenderer(esper.Processor):
    """Draws selection regions."""

    def process(self):
        theme = self.world.context.theme

        for _, (pos, ext, sel) in self.world.get_components(
            Position, Extent, RectangularSelection
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            pyray.begin_mode_2d(camera)

            if sel.type == SelectionType.NORMAL:
                fill_color = theme.color_selection_normal_fill
                outline_color = theme.color_selection_normal_outline
                labeled = False
            elif sel.type == SelectionType.CREATE:
                fill_color = theme.color_selection_create_fill
                outline_color = theme.color_selection_create_outline
                labeled = True
            else:
                continue

            x, x_max = pos.x, pos.x + ext.width
            y, y_max = pos.y, pos.y + ext.height

            if x > x_max:
                x, x_max = x_max, x

            if y > y_max:
                y, y_max = y_max, y

            width = abs(x_max - x)
            height = abs(y_max - y)

            fill_rect = pyray.Rectangle(int(x), int(y), int(width), int(height))
            pyray.draw_rectangle_rec(fill_rect, fill_color)

            outline_rect = get_outline_rect(fill_rect)
            pyray.draw_rectangle_lines_ex(outline_rect, 1, outline_color)

            if labeled:
                text_pos = pyray.Vector2(int(x) - 1, int(y) - 9)
                pyray.draw_text_ex(
                    theme.font,
                    f"{int(width)}x{int(height)}",
                    text_pos,
                    8,
                    1,
                    theme.color_text_normal,
                )

            pyray.end_mode_2d()


class HoverController(esper.Processor):
    def process(self):
        if not (mouse_comps := get_mouse_and_pos(self.world)):
            return
        mouse, mouse_pos = mouse_comps

        for _, (pos, ext, hov) in self.world.get_components(
            Position, Extent, Hoverable
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            hover_pos = pyray.get_screen_to_world_2d((mouse_pos.x, mouse_pos.y), camera)
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            hov.hovered = point_rect_intersect(hover_pos.x, hover_pos.y, rect)


class DragController(esper.Processor):
    def process(self):
        if not self.world.context.tool == Tool.MOVE:
            return

        if not (mouse_comps := get_mouse_and_pos(self.world)):
            return
        mouse, mouse_pos = mouse_comps

        for _, (pos, ext, drag) in self.world.get_components(
            Position, Extent, Draggable
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            drag_pos = pyray.get_screen_to_world_2d((mouse_pos.x, mouse_pos.y), camera)
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            if (
                not mouse.reserved
                and pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON)
                and point_rect_intersect(drag_pos.x, drag_pos.y, rect)
            ):
                mouse.reserved = True
                drag.dragging = True
                drag.offset_x = drag_pos.x - pos.x
                drag.offset_y = drag_pos.y - pos.y

            if drag.dragging:
                pos.x = drag_pos.x - drag.offset_x
                pos.y = drag_pos.y - drag.offset_y

                # todo snap to grid

            if pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON):
                mouse.reserved = False
                drag.dragging = False
                drag.offset_x = 0
                drag.offset_y = 0


class SelectableDeleteController(esper.Processor):
    """Mark any selected Deletables as deleted when Delete is pressed."""

    def process(self):
        if pyray.is_key_pressed(pyray.KEY_DELETE):
            for ent, (sel, del_) in self.world.get_components(Selectable, Deletable):
                if sel.selected:
                    del_.deleted = True


class FinalDeleteController(esper.Processor):
    """
    Delete any deleted Deletable. Immediately before this, other more specific
    deletion processors should run to release any allocated resources. (But don't
    delete the actual entity, that's this thing's job.)
    """

    def process(self):
        for ent, del_ in self.world.get_component(Deletable):
            if del_.deleted:
                self.world.delete_entity(ent)


class ImageController(esper.Processor):
    """Load images, create textures, and keep them in sync."""

    def process(self):
        for ent, img in self.world.get_component(Image):
            if not img.image and img.filename:
                img.image = pyray.load_image(img.filename)

                image_format = pyray.UNCOMPRESSED_R8G8B8A8  # default apparently
                if img.image.format != image_format:
                    pyray.image_format(pyray.pointer(img.image), image_format)

                for ext in self.world.try_component(ent, Extent):
                    ext.width = img.image.width
                    ext.height = img.image.height

            if not img.texture:
                img.texture = pyray.load_texture_from_image(img.image)

            if img.texture and img.dirty:
                pyray.update_texture(img.texture, pyray.get_image_data(img.image))
                img.dirty = False


class ImageDeleteController(esper.Processor):
    """Unloads image (and texture) when the entity is deleted."""

    def process(self):
        for _, (img, del_) in self.world.get_components(Image, Deletable):
            if not del_.deleted:
                continue

            if img.texture:
                pyray.unload_texture(img.texture)
                img.texture = None

            if img.image:
                pyray.unload_image(img.image)
                img.image = None


# debug
class CanvasExportController(esper.Processor):
    """Export selected Canvas images to a directory"""

    def process(self):
        is_control_down = pyray.is_key_down(
            pyray.KEY_LEFT_CONTROL
        ) or pyray.is_key_down(pyray.KEY_RIGHT_CONTROL)

        if not (is_control_down and pyray.is_key_pressed(pyray.KEY_S)):
            return

        for _, (_, sel, img) in self.world.get_components(Canvas, Selectable, Image):
            if not sel.selected:
                continue

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = (
                f"save/thingy_{img.image.width}x{img.image.height}_{timestamp}.png"
            )
            pyray.export_image(img.image, filename)


class CanvasRenderer(esper.Processor):
    """Draws Canvases and their images."""

    def process(self):
        theme = self.world.context.theme

        for ent, (canvas, pos, ext) in self.world.get_components(
            Canvas, Position, Extent
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            pyray.begin_mode_2d(camera)

            # draw texture if it has an image
            # it always should, but who knows.
            for img in self.world.try_component(ent, Image):
                if not img.texture:
                    continue
                pyray.draw_texture(
                    img.texture, int(pos.x), int(pos.y), (255, 255, 255, 255)
                )

            outline_color = theme.color_thingy_outline
            for hov in self.world.try_component(ent, Hoverable):
                if hov.hovered:
                    outline_color = theme.color_thingy_hovered_outline
            for sel in self.world.try_component(ent, Selectable):
                if sel.selected:
                    outline_color = theme.color_thingy_selected_outline

            rect = pyray.Rectangle(
                int(pos.x), int(pos.y), int(ext.width), int(ext.height),
            )
            outline_rect = get_outline_rect(rect)
            pyray.draw_rectangle_lines_ex(
                outline_rect, 1, outline_color,
            )

            # todo: draw ref'd cells
            # for cell_y, cell_ref_row in enumerate(self.cell_refs):
            #     for cell_x, cell_ref in enumerate(cell_ref_row):
            #         if not cell_ref:
            #             continue

            #         source, source_cell_x, source_cell_y = cell_ref

            #         # draw refs as samples from source
            #         pyray.draw_texture_pro(
            #             source.texture,
            #             pyray.Rectangle(
            #                 int(source.w * source_cell_x / source.cells_x),
            #                 int(source.h * source_cell_y / source.cells_y),
            #                 int(source.w / source.cells_x),
            #                 int(source.h / source.cells_y),
            #             ),
            #             pyray.Rectangle(
            #                 self.x + int(self.w * cell_x / self.cells_x),
            #                 self.y + int(self.h * cell_y / self.cells_y),
            #                 int(self.w / self.cells_x),
            #                 int(self.h / self.cells_y),
            #             ),
            #             pyray.Vector2(0, 0),
            #             0,
            #             (255, 255, 255, 255),
            #         )

            # Draw the CellGrid, if this Canvas has one
            for cells in self.world.try_component(ent, CellGrid):
                if not grid_tool.active and not canvas.cell_grid_always_visible:
                    continue

                cell_grid_color = theme.color_grid_cells_subtle
                if grid_tool.active and canvas.cell_grid_always_visible:
                    cell_grid_color = theme.color_grid_cells_obvious

                if cells.x > 1:
                    for ix in range(1, cells.x):
                        x = pos.x + ix / cells.x * ext.width
                        pyray.draw_line(
                            int(x),
                            int(pos.y),
                            int(x),
                            int(pos.y + ext.height),
                            cell_grid_color,
                        )

                if cells.y > 1:
                    for iy in range(1, cells.y):
                        y = pos.y + iy / cells.y * ext.height
                        pyray.draw_line(
                            int(pos.x),
                            int(y),
                            int(pos.x + ext.width),
                            int(y),
                            cell_grid_color,
                        )

            pyray.end_mode_2d()


class ToolSwitcherController(esper.Processor):
    def __init__(self):
        self.hotkeys = {
            pyray.KEY_Q: Tool.MOVE,
            pyray.KEY_W: Tool.PENCIL,
            pyray.KEY_E: Tool.DROPPER,
            # todo...
        }

    def process(self):
        context = self.world.context

        # Update the current tool if we pressed a tool switcher
        for ent, (switcher, press) in self.world.get_components(
            ToolSwitcher, Pressable
        ):
            if press.pressed:
                context.tool = switcher.tool

        # Switch to a tool if we pressed its hotkey
        for key, tool in self.hotkeys.items():
            if pyray.is_key_pressed(key):
                context.tool = tool

        # Tool-specific temporary overrides
        # todo hmmmm this is weird
        is_overriding = False
        if (
            context.tool == Tool.PENCIL or context.underlying_tool == Tool.PENCIL
        ) and pyray.is_key_down(pyray.KEY_LEFT_ALT):
            context.tool = Tool.DROPPER
            context.underlying_tool = Tool.PENCIL
            is_overriding = True

        if context.underlying_tool and not is_overriding:
            context.tool = context.underlying_tool
            context.underlying_tool = None

        # Update the lit state of any buttons that represent the currently
        # selected tool
        for ent, (switcher, btn) in self.world.get_components(ToolSwitcher, Button):
            btn.lit = context.tool == switcher.tool


class PressController(esper.Processor):
    def process(self):
        if not (mouse_comps := get_mouse_and_pos(self.world)):
            return
        mouse, mouse_pos = mouse_comps

        for ent, (pos, ext, press) in self.world.get_components(
            Position, Extent, Pressable
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            press_pos = pyray.get_screen_to_world_2d((mouse_pos.x, mouse_pos.y), camera)
            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            press.pressed = False

            if (
                not mouse.reserved
                and pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON)
                and point_rect_intersect(press_pos.x, press_pos.y, rect)
            ):
                press.pressed = True
                press.down = True

            if pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON):
                press.down = False


class ButtonRenderer(esper.Processor):
    def process(self):
        theme = self.world.context.theme

        for ent, (pos, ext, btn) in self.world.get_components(Position, Extent, Button):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            pyray.begin_mode_2d(camera)

            rect = pyray.Rectangle(
                int(pos.x), int(pos.y), int(ext.width), int(ext.height),
            )

            fill_color = theme.color_button_fill
            border_color = theme.color_button_border

            if btn.lit:
                fill_color = theme.color_button_lit_fill
                border_color = theme.color_button_lit_border

            pyray.draw_rectangle_rec(rect, fill_color)
            pyray.draw_rectangle_lines_ex(rect, 1, border_color)

            for hov in self.world.try_component(ent, Hoverable):
                if hov.hovered:
                    pyray.draw_rectangle_rec(rect, theme.color_button_hover_overlay)

            for img in self.world.try_component(ent, Image):
                if img.texture:
                    pyray.draw_texture(
                        img.texture, int(pos.x), int(pos.y), (255, 255, 255, 255)
                    )

            pyray.end_mode_2d()


class PencilToolController(esper.Processor):
    def __init__(self):
        self.last_pos_x = None
        self.last_pos_y = None
        self.drawing = False

    def process(self):
        if not self.world.context.tool == Tool.PENCIL:
            return

        if not (mouse_comps := get_mouse_and_pos(self.world)):
            return
        mouse, mouse_pos = mouse_comps

        for ent, (canvas, pos, ext, img) in self.world.get_components(
            Canvas, Position, Extent, Image
        ):
            if not (camera := self.world.context.cameras.get(pos.space)):
                continue

            rect = pyray.Rectangle(pos.x, pos.y, ext.width, ext.height)
            pencil_pos = pyray.get_screen_to_world_2d(
                (mouse_pos.x, mouse_pos.y), camera
            )

            if (
                (self.drawing or not mouse.reserved)
                and pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON)
                and point_rect_intersect(pencil_pos.x, pencil_pos.y, rect)
            ):
                mouse.reserved = True
                self.drawing = True

                color = self.world.context.color_primary  # todo

                if self.last_pos_x is None:
                    self.last_pos_x = pencil_pos.x
                if self.last_pos_y is None:
                    self.last_pos_y = pencil_pos.y

                x1 = self.last_pos_x - pos.x
                y1 = self.last_pos_y - pos.y
                x2 = pencil_pos.x - pos.x
                y2 = pencil_pos.y - pos.y

                draw_line(
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2),
                    lambda x, y: pyray.image_draw_pixel(
                        pyray.pointer(img.image), x, y, color
                    ),
                )
                self.last_pos_x = pencil_pos.x
                self.last_pos_y = pencil_pos.y
                img.dirty = True

            if pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON):
                mouse.reserved = False
                self.drawing = False
                self.last_pos_x = None
                self.last_pos_y = None


################################################################################
# Helpers


def rect_rect_intersect(rect_a, rect_b):
    return (
        (rect_a.x < rect_b.x + rect_b.width)
        and (rect_a.x + rect_a.width > rect_b.x)
        and (rect_a.y < rect_b.y + rect_b.height)
        and (rect_a.y + rect_a.height > rect_b.y)
    )


def point_rect_intersect(x, y, rect):
    return (rect.x <= x < rect.x + rect.width) and (rect.y <= y < rect.y + rect.height)


def aabb(x1, y1, x2, y2, snap_x=0, snap_y=0):
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    if snap_x:
        x1 = math.floor(x1 / snap_x) * snap_x
    if snap_y:
        y1 = math.floor(y1 / snap_y) * snap_y

    width = x2 - x1
    height = y2 - y1

    if snap_x:
        width = math.ceil(width / snap_x) * snap_x
    if snap_y:
        height = math.ceil(height / snap_y) * snap_y

    return pyray.Rectangle(x1, y1, width, height)


def get_outline_rect(rect):
    return pyray.Rectangle(rect.x - 1, rect.y - 1, rect.width + 2, rect.height + 2)


def make_rect_extent_positive(rect):
    if rect.width < 0:
        rect.width *= -1
        rect.x -= rect.width

    if rect.height < 0:
        rect.height *= -1
        rect.y -= rect.height


################################################################################
# "Global component" fetching helpers
# Not sure if I like these...


def get_mouse_and_pos(world):
    for _, comps in world.get_components(Mouse, Position):
        return comps


################################################################################
# Cruft that needs to be ported to ECS


class DrawTool:
    def __init__(self):
        self.active = False
        self.color_primary = (255, 255, 255, 255)
        self.color_secondary = (0, 0, 0, 255)
        self.last_pos = None

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_X)
        if not self.active:
            self.last_pos = None

    def update_thingy(self, thingy, camera_2d):
        if not thingy:
            return

        if pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON):
            color = self.color_primary
        elif pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
            color = self.color_secondary
        else:
            self.last_pos = None
            return

        mouse_pos = pyray.get_mouse_position()
        world_pos = pyray.get_screen_to_world_2d(mouse_pos, camera_2d)

        if not self.last_pos:
            self.last_pos = world_pos

        x1 = int(self.last_pos.x - thingy.x)
        y1 = int(self.last_pos.y - thingy.y)
        x2 = int(world_pos.x - thingy.x)
        y2 = int(world_pos.y - thingy.y)
        draw_line(
            x1,
            y1,
            x2,
            y2,
            lambda x, y: pyray.image_draw_pixel(
                pyray.pointer(thingy.image), x, y, color
            ),
        )
        self.last_pos = world_pos
        thingy.dirty = True

    def draw(self):
        if not self.active:
            return

        mouse_pos = pyray.get_mouse_position()

        pyray.draw_rectangle(
            int(mouse_pos.x) + 16, int(mouse_pos.y) - 16, 16, 16, self.color_primary
        )
        pyray.draw_rectangle_lines(
            int(mouse_pos.x) + 15, int(mouse_pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )
        pyray.draw_rectangle(
            int(mouse_pos.x) + 33, int(mouse_pos.y) - 16, 16, 16, self.color_secondary
        )
        pyray.draw_rectangle_lines(
            int(mouse_pos.x) + 32, int(mouse_pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )


class DropperTool:
    def __init__(self):
        self.active = False
        self.color = (0, 0, 0, 0)

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_C)
        if not self.active and self.color:
            self.color = (0, 0, 0, 0)

    def update_thingy(self, thingy, camera_2d):
        if thingy:
            mouse_pos = pyray.get_mouse_position()
            world_pos = pyray.get_screen_to_world_2d(mouse_pos, camera_2d)
            x = int(world_pos.x - thingy.x)
            y = int(world_pos.y - thingy.y)
            self.color = pyray.get_image_data(thingy.image)[y * thingy.image.width + x]
        else:
            self.color = (0, 0, 0, 0)

        if pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON):
            draw_tool.color_primary = self.color
        elif pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
            draw_tool.color_secondary = self.color

    def draw(self):
        if not self.active:
            return

        mouse_pos = pyray.get_mouse_position()

        # hover color
        pyray.draw_rectangle(
            int(mouse_pos.x) + 16, int(mouse_pos.y) - 50, 33, 33, self.color
        )
        pyray.draw_rectangle_lines(
            int(mouse_pos.x) + 15, int(mouse_pos.y) - 51, 35, 35, (255, 255, 255, 255)
        )

        # todo silly globals
        pyray.draw_rectangle(
            int(mouse_pos.x) + 16,
            int(mouse_pos.y) - 16,
            16,
            16,
            draw_tool.color_primary,
        )
        pyray.draw_rectangle_lines(
            int(mouse_pos.x) + 15, int(mouse_pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )
        pyray.draw_rectangle(
            int(mouse_pos.x) + 33,
            int(mouse_pos.y) - 16,
            16,
            16,
            draw_tool.color_secondary,
        )
        pyray.draw_rectangle_lines(
            int(mouse_pos.x) + 32, int(mouse_pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )


class CellRefDropperTool:
    def __init__(self):
        self.active = False

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_R)

    def update_thingy(self, thingy, camera_2d):
        if not thingy:
            return

        mouse_pos = pyray.get_mouse_position()
        world_pos = pyray.get_screen_to_world_2d(mouse_pos, camera_2d)

        if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
            cell_ref_tool.source_primary_cell_x = int(
                (world_pos.x - thingy.x) / thingy.w * thingy.cells_x
            )
            cell_ref_tool.source_primary_cell_y = int(
                (world_pos.y - thingy.y) / thingy.h * thingy.cells_y
            )
            cell_ref_tool.source_primary = thingy

        if pyray.is_mouse_button_pressed(pyray.MOUSE_RIGHT_BUTTON):
            cell_ref_tool.source_secondary_cell_x = int(
                (world_pos.x - thingy.x) / thingy.w * thingy.cells_x
            )
            cell_ref_tool.source_secondary_cell_y = int(
                (world_pos.y - thingy.y) / thingy.h * thingy.cells_y
            )
            cell_ref_tool.source_secondary = thingy

    def draw(self, camera_2d, theme):
        if not self.active:
            return

        mouse_pos = pyray.get_mouse_position()

        # debug: temp ref icon
        pyray.draw_text_ex(
            theme.font,
            b"? ->",
            pyray.Vector2(mouse_pos.x + 16, mouse_pos.y - 16),
            24,
            1,
            theme.color_text_normal,
        )

        pyray.begin_mode_2d(camera_2d)

        crt = cell_ref_tool
        if crt.source_primary:
            pyray.draw_rectangle_lines_ex(
                pyray.Rectangle(
                    crt.source_primary.x
                    + int(
                        crt.source_primary.w
                        * crt.source_primary_cell_x
                        / crt.source_primary.cells_x
                    )
                    - 1,
                    crt.source_primary.y
                    + int(
                        crt.source_primary.h
                        * crt.source_primary_cell_y
                        / crt.source_primary.cells_y
                    )
                    - 1,
                    int(crt.source_primary.w / crt.source_primary.cells_x) + 2,
                    int(crt.source_primary.h / crt.source_primary.cells_y) + 2,
                ),
                1,
                (255, 0, 0, 255),
            )

        if crt.source_secondary:
            pyray.draw_rectangle_lines_ex(
                pyray.Rectangle(
                    crt.source_secondary.x
                    + int(
                        crt.source_secondary.w
                        * crt.source_secondary_cell_x
                        / crt.source_secondary.cells_x
                    )
                    - 1,
                    crt.source_secondary.y
                    + int(
                        crt.source_secondary.h
                        * crt.source_secondary_cell_y
                        / crt.source_secondary.cells_y
                    )
                    - 1,
                    int(crt.source_secondary.w / crt.source_secondary.cells_x) + 2,
                    int(crt.source_secondary.h / crt.source_secondary.cells_y) + 2,
                ),
                1,
                (0, 0, 255, 255),
            )

        pyray.end_mode_2d()


class CellRefTool:
    def __init__(self):
        self.active = False
        self.source_primary = None
        self.source_primary_cell_x = None
        self.source_primary_cell_y = None
        self.source_secondary = None
        self.source_secondary_cell_x = None
        self.source_secondary_cell_y = None

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_T)

    def update_thingy(self, thingy, camera_2d):
        if not thingy:
            return

        mouse_pos = pyray.get_mouse_position()
        world_pos = pyray.get_screen_to_world_2d(mouse_pos, camera_2d)

        cell_x = int((world_pos.x - thingy.x) / thingy.w * thingy.cells_x)
        cell_y = int((world_pos.y - thingy.y) / thingy.h * thingy.cells_y)

        if pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON):
            thingy.cell_refs[cell_y][cell_x] = (
                self.source_primary,
                self.source_primary_cell_x,
                self.source_primary_cell_y,
            )

        if pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
            thingy.cell_refs[cell_y][cell_x] = (
                self.source_secondary,
                self.source_secondary_cell_x,
                self.source_secondary_cell_y,
            )

        # debug delete refs with middle mouse
        if pyray.is_mouse_button_down(pyray.MOUSE_MIDDLE_BUTTON):
            thingy.cell_refs[cell_y][cell_x] = None

    def draw(self, camera_2d, theme):
        if not self.active:
            return

        mouse_pos = pyray.get_mouse_position()

        # debug: temp ref icon
        pyray.draw_text_ex(
            theme.font,
            b"  -> !",
            pyray.Vector2(mouse_pos.x + 16, mouse_pos.y - 16),
            24,
            1,
            theme.color_text_normal,
        )


class GridTool:
    def __init__(self):
        self.active = False
        self.thingy = None

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_G)

    def update_thingy(self, thingy, camera_2d):
        self.thingy = thingy

        if not thingy:
            return

        if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
            thingy.cells_visible = not thingy.cells_visible

        cells_x_delta = 0
        cells_y_delta = 0

        cells_x_delta = cells_y_delta = int(pyray.get_mouse_wheel_move())

        if pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
            cells_y_delta = 0

        thingy.cells_x += cells_x_delta
        thingy.cells_y += cells_y_delta

        thingy.cells_x = max(thingy.cells_x, 1)
        thingy.cells_y = max(thingy.cells_y, 1)

        if cells_x_delta != 0 or cells_y_delta != 0:
            # todo blehhhhhhghghgh
            thingy.cell_refs = [
                [None for x in range(thingy.cells_x)] for y in range(thingy.cells_y)
            ]

    def draw(self, camera_2d, theme):
        if not self.active:
            return

        mouse_pos = pyray.get_mouse_position()

        # debug: temp grid icon
        pyray.draw_text_ex(
            theme.font,
            b"#",
            pyray.Vector2(mouse_pos.x + 16, mouse_pos.y - 16),
            24,
            1,
            theme.color_text_normal,
        )

        if not self.thingy:
            return

        cell_w = self.thingy.w / self.thingy.cells_x
        cell_h = self.thingy.h / self.thingy.cells_y

        if cell_w.is_integer() and cell_h.is_integer():
            text_color = theme.color_text_normal
            cell_dimensions = f"{int(cell_w)}x{int(cell_h)}"
        else:
            text_color = theme.color_text_error
            cell_dimensions = f"{cell_w:.2f}x{cell_h:.2f}"

        text_offset_x = -1 if self.thingy.selected else 0
        text_offset_y = -9 if self.thingy.selected else -8

        pyray.begin_mode_2d(camera_2d)
        pyray.draw_text_ex(
            theme.font,
            str(f"{self.thingy.cells_x}x{self.thingy.cells_y} @ {cell_dimensions}"),
            pyray.Vector2(self.thingy.x + text_offset_x, self.thingy.y + text_offset_y),
            8,
            1,
            text_color,
        )
        pyray.end_mode_2d()


################################################################################


draw_tool = DrawTool()
grid_tool = GridTool()
dropper_tool = DropperTool()
cell_ref_tool = CellRefTool()
cell_ref_dropper_tool = CellRefDropperTool()


def main():
    # pyray.set_config_flags(pyray.FLAG_WINDOW_RESIZABLE)
    pyray.init_window(800, 600, "Dream Table")
    pyray.set_target_fps(60)

    world = esper.World()
    world.context = WorldContext(
        cameras={PositionSpace.SCREEN: pyray.Camera2D((0, 0), (0, 0), 0, 3)},
        theme=Theme(font=pyray.load_font("resources/fonts/alpha_beta.png")),
    )

    # Spawn initial entities
    world.create_entity(Name("Camera"), Camera(active=True, zoom=4))
    world.create_entity(
        Name("Mouse"), Mouse(), Position(space=PositionSpace.SCREEN), DeltaPosition()
    )

    world.create_entity(Name("Origin"), Position(), PositionMarker())
    world.create_entity(
        Name("Minor grid"),
        BackgroundGrid(world.context.theme.color_grid_minor),
        Extent(8, 8),
    )
    world.create_entity(
        Name("Major grid"),
        BackgroundGrid(world.context.theme.color_grid_major),
        Extent(32, 32),
    )

    # debug: a fun lil' testangle
    world.create_entity(
        Name("Testangle"),
        Position(),
        Velocity(5, 5, friction=0.9),
        Extent(40, 10),
        Jitter(),
        DebugEntity(),
        Draggable(),
        Hoverable(),
        Selectable(),
    )

    # debug: a draggable to drag around
    world.create_entity(
        Name("Draggable"),
        Position(40, 40, space=PositionSpace.SCREEN),
        Extent(40, 10),
        DebugEntity(),
        Hoverable(),
        Draggable(),
        Selectable(),
    )

    # debug: a canvas with a preloaded palette image
    world.create_entity(
        Name("Sweetie 16"),
        Canvas(),
        Position(),
        Extent(),
        Image(filename="resources/palettes/sweetie-16-8x.png"),
        Draggable(),
        Hoverable(),
        Selectable(),
        Deletable(),
    )

    # debug: tool buttons
    world.create_entity(
        Name("Move"),
        Button(),
        ToolSwitcher(Tool.MOVE),
        Pressable(),
        Position(2, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename="resources/icons/hand.png"),
        Hoverable(),
    )
    world.create_entity(
        Name("Pencil"),
        Button(),
        ToolSwitcher(Tool.PENCIL),
        Pressable(),
        Position(10, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename="resources/icons/pencil.png"),
        Hoverable(),
    )
    world.create_entity(
        Name("Dropper"),
        Button(),
        ToolSwitcher(Tool.DROPPER),
        Pressable(),
        Position(18, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename="resources/icons/dropper.png"),
        Hoverable(),
    )

    # Register controllers and renderers (flavors of processors)
    world.add_processor(MouseController())
    world.add_processor(CameraController())
    world.add_processor(MotionController())
    world.add_processor(DeltaPositionController())
    world.add_processor(JitterController())
    world.add_processor(PencilToolController())
    world.add_processor(DragController())
    world.add_processor(HoverController())
    world.add_processor(PressController())
    world.add_processor(RectangularSelectionController())
    world.add_processor(ImageController())
    world.add_processor(ToolSwitcherController())

    world.add_processor(BackgroundGridRenderer())
    world.add_processor(PositionMarkerRenderer())
    world.add_processor(RectangularSelectionRenderer())
    world.add_processor(CanvasRenderer())
    world.add_processor(DebugEntityRenderer())
    world.add_processor(ButtonRenderer())

    world.add_processor(SelectableDeleteController())
    world.add_processor(ImageDeleteController())
    world.add_processor(FinalDeleteController())

    while not pyray.window_should_close():
        pyray.begin_drawing()
        pyray.clear_background(world.context.theme.color_background)
        world.process()
        # draw_tool.update()
        # grid_tool.update()
        # dropper_tool.update()
        # cell_ref_tool.update()
        # cell_ref_dropper_tool.update()
        # draw_tool.draw()
        # grid_tool.draw(camera_2d, theme)
        # dropper_tool.draw()
        # cell_ref_tool.draw(camera_2d, theme)
        # cell_ref_dropper_tool.draw(camera_2d, theme)
        pyray.end_drawing()

    pyray.close_window()


if __name__ == "__main__":
    main()
