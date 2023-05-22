import random


class FieldElement(object):
    def __init__(self, value: int, modulus: int):
        self._value = value % modulus
        self._modulus = modulus
        self._qnr = None

    @property
    def modulus(self) -> int:
        return self._modulus

    @staticmethod
    def _extended_euclidian_algorithm(a: int, b: int) -> tuple:
        """ Extended euclidian algorithm. Returns the gcd of (a, b) and
            the Bezout-coefficients.
        """
        s, t, u, v = 1, 0, 0, 1
        while b != 0:
            q, r = a // b, a % b
            next_u, next_v = s, t
            s = u - (q * s)
            t = v - (q * t)
            a, b = b, r
            u, v = next_u, next_v
        return a, u, v

    def inverse(self):
        if int(self) == 0:
            raise ZeroDivisionError('Impossible inverse.')
        gcd, u, v = \
            self._extended_euclidian_algorithm(int(self), self.modulus)
        return FieldElement(v, self.modulus)

    @property
    def is_qr(self) -> bool:
        """ Returns if the number is a quadratic residue according to Euler's
            criterion.
        """
        return not self.is_qnr

    @property
    def is_qnr(self) -> bool:
        """ Returns if the number is a quadratic non-residue according to
            Euler's criterion.
        """
        if self._qnr is None:
            self._qnr = int(self ** ((self._modulus - 1) // 2)) != 1
        return self._qnr

    @property
    def legrende_symbol(self) -> int:
        """ Returns the Legrende symbol of the field element, i.e.
            0 if the element is 0 mod p, 1 if it is a quadratic residue mod p or
            -1 if it is a quadratic non-residue mod p.
        """
        if self == 0:
            return 0
        if self.is_qr:
            return 1
        return -1

    def _tonelli_shanks_sqrt(self):
        """ Performs the Tonelli-Shanks algorithm to determine
            the square root on an element. Note that the algorithm only works
            if the value it is performed on is a quadratic residue mod p.
        """
        q = self._modulus - 1
        s = 0
        while (q % 2) == 0:
            s += 1
            q >>= 1
        assert (q * (2 ** s) == self.modulus - 1)

        while True:
            z = FieldElement(random.randint(1, self.modulus - 1), self.modulus)
            if z.is_qnr:
                break
        assert z.is_qnr
        c = z ** q

        r = self ** ((q + 1) // 2)
        t = self ** q
        m = s
        while int(t) != 1:
            for i in range(1, m):
                if int(t ** (1 << i)) == 1:
                    break

            b = c ** (1 << (m - i - 1))
            r = r * b
            t = t * (b ** 2)
            c = b ** 2
            m = i

        return r

    def sqr(self):
        return self * self

    def sqrt(self):
        """ Returns the square root of the value or None if the value is a
            quadratic non-residue mod p.
        """
        if self.is_qnr:
            return None

        if (self._modulus % 4) == 3:
            root = self ** ((self._modulus + 1) // 4)
            assert (root * root == self)
        else:
            root = self._tonelli_shanks_sqrt()

        if (int(root) & 1) == 0:
            return root, -root
        return -root, root

    def quartic_root(self):
        """ Returns the quartic root of the value or None if no such value
            explicitly exists mod p.
        """
        root = self.sqrt()
        if root is not None:
            r1 = root[0].sqrt() or list()
            r2 = root[1].sqrt() or list()
            for candidate in list(r1) + list(r2):
                if (candidate ** 4) == self:
                    return candidate

    def __checktype(self, value):
        if isinstance(value, int):
            return value
        elif isinstance(value, FieldElement):
            if value.modulus == self.modulus:
                return int(value)
            else:
                raise Exception(
                    'Cannot perform meaningful arithmetic operations '
                    'on field elements in different fields.'
                )

    def sigint(self):
        """ Returns a signed integer if the negative value is less than 10
            decimal digits and the absolute negated value is smaller than the
            absolute positive value.
        """
        neg = abs(int(-self))
        if (neg < int(self)) and (neg < 1000000000):
            return -neg
        return int(self)

    @classmethod
    def any_qnr(cls, modulus):
        """ Returns any quadratic non-residue in F(modulus). """
        for i in range(1000):
            candidate = cls(random.randint(2, modulus - 1), modulus)
            if candidate.is_qnr:
                return candidate
        raise Exception(
            f'Could not find a QNR in F_{modulus} with '
            'a reasonable amount of tries.'
        )

    def __int__(self):
        return self._value

    def __add__(self, value):
        value = self.__checktype(value)
        if value is None:
            return NotImplemented
        return FieldElement(int(self) + value, self.modulus)

    def __sub__(self, value):
        value = self.__checktype(value)
        if value is None:
            return NotImplemented
        return FieldElement(int(self) - value, self.modulus)

    def __mul__(self, value):
        value = self.__checktype(value)
        if value is None:
            return NotImplemented
        return FieldElement(int(self) * value, self.modulus)

    def __floordiv__(self, value):
        value = self.__checktype(value)
        if value is None:
            return NotImplemented
        return self * FieldElement(value, self.modulus).inverse()

    def __pow__(self, exponent: int):
        return FieldElement(
            pow(int(self), exponent, self.modulus), self.modulus
        )

    def __neg__(self):
        return FieldElement(-int(self), self.modulus)

    def __radd__(self, value):
        return self + value

    def __rsub__(self, value):
        return -self + value

    def __rmul__(self, value):
        return self * value

    def __rfloordiv__(self, value):
        return self.inverse() * value

    def __eq__(self, value):
        if value is None:
            return False
        value = self.__checktype(value)
        return int(self) == (value % self.modulus)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, value):
        value = self.__checktype(value)
        return int(self) < value

    def __hash__(self):
        return hash((self._value, self._modulus))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '{0x%x}' % int(self)
