#!/usr/bin/env python

# import raylib.static as rl
from raylib.pyray import PyRay
import random
from datetime import datetime

pyray = PyRay()


# XXX: Something's wrong with pyray.image_draw_line, here's a Python port
def pyray_image_draw_line(
    image_ptr, start_pos_x, start_pos_y, end_pos_x, end_pos_y, color
):
    m = 2 * (end_pos_y - start_pos_y)
    slope_error = m - (end_pos_x - start_pos_x)

    x = start_pos_x
    y = start_pos_y

    while x <= end_pos_x:
        pyray.image_draw_pixel(image_ptr, int(x), int(y), color)
        slope_error += m

        if slope_error >= 0:
            y += 1
            slope_error -= 2 * (end_pos_x - start_pos_x)

        x += 1


class UI:
    BACKGROUND = (9, 12, 17, 255)
    AXIS_X = (164, 84, 30, 255)  # (255, 0, 0, 128)
    AXIS_Y = (164, 84, 30, 255)  # (0, 255, 0, 128)
    GRID_CELLS_SUBTLE = (255, 255, 255, 32)
    GRID_CELLS_OBVIOUS = (255, 255, 255, 64)
    GRID_MINOR = (68, 93, 144, 16)
    GRID_MAJOR = (68, 93, 144, 32)
    HUD_TEXT = (255, 255, 255, 255)
    HUD_ERROR = (164, 84, 30, 255)
    CREATE_OUTLINE = (0, 255, 0, 128)
    CREATE_FILL = (0, 255, 0, 32)
    SELECTION_OUTLINE = (68, 93, 144, 128)
    SELECTION_FILL = (68, 93, 144, 32)
    THINGY_OUTLINE = (68, 93, 144, 16)
    THINGY_HOVERED_OUTLINE = (68, 93, 144, 48)
    THINGY_SELECTED_OUTLINE = (68, 93, 144, 128)


class HUD:
    def __init__(self):
        self.lines = []
        self.size = 12
        self.font = pyray.get_font_default()

    def print(self, line):
        self.lines.append(line)

    def draw(self):
        for i, line in enumerate(self.lines):
            pyray.draw_text_ex(
                self.font,
                str(line),
                pyray.Vector2(0, i * self.size),
                self.size,
                1,
                UI.HUD_TEXT,
            )
        self.lines = []


class Origin:
    def __init__(self, size=8):
        self.size = size

    def draw(self):
        pyray.draw_line_v([-self.size, 0], [self.size, 0], UI.AXIS_Y)
        pyray.draw_line_v([0, -self.size], [0, self.size], UI.AXIS_X)


class Mouse:
    def __init__(self):
        self.pos = pyray.Vector2()
        self.delta = pyray.Vector2()

    def update(self):
        new_pos = pyray.get_mouse_position()
        self.delta = pyray.Vector2(self.pos.x - new_pos.x, self.pos.y - new_pos.y)
        self.pos = new_pos


class Camera:
    def __init__(self, screen, zoom=1):
        self.screen = screen
        self.camera = pyray.Camera2D([screen.w / 2, screen.h / 2], [0, 0], 0, zoom)
        self.zoom_speed = 0.025
        self.zoom_velocity = 0

    def update(self, mouse):
        self.camera.offset.x = self.screen.w / 2
        self.camera.offset.y = self.screen.h / 2
        if pyray.is_mouse_button_down(pyray.MOUSE_MIDDLE_BUTTON):
            self.camera.target.x += mouse.delta.x / self.camera.zoom
            self.camera.target.y += mouse.delta.y / self.camera.zoom

        self.camera.zoom += self.zoom_velocity * self.camera.zoom
        self.zoom_velocity *= 0.85
        if abs(self.zoom_velocity) < 0.005:
            self.zoom_velocity = 0


class BackgroundGrid:
    def __init__(self, w, h, color, width=2, min=4):
        self.w = w
        self.h = h
        self.color = color
        self.width = width
        self.min = min

    def draw(self, screen, camera):
        step_x = self.w * camera.camera.zoom
        if step_x >= self.min:
            x = (-camera.camera.target.x * camera.camera.zoom + screen.w / 2) % step_x
            while x < screen.w:
                pyray.draw_line_ex(
                    [int(x), 0], [int(x), screen.h], self.width, self.color,
                )
                x += step_x

        step_y = self.h * camera.camera.zoom
        if step_y >= self.min:
            y = (-camera.camera.target.y * camera.camera.zoom + screen.h / 2) % step_y
            while y < screen.h:
                pyray.draw_line_ex(
                    [0, int(y)], [screen.w, int(y)], self.width, self.color,
                )
                y += step_y


