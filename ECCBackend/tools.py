def bytes_to_int_le(data):
    return sum(value << (8 * index) for (index, value) in enumerate(data))


def int_to_bytes_le(value, length):
    return bytes((value >> (8 * i)) & 0xff for i in range(length))


def bytes_to_int(data):
    return bytes_to_int_le(reversed(data))


def int_to_bytes(value, length):
    return bytes((value >> (8 * i)) & 0xff for i in reversed(range(length)))


def ecdsa_msg_digest_to_int(message_digest, curve_order):
    """ Обрезает дайджест сообщения до битовой длины порядка кривой. """
    # Дайджест сообщения -> целочисленное значение
    e = bytes_to_int(message_digest)

    # Обрезаем хэш при необходимости
    msg_digest_bits = 8 * len(message_digest)
    if msg_digest_bits > curve_order.bit_length():
        shift = msg_digest_bits - curve_order.bit_length()
        e >>= shift

    return e
