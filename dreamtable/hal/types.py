from dataclasses import dataclass, field
import enum
from typing import Tuple

from dreamtable.hal.geom import Vec2

FontHandle = object
ImageHandle = object
TextureHandle = object


@dataclass
class Color:
    r: int = 0
    g: int = 0
    b: int = 0
    a: int = 0

    @property
    def rgba(self) -> Tuple[int, int, int, int]:
        return self.r, self.g, self.b, self.a


@dataclass
class Camera:
    target: Vec2 = field(default_factory=Vec2)
    offset: Vec2 = field(default_factory=Vec2)
    rotation: float = 0
    zoom: float = 1


class MouseButton(enum.Enum):
    LEFT: int = 0
    RIGHT: int = 1
    MIDDLE: int = 2


class Key(enum.Enum):
    APOSTROPHE: int = 39
    COMMA: int = 44
    MINUS: int = 45
    PERIOD: int = 46
    SLASH: int = 47
    ZERO: int = 48
    ONE: int = 49
    TWO: int = 50
    THREE: int = 51
    FOUR: int = 52
    FIVE: int = 53
    SIX: int = 54
    SEVEN: int = 55
    EIGHT: int = 56
    NINE: int = 57
    SEMICOLON: int = 59
    EQUAL: int = 61
    A: int = 65
    B: int = 66
    C: int = 67
    D: int = 68
    E: int = 69
    F: int = 70
    G: int = 71
    H: int = 72
    I: int = 73
    J: int = 74
    K: int = 75
    L: int = 76
    M: int = 77
    N: int = 78
    O: int = 79
    P: int = 80
    Q: int = 81
    R: int = 82
    S: int = 83
    T: int = 84
    U: int = 85
    V: int = 86
    W: int = 87
    X: int = 88
    Y: int = 89
    Z: int = 90

    # Function keys
    SPACE: int = 32
    ESCAPE: int = 256
    ENTER: int = 257
    TAB: int = 258
    BACKSPACE: int = 259
    INSERT: int = 260
    DELETE: int = 261
    RIGHT: int = 262
    LEFT: int = 263
    DOWN: int = 264
    UP: int = 265
    PAGE_UP: int = 266
    PAGE_DOWN: int = 267
    HOME: int = 268
    END: int = 269
    CAPS_LOCK: int = 280
    SCROLL_LOCK: int = 281
    NUM_LOCK: int = 282
    PRINT_SCREEN: int = 283
    PAUSE: int = 284
    F1: int = 290
    F2: int = 291
    F3: int = 292
    F4: int = 293
    F5: int = 294
    F6: int = 295
    F7: int = 296
    F8: int = 297
    F9: int = 298
    F10: int = 299
    F11: int = 300
    F12: int = 301
    LEFT_SHIFT: int = 340
    LEFT_CONTROL: int = 341
    LEFT_ALT: int = 342
    LEFT_SUPER: int = 343
    RIGHT_SHIFT: int = 344
    RIGHT_CONTROL: int = 345
    RIGHT_ALT: int = 346
    RIGHT_SUPER: int = 347
    KB_MENU: int = 348
    LEFT_BRACKET: int = 91
    BACKSLASH: int = 92
    RIGHT_BRACKET: int = 93
    GRAVE: int = 96

    # Keypad keys
    KP_0: int = 320
    KP_1: int = 321
    KP_2: int = 322
    KP_3: int = 323
    KP_4: int = 324
    KP_5: int = 325
    KP_6: int = 326
    KP_7: int = 327
    KP_8: int = 328
    KP_9: int = 329
    KP_DECIMAL: int = 330
    KP_DIVIDE: int = 331
    KP_MULTIPLY: int = 332
    KP_SUBTRACT: int = 333
    KP_ADD: int = 334
    KP_ENTER: int = 335
    KP_EQUAL: int = 336


class TextureFormat(enum.Enum):
    UNCOMPRESSED_GRAYSCALE: int = 1  # 8 bit per pixel (no alpha)
    UNCOMPRESSED_GRAY_ALPHA: int = 2
    UNCOMPRESSED_R5G6B5: int = 3  # 16 bpp
    UNCOMPRESSED_R8G8B8: int = 4  # 24 bpp
    UNCOMPRESSED_R5G5B5A1: int = 5  # 16 bpp (1 bit alpha)
    UNCOMPRESSED_R4G4B4A4: int = 6  # 16 bpp (4 bit alpha)
    UNCOMPRESSED_R8G8B8A8: int = 7  # 32 bpp
    UNCOMPRESSED_R32: int = 8  # 32 bpp (1 channel - float)
    UNCOMPRESSED_R32G32B32: int = 9  # 32*3 bpp (3 channels - float)
    UNCOMPRESSED_R32G32B32A32: int = 10  # 32*4 bpp (4 channels - float)
    COMPRESSED_DXT1_RGB: int = 11  # 4 bpp (no alpha)
    COMPRESSED_DXT1_RGBA: int = 12  # 4 bpp (1 bit alpha)
    COMPRESSED_DXT3_RGBA: int = 13  # 8 bpp
    COMPRESSED_DXT5_RGBA: int = 14  # 8 bpp
    COMPRESSED_ETC1_RGB: int = 15  # 4 bpp
    COMPRESSED_ETC2_RGB: int = 16  # 4 bpp
    COMPRESSED_ETC2_EAC_RGBA: int = 17  # 8 bpp
    COMPRESSED_PVRT_RGB: int = 18  # 4 bpp
    COMPRESSED_PVRT_RGBA: int = 19  # 4 bpp
    COMPRESSED_ASTC_4x4_RGBA: int = 20  # 8 bpp
    COMPRESSED_ASTC_8x8_RGBA: int = 21  # 2 bpp
