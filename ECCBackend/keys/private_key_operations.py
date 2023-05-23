import collections
import hashlib

import ECCBackend.tools as tools
from ECCBackend.curves.field_element import FieldElement
from ECCBackend.secure_random import rand_int_between


class ECDSASign(object):
    ECDSASignature = collections.namedtuple(
        'ECDSASignature', ['hashalg', 'r', 's']
    )

    def ecdsa_sign_hash(self, message_digest: bytes,
                        digest_name: str = None, nonce: int = None):
        """ Подписывает дайджест сообщения message_digest, используя ECDSA.
            Также есть возможность ввести nonce, чтобы избежать эксплойта.
            Если nonce не введено, то оно выбирается случайно. Если
            введено digest_name, то оно дописывается в конец объекта подписи.
        """
        # Дайджест сообщения -> целочисленное значение
        e = tools.ecdsa_msgdigest_to_int(message_digest, self.curve.order)

        if nonce is None:
            nonce = rand_int_between(1, self.curve.order - 1)

        # r = (k * G)_x mod n
        r_mod_p = nonce * self.curve.gen
        r = int(r_mod_p.x) % self.curve.order
        assert (r != 0)

        s = FieldElement(e + self.scalar * r, self.curve.order) // nonce

        return self.ECDSASignature(r=r, s=int(s), hashalg=digest_name)

    def ecdsa_sign(self, message: bytes, digest_name: str, nonce=None):
        """ Подписывает сообщение message, используя ECDSA. Также есть
            возможность ввести nonce, чтобы избежать эксплойта. Если nonce не
            введено, то оно выбирается случайно. Если введено digest_name, то
            оно дописывается в конец объекта подписи.
        """
        digest_func = hashlib.new(digest_name)
        digest_func.update(message)
        message_digest = digest_func.digest()
        return self.ecdsa_sign_hash(
            message_digest, digest_name=digest_name, nonce=nonce
        )


class ECIESDecrypt(object):
    def ecies_decrypt(self, r):
        # R передан, восстанавливаем симметричный ключ S
        return self._scalar * r


class ECDH(object):
    def ecdh_compute(self, peer_pubkey):
        return self.scalar * peer_pubkey.point

