def rand(length):
    f = open('/dev/urandom', 'rb')
    data = f.read(length)
    assert (len(data) == length)
    f.close()
    return data


def rand_int(max_value: int) -> int:
    assert (max_value >= 2)
    bytecnt = ((max_value - 1).bit_length() + 7) // 8
    max_bin_value = 256 ** bytecnt
    wholecnt = max_bin_value // max_value
    cutoff = wholecnt * max_value
    while True:
        rnd = sum(
            (value << (8 * bytepos))
            for bytepos, value in enumerate(rand(bytecnt))
        )
        if rnd < cutoff:
            break
    return rnd % max_value


def rand_int_between(min_value: int, max_value: int) -> int:
    return rand_int(max_value - min_value + 1) + min_value
