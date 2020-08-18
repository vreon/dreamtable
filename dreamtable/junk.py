################################################################################
# Stuff that still needs to be ported to ECS


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
