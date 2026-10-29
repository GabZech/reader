from __future__ import annotations

import http.server
import socket
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from app import db as dbmod
from app import main as mainmod
from app.main import app

APP_STATIC = Path(mainmod.__file__).parent / "static"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextmanager
def _live_server(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started
    try:
        yield f"http://127.0.0.1:{port}", server
    finally:
        server.should_exit = True
        thread.join(timeout=10)


@pytest.fixture
def phone():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            yield browser.new_context(
                viewport={"width": 390, "height": 844}, service_workers="allow"
            ).new_page()
        finally:
            browser.close()


def test_a_page_that_cannot_load_or_be_found_offline_shows_a_retry_page(
    phone, monkeypatch, tmp_path
):
    # When the network fails and the page was never cached, the service worker
    # used to answer with nothing. An installed iPhone app shows that as a plain
    # white screen with no way out.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        server.should_exit = True
        time.sleep(1.5)

        response = phone.goto(f"{origin}/sources/never-cached")

        assert response is not None
        assert "Couldn't load this page" in phone.inner_text("body")
        assert phone.locator("a", has_text="Try again").count() == 1
        assert phone.evaluate("getComputedStyle(document.body).backgroundColor") != (
            "rgba(0, 0, 0, 0)"
        )
        logged = phone.evaluate("JSON.parse(localStorage.getItem('reader-log') || '[]').map(x => x.e)")
        assert "retry-page" in logged


def test_a_page_seen_before_still_opens_offline(phone, monkeypatch, tmp_path):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        phone.goto(f"{origin}/lists")
        server.should_exit = True
        time.sleep(1.5)

        phone.goto(f"{origin}/lists")

        assert phone.locator("h1", has_text="Lists").count() == 1


PIXEL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d4944415478da63f8ffff3f0005fe02fea7d6a4c50000000049454e44ae426082"
)


