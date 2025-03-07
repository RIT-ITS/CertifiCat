import re

PREFIXED_GROUP_REGEX = re.compile(r"(?:\w+\/)?(?P<group>.+)")


def unprefix_group(group: str) -> str:
    return PREFIXED_GROUP_REGEX.match(group).group("group")
