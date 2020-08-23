from typing import Dict, List, Tuple

import esper

from dreamtable import components as c
from dreamtable.constants import PositionSpace, SelectionType
from dreamtable.utils import get_aabb
from dreamtable.hal import HAL, MouseButton, Rect, Vec2


class BoxSelectionController(esper.Processor):
    """Updates selection regions."""

    def process(self, hal: HAL) -> None:
        context = self.world.context
        mouse_pos = hal.get_mouse_position()

        # Are we hovering over anything? If so, we can't create selections
        hovering_any = False
        for ent, hover in self.world.get_component(c.Hoverable):
            if hover.hovered:
                hovering_any = True

                # If we just clicked, select only this.
                # todo if we're holding shift, don't deselect other stuff
                if hal.is_mouse_button_pressed(MouseButton.LEFT):
                    hal.clear_mouse_button_pressed(MouseButton.LEFT)
                    for sel_ent, sel in self.world.get_component(c.Selectable):
                        sel.selected = ent == sel_ent

                break

        # Create new selections
        if not hovering_any:
            # New selections always go into world space
            # Maybe change this someday? idk
            space = PositionSpace.WORLD
            start_pos = hal.get_screen_to_world(mouse_pos, context.cameras[space])
            if hal.is_mouse_button_pressed(MouseButton.LEFT):
                hal.clear_mouse_button_pressed(MouseButton.LEFT)
                self.world.create_entity(
                    c.Position(space=space),
                    c.Extent(),
                    c.BoxSelection(start_pos=start_pos),
                )
            elif hal.is_mouse_button_pressed(MouseButton.RIGHT):
                hal.clear_mouse_button_pressed(MouseButton.RIGHT)
                self.world.create_entity(
                    c.Position(space=space),
                    c.Extent(),
                    c.BoxSelection(type=SelectionType.CREATE, start_pos=start_pos,),
                )

        # Identify selectables
        selectables_by_space: Dict[PositionSpace, List[Tuple[c.Selectable, Rect]]] = {
            PositionSpace.WORLD: [],
            PositionSpace.SCREEN: [],
        }
        for ent, (pos, ext, selectable) in self.world.get_components(
            c.Position, c.Extent, c.Selectable
        ):
            rect = c.rect(pos.position, ext.extent)
            selectables_by_space[pos.space].append((selectable, rect))

        # Update pos/ext, selectables, and handle release actions
        for ent, (pos, ext, selection) in self.world.get_components(
            c.Position, c.Extent, c.BoxSelection
        ):
            camera = context.cameras[pos.space]
            end_pos = hal.get_screen_to_world(mouse_pos, camera)

            snap = (
                context.snap if selection.type == SelectionType.CREATE else Vec2(1, 1)
            )

            # todo
            pos.position.x, pos.position.y, ext.extent.x, ext.extent.y = get_aabb(
                selection.start_pos.x,
                selection.start_pos.y,
                end_pos.x,
                end_pos.y,
                snap.x,
                snap.y,
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
                selection_rect = c.rect(pos.position, ext.extent)
                for selectable, selectable_rect in selectables_by_space[pos.space]:
                    selectable.selected = selection_rect.touching(selectable_rect)

            # Handle selection complete
            if selection.type == SelectionType.NORMAL and hal.is_mouse_button_released(
                MouseButton.LEFT
            ):
                self.world.delete_entity(ent)
                continue
            elif (
                selection.type == SelectionType.CREATE
                and hal.is_mouse_button_released(MouseButton.RIGHT)
            ):
                self.world.create_entity(
                    c.Name("Canvas"),
                    c.Position(pos.position.copy()),
                    c.Extent(ext.extent.copy()),
                    c.Canvas(),
                    c.Image(
                        image=hal.gen_image_from_color(
                            ext.extent, context.color_secondary
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
