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


# Tapping a link in an article's text did the same as the old Original: iOS
# loaded the site in the app's own window and the bar stayed raised after Done.
# Web links in the text open in a new window too; links inside the app and
# email links are left as they are.

BODY_ARTICLE = """<!doctype html>
<html><head><meta charset="utf-8"></head><body>
<div class="scroller"><main class="page">
<div class="article-body">
  <p><a id="web" href="https://example.test/story">story</a>
  <a id="relative" href="/items/1">item</a>
  <a id="mail" href="mailto:a@example.test">mail</a></p>
</div>
</main></div>
<script src="/static/app.js"></script>
</body></html>"""


def test_web_links_in_an_article_open_in_a_new_window(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.route(
            f"{origin}/body-copy",
            lambda route: route.fulfill(content_type="text/html", body=BODY_ARTICLE),
        )
        phone.goto(f"{origin}/body-copy")
        phone.wait_for_load_state("load")

        web = phone.locator("#web")
        assert web.get_attribute("target") == "_blank"
        assert web.get_attribute("rel") == "noopener noreferrer"
        assert phone.locator("#relative").get_attribute("target") is None
        assert phone.locator("#mail").get_attribute("target") is None