@contextmanager
def _image_server():
    """A second origin serving one image, like a blog's own image host."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(PIXEL_PNG)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}", server
    finally:
        server.shutdown()


def _wait_until_cached(phone, url, cache=None, timeout=15):
    lookup = f"caches.open('{cache}').then(c => c.match(u))" if cache else "caches.match(u)"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if phone.evaluate(f"(u) => {lookup}.then(r => !!r)", url):
            return
        time.sleep(0.2)
    raise AssertionError(f"{url} never reached the offline cache")


def test_a_read_later_article_never_opened_still_opens_offline(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server), _image_server() as (
        image_origin,
        image_server,
    ):
        item_id = httpx.post(
            f"{origin}/capture",
            data={"url": "https://blog.test/offline", "html": "<p>x</p>"},
        ).json()["item_id"]
        image_url = f"{image_origin}/pic.png"
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            conn.execute(
                "UPDATE items SET title = ?, body_html = ? WHERE id = ?",
                (
                    "Saved for the plane",
                    f'<p>Words to read offline</p><p><img src="{image_url}"></p>',
                    item_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _wait_until_cached(phone, image_url, cache="reader-images-v1")
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            assert dbmod.get_item(conn, item_id)["seen_at"] is None
        finally:
            conn.close()
        server.should_exit = True
        image_server.shutdown()
        time.sleep(1.5)

        for context in ("?from_list=later", "?from_home=1", ""):
            phone.goto(f"{origin}/items/{item_id}{context}")
            assert "Words to read offline" in phone.inner_text(".article-body")
            phone.wait_for_function(
                "document.querySelector('.article-body img').complete"
            )
            assert phone.evaluate(
                "document.querySelector('.article-body img').naturalWidth"
            ) == 1


# A worker like the one a phone already has installed: it keeps a page the
# reader opened earlier and knows nothing about downloading ahead.
OLDER_WORKER = """
self.addEventListener("install", (event) => {
  event.waitUntil(caches.open("reader-shell-v4").then((c) => c.add("/settings")));
  self.skipWaiting();
});
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
"""


def test_updating_from_an_older_worker_downloads_read_later_and_keeps_old_pages(
    phone, monkeypatch, tmp_path
):
    # On the phone the page that asks for the download is still controlled by
    # the older worker, which ignores the ask; and a renamed cache used to wipe
    # every page stored before the update.
    served = tmp_path / "served"
    (served / "static").mkdir(parents=True)
    worker = served / "static" / "sw.js"
    worker.write_text(OLDER_WORKER)
    monkeypatch.setattr(mainmod, "APP_DIR", served)
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = httpx.post(
            f"{origin}/capture",
            data={"url": "https://blog.test/update", "html": "<p>x</p>"},
        ).json()["item_id"]
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            conn.execute(
                "UPDATE items SET title = ?, body_html = ? WHERE id = ?",
                ("Saved before the update", "<p>Read me after updating</p>", item_id),
            )
            conn.commit()
        finally:
            conn.close()
        # Not Home: its sync reloads the page, and a reload that starts just
        # as the worker claims pages leaves that page with no worker at all.
        phone.goto(f"{origin}/sources")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        _wait_until_cached(phone, f"{origin}/settings")

        worker.write_text((APP_STATIC / "sw.js").read_text())
        phone.goto(f"{origin}/lists")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _wait_until_cached(phone, f"{origin}/lists/later")
        server.should_exit = True
        time.sleep(1.5)

        phone.goto(f"{origin}/lists/later")
        assert "Saved before the update" in phone.inner_text("body")
        phone.click("text=Saved before the update")
        phone.wait_for_selector(".article-body")
        assert "Read me after updating" in phone.inner_text(".article-body")
        phone.goto(f"{origin}/settings")
        assert "Couldn't load this page" not in phone.inner_text("body")


def test_homes_cog_turns_while_read_later_downloads_and_stops_when_done(
    phone, monkeypatch, tmp_path
):
    # The reader has to know when it is safe to go offline.
    slow_lists = mainmod.lists_for_home_edit

    def slowly(conn):
        time.sleep(2.5)
        return slow_lists(conn)

    monkeypatch.setattr(mainmod, "lists_for_home_edit", slowly)
    # Home's own sync turns the same cog; keep it out of the way.
    phone.add_init_script("sessionStorage.setItem('reader-synced', '1')")
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        item_id = httpx.post(
            f"{origin}/capture",
            data={"url": "https://blog.test/cog", "html": "<p>x</p>"},
        ).json()["item_id"]

        phone.goto(f"{origin}/")
        phone.wait_for_selector("#sync-status.is-updating", timeout=5000)
        assert phone.get_attribute("#sync-status", "aria-label") == "Settings (updating)"
        phone.wait_for_selector("#sync-status:not(.is-updating)", timeout=15000)

        assert phone.evaluate(
            "(u) => caches.match(u).then(r => !!r)", f"{origin}/items/{item_id}"
        )
        assert phone.get_attribute("#sync-status", "aria-label") == "Settings"


def test_a_highlight_made_online_still_shows_in_the_offline_copy(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = httpx.post(
            f"{origin}/capture",
            data={"url": "https://blog.test/stale", "html": "<p>x</p>"},
        ).json()["item_id"]
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            conn.execute(
                "UPDATE items SET body_html = ? WHERE id = ?",
                ("<p>Highlight me before the plane</p>", item_id),
            )
            conn.commit()
        finally:
            conn.close()
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")

        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        phone.evaluate(
            """() => {
              const p = document.querySelector(".article-body").children[0];
              const range = document.createRange();
              range.setStart(p.firstChild, 0);
              range.setEnd(p.firstChild, 12);
              getSelection().removeAllRanges();
              getSelection().addRange(range);
              p.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
            }"""
        )
        phone.wait_for_selector(".article-body mark.hl")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            stored = phone.evaluate(
                "(u) => caches.match(u).then(r => r.text())", f"{origin}/items/{item_id}"
            )
            if '"start_offset": 0' in stored:
                break
            time.sleep(0.2)
        server.should_exit = True
        time.sleep(1.5)

        phone.goto(f"{origin}/items/{item_id}?from_home=1")

        assert phone.inner_text(".article-body mark.hl") == "Highlight me"


def test_pages_leave_breadcrumbs_that_reach_the_server(phone, monkeypatch, tmp_path):
    # A white screen on the phone can only be traced if the page records what
    # it did and the next page sends that record to the server.
    import httpx

    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/sources")
        phone.wait_for_timeout(3600)
        phone.click(".tabbar >> text=Home")
        phone.wait_for_url(f"{origin}/")
        phone.wait_for_timeout(1500)

        events = httpx.get(f"{origin}/diagnostics?format=json").json()["events"]
        seen = {(e["e"], e["p"]) for e in events}

        assert ("start", "/sources") in seen
        assert ("load", "/sources") in seen
        assert ("check", "/sources") in seen
        assert ("tap", "/sources") in seen
        assert ("start", "/") in seen
        check = next(e for e in events if e["e"] == "check" and e["p"] == "/sources")
        assert "fcp=1" in check["d"]


def test_pages_record_where_the_bar_sits_while_scrolling(phone, monkeypatch, tmp_path):
    # The bottom bar leaves a gap on the phone while scrolling; the log has to
    # carry the numbers (viewport, safe areas, bar position) to explain it.
    import httpx

    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/sources")
        phone.evaluate("document.querySelector('.page').style.minHeight = '3000px'")
        phone.wait_for_timeout(900)
        phone.evaluate("document.querySelector('.scroller').scrollTo(0, 400)")
        phone.wait_for_timeout(900)
        phone.click(".tabbar >> text=Home")
        phone.wait_for_url(f"{origin}/")
        phone.wait_for_timeout(1200)

        events = httpx.get(f"{origin}/diagnostics?format=json").json()["events"]
        geo = [e["d"] for e in events if e["e"] == "geo" and e["p"] == "/sources"]

        assert any(d.startswith("load ") for d in geo)
        assert any(d.startswith("scroll ") for d in geo)
        scrolled = next(d for d in geo if d.startswith("scroll "))
        for part in ("ih=", "sh=", "vv=", "y=", "safe=", "bar=", "standalone="):
            assert part in scrolled


def _saved_article(origin, tmp_path, slug, body_html):
    item_id = httpx.post(
        f"{origin}/capture", data={"url": f"https://blog.test/{slug}", "html": "<p>x</p>"}
    ).json()["item_id"]
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        conn.execute("UPDATE items SET body_html = ? WHERE id = ?", (body_html, item_id))
        conn.commit()
    finally:
        conn.close()
    return item_id


def _select(phone, block, start, end):
    phone.evaluate(
        """([block, start, end]) => {
          const p = document.querySelector(".article-body").children[block];
          const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
          const at = (offset) => {
            let pos = 0;
            for (let n = walker.nextNode(); n; n = walker.nextNode()) {
              if (pos + n.textContent.length >= offset) return [n, offset - pos];
              pos += n.textContent.length;
            }
          };
          const range = document.createRange();
          range.setStart(...at(start));
          walker.currentNode = p;
          range.setEnd(...at(end));
          getSelection().removeAllRanges();
          getSelection().addRange(range);
          p.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
        }""",
        [block, start, end],
    )


def _marked(phone):
    return phone.evaluate(
        """() => [...document.querySelectorAll(".article-body mark.hl")].map((m) => ({
          text: m.textContent, id: m.dataset.highlightId, pending: m.classList.contains("is-pending"),
        }))"""
    )


def _highlight_texts(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [r["text"] for r in conn.execute("SELECT text FROM highlights ORDER BY id")]
    finally:
        conn.close()


def _wait_for(check, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if check():
            return
        time.sleep(0.2)
    raise AssertionError("never happened")


def test_a_highlight_made_offline_is_kept_and_sent_once_back_online(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        item_id = _saved_article(
            origin, tmp_path, "plane", "<p>Highlight me on the plane today</p><p>More</p>"
        )
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        phone.context.set_offline(True)

        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        _select(phone, 0, 0, 12)
        phone.wait_for_selector(".article-body mark.hl.is-pending")
        # A second, overlapping one joins the first on the phone.
        _select(phone, 0, 6, 25)
        _wait_for(lambda: "".join(m["text"] for m in _marked(phone)) == "Highlight me on the plane")
        assert {m["pending"] for m in _marked(phone)} == {True}

        phone.reload()
        phone.wait_for_selector(".article-body mark.hl.is-pending")
        assert "".join(m["text"] for m in _marked(phone)) == "Highlight me on the plane"
        assert _highlight_texts(tmp_path) == []

        phone.context.set_offline(False)
        _wait_for(lambda: _highlight_texts(tmp_path) == ["Highlight me on the plane"])
        _wait_for(lambda: all(not m["pending"] and m["id"].isdigit() for m in _marked(phone)))

        phone.reload()
        phone.wait_for_selector(".article-body mark.hl")
        assert "".join(m["text"] for m in _marked(phone)) == "Highlight me on the plane"
        assert _highlight_texts(tmp_path) == ["Highlight me on the plane"]


def test_reading_position_offline_is_kept_and_sent_back_online(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        body = "".join(f"<p>Paragraph {n} " + "word " * 120 + "</p>" for n in range(12))
        item_id = _saved_article(origin, tmp_path, "long", body)
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        phone.context.set_offline(True)

        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        phone.evaluate("document.querySelector('.article-body').children[6].scrollIntoView()")
        phone.wait_for_timeout(500)
        phone.goto(f"{origin}/lists/later")
        phone.goto(f"{origin}/items/{item_id}?from_list=later")

        assert phone.evaluate(
            "document.querySelector('.article-body').children[6].classList.contains('is-resume')"
        )

        phone.context.set_offline(False)
        phone.goto(f"{origin}/lists/later")

        def sent():
            conn = dbmod.connect(tmp_path / "reader.db")
            try:
                return dbmod.get_item(conn, item_id)["progress_index"] == 6
            finally:
                conn.close()

        _wait_for(sent)


def test_a_queued_highlight_the_server_refuses_is_dropped_not_retried_forever(
    phone, monkeypatch, tmp_path
):
    # Deleted on another device while this phone was offline: a refusal kept
    # in the queue would hold back every highlight queued after it.
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        gone = _saved_article(origin, tmp_path, "gone", "<p>Deleted elsewhere soon</p>")
        kept = _saved_article(origin, tmp_path, "kept", "<p>Still here afterwards</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{gone}")
        _wait_until_cached(phone, f"{origin}/items/{kept}")
        phone.context.set_offline(True)
        for item_id in (gone, kept):
            phone.goto(f"{origin}/items/{item_id}")
            _select(phone, 0, 0, 5)
            phone.wait_for_selector(".article-body mark.hl.is-pending")
        httpx.post(f"{origin}/items/{gone}/delete")

        phone.context.set_offline(False)

        _wait_for(lambda: _highlight_texts(tmp_path) == ["Still"])
        _wait_for(
            lambda: phone.evaluate(
                """() => new Promise((resolve) => {
                  const open = indexedDB.open("reader", 1);
                  open.onsuccess = () => {
                    const all = open.result.transaction("outbox").objectStore("outbox").getAll();
                    all.onsuccess = () => resolve(all.result.length === 0);
                  };
                })"""
            )
        )
        logged = phone.evaluate(
            "JSON.parse(localStorage.getItem('reader-log') || '[]').map(x => x.e)"
        )
        assert "outbox-dropped" in logged
