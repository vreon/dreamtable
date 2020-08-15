"""
Drawing-related helpers.
"""


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
