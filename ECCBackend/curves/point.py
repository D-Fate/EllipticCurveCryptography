from ECCBackend.curves.field_element import FieldElement
from ECCBackend.curves.point_operations import NaiveOrderCalculation, \
    Serialization, ScalarMultiplicationXOnly


class Point(NaiveOrderCalculation, Serialization,
            ScalarMultiplicationXOnly):
    def __init__(self, x: int | None, y: int | None, curve):
        """ Generate a curve point (x, y) on the curve 'curve'. x and y have to
            be integers. If the neutral element of the group O
            (for some curves, this is a point at infinity) should be created,
            use the static method 'neutral', since representations of O
            differ on various curves (e.g. in short Weierstrass curves, they
            have no explicit notation in affine space while on twisted Edwards
            curves they do.
        """
        assert (((x is None) and (y is None)) or
                ((x is not None) and (y is not None)))
        if x is None:
            # infinity
            self._x = None
            self._y = None
        else:
            self._x = FieldElement(x, curve.modulus)
            self._y = FieldElement(y, curve.modulus)
        self._curve = curve

    @staticmethod
    def neutral(curve):
        """ Returns the neutral element of the curve group. """
        return curve.neutral()

    @property
    def is_neutral(self):
        """ Indicates if the point is the neutral element O of the curve (point
            at infinity for some curves). """
        return self.curve.is_neutral(self)

    @property
    def x(self):
        """ Affine X component of the point, field element of p. """
        return self._x

    @property
    def y(self):
        """ Affine Y component of the point, field element of p. """
        return self._y

    @property
    def curve(self):
        """ Curve that the point is located on. """
        return self._curve

    def __add__(self, other):
        """ Returns the point addition. """
        assert (isinstance(other, Point))
        return self.curve.point_addition(self, other)

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        """ Returns the conjugated point. """
        return self.curve.point_conjugate(self)

    def __mul__(self, scalar: int):
        """ Returns the scalar point multiplication. The scalar needs to be an
            integer value.
        """
        assert (scalar >= 0)

        result = self.curve.neutral()
        n = self
        if scalar > 0:
            for bit in range(scalar.bit_length()):
                if scalar & (1 << bit):
                    result += n
                n += n
        return result

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.x, self.y))

    def on_curve(self):
        """ Indicates if the given point is satisfying the curve equation (i.e.
            if it is a point on the curve).
        """
        return self.curve.on_curve(self)

    def compress(self):
        """ Returns the compressed point format (if this is possible on the
            given curve).
        """
        return self.curve.compress(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.is_neutral:
            return '(neutral)'
        return '(0x%x, 0x%x)' % (int(self.x), int(self.y))
