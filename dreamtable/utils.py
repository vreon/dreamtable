import math
from typing import Any, Callable, Tuple


# XXX: Something's wrong with pyray.image_draw_line
# here's Bresenham from Wikipedia lol
def draw_line(
    x1: int, y1: int, x2: int, y2: int, draw_pixel: Callable[[int, int], Any]
) -> None:
    dx = abs(x2 - x1)
    sx = 1 if x1 < x2 else -1
    dy = -abs(y2 - y1)
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        draw_pixel(x1, y1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy


def point_rect_intersect(
    x: float, y: float, rx: float, ry: float, rw: float, rh: float
) -> bool:
    return (rx <= x < rx + rw) and (ry <= y < ry + rh)


def get_aabb(
    x1: float, y1: float, x2: float, y2: float, snap_x: int = 0, snap_y: int = 0
) -> Tuple[float, float, float, float]:
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

    return (x1, y1, width, height)


def get_outline_rect(
    x: float, y: float, w: float, h: float
) -> Tuple[float, float, float, float]:
    return (x - 1, y - 1, w + 2, h + 2)
