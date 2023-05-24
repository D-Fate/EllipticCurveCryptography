class NaiveOrderCalculation:
    def naive_order_calculation(self):
        current_point = self
        order = 1
        while not current_point.is_neutral:
            order += 1
            current_point += self
        return order


class ScalarMultiplicationXOnly:
    def _x_double(self, x):
        if x is None:
            return None
        den = 4 * (x ** 3 + self.curve.a * x + self.curve.b)
        if den == 0:
            # бесконечность
            return None
        num = (x ** 2 - self.curve.a) ** 2 - (8 * self.curve.b * x)
        return num // den

    def _x_add(self, x1, x2, x3prime):
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
