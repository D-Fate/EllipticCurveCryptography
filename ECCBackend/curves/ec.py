from ECCBackend.curves.point import Point


class EllipticCurve:
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

    @property
    def modulus(self):
        return self._modulus

    @property
    def order(self):
        return self._order

    @property
    def cofactor(self):
        return self._cofactor

    @property
    def gen(self):
        return self._gen

    @property
    def curve_order(self):
        """ Порядок эллиптической кривой. """
        if (self.cofactor is None) or (self.order is None):
            raise Exception('#E(F_p) is unknown for this curve')
        return self.cofactor * self.order

    @property
    def frobenius_trace(self):
        """ Cлед эндоморфизма Фробениуса. """
        return self.modulus + 1 - self.curve_order

    @property
    def domain_params(self):
        raise Exception(NotImplemented)

    @property
    def has_generator(self):
        return self.gen is not None

    @property
    def has_name(self):
        return self.name is not None

    @property
    def name(self):
        return self.name

    @property
    def domain_param_dict(self):
        return dict(self.domain_params._asdict())

    @property
    def security_bit_estimate(self):
        """ Бессистемная оценка безопасности базового поля в битах. """
        return self.order.bit_length() // 2

    def enumerate_points(self):
        """ Возвращает enumeration точек. """
        raise Exception(NotImplemented)

    def naive_order_calculation(self):
        order = 0
        for _ in self.enumerate_points():
            order += 1
        return order

    def neutral(self):
        """ Нейтральный элемент группы кривой. """
        return Point(None, None, self)

    def is_neutral(self, point):
        """ True, если point — нейтральный элемент, иначе False. """
        return point.x is None

    def on_curve(self, point):
        """ True, если точка point лежит на данной кривой, иначе False. """
        raise Exception(NotImplemented)

    def point_conjugate(self, point):
        """ Возвращает точку -point для данной точки point. """
        raise Exception(NotImplemented)

    def point_addition(self, point1, point2):
        """ Возвращает результат сложения двух точек. """
        raise Exception(NotImplemented)

    def __eq__(self, other):
        return self.domain_params == other.domain_params

    def __ne__(self, other):
        return not (self == other)
