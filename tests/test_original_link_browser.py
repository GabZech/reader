from __future__ import annotations

from test_service_worker_browser import _live_server

# An article the phone downloaded before Original opened in a new window keeps
# its old markup (stored copies are not refreshed when the app updates), so on
# an iPhone its Original still left the app's own window and the bottom bar
# stayed raised after Done. The script, fetched again with every download run,
# gives such a link the new window too.

OLD_ARTICLE = """<!doctype html>
<html><head><meta charset="utf-8"></head><body>
<div class="scroller"><main class="page">
<nav class="article-bar" aria-label="Article">
  <a class="bar-close" href="/">Close</a>
  <span class="article-bar-right">
    <a href="https://example.test/post" rel="noreferrer">Original</a>
  </span>
</nav>
<header class="top article-head"><h1>Old copy</h1></header>
</main></div>
<script src="/static/app.js"></script>
</body></html>"""


def test_an_article_stored_before_the_change_opens_original_in_a_new_window(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.route(
            f"{origin}/old-copy",
            lambda route: route.fulfill(content_type="text/html", body=OLD_ARTICLE),
        )
        phone.goto(f"{origin}/old-copy")
        phone.wait_for_load_state("load")

        link = phone.locator(".article-bar-right a", has_text="Original")
        assert link.get_attribute("target") == "_blank"
        assert link.get_attribute("rel") == "noopener noreferrer"
