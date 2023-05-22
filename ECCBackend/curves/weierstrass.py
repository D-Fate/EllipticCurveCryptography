import collections

from ECCBackend.curves.ec import EllipticCurve
from ECCBackend.curves.field_element import FieldElement
from ECCBackend.curves.point import Point

_ShortWeierstrassCurveDomainParameters = collections.namedtuple(
    'ShortWeierstrassCurveDomainParameters',
    ['curvetype', 'a', 'b', 'p', 'n', 'h', 'G']
)


class ShortWeierstrass(EllipticCurve):
    """ Represents an elliptic curve over a finite field F_P that satisfies the
        short Weierstrass equation y^2 = x^3 + ax + b.
    """
    pretty_name = 'Short Weierstrass'

    def __init__(self, a: int, b: int,
                 modulus, order, cofactor, gen_x, gen_y, **kwargs):
        EllipticCurve.__init__(
            self, modulus, order, cofactor, gen_x, gen_y, **kwargs
        )
        self._a = FieldElement(a, modulus)
        self._b = FieldElement(b, modulus)
        self._name = kwargs.get('name')

        # Check that the curve is not singular
        assert ((4 * (self.a ** 3)) + (27 * (self.b ** 2)) != 0)

        if self._gen is not None:
            assert (self._gen.on_curve())

            if self.order is not None:
                # Check that the generator G is of curve order if a order was
                # passed as well
                assert (self.order * self.gen).is_neutral

    @classmethod
    def init_rawcurve(cls, a, b, p):
        """ Returns a raw curve which has an undiscovered amount of points
            #E(F_p) (i.e. the domain parameters n and h are not set). This
            function can be used to create a curve which is later completed by
            counting #E(F_p) using Schoof's algorithm.
        """
        return cls(a=a, b=b, modulus=p, order=None,
                   cofactor=None, gen_x=None, gen_y=None)

    @property
    def is_anomalous(self):
        """ Returns if the curve is anomalous, i.e. if #F(p) == p. If this is
            the case then there is an efficient method to solve the ECDLP.
            Therefore, the curve is not suitable for cryptographic use.
        """
        return self.jinv in [0, 1728]

    @property
    def domain_params(self):
        return _ShortWeierstrassCurveDomainParameters(
            curvetype=self.curve_type,
            a=self.a,
            b=self.b,
            p=self.modulus,
            n=self.order,
            h=self.cofactor,
            G=self.gen
        )

    @property
    def curve_type(self):
        return 'shortweierstrass'

    @property
    def is_koblitz(self):
        """ Returns whether the curve allows for efficient computation of a map
            phi in the field (i.e. that the curve is commonly known as
            a 'Koblitz Curve'). This corresponds to examples 3 and 4 of
            the paper "Faster Point Multiplication on Elliptic Curves with
            Efficient Endomorphisms" by Gallant, Lambert and Vanstone.
        """
        return ((self.b == 0) and ((self.modulus % 4) == 1)) or \
            ((self.a == 0) and ((self.modulus % 3) == 1))

    @property
    def security_bit_estimate(self):
        """ Returns the bit security estimate of the curve. Subtracts four bits
            security margin for Koblitz curves.
        """
        security_bits = self.order.bit_length() // 2
        if self.is_koblitz:
            security_bits -= 4
        return security_bits

    @property
    def pretty_name(self):
        name = [self.pretty_name]
        if self.is_koblitz:
            name.append('(Koblitz)')
        return ' '.join(name)

    @property
    def a(self):
        """ Returns the coefficient a of the
            curve equation y^2 = x^3 + ax + b.
        """
        return self._a

    @property
    def b(self):
        """ Returns the coefficient b of the
            curve equation y^2 = x^3 + ax + b.
        """
        return self._b

    @property
    def jinv(self):
        """ Returns the j-invariant of the curve, i.e.
            1728 * 4 * a^3 / (4 * a^3 + 27 * b^2)."""
        return 1728 * (4 * self.a ** 3) // (
                (4 * self.a ** 3) + (27 * self.b ** 2))

    def get_point_with_x(self, x: int):
        """ Returns a tuple of two points which fulfill the curve equation or
            None if not such points exist.
        """
        yy = ((FieldElement(x, self._modulus) ** 3) + (self._a * x) + self._b)
        y = yy.sqrt()
        if y:
            return Point(x, int(y[0]), self), Point(x, int(y[1]), self)
        else:
            return None

    def on_curve(self, point):
        return point.is_neutral or \
            ((point.y ** 2) == (point.x ** 3) + (self.a * point.x) + self.b)

    def point_conjugate(self, point):
        return Point(int(point.x), int(-point.y), self)

    def point_addition(self, point1, point2):
        if point1.is_neutral:
            # P is at infinity, O + Q = Q
            return point2
        if point2.is_neutral:
            # Q is at infinity, P + O = P
            return point1
        if point1 == -point2:
            # P == -Q, return O (point at infinity)
            return self.neutral()
        if point1 == point2:
            # P == Q, point doubling
            s = ((3 * point1.x ** 2) + self.a) // (2 * point1.y)
            new_x = s * s - (2 * point1.x)
            new_y = s * (point1.x - new_x) - point1.y
            return Point(int(new_x), int(new_y), self)
        # P != Q, point addition
        s = (point1.y - point2.y) // (point1.x - point2.x)
        new_x = (s ** 2) - point1.x - point2.x
        new_y = s * (point1.x - new_x) - point1.y
        return Point(int(new_x), int(new_y), self)

    def compress(self, point):
        return int(point.x), int(point.y) % 2

    def uncompress(self, compressed):
        (x, ybit) = compressed
        x = FieldElement(x, self.modulus)
        alpha = (x ** 3) + (self.a * x) + self.b
        (beta1, beta2) = alpha.sqrt()
        if (int(beta1) % 2) == ybit:
            y = beta1
        else:
            y = beta2
        return Point(int(x), int(y), self)

    def enumerate_points(self):
        yield self.neutral()
        for x in range(self.modulus):
            points = self.get_point_with_x(x)
            if points is not None:
                yield points[0]
                yield points[1]

    def __str__(self):
        if self.has_name:
            return 'ShortWeierstrassCurve<%s>' % self.name
        return 'ShortWeierstrassCurve<y^2 = x^3 + 0x%x x + 0x%x mod 0x%x>' % \
            (int(self.a), int(self.b), int(self.modulus))
