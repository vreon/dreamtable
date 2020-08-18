import math
import random


# XXX: Something's wrong with pyray.image_draw_line
# here's Bresenham from Wikipedia lol
def draw_line(x1, y1, x2, y2, draw_pixel):
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
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


def rect_rect_intersect(rect_a, rect_b):
    return (
        (rect_a.x < rect_b.x + rect_b.width)
        and (rect_a.x + rect_a.width > rect_b.x)
        and (rect_a.y < rect_b.y + rect_b.height)
        and (rect_a.y + rect_a.height > rect_b.y)
    )


def point_rect_intersect(x, y, rect):
    return (rect.x <= x < rect.x + rect.width) and (rect.y <= y < rect.y + rect.height)


def get_aabb(x1, y1, x2, y2, snap_x=0, snap_y=0):
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


def get_outline_rect(rect):
    return (rect.x - 1, rect.y - 1, rect.width + 2, rect.height + 2)


def make_random_vector(dims):
    vec = [random.gauss(0, 1) for i in range(dims)]
    mag = sum(x ** 2 for x in vec) ** 0.5
    return [x / mag for x in vec]
