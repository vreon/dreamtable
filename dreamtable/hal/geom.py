"""
Geometry classes.
"""

# Original implementation from `vecrec`: https://github.com/kxgames/vecrec
# Removed autoprop, added more strict typing + annotations, broke things
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Kale Kundert and Alex Mitchell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import math
import operator
import random
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Tuple, Union

BinaryOperator = Callable[[Any, Any], Any]
Vec2Operand = Union["Vec2", float]
Vec2Operator = Callable[["Vec2", Vec2Operand], "Vec2"]

PHI = GOLDEN_RATIO = 1 / 2 + math.sqrt(5) / 2


def _overload_left_side(f: BinaryOperator) -> Vec2Operator:
    """Helper function to make left-side operators."""

    def operator(self: Vec2, other: Vec2Operand) -> Vec2:
        if isinstance(other, Vec2):
            x, y = other.x, other.y
        else:
            x = y = other
        return Vec2(f(self.x, x), f(self.y, y))

    return operator


def _overload_right_side(f: BinaryOperator) -> Vec2Operator:
    """Helper function to make right-side operators."""

    def operator(self: Vec2, other: Any) -> Vec2:
        if isinstance(other, Vec2):
            x, y = other.x, other.y
        else:
            x = y = other
        return Vec2(f(x, self.x), f(y, self.y))

    return operator


def _overload_in_place(f: BinaryOperator) -> Vec2Operator:
    """Helper function to make in-place operators."""

    def operator(self: Vec2, other: Any) -> Vec2:
        if isinstance(other, Vec2):
            x, y = other.x, other.y
        else:
            x = y = other
        self.x, self.y = f(self.x, x), f(self.y, y)
        return self

    return operator


