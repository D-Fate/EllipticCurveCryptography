import ECCBackend.tools as tools
from ECCBackend.curves.field_element import FieldElement
from ECCBackend.exceptions import UnsupportedPointFormatException


class NaiveOrderCalculation(object):
    def naive_order_calculation(self):
        """ Calculates the order of the point naively, i.e.
            by walking through all points until the given neutral element is
            hit. Note that this only works for smallest of curves and is not
            computationally feasible for anything else.
        """
        current_point = self
        order = 1
        while not current_point.is_neutral:
            order += 1
            current_point += self
        return order


class Serialization(object):
    def serialize_uncompressed(self):
        """ Serializes the point into a bytes object in uncompressed form. """
        length = (self.curve.modulus.bit_length() + 7) // 8
        serialized = bytes([0x04]) + \
                     tools.int_to_bytes(int(self.x), length) + \
                     tools.int_to_bytes(int(self.y), length)
        return serialized

    @classmethod
    def deserialize_uncompressed(cls, data, curve=None):
        """ Deserializes a curve point which is given in uncompressed form. A
            curve may be passed with the 'curve' argument in which case an
            Point is returned from this method. Otherwise, X and Y coordinates
            are returned as a tuple.
        """
        if data[0] != 0x04:
            raise UnsupportedPointFormatException(
                'Generator point of explicitly encoded curve is given in'
                'unsupported form (0x%x).' % data[0]
            )
        data = data[1:]
        assert ((len(data) % 2) == 0)
        px = tools.bytes_to_int(data[: len(data) // 2])
        py = tools.bytes_to_int(data[len(data) // 2:])
        if curve is not None:
            return cls(px, py, curve)
        return px, py


class ScalarMultiplicationXOnly:
    """ Compute an X-only ladder scalar multiplication of the private key and
        the X coordinate of a given point.
    """

    def _x_double(self, x):
        """ Doubling of point with coordinate x. """
        if x is None:
            return None
        den = 4 * (x ** 3 + self.curve.a * x + self.curve.b)
        if den == 0:
            # Point at infinity
            return None
        num = (x ** 2 - self.curve.a) ** 2 - (8 * self.curve.b * x)
        return num // den

    def _x_add_multiplicative(self, x1, x2, x3prime):
        """ Multiplicative formula addition of x1 + x2, where x3' is
            the difference in X of P1 - P2. Using this function only makes
            sense where (P1 - P2) is fixed, as it is in
            the ladder implementation.
        """
        if x1 is None:
            return x2
        if x2 is None:
            return x1
        if x1 == x2:
            return None
        num = -4 * self.curve.b * (x1 + x2) + (x1 * x2 - self.curve.a) ** 2
        den = x3prime * (x1 - x2) ** 2
        result = num // den
        return result

    def _x_add_additive(self, x1, x2, x3prime):
        """ Additive formula addition of x1 + x2, where x3' is the difference in
            X of P1 - P2. Using this function only makes sense where (P1 - P2)
            is fixed, as it is in the ladder implementation.
        """
        if x1 is None:
            return x2
        if x2 is None:
            return x1
        if x1 == x2:
            return None
        num = 2 * (x1 + x2) * (x1 * x2 + self.curve.a) + 4 * self.curve.b
        den = (x1 - x2) ** 2
        result = num // den - x3prime
        return result

    def _x_add(self, x1, x2, x3prime):
        """ There are two equivalent implementations, one using the
            multiplicative and the other using the additive representation. Both
            should work equally well.
        """
        return self._x_add_multiplicative(x1, x2, x3prime)

    def scalar_mul_xonly(self, scalar):
        """ This implements the X-coordinate-only multiplication algorithm of a
            Short Weierstrass curve with the X coordinate of a given point.
            Reference is "Izu and Takagi: A Fast Parallel Elliptic Curve
            Multiplication Resistant against Side Channel Attacks" (2002)
        """
        if self.is_neutral:
            # Point at infinity is input
            return None
        if scalar == 0:
            # Multiplication with zero -> point at infinity is output
            return None

        x_coordinate = int(self.x)
        if not isinstance(x_coordinate, FieldElement):
            x_coordinate = FieldElement(x_coordinate, self.curve.modulus)
        q = [x_coordinate, self._x_double(x_coordinate), None]
        for bit_number in reversed(range(scalar.bit_length() - 1)):
            bit = (scalar >> bit_number) & 1
            q[2] = self._x_double(q[bit])
            q[1] = self._x_add(q[0], q[1], x_coordinate)
            q[0] = q[2 - bit]
            q[1] = q[1 + bit]
        return q[0]
