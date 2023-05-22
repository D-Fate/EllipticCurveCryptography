def rand(length):
    """Returns a secure random bytes() object of the length 'length' bytes."""
    f = open('/dev/urandom', 'rb')
    data = f.read(length)
    assert (len(data) == length)
    f.close()
    return data


def rand_int(max_value):
    """ Yields a value 0 <= return < maxvalue. """
    assert (max_value >= 2)
    bytecnt = ((max_value - 1).bit_length() + 7) // 8
    max_bin_value = 256 ** bytecnt
    wholecnt = max_bin_value // max_value
    cutoff = wholecnt * max_value
    while True:
        rnd = sum(
            (value << (8 * bytepos))
            for (bytepos, value) in enumerate(rand(bytecnt))
        )
        if rnd < cutoff:
            break
    return rnd % max_value


def rand_int_between(min_value, max_value):
    """ Yields a random number which goes
        from min_value (inclusive) to max_value (inclusive).
    """
    return rand_int(max_value - min_value + 1) + min_value
