import re
import warnings
from collections.abc import Callable

from django.core.paginator import Page, Paginator
from django.db.models import QuerySet

# Deprecated: groups synced from an identity provider are no longer prefixed
# (e.g. "SAML/admins"); they map directly to Django group names. Migration
# acme.0020_remove_group_prefixes renames existing groups. Kept only for
# third-party code and will be removed in a future release.
PREFIXED_GROUP_REGEX = re.compile(r"(?:\w+\/)?(?P<group>.+)")


def unprefix_group(group: str) -> str:
    """Deprecated: group names are no longer prefixed, use the name directly."""
    warnings.warn(
        "unprefix_group is deprecated, group names are no longer prefixed.",
        DeprecationWarning,
        stacklevel=2,
    )
    return PREFIXED_GROUP_REGEX.match(group).group("group")


def paginate(
    queryset: QuerySet, page: int | str | None = 1, per_page: int = 20
) -> tuple[Paginator, Page]:
    """Returns the paginator and requested page. A page number that isn't a
    number shows the first page, and one past the end shows the last page."""
    paginator = Paginator(queryset, per_page)
    return paginator, paginator.get_page(page)


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
