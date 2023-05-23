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
        """ Возвращает НОД и коэффициенты Безу. """
        s, t, u, v = 1, 0, 0, 1
        while b != 0:
            q, r = a // b, a % b
            next_u, next_v = s, t
            s = u - q * s
            t = v - q * t
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
        """ True, если квадратичный вычет по критерию Эйлера, иначе False. """
        return not self.is_qnr

    @property
    def is_qnr(self) -> bool:
        """ True, если не квадратичный невычет по критерию Эйлера, иначе False.
        """
        if self._qnr is None:
            self._qnr = int(self ** ((self._modulus - 1) // 2)) != 1
        return self._qnr

    @property
    def legrende_symbol(self) -> int:
        """ 0, если value = 0 по модулю modulus;
            1, если квадратичный вычет;
            -1, если квадратичный невычет.
        """
        if self == 0:
            return 0
        if self.is_qr:
            return 1
        return -1

    def _tonelli_shanks_sqrt(self):
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
