from ECCBackend.keys.public_key_operations import ECDSAVerify, \
    ECDSAExploitReusedNonce, ECIESEncrypt


class ECPublicKey(ECDSAVerify, ECDSAExploitReusedNonce, ECIESEncrypt):
    def __init__(self, point):
        self._point = point

    @property
    def curve(self):
        return self._point.curve

    @property
    def point(self):
        return self._point

    def __str__(self):
        return str(self.point)
