import random
import secrets


def random_prime(bits: int, tests: int = None) -> int:
    if bits < 8:
        raise ValueError(
            'Please use a bit-length greater than '
            'or equal to 8 for the required prime number.'
        )
    prime = secrets.randbits(bits)
    i = 1
    while not is_probable_prime(prime, tests):
        prime = secrets.randbits(bits)
        i += 1

    return prime


def is_probable_prime(candidate: int, tests: int = None) -> bool:
    if candidate <= 1:
        return False
    if candidate in (2, 3):
        return True
    prime_list_up_to_256 = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
        71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139,
        149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223,
        227, 229, 233, 239, 241, 251
    ]
    for prime in prime_list_up_to_256:
        if candidate % prime == 0:
            return False
    if tests:
        if tests < 1:
            raise ValueError(
                'Please use a number of tests >= 1 for prime number generation.'
            )
        return miller_rabin(candidate, tests)
    else:
        default_tests = 5
        return miller_rabin(candidate, default_tests)


def miller_rabin(integer: int, security: int) -> bool:
    if integer < 3 or security < 1:
        return False
    s = 0
    r = integer - 1
    while r % 2 == 0:
        r //= 2
        s += 1
    for _ in range(security):
        base = random.randint(2, integer - 2)
        y = pow(base, r, integer)
        if y != 1 and y != integer - 1:
            i = 0
            while i <= s - 1 and y != integer - 1:
                y = pow(y, 2, integer)
                if y == 1:
                    return False
                i += 1
            if y != integer - 1:
                return False
    return True
