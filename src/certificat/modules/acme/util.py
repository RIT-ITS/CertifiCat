import random
import string


def gen_id(length=10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