@dataclass
class Vec2:
    """
    A mutable two-dimensional vector.
    """

    x: float = 0
    y: float = 0

    @staticmethod
    def random(magnitude: float = 1) -> Vec2:
        """Create a unit vector pointing in a random direction."""
        theta = random.uniform(0, 2 * math.pi)
        return magnitude * Vec2(math.cos(theta), math.sin(theta))

    @staticmethod
    def from_radians(angle: float) -> Vec2:
        """Create a unit vector that makes the given angle with the x-axis."""
        return Vec2(math.cos(angle), math.sin(angle))

    @staticmethod
    def from_degrees(angle: float) -> Vec2:
        """Create a unit vector that makes the given angle with the x-axis."""
        return Vec2.from_radians(angle * math.pi / 180)

    @staticmethod
    def from_scalar(scalar: float) -> Vec2:
        """Create a vector from a single scalar value."""
        return Vec2(scalar, scalar)

    @staticmethod
    def from_rectangle(rect: Rect) -> Vec2:
        """Create a vector randomly within the given rectangle."""
        x = rect.x + rect.width * random.uniform(0, 1)
        y = rect.y + rect.height * random.uniform(0, 1)
        return Vec2(x, y)

    def copy(self) -> Vec2:
        """Return a copy of this vector."""
        return Vec2(self.x, self.y)

    def assign(self, other: Vec2) -> None:
        """Copy the given vector into this one."""
        self.x, self.y = other.xy

    def normalize(self) -> None:
        """
        Set the magnitude of this vector to unity, in place.
        Note: |0| is 0, because video games.
        """
        try:
            self /= self.magnitude
        except ZeroDivisionError:
            self.x = self.y = 0

    def scale(self, magnitude: float) -> None:
        """Set the magnitude of this vector in place."""
        self.normalize()
        self *= magnitude

    def interpolate(self, target: Vec2, alpha: float) -> None:
        """Linearly interpolate this vector toward the target by the given
        alpha (between 0 and 1)."""
        self.assign((1 - alpha) * self + alpha * target)

    def project(self, axis: Vec2) -> None:
        """Project this vector onto the given axis."""
        projection = self.projection(axis)
        self.assign(projection)

    def zero(self) -> None:
        self.x = self.y = 0

    def dot_product(self, other: Vec2) -> float:
        """Return the dot product of the given vectors."""
        return self.x * other.x + self.y * other.y

    def perp_product(self, other: Vec2) -> float:
        """Return the perp product of the given vectors.  The perp product is
        just a cross product where the third dimension is taken to be zero and
        the result is returned as a scalar."""

        return self.x * other.y - self.y * other.x

    def rotate(self, angle: float) -> None:
        """
        Rotate the given vector by an angle. Angle measured in radians
        counter-clockwise.
        """
        x, y = self.xy
        self.x = x * math.cos(angle) - y * math.sin(angle)
        self.y = x * math.sin(angle) + y * math.cos(angle)

    def round(self, digits: int = 0) -> None:
        """
        Round the elements of the given vector to the given number of digits.
        """
        self.x = round(self.x, digits)
        self.y = round(self.y, digits)

    def floor(self) -> None:
        """
        Round the elements of the given vector down to the nearest integer.
        """
        self.x = math.floor(self.x)
        self.y = math.floor(self.y)

    def __iter__(self) -> Iterator[float]:
        """Iterate over this vector's coordinates."""
        yield self.x
        yield self.y

    def __bool__(self) -> bool:
        """Return true is the vector is not the zero vector."""
        return not (self.x == 0 and self.y == 0)

    __nonzero__ = __bool__

    def __getitem__(self, i: int) -> float:
        """Return the specified coordinate."""
        return self.xy[i]

    def __neg__(self) -> Vec2:
        """Return a copy of this vector with the signs flipped."""
        return Vec2(-self.x, -self.y)

    def __abs__(self) -> Vec2:
        """Return the absolute value of this vector."""
        return Vec2(abs(self.x), abs(self.y))

    __add__ = _overload_left_side(operator.add)
    __radd__ = _overload_right_side(operator.add)
    __iadd__ = _overload_in_place(operator.add)

    __sub__ = _overload_left_side(operator.sub)
    __rsub__ = _overload_right_side(operator.sub)
    __isub__ = _overload_in_place(operator.sub)

    __mul__ = _overload_left_side(operator.mul)
    __rmul__ = _overload_right_side(operator.mul)
    __imul__ = _overload_in_place(operator.mul)

    __floordiv__ = _overload_left_side(operator.floordiv)
    __rfloordiv__ = _overload_right_side(operator.floordiv)
    __ifloordiv__ = _overload_in_place(operator.floordiv)

    __truediv__ = _overload_left_side(operator.truediv)
    __rtruediv__ = _overload_right_side(operator.truediv)
    __itruediv__ = _overload_in_place(operator.truediv)

    __div__ = __truediv__
    __rdiv__ = __rtruediv__
    __idiv__ = __itruediv__

    __mod__ = _overload_left_side(operator.mod)
    __rmod__ = _overload_right_side(operator.mod)
    __imod__ = _overload_in_place(operator.mod)

    __pow__ = _overload_left_side(operator.pow)
    __rpow__ = _overload_right_side(operator.pow)
    __ipow__ = _overload_in_place(operator.pow)

    @property
    def xy(self) -> Tuple[float, float]:
        """Return the vector as a tuple."""
        return self.x, self.y

    @xy.setter
    def xy(self, xy: Tuple[float, float]) -> None:
        """Set the x and y coordinates of this vector from a tuple."""
        self.x, self.y = xy

    @property
    def magnitude(self) -> float:
        """Calculate the length of this vector."""
        return math.sqrt(self.magnitude_squared)

    @magnitude.setter
    def magnitude(self, scale: float) -> None:
        """Set the magnitude of this vector.   This is an alias for
        `scale()`."""
        self.scale(scale)

    @property
    def magnitude_squared(self) -> float:
        """Calculate the square of the length of this vector.  This is
        slightly more efficient that finding the real length."""
        return self.x ** 2 + self.y ** 2

    def distance(self, other: Vec2) -> float:
        """Return the Euclidean distance between the two input vectors."""
        return (other - self).magnitude

    def distance_squared(self, other: Vec2) -> float:
        """Return the squared Euclidean distance between the two input vectors."""
        return (other - self).magnitude_squared

    def manhattan(self, other: Vec2) -> float:
        """Return the Manhattan distance between the two input vectors."""
        return sum(abs(other - self))

    @property
    def normalized(self) -> Vec2:
        """Return a normalized copy of this vector."""
        result = self.copy()
        result.normalize()
        return result

    @property
    def orthogonal(self) -> Vec2:
        """Return a vector that is orthogonal to this one.  The resulting
        vector is not normalized."""
        return Vec2(-self.y, self.x)

    @property
    def orthonormal(self) -> Vec2:
        """Return a vector that is orthogonal to this one and that has been
        normalized."""
        return self.orthogonal.normalized

    def scaled(self, magnitude: float) -> Vec2:
        """Return a scaled vector parallel to this one."""
        result = self.copy()
        result.scale(magnitude)
        return result

    def interpolated(self, target: Vec2, alpha: float) -> Vec2:
        """Return a new vector that has been interpolated toward the given target by
        the given alpha (between 0 and 1)."""
        result = self.copy()
        result.interpolate(target, alpha)
        return result

    def projection(self, axis: Vec2) -> Vec2:
        """Return the projection of this vector onto the given axis.  The
        axis does not need to be normalized."""
        scale = axis.dot(self) / axis.dot(axis)
        return axis * scale

    def components(self, other: Vec2) -> Tuple[Vec2, Vec2]:
        """Break this vector into one vector that is perpendicular to the
        given vector and another that is parallel to it."""
        tangent = self.projection(other)
        normal = self - tangent
        return normal, tangent

    @property
    def radians(self) -> float:
        """Return the angle between this vector and the positive x-axis
        measured in radians.  Result will be between -pi and pi."""
        if not self:
            raise ValueError("Undefined for zero vector")
        return math.atan2(self.y, self.x)

    @radians.setter
    def radians(self, angle: float) -> None:
        """Set the angle that this vector makes with the x-axis."""
        self._x, self._y = math.cos(angle), math.sin(angle)

    @property
    def positive_radians(self) -> float:
        """Return the positive angle between this vector and the positive x-axis
        measured in radians."""
        return (2 * math.pi + self.radians) % (2 * math.pi)

    @property
    def degrees(self) -> float:
        """Return the angle between this vector and the positive x-axis measured
        in degrees."""
        return self.radians * 180 / math.pi

    @degrees.setter
    def degrees(self, angle: float) -> None:
        """Set the angle that this vector makes with the x-axis."""
        self.radians = angle * math.pi / 180

    def radians_to(self, other: Vec2) -> float:
        """Return the angle between the two given vectors in radians.  If
        either of the inputs are zero vectors, ValueError is raised."""
        return other.radians - self.radians

    def degrees_to(self, other: Vec2) -> float:
        """Return the angle between the two given vectors in degrees.  If
        either of the inputs are zero vectors, ValueError is raised."""
        return other.degrees - self.degrees

    def rotated(self, angle: float) -> Vec2:
        """Return a vector rotated by angle from the given vector.  Angle
        measured in radians counter-clockwise."""
        result = self.copy()
        result.rotate(angle)
        return result

    def rounded(self, digits: int) -> Vec2:
        """Return a vector with the elements rounded to the given number of
        digits."""
        result = self.copy()
        result.round(digits)
        return result

    @property
    def floored(self) -> Vec2:
        """Return a vector with the elements rounded down to the nearest integer."""
        result = self.copy()
        result.floor()
        return result

    # Aliases
    dot = dot_product
    perp = perp_product


