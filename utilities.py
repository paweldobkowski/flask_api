import random
from string import ascii_lowercase, digits


def create_id(size: int) -> str:
    ascii_l = ascii_lowercase
    dgts = digits

    new_id = ''.join([random.choice(ascii_l + dgts) for n in range(size)])

    return new_id