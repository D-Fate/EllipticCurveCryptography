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
                        k: int =None, digestname=None):
        """ Signs a given messagedigest, given as bytes, using ECDSA.
            Optionally a nonce k can be supplied which should usually be
            unqiuely chosen for every ECDSA signature. This way it is possible
            to deliberately create broken signatures which can be exploited
            later on. If k is not supplied, it is randomly chosen. If a
            digestname is supplied the name of this digest eventually ends up
            in the ECDSASignature object.
        """
        # Convert message digest to integer value
        e = tools.ecdsa_msgdigest_to_int(message_digest, self.curve.order)

        # Select a random integer (if None is supplied!)
        if k is None:
            k = rand_int_between(1, self.curve.order - 1)

        # r = (k * G)_x mod n
        Rmodp = k * self.curve.gen
        r = int(Rmodp.x) % self.curve.order
        assert (r != 0)

        s = FieldElement(e + self.scalar * r, self.curve.order) // k

        return self.ECDSASignature(r=r, s=int(s), hashalg=digestname)

    def ecdsa_sign(self, message: bytes, digestname: str, k=None):
        """ Signs a given message with the digest that is given as a string.
            Optionally a nonce k can be supplied which should usually be
            unqiuely chosen for every ECDSA signature. This way it is possible
            to deliberately create broken signatures which can be exploited
            later on. If k is not supplied, it is randomly chosen.
        """
        digest_fnc = hashlib.new(digestname)
        digest_fnc.update(message)
        message_digest = digest_fnc.digest()
        return self.ecdsa_sign_hash(message_digest, k=k, digestname=digestname)


class ECIESDecrypt(object):
    def ecies_decrypt(self, R):
        """ Takes the transmitted point R and reconstructs the shared secret
            point S using the private key.
        """
        # Transmitted R is given, restore the symmetric key S
        return self._scalar * R


class ECDH(object):
    def ecdh_compute(self, peer_pubkey):
        """ Compute the shared secret point using our own private key and the
            public key of our peer.
        """
        return self.scalar * peer_pubkey.point

