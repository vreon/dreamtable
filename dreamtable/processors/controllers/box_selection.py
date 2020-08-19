from typing import Dict, List, Tuple

import esper
from raylib.pyray import PyRay

from dreamtable import components as c
from dreamtable.constants import PositionSpace, SelectionType
from dreamtable.utils import get_aabb, rect_rect_intersect
from dreamtable.hal import HAL


class BoxSelectionController(esper.Processor):
    """Updates selection regions."""

    def process(self, pyray: PyRay, hal: HAL) -> None:
        mouse_pos_x = self.world.context.mouse_pos_x
        mouse_pos_y = self.world.context.mouse_pos_y
        # Are we hovering over anything? If so, we can't create selections
        hovering_any = False
        for ent, hover in self.world.get_component(c.Hoverable):
            if hover.hovered:
                hovering_any = True

                # If we just clicked, select only this.
                # todo if we're holding shift, don't deselect other stuff
                if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
                    for sel_ent, sel in self.world.get_component(c.Selectable):
                        sel.selected = ent == sel_ent

                break

        # Create new selections
        if not hovering_any and not self.world.context.mouse_reserved:
            # New selections always go into world space
            # Maybe change this someday? idk
            space = PositionSpace.WORLD
            start_pos = pyray.get_screen_to_world_2d(
                (mouse_pos_x, mouse_pos_y), self.world.context.cameras[space]
            )
            if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
                self.world.context.mouse_reserved = True
                self.world.create_entity(
                    c.Name("Selection region"),
                    c.Position(space=space),
                    c.Extent(),
                    c.BoxSelection(start_x=start_pos.x, start_y=start_pos.y),
                )
            elif pyray.is_mouse_button_pressed(pyray.MOUSE_RIGHT_BUTTON):
                self.world.context.mouse_reserved = True
                self.world.create_entity(
                    c.Name("Create thingy region"),
                    c.Position(space=space),
                    c.Extent(),
                    c.BoxSelection(
                        type=SelectionType.CREATE,
                        start_x=start_pos.x,
                        start_y=start_pos.y,
                    ),
                )

        # Identify selectables
        selectables_by_space: Dict[
            PositionSpace, List[Tuple[c.Selectable, Tuple[float, float, float, float]]]
        ] = {
            PositionSpace.WORLD: [],
            PositionSpace.SCREEN: [],
        }
        for ent, (pos, ext, selectable) in self.world.get_components(
            c.Position, c.Extent, c.Selectable
        ):
            rect = (pos.x, pos.y, ext.width, ext.height)
            selectables_by_space[pos.space].append((selectable, rect))

        # Update pos/ext, selectables, and handle release actions
        for ent, (pos, ext, selection) in self.world.get_components(
            c.Position, c.Extent, c.BoxSelection
        ):
            camera = self.world.context.cameras[pos.space]
            end_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)

            snap_x, snap_y = (
                (self.world.context.snap_x, self.world.context.snap_y)
                if selection.type == SelectionType.CREATE
                else (1, 1)
            )

            pos.x, pos.y, ext.width, ext.height = get_aabb(
                selection.start_x,
                selection.start_y,
                end_pos.x,
                end_pos.y,
                snap_x,
                snap_y,
            )

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
                for selectable, (sx, sy, sw, sh) in selectables_by_space[pos.space]:
                    selectable.selected = rect_rect_intersect(
                        sx, sy, sw, sh, pos.x, pos.y, ext.width, ext.height
                    )

            # Handle selection complete
            if (
                selection.type == SelectionType.NORMAL
                and pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON)
            ):
                self.world.context.mouse_reserved = False
                self.world.delete_entity(ent)
                continue
            elif (
                selection.type == SelectionType.CREATE
                and pyray.is_mouse_button_released(pyray.MOUSE_RIGHT_BUTTON)
            ):
                self.world.context.mouse_reserved = False
                self.world.create_entity(
                    c.Name("Canvas"),
                    c.Position(pos.x, pos.y),
                    c.Extent(ext.width, ext.height),
                    c.Canvas(),
                    c.Image(
                        image=pyray.gen_image_color(
                            int(ext.width),
                            int(ext.height),
                            self.world.context.color_secondary,
                        )
                    ),
                    c.CellGrid(3, 3),
                    c.Draggable(),
                    c.Hoverable(),
                    c.Selectable(),
                    c.Deletable(),
                )
                self.world.delete_entity(ent)
                continue
