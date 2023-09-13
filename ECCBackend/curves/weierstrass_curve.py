import collections

from ECCBackend.curves.ec import EllipticCurve
from ECCBackend.curves.field_element import FieldElement
from ECCBackend.curves.point import Point

_WeierstrassCurveDomainParameters = collections.namedtuple(
    'WeierstrassCurveDomainParameters',
    ['a', 'b', 'modulus', 'order', 'cofactor', 'gen']
)


class WeierstrassCurve(EllipticCurve):
    def __init__(self, a: int, b: int,
                 modulus, order, cofactor, gen_x, gen_y, **kwargs):
        EllipticCurve.__init__(
            self, modulus, order, cofactor, gen_x, gen_y, **kwargs
        )
        self._a = FieldElement(a, modulus)
        self._b = FieldElement(b, modulus)
        self._name = kwargs.get('name')

        # кривая не вырождена
        assert ((4 * (self.a ** 3)) + (27 * (self.b ** 2)) != 0)

        if self._gen is not None:
            assert (self._gen.on_curve())

            if self.order is not None:
                assert (self.order * self.gen).is_neutral

    @property
    def is_anomalous(self):
        """ True, если кривая "аномальная" (то есть, #F(p) == p), иначе False.
            Такие кривые уязвимы к атаке Смарта.
        """
        return self.j_invariant in (0, 1728)

    @property
    def domain_params(self):
        return _WeierstrassCurveDomainParameters(
            a=self.a,
            b=self.b,
            modulus=self.modulus,
            order=self.order,
            cofactor=self.cofactor,
            gen=self.gen
        )

    @property
    def is_koblitz(self):
        """ True, если кривая является кривой Коблица, иначе False.
            Свойства описаны в "Faster Point Multiplication on Elliptic Curves
            with Efficient Endomorphisms" Галланта, Ламберта и Ванстоуна.
        """
        return ((self.b == 0) and ((self.modulus % 4) == 1)) or \
            ((self.a == 0) and ((self.modulus % 3) == 1))

    @property
    def security_bit_estimate(self):
        """ Бессистемная оценка безопасности базового поля в битах. Для кривых
            Коблица на 4 меньше.
        """
        security_bits = self.order.bit_length() // 2
        if self.is_koblitz:
            security_bits -= 4
        return security_bits

    def enumerate_points(self):
        """ Возвращает enumeration точек. """
        yield self.neutral()
        for x in range(self.modulus):
            points = self.get_point_with_x(x)
            if points is not None:
                yield points[0]
                yield points[1]

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def j_invariant(self):
        """ j-инвариант кривой: 1728 * 4 * a^3 / (4 * a^3 + 27 * b^2).
            Пригодится в алгоритме Шуфа — Элкиса — Аткина.
        """
        return 1728 * (4 * self.a ** 3) // \
            ((4 * self.a ** 3) + (27 * self.b ** 2))

    def get_point_with_x(self, x: int):
        """ Возвращает кортеж из двух точек с заданной компонентой x,
            удовлетворящих уровнению кривой. Если их не существовует, то — None.
        """
        y_sq = ((FieldElement(x, self._modulus) ** 3) + (self._a * x) + self._b)
        y = y_sq.sqrt()
        if y:
            return Point(x, int(y[0]), self), Point(x, int(y[1]), self)
        else:
            return None

    def on_curve(self, point):
        """ True, если точка point лежит на данной кривой, иначе False. """
        return point.is_neutral or \
            ((point.y ** 2) == (point.x ** 3) + (self.a * point.x) + self.b)

    def point_conjugate(self, point):
        """ Возвращает точку -point для данной точки point. """
        return Point(int(point.x), int(-point.y), self)

    def point_addition(self, point1, point2):
        """ Возвращает результат сложения двух точек. """
        if point1.is_neutral:
            # O + point2 = point2
            return point2
        if point2.is_neutral:
            # point1 + O = point1
            return point1
        if point1 == -point2:
            # point1 = -point2 (бесконечность)
            return self.neutral()
        if point1 == point2:
            # point1 = point2
            s = ((3 * point1.x ** 2) + self.a) // (2 * point1.y)
            new_x = s * s - (2 * point1.x)
            new_y = s * (point1.x - new_x) - point1.y
            return Point(int(new_x), int(new_y), self)
        # point1 != point2
        s = (point1.y - point2.y) // (point1.x - point2.x)
        new_x = (s ** 2) - point1.x - point2.x
        new_y = s * (point1.x - new_x) - point1.y
        return Point(int(new_x), int(new_y), self)

    def __str__(self):
        if self.has_name:
            return 'WeierstrassCurve<%s>' % self.name
        return 'WeierstrassCurve<y^2 = x^3 + 0x%x x + 0x%x mod 0x%x>' % \
            (int(self.a), int(self.b), int(self.modulus))
