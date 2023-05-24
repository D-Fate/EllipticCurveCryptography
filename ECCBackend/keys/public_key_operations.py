import hashlib

import ECCBackend.tools as tools
from ECCBackend.curves.field_element import FieldElement
from ECCBackend.secure_random import rand_int_between


class ECDSAExploitReusedNonce:
    def ecdsa_exploit_reused_nonce(self, msg1: bytes, sig1, msg2: bytes, sig2):
        """ Даны два разных сообщения msg1 и msg2 и соответствующие им
            подписи sig1, sig2, попытаться вычислить приватный ключ,
            использованный для подписи, если при подписи не были использованы
            уникальные nonce.
        """
        assert (msg1 != msg2)
        assert (sig1.r == sig2.r)

        dig1 = hashlib.new(sig1.hashalg)
        dig1.update(msg1)
        dig1 = dig1.digest()
        dig2 = hashlib.new(sig2.hashalg)
        dig2.update(msg2)
        dig2 = dig2.digest()

        e1 = tools.ecdsa_msg_digest_to_int(dig1, self.point.curve.order)
        e2 = tools.ecdsa_msg_digest_to_int(dig2, self.point.curve.order)

        e1 = FieldElement(e1, self.point.curve.order)
        e2 = FieldElement(e2, self.point.curve.order)

        s1, s2 = (FieldElement(sig1.s, self.point.curve.order),
                  FieldElement(sig2.s, self.point.curve.order))
        r = sig1.r

        # Восстановить nonce
        nonce = (e1 - e2) // (s1 - s2)

        # Восстановить приватный ключ
        private = ((nonce * s1) - e1) // r

        return {'nonce': nonce, 'privatekey': private}


class ECDSAVerify:
    def ecdsa_verify_hash(self, message_digest: bytes, signature):
        assert (0 < signature.r < self.curve.order)
        assert (0 < signature.s < self.curve.order)

        # Дайджест сообщения -> целочисленное значение
        e = tools.ecdsa_msg_digest_to_int(message_digest, self.curve.order)

        r, s = (signature.r, FieldElement(signature.s, self.curve.order))
        w = s.inverse()
        u1 = int(e * w)
        u2 = int(r * w)

        point = (u1 * self.curve.gen) + (u2 * self.point)
        x1 = int(point.x) % self.curve.order
        return x1 == r

    def ecdsa_verify(self, message: bytes, signature):
        digest_fnc = hashlib.new(signature.hashalg)
        digest_fnc.update(message)
        message_digest = digest_fnc.digest()
        return self.ecdsa_verify_hash(message_digest, signature)


class ECIESEncrypt:
    def ecies_encrypt(self, r: int = None):
        """ Генерирует общий секрет для симметричного шифрования данных,
            которые может прочитать только владелец соответствующего закрытого
            ключа. На выходе получаются две точки, R и S: R — это открытая
            точка, которая передается вместе с сообщением, S — это точка,
            "похожая" на общий секрет. Получатель может использовать R вместе со
            своим закрытым ключом для восстановления S. В качестве входных может
            быть также введен nonce r. Если он не введен, то r выбирается
            случайным образом.
        """
        if r is None:
            r = rand_int_between(1, self.curve.order - 1)
        return {'R': r * self.curve.gen, 'S': r * self.point}
