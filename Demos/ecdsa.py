from ECCBackend.keys.private_key import ECPrivateKey
from ECCData.preset_curves import get_curve
from random import randint

SECP521R1 = get_curve('secp521r1')


def modify(msg: bytes) -> bytes:
    """ Изменяет случайный байт сообщения """
    msg_array = bytearray(msg)
    msg_array[randint(0, len(msg_array) - 1)] = randint(0, 255)
    return bytes(msg_array)


def main():
    message = input('Введите сообщение:\n>> ').encode('utf-8')

    private_key = ECPrivateKey.generate(SECP521R1)
    print('Сгенерированный закрытый ключ:', private_key)

    signature = private_key.ecdsa_sign(message, 'sha1')
    print('Подписываем сообщение:')
    print('    r:', signature.r)
    print('    s:', signature.s)

    modified_message = modify(message)
    print('Сообщение:                 ', message)
    print('Модифицированное сообщение:', modified_message)

    print('Проверка электронной подписи:')
    verify_original = private_key.pubkey.ecdsa_verify(message, signature)
    verify_modified = private_key.pubkey.ecdsa_verify(
        modified_message, signature
    )
    print(f'Оригинальное сообщение: {verify_original} (ожидается Истина)')
    print(f'Модифицированное сообщение: {verify_modified} (ожидается Ложь)')

    print('Подпишем теперь данные сообщения с одинаковыми nonce:')
    signature1 = private_key.ecdsa_sign(message, 'sha1', nonce=123456)
    signature2 = private_key.ecdsa_sign(modified_message, 'sha1', nonce=123456)
    print('    r1:', signature1.r)
    print('    s1:', signature1.s)
    print('    r2:', signature2.r)
    print('    s2:', signature2.s)
    recovered = private_key.pubkey.ecdsa_exploit_reused_nonce(
        message, signature1,
        modified_message, signature2
    )

    print('Восстановленный nonce:', int(recovered['nonce']))
    print('Восстановленный закрытый ключ: 0x%x' % int(recovered['privatekey']))


if __name__ == '__main__':
    main()
