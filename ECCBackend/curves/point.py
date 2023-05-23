from ECCBackend.curves.field_element import FieldElement
from ECCBackend.curves.point_operations import NaiveOrderCalculation,\
    ScalarMultiplicationXOnly


class Point(NaiveOrderCalculation, ScalarMultiplicationXOnly):
    def __init__(self, x: int | None, y: int | None, curve):
        assert (((x is None) and (y is None)) or
                ((x is not None) and (y is not None)))
        if x is None:
            # бесконечность
            self._x = None
            self._y = None
        else:
            self._x = FieldElement(x, curve.modulus)
            self._y = FieldElement(y, curve.modulus)
        self._curve = curve

    @staticmethod
    def neutral(curve):
        """ Нейтральный элемент группы кривой. """
        return curve.neutral()

    @property
    def is_neutral(self):
        """ True, если point — нейтральный элемент, иначе False """
        return self.curve.is_neutral(self)

    @property
    def x(self):
        """ Компонента x. """
        return self._x

    @property
    def y(self):
        """ Компонента y. """
        return self._y

    @property
    def curve(self):
        """ Кривая, на которой данная точка лежит. """
        return self._curve

    def __add__(self, other):
        assert (isinstance(other, Point))
        return self.curve.point_addition(self, other)

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return self.curve.point_conjugate(self)

    def __mul__(self, scalar: int):
        """ Умножение точки на скаляр. """
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
        """ True, если точка лежит на кривой, иначе False. """
        return self.curve.on_curve(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.is_neutral:
            return '(neutral)'
        return '(0x%x, 0x%x)' % (int(self.x), int(self.y))
