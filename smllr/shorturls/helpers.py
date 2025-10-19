import string
import random


def generate_short_code(length: int = 10) -> str:
    """
    Generates a random short URL slug of the specified length.

    :param length: Length of the generated slug. Default is 10 characters.
    :return: A random string of the specified length consisting of alphanumeric characters.
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))
