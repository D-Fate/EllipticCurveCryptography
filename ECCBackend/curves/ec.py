from ECCBackend.curves.point import Point


class EllipticCurve(object):
    def __init__(self, modulus: int, order: int = None, cofactor: int = None,
                 gen_x: int = None, gen_y: int = None, **kwargs):
        assert ((gen_x is None) == (gen_y is None))

        self._modulus = modulus
        self._order = order
        self._cofactor = cofactor

        if (gen_x is not None) and (gen_y is not None):
            self._gen = Point(gen_x, gen_y, self)
        else:
            self._gen = None

        if 'quirks' in kwargs:
            self._quirks = {
                quirk.identifier: quirk for quirk in kwargs['quirks']
            }
        else:
            self._quirks = {}

    @property
    def modulus(self):
        """ Returns the prime modulus which constitutes the finite field in
            which the curve lies.
        """
        return self._modulus

    @property
    def order(self):
        """ Returns the order of the subgroup that
            is created by the generator G.
        """
        return self._order

    @property
    def cofactor(self):
        """ Returns the cofactor of the generator subgroup, i.e. h = #E(F_p) /
            n. This will always be an integer according to Lagrange's Theorem.
        """
        return self._cofactor

    @property
    def gen(self):
        """ Returns the generator point G of the curve or None if no such point
            was set. The generator point generates a subgroup over #E(F_p).
        """
        return self._gen

    @property
    def curve_order(self):
        """ Returns the order of the curve in the underlying field, i.e.
            #E(F_p). Intuitively, this is the total number of points on the
            curve (plus maybe points at infinity, depending on the curve type)
            that satisfy the curve equation.
        """
        if (self.cofactor is None) or (self.order is None):
            raise Exception('#E(F_p) is unknown for this curve')
        return self.cofactor * self.order

    @property
    def frobenius_trace(self):
        """ Returns the Frobenius trace t of the curve. Since
            #E(F_p) = p + 1	- t it follows that t = p + 1 - #E(F_p).
        """
        return self.modulus + 1 - self.curve_order

    @property
    def domain_params(self):
        """ Returns the curve parameters as a named tuple. """
        raise Exception(NotImplemented)

    @property
    def has_generator(self):
        """ Returns if a generator point was supplied for the curve. """
        return self.gen is not None

    @property
    def has_name(self):
        """Returns if the curve is named (i.e. its name is not None)."""
        return self.name is not None

    @property
    def name(self):
        """ Returns the name of the curve, if it was given one during
            construction. Purely informational.
        """
        return self.name

    @property
    def pretty_name(self):
        """ Returns the pretty name of the curve type. This might depend on the
            actual curve, since it may also vary on the actual domain parameters
            to include if the curve is a Koblitz curve or not.
        """
        return self.pretty_name

    @property
    def curve_type(self):
        """ Returns a string that corresponds to the curve type. For example,
            this string can be 'shortweierstrass', 'twistededwards' or
            'montgomery'.
        """
        raise Exception(NotImplemented)

    @property
    def domain_param_dict(self):
        """ Returns the domain parameters of the curve as a dictionary. """
        return dict(self.domain_params._asdict())

    @property
    def security_bit_estimate(self):
        """ Gives a haphazard estimate of the security of the underlying field,
            in bits. For most curves, this will be half the bitsize of n (but
            might be less, for example for Koblitz curves some bits might be
            subtracted).
        """
        return self.order.bit_length() // 2

    def enumerate_points(self):
        """ Enumerates all points on the curve, including the point at infinity
            (if the curve has such a special point).
        """
        raise Exception(NotImplemented)

    def naive_order_calculation(self):
        """ Naively calculates the order #E(F_p) of the curve by enumerating and
            counting all points which fulfull the curve equation. Note that this
            implementation only works for the smallest of curves and is
            computationally infeasible for all practical applications.
        """
        order = 0
        for _ in self.enumerate_points():
            order += 1
        return order

    def neutral(self):
        """ Returns the neutral element of the curve group (for some curves,
            this will be the point at infinity).
        """
        return Point(None, None, self)

    def is_neutral(self, point):
        """ Checks if a given point P is the neutral element of the group. """
        return point.x is None

    def on_curve(self, point):
        """ Checks is a given point P is on the curve. """
        raise Exception(NotImplemented)

    def point_addition(self, point1, point2):
        """ Returns the sum of two points P and Q on the curve. """
        raise Exception(NotImplemented)

    def point_conjugate(self, point):
        """ Returns the negated point -P to a given point P. """
        raise Exception(NotImplemented)

    def compress(self, point):
        """ Returns the compressed representation of the point P on the curve.
            Not all curves may support this operation.
        """
        raise Exception(NotImplemented)

    def uncompress(self, compressed):
        """ Returns the uncompressed representation of a point on the curve.
            Not all curves may support this operation.
        """
        raise Exception(NotImplemented)

    def has_quirk(self, quirk_class):
        """ Some elliptic curves may have quirks or tweaks for certain
            algorithms. These are attached to the curve using the 'quirks'
            kwarg of the constructor.  Code that wants to query if a specific
            quirk is present may do so by calling 'has_quirk' with the according
            quirk class (not a quirk class instance!).
        """
        return quirk_class.identifier in self._quirks

    def get_quirk(self, quirk_class):
        """ If a quirk is present for a given elliptic curve, this quirk may
            have been parametrized during instanciation. The get_quirk() method
            returns that quirk instance when given a specific quirk class as
            input. It raises a KeyError if the requested quirk is not present
            for the elliptic curve.
        """
        return self._quirks[quirk_class.identifier]

    def __eq__(self, other):
        return self.domain_params == other.domain_params

    def __ne__(self, other):
        return not (self == other)
