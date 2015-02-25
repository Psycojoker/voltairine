import string
import random


def generate_random_string(size):
    return ''.join(random.SystemRandom().choice(string.hexdigits) for n in xrange(size))