class Screen:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def update(self):
        if pyray.is_window_resized():
            self.w = pyray.get_screen_width()
            self.h = pyray.get_screen_height()


class Selection:
    def __init__(self, start):
        self.start = start
        self.end = start

    # todo square
    def rect(self, snap=None):
        x1, x2 = self.start.x, self.end.x
        y1, y2 = self.start.y, self.end.y

        if x1 > x2:
            x1, x2 = x2, x1

        if y1 > y2:
            y1, y2 = y2, y1

        if snap:
            x1 = round(x1 / snap.x) * snap.x
            y1 = round(y1 / snap.y) * snap.y
            x2 = round(x2 / snap.x) * snap.x
            y2 = round(y2 / snap.y) * snap.y

        w = abs(x2 - x1)
        h = abs(y2 - y1)

        if pyray.is_key_down(pyray.KEY_LEFT_CONTROL) or pyray.is_key_down(
            pyray.KEY_RIGHT_CONTROL
        ):
            # todo need to iron out x and y offsets with square selections in
            # all of the negative-coord quadrants
            w = h = max(w, h)

        if not w or not h:
            return

        return pyray.Rectangle(x1, y1, w, h)

    def draw(self, fill_color, outline_color=None, snap=None, label=True, font=None):
        rect = self.rect(snap=snap)
        if not rect:
            return

        pyray.draw_rectangle_rec(rect, fill_color)

        if outline_color:
            pyray.draw_rectangle_lines_ex(
                pyray.Rectangle(
                    rect.x - 1, rect.y - 1, rect.width + 2, rect.height + 2
                ),
                1,
                outline_color,
            )

        if label and font:
            pyray.draw_text_ex(
                font,
                str(f"{int(rect.width)}x{int(rect.height)}"),
                pyray.Vector2(rect.x - 1, rect.y - 9),
                8,
                1,
                UI.HUD_TEXT,
            )


