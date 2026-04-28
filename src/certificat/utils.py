import re
from typing import Callable

PREFIXED_GROUP_REGEX = re.compile(r"(?:\w+\/)?(?P<group>.+)")


def unprefix_group(group: str) -> str:
    return PREFIXED_GROUP_REGEX.match(group).group("group")


def coerce_to_list(obj):
    return obj if isinstance(obj, list) else [obj]


def split_delimited_string(text: str, delimiter: str) -> list[str]:
    if len(delimiter) != 1:
        raise ValueError("delimiter must be a single character")

    parts = []
    current = []
    i = 0

    while i < len(text):
        ch = text[i]

        if ch == "\\" and i + 1 < len(text) and text[i + 1] == delimiter:
            current.append(delimiter)
            i += 2
            continue

        if ch == delimiter:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)

        i += 1

    parts.append("".join(current))
    return [p for p in parts if p.strip()]


class LazyLoggedMethod:
    def __init__(self, func: Callable):
        self.func = func

    def __str__(self):
        return self.func()