@dataclass
class Rect:
    """
    A mutable two-dimensional rectangle.
    """

    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0

    #     @accept_anything_as_vector
    #     def __add__(self, vector):
    #         result = self.copy()
    #         result.displace(vector)
    #         return result

    #     @accept_anything_as_vector
    #     def __iadd__(self, vector):
    #         self.displace(vector)
    #         return self

    #     @accept_anything_as_vector
    #     def __sub__(self, vector):
    #         result = self.copy()
    #         result.displace(-vector)
    #         return result

    #     @accept_anything_as_vector
    #     def __isub__(self, vector):
    #         self.displace(-vector)
    #         return self

    def __contains__(self, other: Union[Vec2, Rect]) -> bool:
        return self.contains(other)

    @staticmethod
    def from_size(width: float, height: float) -> Rect:
        """Create a rectangle with the given width and height.  The bottom-left
        corner will be on the origin."""
        return Rect(0, 0, width, height)

    #     @staticmethod
    #     def from_width(width, ratio=1 / PHI):
    #         """Create a rectangle with the given width.  The height will be
    #         calculated from the given ratio, or the golden ratio by default."""
    #         return Rect.from_size(width, ratio * width)

    #     @staticmethod
    #     def from_height(height, ratio=PHI):
    #         """Create a rectangle with the given height.  The width will be
    #         calculated from the given ratio, or the golden ratio by default."""
    #         return Rect.from_size(ratio * height, height)

    #     @staticmethod
    #     def from_square(size):
    #         """Create a rectangle with the same width and height."""
    #         return Rect.from_size(size, size)

    #     @staticmethod
    #     def from_dimensions(left, bottom, width, height):
    #         """Create a rectangle with the given dimensions.  This is an alias for
    #         the constructor."""
    #         return Rect(left, bottom, width, height)

    #     @staticmethod
    #     def from_sides(left, top, right, bottom):
    #         """Create a rectangle with the specified edge coordinates."""
    #         width = right - left
    #         height = top - bottom
    #         return Rect.from_dimensions(left, bottom, width, height)

    #     @staticmethod
    #     def from_corners(v1, v2):
    #         """Create the rectangle defined by the two corners.  The corners can be
    #         specified in any order."""
    #         v1 = cast_anything_to_vector(v1)
    #         v2 = cast_anything_to_vector(v2)

    #         left = min(v1.x, v2.x)
    #         top = max(v1.y, v2.y)
    #         right = max(v1.x, v2.x)
    #         bottom = min(v1.y, v2.y)

    #         return Rect.from_sides(left, top, right, bottom)

    #     @staticmethod
    #     def from_bottom_left(position, width, height):
    #         """Create a rectangle with the given width, height, and bottom-left
    #         corner."""
    #         position = cast_anything_to_vector(position)
    #         return Rect(position.x, position.y, width, height)

    #     @staticmethod
    #     def from_center(position, width, height):
    #         """Create a rectangle with the given dimensions centered at the given
    #         position."""
    #         position = cast_anything_to_vector(position) - (width / 2, height / 2)
    #         return Rect(position.x, position.y, width, height)

    @staticmethod
    def from_top_left(position: Vec2) -> Rect:
        """Create a rectangle from a vector.  The rectangle will have no area,
        and its top left corner will be the same as the vector."""
        return Rect(position.x, position.y, 0, 0)

    #     @staticmethod
    #     def from_points(*points):
    #         """Create a rectangle that contains all the given points."""
    #         left = min(cast_anything_to_vector(p).x for p in points)
    #         top = max(cast_anything_to_vector(p).y for p in points)
    #         right = max(cast_anything_to_vector(p).x for p in points)
    #         bottom = min(cast_anything_to_vector(p).y for p in points)
    #         return Rect.from_sides(left, top, right, bottom)

    #     @staticmethod
    #     def from_union(*inputs):
    #         """Create a rectangle that contains all the given inputs.  Each input
    #         must implement the `Shape` interface."""
    #         rects = [cast_shape_to_rectangle(x) for x in inputs]
    #         left = min(x.left for x in rects)
    #         top = max(x.top for x in rects)
    #         right = max(x.right for x in rects)
    #         bottom = min(x.bottom for x in rects)
    #         return Rect.from_sides(left, top, right, bottom)

    #     @staticmethod
    #     def from_intersection(*inputs):
    #         """Create a rectangle that represents the overlapping area between all
    #         the given inputs.  Each input must implement the `Shape` interface."""
    #         rects = [cast_shape_to_rectangle(x) for x in inputs]
    #         left = max(x.left for x in rects)
    #         top = min(x.top for x in rects)
    #         right = min(x.right for x in rects)
    #         bottom = max(x.bottom for x in rects)
    #         return Rect.from_sides(left, top, right, bottom)

    def grow(self, *padding: float) -> None:
        """Grow this rectangle by the given padding on all sides."""
        try:
            tpad, rpad, bpad, lpad = padding
        except ValueError:
            lpad = rpad = tpad = bpad = padding[0]

        self.y -= bpad
        self.x -= lpad
        self.width += lpad + rpad
        self.height += tpad + bpad

    #     def shrink(self, *padding):
    #         """
    #         Shrink this rectangle by the given padding on all sides.

    #         The padding can either be a single number (to be applied to all sides), or
    #         a tuple of 4 number (to be applied to the left, right, top, and bottom,
    #         respectively).
    #         """
    #         try:
    #             lpad, rpad, tpad, bpad = padding
    #         except ValueError:
    #             lpad = rpad = tpad = bpad = padding[0]

    #         self._bottom += bpad
    #         self._left += lpad
    #         self._width -= lpad + rpad
    #         self._height -= tpad + bpad
    #         return self

    #     @accept_anything_as_vector
    #     def displace(self, vector):
    #         """Displace this rectangle by the given vector."""
    #         self._bottom += vector.y
    #         self._left += vector.x
    #         return self

    #     def round(self, digits=0):
    #         """Round the dimensions of the given rectangle to the given number of digits."""
    #         self._left = round(self._left, digits)
    #         self._bottom = round(self._bottom, digits)
    #         self._width = round(self._width, digits)
    #         self._height = round(self._height, digits)

    #     def set(self, shape):
    #         """Fill this rectangle with the dimensions of the given shape."""
    #         self.bottom, self.left = shape.bottom, shape.left
    #         self.width, self.height = shape.width, shape.height
    #         return self

    def copy(self) -> Rect:
        """Return a copy of this rectangle."""
        return Rect(self.x, self.y, self.width, self.height)

    #     @accept_shape_as_rectangle
    #     def inside(self, other):
    #         """Return true if this rectangle is inside the given shape."""
    #         return (
    #             self.left >= other.left
    #             and self.right <= other.right
    #             and self.top <= other.top
    #             and self.bottom >= other.bottom
    #         )

    #     @accept_anything_as_rectangle
    #     def outside(self, other):
    #         """Return true if this rectangle is outside the given shape."""
    #         return not self.touching(other)

    def touching(self, other: Rect) -> bool:
        """Return true if this rectangle is touching the given shape."""
        if self.y > other.bottom:
            return False
        if self.bottom < other.y:
            return False

        if self.x > other.right:
            return False
        if self.right < other.x:
            return False

        return True

    def contains(self, other: Union[Vec2, Rect]) -> bool:
        """Return true if the other Vec2 or Rect is inside this rectangle."""
        if isinstance(other, Vec2):
            return (self.x <= other.x < self.right) and (
                self.y <= other.y < self.bottom
            )
        else:
            return (
                self.x <= other.x
                and self.right >= other.right
                and self.y >= other.y
                and self.bottom <= other.bottom
            )

    #     @accept_anything_as_rectangle
    #     def align_left(self, target):
    #         """Make the left coordinate of this rectangle equal to that of the
    #         given rectangle."""
    #         self.left = target.left

    #     @accept_anything_as_rectangle
    #     def align_center_x(self, target):
    #         """Make the center-x coordinate of this rectangle equal to that of the
    #         given rectangle."""
    #         self.center_x = target.center_x

    #     @accept_anything_as_rectangle
    #     def align_right(self, target):
    #         """Make the right coordinate of this rectangle equal to that of the
    #         given rectangle."""
    #         self.right = target.right

    #     @accept_anything_as_rectangle
    #     def align_top(self, target):
    #         """Make the top coordinate of this rectangle equal to that of the
    #         given rectangle."""
    #         self.top = target.top

    #     @accept_anything_as_rectangle
    #     def align_center_y(self, target):
    #         """Make the center-y coordinate of this rectangle equal to that of the
    #         given rectangle."""
    #         self.center_y = target.center_y

    #     @accept_anything_as_rectangle
    #     def align_bottom(self, target):
    #         """Make the bottom coordinate of this rectangle equal to that of the
    #         given rectangle."""
    #         self.bottom = target.bottom

    #     # Scalar properties

    #     def get_left(self):
    #         return self._left

    #     def set_left(self, x):
    #         self._left = x

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    #     def set_center_x(self, x):
    #         self._left = x - self._width / 2

    @property
    def right(self) -> float:
        return self.x + self.width

    #     def set_right(self, x):
    #         self._left = x - self._width

    #     def get_top(self):
    #         return self._bottom + self._height

    #     def set_top(self, y):
    #         self._bottom = y - self._height

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    #     def set_center_y(self, y):
    #         self._bottom = y - self._height / 2

    @property
    def bottom(self) -> float:
        return self.y + self.height

    #     def set_bottom(self, y):
    #         self._bottom = y

    #     def get_area(self):
    #         return self._width * self._height

    #     def get_width(self):
    #         return self._width

    #     def set_width(self, width):
    #         self._width = width

    #     def get_height(self):
    #         return self._height

    #     def set_height(self, height):
    #         self._height = height

    #     def get_half_width(self):
    #         return self._width / 2

    #     def set_half_width(self, half_width):
    #         self._width = 2 * half_width

    #     def get_half_height(self):
    #         return self._height / 2

    #     def set_half_height(self, half_height):
    #         self._height = 2 * half_height

    #     # Vec2 properties

    #     def get_top_left(self):
    #         return Vec2(self.left, self.top)

    #     @accept_anything_as_vector
    #     def set_top_left(self, point):
    #         self.top = point[1]
    #         self.left = point[0]

    #     def get_top_center(self):
    #         return Vec2(self.center_x, self.top)

    #     @accept_anything_as_vector
    #     def set_top_center(self, point):
    #         self.top = point[1]
    #         self.center_x = point[0]

    #     def get_top_right(self):
    #         return Vec2(self.right, self.top)

    #     @accept_anything_as_vector
    #     def set_top_right(self, point):
    #         self.top = point[1]
    #         self.right = point[0]

    #     def get_center_left(self):
    #         return Vec2(self.left, self.center_y)

    #     @accept_anything_as_vector
    #     def set_center_left(self, point):
    #         self.center_y = point[1]
    #         self.left = point[0]

    @property
    def center(self) -> Vec2:
        return Vec2(self.center_x, self.center_y)

    #     @accept_anything_as_vector
    #     def set_center(self, point):
    #         self.center_y = point[1]
    #         self.center_x = point[0]

    #     def get_center_right(self):
    #         return Vec2(self.right, self.center_y)

    #     @accept_anything_as_vector
    #     def set_center_right(self, point):
    #         self.center_y = point[1]
    #         self.right = point[0]

    #     def get_bottom_left(self):
    #         return Vec2(self.left, self.bottom)

    #     @accept_anything_as_vector
    #     def set_bottom_left(self, point):
    #         self.bottom = point[1]
    #         self.left = point[0]

    #     def get_bottom_center(self):
    #         return Vec2(self.center_x, self.bottom)

    #     @accept_anything_as_vector
    #     def set_bottom_center(self, point):
    #         self.bottom = point[1]
    #         self.center_x = point[0]

    #     def get_bottom_right(self):
    #         return Vec2(self.right, self.bottom)

    #     @accept_anything_as_vector
    #     def set_bottom_right(self, point):
    #         self.bottom = point[1]
    #         self.right = point[0]

    #     def get_vertices(self):
    #         return self.top_left, self.top_right, self.bottom_right, self.bottom_left

    #     def set_vertices(self, vertices):
    #         self.top_left = vertices[0]
    #         self.top_right = vertices[1]
    #         self.bottom_right = vertices[2]
    #         self.bottom_left = vertices[3]

    @property
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    #     def set_size(self, width, height):
    #         self._width = width
    #         self._height = height

    #     def get_size_as_int(self):
    #         from math import ceil

    #         return Vec2(int(ceil(self._width)), int(ceil(self._height)))

    #     def get_dimensions(self):
    #         return (self._left, self._bottom), (self._width, self._height)

    @property
    def xywh(self) -> Tuple[float, float, float, float]:
        return self.x, self.y, self.width, self.height

    #     # Rect properties

    #     def get_union(self, *rectangles):
    #         return Rect.from_union(self, *rectangles)

    #     def get_intersection(self, *rectangles):
    #         return Rect.from_intersection(self, *rectangles)

    def grown(self, *padding: float) -> Rect:
        result = self.copy()
        result.grow(*padding)
        return result

    #     def get_shrunk(self, padding):
    #         result = self.copy()
    #         result.shrink(padding)
    #         return result

    #     def get_rounded(self, digits=0):
    #         result = self.copy()
    #         result.round(digits)
    #         return result

    def floor(self) -> None:
        self.x = math.floor(self.x)
        self.y = math.floor(self.y)
        self.width = math.floor(self.width)
        self.height = math.floor(self.height)

    @property
    def floored(self) -> Rect:
        result = self.copy()
        result.floor()
        return result