class DrawTool:
    def __init__(self):
        self.active = False
        self.color_primary = (255, 255, 255, 255)
        self.color_secondary = (0, 0, 0, 255)

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_X)

    def update_thingy(self, thingy, mouse, camera):
        if not thingy:
            return

        if pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON):
            color = self.color_primary
        elif pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
            color = self.color_secondary
        else:
            return

        world_pos = pyray.get_screen_to_world_2d(mouse.pos, camera.camera)
        x = int(world_pos.x - thingy.x)
        y = int(world_pos.y - thingy.y)
        pyray.image_draw_pixel(pyray.pointer(thingy.image), x, y, color)
        thingy.dirty = True

    def draw(self, mouse):
        if not self.active:
            return

        pyray.draw_rectangle(
            int(mouse.pos.x) + 16, int(mouse.pos.y) - 16, 16, 16, self.color_primary
        )
        pyray.draw_rectangle_lines(
            int(mouse.pos.x) + 15, int(mouse.pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )
        pyray.draw_rectangle(
            int(mouse.pos.x) + 33, int(mouse.pos.y) - 16, 16, 16, self.color_secondary
        )
        pyray.draw_rectangle_lines(
            int(mouse.pos.x) + 32, int(mouse.pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )


class DropperTool:
    def __init__(self):
        self.active = False
        self.color = (0, 0, 0, 0)

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_C)
        if not self.active and self.color:
            self.color = (0, 0, 0, 0)

    def update_thingy(self, thingy, mouse, camera):
        if thingy:
            world_pos = pyray.get_screen_to_world_2d(mouse.pos, camera.camera)
            x = int(world_pos.x - thingy.x)
            y = int(world_pos.y - thingy.y)
            self.color = pyray.get_image_data(thingy.image)[y * thingy.image.width + x]
        else:
            self.color = (0, 0, 0, 0)

        if pyray.is_mouse_button_down(pyray.MOUSE_LEFT_BUTTON):
            draw_tool.color_primary = self.color
        elif pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
            draw_tool.color_secondary = self.color

    def draw(self, mouse):
        if not self.active:
            return

        # hover color
        pyray.draw_rectangle(
            int(mouse.pos.x) + 16, int(mouse.pos.y) - 50, 33, 33, self.color
        )
        pyray.draw_rectangle_lines(
            int(mouse.pos.x) + 15, int(mouse.pos.y) - 51, 35, 35, (255, 255, 255, 255)
        )

        # todo silly globals
        pyray.draw_rectangle(
            int(mouse.pos.x) + 16,
            int(mouse.pos.y) - 16,
            16,
            16,
            draw_tool.color_primary,
        )
        pyray.draw_rectangle_lines(
            int(mouse.pos.x) + 15, int(mouse.pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )
        pyray.draw_rectangle(
            int(mouse.pos.x) + 33,
            int(mouse.pos.y) - 16,
            16,
            16,
            draw_tool.color_secondary,
        )
        pyray.draw_rectangle_lines(
            int(mouse.pos.x) + 32, int(mouse.pos.y) - 17, 18, 18, (255, 255, 255, 255)
        )


class GridTool:
    def __init__(self):
        self.active = False
        self.thingy = None

    def update(self):
        self.active = pyray.is_key_down(pyray.KEY_G)

    def update_thingy(self, thingy, mouse, camera):
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

    def draw(self, mouse, camera):
        if not self.active:
            return

        # debug: temp grid icon
        pyray.draw_text_ex(
            hud.font,
            b"#",
            pyray.Vector2(mouse.pos.x + 16, mouse.pos.y - 16),
            24,
            1,
            UI.HUD_TEXT,
        )

        if not self.thingy:
            return

        cell_w = self.thingy.w / self.thingy.cells_x
        cell_h = self.thingy.h / self.thingy.cells_y

        if cell_w.is_integer() and cell_h.is_integer():
            text_color = UI.HUD_TEXT
            cell_dimensions = f"{int(cell_w)}x{int(cell_h)}"
        else:
            text_color = UI.HUD_ERROR
            cell_dimensions = f"{cell_w:.2f}x{cell_h:.2f}"

        text_offset_x = -1 if self.thingy.selected else 0
        text_offset_y = -9 if self.thingy.selected else -8

        pyray.begin_mode_2d(camera.camera)
        pyray.draw_text_ex(
            hud.font,
            str(f"{self.thingy.cells_x}x{self.thingy.cells_y} @ {cell_dimensions}"),
            pyray.Vector2(self.thingy.x + text_offset_x, self.thingy.y + text_offset_y),
            8,
            1,
            text_color,
        )
        pyray.end_mode_2d()


class ThingySpace:
    def __init__(self, grid_size, font, thingies=None):
        self.grid_size = grid_size
        self.font = font
        self.thingies = thingies or []

        self._origin = Origin()
        self._grid_minor = BackgroundGrid(grid_size.x, grid_size.y, UI.GRID_MINOR)
        self._grid_major = BackgroundGrid(
            grid_size.x * 4, grid_size.y * 4, UI.GRID_MAJOR
        )

        self._selection = None  # regular selection
        self._create_selection = None  # "create thingy" selection

        self._hovered_thingy = None

        self._dragged_thingy = None
        self._dragged_thingy_offset = None

        self._resized_thingy = None
        self._resized_thingy_start = None

    def update(self, mouse, camera):
        mouse_world_pos = pyray.get_screen_to_world_2d(mouse.pos, camera.camera)
        self._hovered_thingy = self._get_thingy_at_pos(mouse_world_pos)

        if draw_tool.active:
            draw_tool.update_thingy(self._hovered_thingy, mouse, camera)
        elif grid_tool.active:
            grid_tool.update_thingy(self._hovered_thingy, mouse, camera)
        elif dropper_tool.active:
            dropper_tool.update_thingy(self._hovered_thingy, mouse, camera)
        else:
            # todo: this smooth zoom stuff is super fudged, but feels OK for now
            if wheel := pyray.get_mouse_wheel_move():
                # smooth zoom
                camera.zoom_velocity += camera.zoom_speed * wheel

            # todo: SelectTool (from Selection), CreateTool
            if pyray.is_mouse_button_pressed(pyray.MOUSE_LEFT_BUTTON):
                # Begin regular selection
                for other_thingy in self.thingies:
                    other_thingy.selected = False

                if self._hovered_thingy:
                    self._hovered_thingy.selected = True
                    self._dragged_thingy = self._hovered_thingy
                    self._dragged_thingy_offset = pyray.Vector2(
                        mouse_world_pos.x - self._hovered_thingy.x,
                        mouse_world_pos.y - self._hovered_thingy.y,
                    )
                else:
                    self._selection = Selection(mouse_world_pos)
                    self._dragged_thingy = None

            if pyray.is_mouse_button_down(pyray.MOUSE_RIGHT_BUTTON):
                if self._hovered_thingy and not self._resized_thingy:
                    self._resized_thingy = self._hovered_thingy
                    self._resized_thingy_start = pyray.Vector2(
                        mouse_world_pos.x, mouse_world_pos.y,
                    )
                elif (
                    pyray.is_mouse_button_pressed(pyray.MOUSE_RIGHT_BUTTON)
                    and not self._hovered_thingy
                    and not self._create_selection
                ):
                    # Begin create selection
                    self._create_selection = Selection(mouse_world_pos)

        if pyray.is_key_pressed(pyray.KEY_DELETE):
            keep_thingies = []
            destroy_thingies = []
            for thingy in self.thingies:
                if thingy.selected:
                    destroy_thingies.append(thingy)
                else:
                    keep_thingies.append(thingy)
            self.thingies = keep_thingies
            for thingy in destroy_thingies:
                thingy.destroy()

        if self._selection:
            self._selection.end = mouse_world_pos

            rect = self._selection.rect()
            if rect:
                for thingy in self.thingies:
                    thingy.selected = (
                        (rect.x < thingy.x + thingy.w)
                        and (rect.x + rect.width > thingy.x)
                        and (rect.y < thingy.y + thingy.h)
                        and (rect.y + rect.height > thingy.y)
                    )

        if self._create_selection:
            self._create_selection.end = mouse_world_pos

        if self._dragged_thingy:
            self._dragged_thingy.x = mouse_world_pos.x - self._dragged_thingy_offset.x
            self._dragged_thingy.y = mouse_world_pos.y - self._dragged_thingy_offset.y

            # snap to grid (todo make this a toggle)
            self._dragged_thingy.x = int(
                round(self._dragged_thingy.x / self.grid_size.x) * self.grid_size.x
            )
            self._dragged_thingy.y = int(
                round(self._dragged_thingy.y / self.grid_size.y) * self.grid_size.y
            )

        if pyray.is_mouse_button_released(pyray.MOUSE_LEFT_BUTTON):
            self._selection = None
            self._dragged_thingy = None
            self._dragged_thingy_offset = None

        if pyray.is_mouse_button_released(pyray.MOUSE_RIGHT_BUTTON):
            if self._create_selection:
                rect = self._create_selection.rect(snap=self.grid_size)
                if rect:
                    self.thingies.append(
                        CanvasThingy(
                            x=int(rect.x),
                            y=int(rect.y),
                            w=int(rect.width),
                            h=int(rect.height),
                        )
                    )
                self._create_selection = None
            elif self._resized_thingy:
                # todo perform resize
                self._resized_thingy = None
                self._resized_thingy_start = None

        for thingy in self.thingies:
            thingy.update(mouse, camera)

    def _get_thingy_at_pos(self, pos):
        # note: reversed to match draw order
        # eventually, make selection change the draw order
        for thingy in reversed(self.thingies):
            if (thingy.x <= pos.x < thingy.x + thingy.w) and (
                thingy.y <= pos.y < thingy.y + thingy.h
            ):
                return thingy

    def draw(self, screen, mouse, camera):
        self._grid_minor.draw(screen, camera)
        self._grid_major.draw(screen, camera)

        pyray.begin_mode_2d(camera.camera)

        if not self.thingies:
            self._origin.draw()

        for thingy in self.thingies:
            thingy.draw(self._hovered_thingy)

        if self._selection:
            self._selection.draw(
                UI.SELECTION_FILL, UI.SELECTION_OUTLINE, snap=self.grid_size,
            )

        if self._create_selection:
            self._create_selection.draw(
                UI.CREATE_FILL,
                UI.CREATE_OUTLINE,
                snap=self.grid_size,
                label=True,
                font=self.font,
            )

        if self._resized_thingy:
            # todo draw a box instead of this
            mouse_world_pos = pyray.get_screen_to_world_2d(mouse.pos, camera.camera)
            pyray.draw_line_ex(
                mouse_world_pos, self._resized_thingy_start, 1, (255, 0, 0, 255),
            )

        pyray.end_mode_2d()


class CanvasThingy:
    def __init__(
        self,
        x=0,
        y=0,
        w=None,
        h=None,
        cells_x=1,
        cells_y=1,
        image=None,
        reference=None,
        color=(0, 0, 0, 255),
    ):
        if not w and not h and not image:
            raise ValueError("Expected (w, h) or an image")

        self.x = x
        self.y = y
        # self.image = pyray.gen_image_color(w, h, color)

        # debug: create interesting default images
        self.image = (
            image
            or random.choice(
                [
                    lambda: pyray.gen_image_color(w, h, color),
                    # lambda: pyray.gen_image_white_noise(w, h, 0.05),
                    # lambda: pyray.gen_image_perlin_noise(w, h, 0, 0, 5),
                ]
            )()
        )

        self.w = self.image.width
        self.h = self.image.height
        self.cells_x = cells_x
        self.cells_y = cells_y
        self.cells_visible = False

        self.texture = pyray.load_texture_from_image(self.image)
        self.selected = False
        self.dirty = False

    def update(self, mouse, camera):
        if self.selected:
            # debug: copy to hud font, lol
            # if pyray.is_key_pressed(pyray.KEY_F):
            #     image = pyray.image_copy(
            #         self.image
            #     )  # raylib unloads the image afterward
            #     pyray.unload_font(hud.font)
            #     hud.font = pyray.load_font_from_image(image, (255, 0, 255, 255), 32)

            # debug: save to file
            if (
                pyray.is_key_down(pyray.KEY_LEFT_CONTROL)
                or pyray.is_key_down(pyray.KEY_RIGHT_CONTROL)
            ) and pyray.is_key_pressed(pyray.KEY_S):
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"save/thingy_{self.w}x{self.h}_{timestamp}.png"
                pyray.export_image(self.image, filename)

        if not self.dirty:
            return

        pyray.update_texture(self.texture, pyray.get_image_data(self.image))

    def draw(self, hovered_thingy):
        tint = (255, 255, 255, 255)
        pyray.draw_texture(self.texture, self.x, self.y, tint)

        if self.selected:
            outline_color = UI.THINGY_SELECTED_OUTLINE
        elif self is hovered_thingy:
            outline_color = UI.THINGY_HOVERED_OUTLINE
        else:
            outline_color = UI.THINGY_OUTLINE

        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(self.x - 1, self.y - 1, self.w + 2, self.h + 2),
            1,
            outline_color,
        )

        if self.cells_visible or grid_tool.active:
            color = (
                UI.GRID_CELLS_OBVIOUS
                if self.cells_visible and grid_tool.active
                else UI.GRID_CELLS_SUBTLE
            )
            if self.cells_x > 1:
                for ix in range(1, self.cells_x):
                    x = self.x + ix / self.cells_x * self.w
                    pyray.draw_line(int(x), self.y, int(x), self.y + self.h, color)

            if self.cells_y > 1:
                for iy in range(1, self.cells_y):
                    y = self.y + iy / self.cells_y * self.h
                    pyray.draw_line(self.x, int(y), self.x + self.w, int(y), color)

    def destroy(self):
        pyray.unload_texture(self.texture)
        pyray.unload_image(self.image)


hud = HUD()
draw_tool = DrawTool()
grid_tool = GridTool()
dropper_tool = DropperTool()


def main():
    screen = Screen(800, 600)
    pyray.init_window(screen.w, screen.h, "Dream Table")
    pyray.set_target_fps(60)

    font = pyray.load_font("resources/fonts/alpha_beta.png")
    hud.font = font

    palette_image = pyray.load_image("resources/palettes/sweetie-16-8x.png")
    palette_thingy = CanvasThingy(image=palette_image)

    mouse = Mouse()
    camera = Camera(screen, zoom=4)

    thingy_space = ThingySpace(
        grid_size=pyray.Vector2(8, 8), font=font, thingies=[palette_thingy]
    )

    while not pyray.window_should_close():
        # update
        screen.update()
        mouse.update()
        camera.update(mouse)
        draw_tool.update()
        grid_tool.update()
        dropper_tool.update()
        thingy_space.update(mouse, camera)

        hud.print("Hello, world!")
        hud.print(f"mouse: ({mouse.pos.x}, {mouse.pos.y})")
        hud.print(f"mouse delta: ({mouse.delta.x}, {mouse.delta.y})")
        hud.print(
            f"camera: ({camera.camera.target.x}, {camera.camera.target.y}), zoom {camera.camera.zoom}, zoomvel {camera.zoom_velocity}"
        )

        # debug: will set up proper hotkeys eventually...
        if pyray.is_key_pressed(pyray.KEY_HOME):
            camera.camera.target = pyray.Vector2(0, 0)
        if pyray.is_key_pressed(pyray.KEY_ONE):
            camera.camera.zoom = 1
        if pyray.is_key_pressed(pyray.KEY_TWO):
            camera.camera.zoom = 2
        if pyray.is_key_pressed(pyray.KEY_THREE):
            camera.camera.zoom = 3
        if pyray.is_key_pressed(pyray.KEY_FOUR):
            camera.camera.zoom = 4

        # draw
        pyray.begin_drawing()
        pyray.clear_background(UI.BACKGROUND)
        thingy_space.draw(screen, mouse, camera)
        hud.draw()
        draw_tool.draw(mouse)
        grid_tool.draw(mouse, camera)
        dropper_tool.draw(mouse)
        pyray.end_drawing()

    pyray.close_window()


if __name__ == "__main__":
    main()
