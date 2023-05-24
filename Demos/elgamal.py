from ECCBackend.keys.private_key import ECPrivateKey
from ECCData.preset_curves import get_curve

SECP521R1 = get_curve('secp521r1')


def msg_to_point(curve, msg, msg_width_bits):
    int_message = int.from_bytes(msg, byteorder='little')
    for i in range(100):
        try_message = int_message | (i << msg_width_bits)
        point = curve.get_point_with_x(try_message)
        if point:
            point = point[0]
            break
    return point


def elgamal_encrypt(recipient_public_key, msg, msg_width_bits, curve):
    k = ECPrivateKey.generate(curve)
    c1 = k.pubkey.point
    c2 = k.scalar * recipient_public_key.point
    p_m = msg_to_point(curve, msg, msg_width_bits=msg_width_bits)
    ciphertext = c1, c2 + p_m
    return ciphertext


def elgamal_decrypt(recipient_private_key, ciphertext, msg_width_bits):
    c1, c2 = ciphertext
    cp = c1 * recipient_private_key.scalar
    p_m = c2 + (-cp)
    int_message = int(p_m.x) & ((1 << msg_width_bits) - 1)
    msg = int.to_bytes(
        int_message, byteorder='little', length=(msg_width_bits + 7) // 8
    )
    return msg


def main():
    message = input('Введите сообщение:\n>> ').encode('utf-8')
    msg_width_bits = len(message) * 8

    private_key = ECPrivateKey.generate(SECP521R1)
    public_key = private_key.pubkey
    print('Сгенерированный закрытый ключ:', private_key)
    print('Открытый ключ:', public_key)

    ciphertext = elgamal_encrypt(
        public_key, message, msg_width_bits=msg_width_bits, curve=SECP521R1
    )
    print('Шифротекст:')
    print('    C1 =', ciphertext[0])
    print('    C2 =', ciphertext[1])

    plaintext = elgamal_decrypt(
        private_key, ciphertext, msg_width_bits=msg_width_bits
    ).decode('utf-8')
    print('Открытый текст:', plaintext)


if __name__ == '__main__':
    main()
