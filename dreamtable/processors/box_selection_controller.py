import esper

from ..components import (
    Hoverable,
    Selectable,
    Name,
    Position,
    Extent,
    BoxSelection,
    Canvas,
    Image,
    CellGrid,
    Draggable,
    Deletable,
)
from ..constants import SelectionType, PositionSpace
from ..utils import get_aabb, rect_rect_intersect


class BoxSelectionController(esper.Processor):
    """Updates selection regions."""

    def process(self, pyray):
        mouse_pos_x = self.world.context.mouse_pos_x
        mouse_pos_y = self.world.context.mouse_pos_y
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
                    Name("Selection region"),
                    Position(space=space),
                    Extent(),
                    BoxSelection(start_x=start_pos.x, start_y=start_pos.y),
                )
            elif pyray.is_mouse_button_pressed(pyray.MOUSE_RIGHT_BUTTON):
                self.world.context.mouse_reserved = True
                self.world.create_entity(
                    Name("Create thingy region"),
                    Position(space=space),
                    Extent(),
                    BoxSelection(
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
            Position, Extent, BoxSelection
        ):
            camera = self.world.context.cameras[pos.space]
            end_pos = pyray.get_screen_to_world_2d((mouse_pos_x, mouse_pos_y), camera)

            snap_x, snap_y = (
                (self.world.context.snap_x, self.world.context.snap_y)
                if selection.type == SelectionType.CREATE
                else (1, 1)
            )

            selection_rect = pyray.Rectangle(
                *get_aabb(
                    selection.start_x,
                    selection.start_y,
                    end_pos.x,
                    end_pos.y,
                    snap_x,
                    snap_y,
                )
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
                self.world.context.mouse_reserved = False
                self.world.delete_entity(ent)
                continue
            elif (
                selection.type == SelectionType.CREATE
                and pyray.is_mouse_button_released(pyray.MOUSE_RIGHT_BUTTON)
            ):
                self.world.context.mouse_reserved = False
                self.world.create_entity(
                    Name("Canvas"),
                    Position(selection_rect.x, selection_rect.y),
                    Extent(selection_rect.width, selection_rect.height),
                    Canvas(),
                    Image(
                        image=pyray.gen_image_color(
                            int(selection_rect.width),
                            int(selection_rect.height),
                            self.world.context.color_secondary,
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
