from __future__ import annotations

import json
from contextlib import contextmanager
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import sync_playwright
from test_app import (
    _add_to_news,
    _client,
    _first_item_id,
    _save_highlight,
    _set_body_html,
)

from app import db as dbmod

ORIGIN = "http://reader.test"
IMAGE_BODY = (
    "<p>First paragraph</p>"
    '<p><img src="/static/favicon.svg" alt="chart"></p>'
    "<p>Second paragraph</p>"
)
BARE_IMAGE_BODY = (
    "<p>First paragraph</p>"
    '<img src="/static/favicon.svg" alt="chart">'
    "<p>Second paragraph</p>"
)


@pytest.fixture
def browser_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            yield browser.new_page()
        finally:
            browser.close()


def _serve_through(page, client):
    """Answer every request the page makes from the app's TestClient."""

    def handle(route):
        request = route.request
        parts = urlsplit(request.url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        response = client.request(
            request.method,
            path,
            content=request.post_data_buffer,
            headers={k: v for k, v in request.headers.items() if k.lower() == "content-type"},
            follow_redirects=False,
        )
        route.fulfill(
            status=response.status_code,
            headers=dict(response.headers),
            body=response.content,
        )

    page.route(f"{ORIGIN}/**", handle)


def _outlined(page):
    return page.eval_on_selector_all(".article-body img.hl-image", "els => els.length")


def _stored_images(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        rows = conn.execute("SELECT image_urls FROM highlights").fetchall()
    finally:
        conn.close()
    return [json.loads(row["image_urls"] or "[]") for row in rows]


def _select_and_save(page, start, end):
    """Select from `start` to `end`, each a JS (container, offset) pair over
    `b`, the article's top-level blocks, and let the page save it."""
    page.evaluate(
        f"""() => {{
          const b = document.querySelector(".article-body").children;
          const range = document.createRange();
          range.setStart({start});
          range.setEnd({end});
          const selection = window.getSelection();
          selection.removeAllRanges();
          selection.addRange(range);
          document.querySelector(".article-body").dispatchEvent(
            new MouseEvent("mouseup", {{ bubbles: true }})
          );
        }}"""
    )
    # The text highlight lands, so the save went through.
    page.wait_for_selector(".article-body mark.hl", timeout=5000)


@contextmanager
def _opened(page, monkeypatch, tmp_path, body=IMAGE_BODY):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(tmp_path, item_id, body)
        _serve_through(page, client)
        page.goto(f"{ORIGIN}/items/{item_id}")
        yield client, item_id


@pytest.mark.parametrize(
    ("start", "end"),
    [
        pytest.param("b[0].firstChild, 0", "b[2].firstChild, 6", id="across"),
        pytest.param("b[1], 0", "b[2].firstChild, 6", id="starts-on-image"),
        pytest.param("b[0].firstChild, 0", "b[1], 1", id="ends-on-image"),
    ],
)
def test_selecting_over_an_image_marks_and_stores_it(
    monkeypatch, tmp_path, browser_page, start, end
):
    with _opened(browser_page, monkeypatch, tmp_path):
        assert _outlined(browser_page) == 0
        _select_and_save(browser_page, start, end)
        assert _outlined(browser_page) == 1
        assert _stored_images(tmp_path) == [["/static/favicon.svg"]]


def test_selection_stopping_just_before_an_image_leaves_it_out(
    monkeypatch, tmp_path, browser_page
):
    # A browser often reports a selection that ends at a paragraph's end as
    # ending at the very start of the next block; that touches the image
    # block without covering the image.
    with _opened(browser_page, monkeypatch, tmp_path):
        _select_and_save(browser_page, "b[0].firstChild, 0", "b[1], 0")
        assert _outlined(browser_page) == 0
        assert _stored_images(tmp_path) == [[]]


@pytest.mark.parametrize(
    ("body", "end_block", "end_offset"),
    [
        pytest.param(IMAGE_BODY, 2, 6, id="spanning"),
        pytest.param(IMAGE_BODY, 1, 0, id="ending-on-image"),
        pytest.param(BARE_IMAGE_BODY, 2, 6, id="bare-img-block"),
    ],
)
def test_saved_highlight_over_an_image_marks_it_on_reload(
    monkeypatch, tmp_path, browser_page, body, end_block, end_offset
):
    with _opened(browser_page, monkeypatch, tmp_path, body) as (client, item_id):
        _save_highlight(
            client, item_id, start_block=0, start_offset=0,
            end_block=end_block, end_offset=end_offset,
        )
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        assert _outlined(browser_page) == 1


@pytest.mark.parametrize(
    "body", [IMAGE_BODY, BARE_IMAGE_BODY], ids=["wrapped-img", "bare-img-block"]
)
def test_double_clicking_an_image_highlights_it_without_selecting_text(
    monkeypatch, tmp_path, browser_page, body
):
    with _opened(browser_page, monkeypatch, tmp_path, body):
        assert _outlined(browser_page) == 0
        browser_page.dblclick(".article-body img")
        browser_page.wait_for_selector(".article-body img.hl-image", timeout=5000)
        assert _outlined(browser_page) == 1
        assert _stored_images(tmp_path) == [["/static/favicon.svg"]]


def test_double_clicking_an_already_highlighted_image_opens_its_detail_page(
    monkeypatch, tmp_path, browser_page
):
    with _opened(browser_page, monkeypatch, tmp_path, IMAGE_BODY) as (client, item_id):
        highlight_id = _save_highlight(
            client, item_id, start_block=1, start_offset=0, end_block=1, end_offset=0, text=""
        )
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        browser_page.dblclick(".article-body img")
        browser_page.wait_for_url(f"{ORIGIN}/items/{item_id}/highlights/{highlight_id}")
        # No duplicate highlight was created by the double-click.
        assert len(_stored_images(tmp_path)) == 1


def test_double_clicking_an_image_beside_text_in_its_block_does_nothing(
    monkeypatch, tmp_path, browser_page
):
    body = "<p>Caption text <img src=\"/static/favicon.svg\" alt=\"chart\"></p>"
    with _opened(browser_page, monkeypatch, tmp_path, body):
        browser_page.dblclick(".article-body img")
        browser_page.wait_for_timeout(200)
        assert _outlined(browser_page) == 0
        assert _stored_images(tmp_path) == []


LIST_BODY = (
    "<p>Two thresholds.</p>"
    "<ul>\n<li>Minimum viable</li>\n<li><em>Maximum</em> necessary</li>\n</ul>"
    "<p>After the list</p>"
)


def _list_state(page):
    return page.evaluate(
        """() => {
          const ul = document.querySelector(".article-body ul");
          return {
            items: Array.from(ul.children).map((el) => el.tagName + ":" + el.textContent),
            unmarked: Array.from(ul.querySelectorAll("li"))
              .flatMap((li) => {
                const walker = document.createTreeWalker(li, NodeFilter.SHOW_TEXT);
                const out = [];
                for (let n = walker.nextNode(); n; n = walker.nextNode()) {
                  if (n.textContent && !n.parentElement.closest("mark.hl")) out.push(n.textContent);
                }
                return out;
              }),
          };
        }"""
    )


def test_highlight_into_a_list_keeps_its_items_and_marks_them(
    monkeypatch, tmp_path, browser_page
):
    # A highlight running from a paragraph into a list used to wrap the
    # list items themselves in one <mark>, leaving empty bullets behind and
    # no visible highlight colour on the items.
    list_text = "\nMinimum viable\nMaximum necessary\n"
    with _opened(browser_page, monkeypatch, tmp_path, LIST_BODY) as (client, item_id):
        _save_highlight(
            client, item_id, start_block=0, start_offset=0,
            end_block=1, end_offset=len(list_text),
        )
        browser_page.goto(f"{ORIGIN}/items/{item_id}")
        state = _list_state(browser_page)
        assert state["items"] == ["LI:Minimum viable", "LI:Maximum necessary"]
        assert state["unmarked"] == []


def test_selecting_into_a_list_keeps_its_items(monkeypatch, tmp_path, browser_page):
    with _opened(browser_page, monkeypatch, tmp_path, LIST_BODY):
        _select_and_save(
            browser_page, "b[0].firstChild, 0", "b[1].children[1].lastChild, 10"
        )
        state = _list_state(browser_page)
        assert state["items"] == ["LI:Minimum viable", "LI:Maximum necessary"]
        assert state["unmarked"] == []


# Every block structure the sanitizer lets through (app/ingest.py
# ALLOWED_TAGS, plus tables kept for captured articles), with the
# whitespace between elements a real article carries.
STRUCTURES = {
    "bulleted-list": "<ul>\n<li>Bullet one</li>\n<li>Bullet <em>two</em></li>\n</ul>",
    "numbered-list": "<ol>\n<li>First step</li>\n<li>Second step</li>\n<li>Third step</li>\n</ol>",
    "nested-list": (
        "<ul>\n<li>Outer one\n<ul>\n<li>Inner a</li>\n<li>Inner b</li>\n</ul>\n</li>\n"
        "<li>Outer two</li>\n</ul>"
    ),
    "list-of-paragraphs": "<ul>\n<li><p>Para in item</p></li>\n<li><p>Another para</p></li>\n</ul>",
    "quote-box": "<blockquote>\n<p>Quoted first</p>\n<p>Quoted <strong>second</strong></p>\n</blockquote>",
    "table": (
        "<table>\n<thead><tr><th>Model</th><th>Score</th></tr></thead>\n<tbody>\n"
        "<tr><td>Alpha</td><td>91</td></tr>\n<tr><td>Beta</td><td>87</td></tr>\n</tbody>\n</table>"
    ),
    "code-block": "<pre><code>line one\n  line two\nline three</code></pre>",
    "figure": (
        '<figure>\n<img src="/static/favicon.svg" alt="c">\n'
        "<figcaption>A caption here</figcaption>\n</figure>"
    ),
    "inline-formatting": (
        '<p>Plain <a href="https://x.test">link <strong>bold</strong></a> and '
        "<em>em</em> <code>code</code> end</p>"
    ),
}

# Draws the page's highlights back off (as unwrapHighlight does) so the
# result can be compared with the page as served.
_UNWRAPPED_BODY = """() => {
  const clone = document.querySelector(".article-body").cloneNode(true);
  clone.querySelectorAll(".hl-title-marker").forEach((m) => m.remove());
  clone.querySelectorAll("mark.hl").forEach((m) => m.replaceWith(...m.childNodes));
  clone.querySelectorAll("img").forEach((i) => { i.removeAttribute("class"); delete i.dataset.highlightId; });
  clone.normalize();
  return clone.innerHTML;
}"""

_MARK_PROBLEMS = """() => {
  const problems = [];
  document.querySelectorAll(".article-body mark.hl").forEach((m) => {
    if (m.children.length) problems.push("mark holds elements: " + m.innerHTML);
    if (m.parentElement.matches("ul, ol, table, thead, tbody, tfoot, tr"))
      problems.push("mark loose in <" + m.parentElement.tagName + ">");
    const blockSibling = [m.previousSibling, m.nextSibling].some(
      (s) => s && s.nodeType === 1 && !getComputedStyle(s).display.startsWith("inline"));
    if (!m.textContent.trim() && blockSibling) problems.push("layout whitespace marked");
  });
  return problems;
}"""


@pytest.mark.parametrize("shape", ["into", "out-of", "over"])
@pytest.mark.parametrize("structure", list(STRUCTURES))
def test_highlight_across_a_block_structure_keeps_it_intact(
    monkeypatch, tmp_path, browser_page, structure, shape
):
    body = f"<p>Before text</p>{STRUCTURES[structure]}<p>After text</p>"
    with _opened(browser_page, monkeypatch, tmp_path, body) as (client, item_id):
        served = browser_page.evaluate(_UNWRAPPED_BODY)
        texts = browser_page.eval_on_selector_all(
            ".article-body > *", "els => els.map((e) => e.textContent)"
        )
        mid = len(texts[1]) // 2
        start, end = {
            "into": ((0, 3), (1, mid)),
            "out-of": ((1, mid), (2, 5)),
            "over": ((0, 3), (2, 5)),
        }[shape]
        _save_highlight(
            client, item_id, start_block=start[0], start_offset=start[1],
            end_block=end[0], end_offset=end[1],
        )
        browser_page.goto(f"{ORIGIN}/items/{item_id}")

        assert browser_page.evaluate(_UNWRAPPED_BODY) == served
        assert browser_page.evaluate(_MARK_PROBLEMS) == []
        if start[0] == end[0]:
            expected = texts[start[0]][start[1]:end[1]]
        else:
            expected = texts[start[0]][start[1]:] + "".join(
                texts[start[0] + 1:end[0]]) + texts[end[0]][:end[1]]
        marked = browser_page.eval_on_selector_all(
            ".article-body mark.hl", "els => els.map((e) => e.textContent).join('')"
        )
        assert "".join(marked.split()) == "".join(expected.split())
