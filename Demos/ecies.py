from ECCBackend.keys.private_key import ECPrivateKey
from ECCData.preset_curves import get_curve
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BRAINPOOLP192R1 = get_curve('brainpoolP192r1')


def padding(msg: bytes, block_size: int) -> bytes:
    return msg + b'\x00' * (block_size - len(msg) // block_size)


def get_kdf(length):
    return X963KDF(algorithm=hashes.SHA256(), length=length, sharedinfo=None)


def ecies_encrypt(recipient_public_key, msg):
    r, s = recipient_public_key.ecies_encrypt().values()
    kdf = get_kdf(length=(int(s.x).bit_length() + 7) // 8)
    k_e = kdf.derive(
        int.to_bytes(
            int(s.x), byteorder='little', length=(int(s.x).bit_length() + 7) // 8
        )
    )
    kdf = get_kdf(length=(int(s.y).bit_length() + 7) // 8)
    k_m = kdf.derive(
        int.to_bytes(
            int(s.y), byteorder='little', length=(int(s.y).bit_length() + 7) // 8
        )
    )
    cipher = Cipher(
        algorithms.TripleDES(k_e),
        mode=modes.CBC(b'00000000')
    )
    c = cipher.encryptor().update(msg) + cipher.encryptor().finalize()
    h = hmac.HMAC(k_m, hashes.SHA256())
    h.update(c)
    d = h.finalize()
    return r, c, d


def ecies_decrypt(recipient_private_key, r, ciphertext, tag):
    recovered_s = recipient_private_key.ecies_decrypt(r)
    kdf = get_kdf(length=(int(recovered_s.x).bit_length() + 7) // 8)
    k_e = kdf.derive(
        int.to_bytes(
            int(recovered_s.x), byteorder='little',
            length=(int(recovered_s.x).bit_length() + 7) // 8
        )
    )
    kdf = get_kdf(length=(int(recovered_s.y).bit_length() + 7) // 8)
    k_m = kdf.derive(
        int.to_bytes(
            int(recovered_s.y), byteorder='little',
            length=(int(recovered_s.y).bit_length() + 7) // 8
        )
    )
    h = hmac.HMAC(k_m, hashes.SHA256())
    h.update(ciphertext)
    d = h.finalize()
    if d != tag:
        return None
    cipher = Cipher(
        algorithms.TripleDES(k_e),
        mode=modes.CBC(b'00000000')
    )
    m = cipher.decryptor().update(ciphertext) + cipher.decryptor().finalize()
    return m


def main():
    message = padding(input('Введите сообщение:\n>> ').encode('utf-8'), 8)

    private_key = ECPrivateKey.generate(BRAINPOOLP192R1)
    public_key = private_key.pubkey
    print('Сгенерированный закрытый ключ:', private_key)
    print('Открытый ключ:', public_key)

    r, ciphertext, tag = ecies_encrypt(public_key, message)
    print('Результат шифрования:')
    print('    R:', r)
    print('    Шифртекст:', ciphertext)
    print('    Тег:', tag)

    plaintext = ecies_decrypt(private_key, r, ciphertext, tag)
    if not plaintext:
        print('Расшифровка не удалась.')
    else:
        print('Открытый текст:', plaintext.decode('utf-8'))


if __name__ == '__main__':
    main()
