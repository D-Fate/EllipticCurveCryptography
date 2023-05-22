import hashlib

import ECCBackend.tools as tools
from ECCBackend.curves.field_element import FieldElement
from ECCBackend.secure_random import rand_int_between


class ECDSAExploitReusedNonce(object):
    def ecdsa_exploit_reused_nonce(self, msg1: bytes, sig1, msg2: bytes, sig2):
        """ Given two different messages msg1 and msg2 and their corresponding
            signatures sig1, sig2, try to calculate the private key that was
            used for signing if during signature generation no unique nonces
            were used.
        """
        assert (msg1 != msg2)
        assert (sig1.r == sig2.r)

        # Hash the messages
        dig1 = hashlib.new(sig1.hashalg)
        dig1.update(msg1)
        dig1 = dig1.digest()
        dig2 = hashlib.new(sig2.hashalg)
        dig2.update(msg2)
        dig2 = dig2.digest()

        # Calculate hashes of messages
        e1 = tools.ecdsa_msgdigest_to_int(dig1, self.point.curve.order)
        e2 = tools.ecdsa_msgdigest_to_int(dig2, self.point.curve.order)

        # Take them modulo n
        e1 = FieldElement(e1, self.point.curve.order)
        e2 = FieldElement(e2, self.point.curve.order)

        (s1, s2) = (FieldElement(sig1.s, self.point.curve.order),
                    FieldElement(sig2.s, self.point.curve.order))
        r = sig1.r

        # Recover (supposedly) random nonce
        nonce = (e1 - e2) // (s1 - s2)

        # Recover private key
        private = ((nonce * s1) - e1) // r

        return {'nonce': nonce, 'privatekey': private}


class ECDSAVerify(object):
    def ecdsa_verify_hash(self, message_digest: bytes, signature):
        """ Verify ECDSA signature over the hash of
            a message (the message digest).
        """
        assert (0 < signature.r < self.curve.order)
        assert (0 < signature.s < self.curve.order)

        # Convert message digest to integer value
        e = tools.ecdsa_msgdigest_to_int(message_digest, self.curve.order)

        (r, s) = (signature.r, FieldElement(signature.s, self.curve.order))
        w = s.inverse()
        u1 = int(e * w)
        u2 = int(r * w)

        point = (u1 * self.curve.gen) + (u2 * self.point)
        x1 = int(point.x) % self.curve.order
        return x1 == r

    def ecdsa_verify(self, message: bytes, signature):
        """ Verify an ECDSA signature over a message. """
        digest_fnc = hashlib.new(signature.hashalg)
        digest_fnc.update(message)
        message_digest = digest_fnc.digest()
        return self.ecdsa_verify_hash(message_digest, signature)


class ECIESEncrypt(object):
    def ecies_encrypt(self, r=None):
        """ Generates a shared secret which can be used to symetrically encrypt
            data that only the holder of the corresponding private key can read.
            The output are two points, R and S: R is the public point that is
            transmitted together with the message while S is the point which
            resembles the shared secret. The receiver can use R together with
            her private key to reconstruct S. A random nonce r can be supplied
            for this function. If it isn't supplied, it is randomly chosen.
        """
        if r is None:
            r = rand_int_between(1, self.curve.order - 1)

        # Return the publicly transmitted R and the symmetric key S
        return {'R': r * self.curve.gen, 'S': r * self.point}
