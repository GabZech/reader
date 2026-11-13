"""Which addresses may become a link or an image the app draws.

Only absolute web addresses: anything else (`javascript:`, `data:`, a path
on this app) would run or load something as the app when tapped.
"""

from __future__ import annotations

import re
from urllib.parse import quote, urlsplit

# Browsers drop these from an address before reading its scheme.
_IGNORED = re.compile(r"[\x00-\x20]")


def web_url(raw: str | None) -> str | None:
    """`raw` as an absolute http(s) address, or None. A scheme-relative
    address (`//cdn...`) is taken as https."""
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("//"):
        text = "https:" + text
    parts = urlsplit(_IGNORED.sub("", text))
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        return None
    # Kept as written (spaces inside a path included), now that it is known safe.
    return text


def css_url(raw: str | None) -> str:
    """A web address safe inside `url('...')` in a style attribute: quotes,
    brackets, backslashes and spaces are percent-encoded, so it cannot end
    the value early. Empty when the address is not a web address."""
    url = web_url(raw)
    if url is None:
        return ""
    return quote(url, safe="/:?#[]@!$&*+,;=%~-._")
