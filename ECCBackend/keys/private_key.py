from ECCBackend.keys.private_key_operations import ECDSASign, ECIESDecrypt, ECDH
from ECCBackend.keys.public_key import ECPublicKey
from ECCBackend.secure_random import rand_int_between


class ECPrivateKey(ECDSASign, ECIESDecrypt, ECDH):
    def __init__(self, scalar, curve):
        self._scalar = scalar
        self._curve = curve
        self._pubkey = ECPublicKey(self._scalar * self._curve.gen)

    @property
    def scalar(self):
        return self._scalar

    @property
    def curve(self):
        """ Группа кривой, используемая для вычислений. """
        return self._curve

    @property
    def pubkey(self):
        return self._pubkey

    @staticmethod
    def generate(curve):
        scalar = rand_int_between(1, curve.order - 1)
        return ECPrivateKey(scalar, curve)

    def __str__(self):
        return 'PrivateKey<d = 0x%x>' % self.scalar


def generate(curve):
    return None
