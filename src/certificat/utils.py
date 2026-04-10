import re
from typing import Callable

PREFIXED_GROUP_REGEX = re.compile(r"(?:\w+\/)?(?P<group>.+)")


def unprefix_group(group: str) -> str:
    return PREFIXED_GROUP_REGEX.match(group).group("group")


class LazyLoggedMethod:
    def __init__(self, func: Callable):
        self.func = func

    def __str__(self):
        return self.func()
