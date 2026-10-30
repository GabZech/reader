from __future__ import annotations

import asyncio
import http.server
import re
import socket
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import uvicorn

from app import db as dbmod
from app import main as mainmod
from app.main import app

APP_STATIC = Path(mainmod.__file__).parent / "static"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class _Network:
    """A relay between the browser and the app that can drop, like airplane
    mode: every open connection is cut and new ones are refused, so requests
    fail as a network error and only the service worker can answer.
    WebKit's own offline switch also refuses pages the worker could serve,
    which a real iPhone does not do."""

    def __init__(self, upstream_port: int):
        self.upstream_port = upstream_port
        self.open: set[socket.socket] = set()
        self.lock = threading.Lock()
        self.port = 0
        self.listener = None
        self.up()

    def _accept(self, listener):
        while True:
            try:
                client, _ = listener.accept()
            except OSError:
                return
            try:
                upstream = socket.create_connection(("127.0.0.1", self.upstream_port))
            except OSError:
                client.close()
                continue
            with self.lock:
                self.open.update((client, upstream))
            for a, b in ((client, upstream), (upstream, client)):
                threading.Thread(target=self._pipe, args=(a, b), daemon=True).start()

    def _pipe(self, source, target):
        try:
            while chunk := source.recv(65536):
                target.sendall(chunk)
        except OSError:
            pass
        finally:
            # Shut down before closing: the thread piping the other way is
            # blocked reading one of these sockets, and a bare close() neither
            # wakes it nor stops it reading whatever new connection reuses
            # the freed descriptor (which stalled page loads at random).
            for sock in (source, target):
                with self.lock:
                    self.open.discard(sock)
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            for sock in (source, target):
                try:
                    sock.close()
                except OSError:
                    pass

    def down(self):
        # No listener at all: a connection is refused outright, as in
        # airplane mode, rather than accepted and dropped.
        if self.listener is not None:
            # Shut down first: the thread waiting in accept() otherwise keeps
            # the port, and going back online cannot bind it again.
            try:
                self.listener.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.listener.close()
            self.listener = None
        with self.lock:
            cut, self.open = list(self.open), set()
        for sock in cut:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except OSError:
                pass

    def up(self):
        if self.listener is not None:
            return
        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", self.port))
        listener.listen(64)
        self.port = listener.getsockname()[1]
        self.listener = listener
        threading.Thread(target=self._accept, args=(listener,), daemon=True).start()

    def close(self):
        self.down()


class _SlowSaves:
    """Holds back new highlights for a few seconds when switched on, without
    holding up anything else the server answers."""

    def __init__(self, app):
        self.app = app
        self.seconds = 0

    async def __call__(self, scope, receive, send):
        if (
            self.seconds
            and scope["type"] == "http"
            and scope["method"] == "POST"
            and scope["path"].endswith("/highlights")
        ):
            await asyncio.sleep(self.seconds)
        await self.app(scope, receive, send)


@contextmanager
def _live_server(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    port = _free_port()
    slow_saves = _SlowSaves(app)
    server = uvicorn.Server(uvicorn.Config(slow_saves, port=port, log_level="warning"))
    server.slow_saves = slow_saves
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started
    server.network = _Network(port)
    try:
        yield f"http://127.0.0.1:{server.network.port}", server
    finally:
        server.network.close()
        server.should_exit = True
        thread.join(timeout=10)


def _app_url(server):
    """The app itself, past the relay: for what another device does."""
    return f"http://127.0.0.1:{server.network.upstream_port}"


def _wait_for_quote(phone, text):
    # Offline the page fills its passage in a moment after it opens.
    phone.wait_for_function(
        "(t) => document.querySelector('blockquote.quote').textContent === t", arg=text
    )


def _go_offline(phone, server):
    server.network.down()
    phone.evaluate(
        "sessionStorage.setItem('test-offline', '1'); window.dispatchEvent(new Event('offline'))"
    )


def _go_online(phone, server):
    server.network.up()
    phone.evaluate(
        "sessionStorage.removeItem('test-offline'); window.dispatchEvent(new Event('online'))"
    )


def test_a_page_that_cannot_load_or_be_found_offline_shows_a_retry_page(
    phone, monkeypatch, tmp_path
):
    # When the network fails and the page was never cached, the service worker
    # used to answer with nothing. An installed iPhone app shows that as a plain
    # white screen with no way out.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        server.network.down()
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
        server.network.down()
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
    # An article is stored once per way in (?from_list=...): any will do.
    ignore = "true" if re.search(r"/items/\d+$", url) else "false"
    options = f"{{ ignoreSearch: {ignore} }}"
    lookup = (
        f"caches.open('{cache}').then(c => c.match(u, {options}))"
        if cache
        else f"caches.match(u, {options})"
    )
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
        # WebKit sometimes leaves the ask made during the update unanswered;
        # every page asks, so the download happens by the next one.
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        phone.goto(f"{origin}/sources")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _wait_until_cached(phone, f"{origin}/lists/later")
        server.network.down()
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
            "(u) => caches.match(u, { ignoreSearch: true }).then(r => !!r)",
            f"{origin}/items/{item_id}",
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
                "(u) => caches.match(u).then(r => (r ? r.text() : ''))", f"{origin}/items/{item_id}"
            )
            if '"start_offset": 0' in stored:
                break
            time.sleep(0.2)
        server.network.down()
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
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(
            origin, tmp_path, "plane", "<p>Highlight me on the plane today</p><p>More</p>"
        )
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)

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

        _go_online(phone, server)
        _wait_for(lambda: _highlight_texts(tmp_path) == ["Highlight me on the plane"])
        _wait_for(lambda: all(not m["pending"] and m["id"].isdigit() for m in _marked(phone)))

        phone.reload()
        phone.wait_for_selector(".article-body mark.hl")
        assert "".join(m["text"] for m in _marked(phone)) == "Highlight me on the plane"
        assert _highlight_texts(tmp_path) == ["Highlight me on the plane"]


def test_reading_position_offline_is_kept_and_sent_back_online(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        body = "".join(f"<p>Paragraph {n} " + "word " * 120 + "</p>" for n in range(12))
        item_id = _saved_article(origin, tmp_path, "long", body)
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)

        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        phone.evaluate("document.querySelector('.article-body').children[6].scrollIntoView()")
        phone.wait_for_timeout(500)
        phone.goto(f"{origin}/lists/later")
        phone.goto(f"{origin}/items/{item_id}?from_list=later")

        assert phone.evaluate(
            "document.querySelector('.article-body').children[6].classList.contains('is-resume')"
        )

        _go_online(phone, server)
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
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        gone = _saved_article(origin, tmp_path, "gone", "<p>Deleted elsewhere soon</p>")
        kept = _saved_article(origin, tmp_path, "kept", "<p>Still here afterwards</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{gone}")
        _wait_until_cached(phone, f"{origin}/items/{kept}")
        _go_offline(phone, server)
        for item_id in (gone, kept):
            phone.goto(f"{origin}/items/{item_id}")
            _select(phone, 0, 0, 5)
            phone.wait_for_selector(".article-body mark.hl.is-pending")
        # Another device, which still has a connection.
        httpx.post(f"{_app_url(server)}/items/{gone}/delete")

        _go_online(phone, server)

        _wait_for(lambda: _highlight_texts(tmp_path) == ["Still"])
        _wait_for(
            lambda: phone.evaluate("JSON.parse(localStorage.getItem('reader-outbox') || '[]').length")
            == 0
        )
        logged = phone.evaluate(
            "JSON.parse(localStorage.getItem('reader-log') || '[]').map(x => x.e)"
        )
        assert "outbox-dropped" in logged


def _highlight_rows(tmp_path):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM highlights ORDER BY id")]
    finally:
        conn.close()


def _open_highlight(phone, text):
    phone.click(f".article-body mark.hl >> text={text}")
    phone.wait_for_selector("h1:has-text('Highlight')")


def test_a_pending_highlight_can_be_titled_keyed_and_deleted_offline(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(
            origin, tmp_path, "edits", "<p>First passage to keep</p><p>Second one to drop</p>"
        )
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        _select(phone, 0, 0, 13)
        phone.wait_for_selector(".article-body mark.hl.is-pending")

        _open_highlight(phone, "First passage")
        _wait_for_quote(phone, "First passage")
        phone.click("text=Add section title")
        phone.wait_for_selector("h1:has-text('Section title')")
        _wait_for_quote(phone, "First passage")
        phone.fill("#highlight-title", "Part one")
        phone.click("button:has-text('Done')")
        phone.wait_for_selector(".article-body .hl-title-marker")

        _open_highlight(phone, "First passage")
        phone.click("text=Mark as key passage")
        phone.wait_for_selector(".article-body .hl-key-marker")

        _select(phone, 1, 0, 10)
        phone.wait_for_selector(".article-body mark.hl >> text=Second one")
        _open_highlight(phone, "Second one")
        phone.click("text=Delete highlight")
        phone.wait_for_selector(".article-body")
        _wait_for(lambda: len(_marked(phone)) == 1)

        phone.reload()
        phone.wait_for_selector(".article-body .hl-key-marker")
        assert phone.locator(".article-body .hl-title-marker").count() == 1
        assert [m["text"] for m in _marked(phone)] == ["First passage"]
        _open_highlight(phone, "First passage")
        assert phone.locator("text=Unmark key passage").count() == 1

        _go_online(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")

        _wait_for(lambda: len(_highlight_rows(tmp_path)) == 1 and _highlight_rows(tmp_path)[0]["is_key"])
        [row] = _highlight_rows(tmp_path)
        assert (row["text"], row["section_title"], row["is_key"]) == ("First passage", "Part one", 1)


def test_a_synced_highlight_can_be_edited_and_deleted_offline(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(
            origin, tmp_path, "synced", "<p>Already saved passage</p><p>Another saved one</p>"
        )
        for block, end, text in ((0, 13, "Already saved"), (1, 13, "Another saved")):
            httpx.post(
                f"{origin}/items/{item_id}/highlights",
                data={
                    "start_block": str(block),
                    "start_offset": "0",
                    "end_block": str(block),
                    "end_offset": str(end),
                    "text": text,
                },
            )
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight-title/subsection")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")

        _open_highlight(phone, "Already saved")
        _wait_for_quote(phone, "Already saved")
        phone.click("text=Add subsection title")
        phone.fill("#highlight-title", "Detail")
        phone.click("button:has-text('Done')")
        phone.wait_for_selector(".article-body .hl-title-marker")
        _open_highlight(phone, "Another saved")
        phone.click("text=Delete highlight")
        phone.wait_for_selector(".article-body")
        _wait_for(lambda: [m["text"] for m in _marked(phone)] == ["Already saved"])
        assert len(_highlight_rows(tmp_path)) == 2

        _go_online(phone, server)
        phone.goto(f"{origin}/lists/later")

        _wait_for(lambda: len(_highlight_rows(tmp_path)) == 1)
        _wait_for(lambda: _highlight_rows(tmp_path)[0]["subsection_title"] == "Detail")


def test_the_article_bar_says_offline_and_what_waits_only_while_offline(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(origin, tmp_path, "label", "<p>Label me while away</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        assert not phone.is_visible(".sync-state")

        _go_offline(phone, server)
        phone.wait_for_selector(".sync-state:has-text('Offline')")
        assert phone.inner_text(".sync-state") == "Offline"
        _select(phone, 0, 0, 8)
        phone.wait_for_selector(".sync-state:has-text('Offline · 1 to sync')")

        # Online the label goes at once, sent yet or not.
        failing = lambda route: route.fulfill(status=503, body="busy")
        phone.route(f"{origin}/items/{item_id}/highlights", failing)
        _go_online(phone, server)
        phone.wait_for_selector(".sync-state", state="hidden")

        phone.unroute(f"{origin}/items/{item_id}/highlights", failing)
        phone.evaluate("window.dispatchEvent(new Event('online'))")
        _wait_for(lambda: _highlight_texts(tmp_path) == ["Label me"])


def test_a_cog_left_turning_by_a_lost_done_message_stops_at_the_next_ask(
    phone, monkeypatch, tmp_path
):
    # During an update the worker that finished the download no longer
    # controls the page, and its "done" never arrived: the cog kept turning.
    phone.add_init_script("sessionStorage.setItem('reader-synced', '1')")
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/")
        phone.wait_for_function("navigator.serviceWorker.controller !== null")
        phone.wait_for_selector("#sync-status:not(.is-updating)")
        phone.evaluate(
            """() => navigator.serviceWorker.dispatchEvent(
              new MessageEvent("message", { data: { type: "downloading", running: true } })
            )"""
        )
        phone.wait_for_selector("#sync-status.is-updating")

        phone.evaluate("window.dispatchEvent(new Event('online'))")

        phone.wait_for_selector("#sync-status:not(.is-updating)", timeout=5000)


def test_closing_a_pending_highlights_page_returns_to_the_article_with_it(
    phone, monkeypatch, tmp_path
):
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(origin, tmp_path, "close", "<p>Close me and come back</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        _select(phone, 0, 0, 8)
        phone.wait_for_selector(".article-body mark.hl.is-pending")

        _open_highlight(phone, "Close me")
        phone.click(".top-edit")

        phone.wait_for_selector(".article-body")
        assert urlsplit(phone.url).path == f"/items/{item_id}"
        phone.wait_for_selector(".article-body mark.hl.is-pending")
        assert [m["text"] for m in _marked(phone)] == ["Close me"]


def test_close_leads_back_to_the_article_before_the_page_is_filled_in(
    phone, monkeypatch, tmp_path
):
    # On a phone, filling the page in can take a moment; a Close tapped
    # meanwhile went to Home.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(origin, tmp_path, "early", "<p>Close me early on</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        _select(phone, 0, 0, 8)
        phone.wait_for_selector(".article-body mark.hl.is-pending")
        # Stall the outbox on the highlight page only, so it never fills in.
        phone.add_init_script(
            "if (location.pathname.includes('/highlights/')) indexedDB.open = () => ({});"
        )

        _open_highlight(phone, "Close me")
        phone.click(".top-edit")

        phone.wait_for_selector(".article-body mark.hl.is-pending")
        assert urlsplit(phone.url).path == f"/items/{item_id}"


# The phone's database answering slowly, as on a phone opening it cold.
SLOW_PHONE_DATABASE = """
const realOpen = IDBFactory.prototype.open;
IDBFactory.prototype.open = function (...args) {
  const real = realOpen.apply(this, args);
  const slow = { result: null, error: null, onsuccess: null, onerror: null, onupgradeneeded: null };
  real.onupgradeneeded = (e) => {
    slow.result = real.result;
    if (slow.onupgradeneeded) slow.onupgradeneeded(e);
  };
  real.onsuccess = () =>
    setTimeout(() => {
      slow.result = real.result;
      if (slow.onsuccess) slow.onsuccess();
    }, 1500);
  real.onerror = () => {
    slow.error = real.error;
    if (slow.onerror) slow.onerror();
  };
  return slow;
};
"""


def test_a_highlight_made_right_after_opening_an_article_is_not_wiped(
    phone, monkeypatch, tmp_path
):
    # The page catches up with the phone's queue a moment after opening; a
    # highlight made before that catch-up finished was removed by it.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(origin, tmp_path, "quick", "<p>Highlight me straight away</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        phone.add_init_script(SLOW_PHONE_DATABASE)
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")

        _select(phone, 0, 0, 12)
        phone.wait_for_timeout(2500)

        assert [m["text"] for m in _marked(phone)] == ["Highlight me"]
        phone.reload()
        phone.wait_for_selector(".article-body mark.hl.is-pending", timeout=5000)
        assert [m["text"] for m in _marked(phone)] == ["Highlight me"]


def test_a_highlight_page_button_returns_at_once_while_saves_are_still_sending(
    phone, monkeypatch, tmp_path
):
    # Done, Delete and the key button used to wait for every queued save to
    # reach the server first: on a slow connection, tapping seemed to do
    # nothing (a title tapped five times was sent five times).
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(origin, tmp_path, "slow", "<p>Key me while it is slow</p>")
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        _select(phone, 0, 0, 6)
        phone.wait_for_selector(".article-body mark.hl.is-pending")
        _open_highlight(phone, "Key me")
        _wait_for_quote(phone, "Key me")

        server.slow_saves.seconds = 4
        _go_online(phone, server)
        phone.click("text=Mark as key passage")

        phone.wait_for_url(lambda url: url.endswith(f"/items/{item_id}") or f"/items/{item_id}#highlight-" in url, timeout=1500)
        _wait_for(
            lambda: [(r["text"], r["is_key"]) for r in _highlight_rows(tmp_path)]
            == [("Key me", 1)],
            timeout=20,
        )


def test_the_whole_offline_highlighting_journey(phone, monkeypatch, tmp_path):
    # The reader's own steps on the phone, end to end, as reported back.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(
            origin, tmp_path, "journey", "<p>Keep this passage safe</p><p>Drop this one later</p>"
        )
        article = f"{origin}/items/{item_id}"
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight-title/section")
        phone.goto(f"{article}?from_list=later")
        # A phone's database is slow to answer when a page opens.
        phone.add_init_script(SLOW_PHONE_DATABASE)

        _go_offline(phone, server)
        phone.goto(f"{article}?from_list=later")
        _select(phone, 0, 0, 14)
        _select(phone, 1, 0, 13)
        _wait_for(lambda: len(_marked(phone)) == 2)

        _open_highlight(phone, "Keep this pass")
        _wait_for_quote(phone, "Keep this pass")
        phone.click("text=Add section title")
        phone.wait_for_selector("h1:has-text('Section title')")
        _wait_for_quote(phone, "Keep this pass")
        phone.fill("#highlight-title", "Part one")
        phone.click("button:has-text('Done')")
        phone.wait_for_selector(".article-body .hl-title-marker", timeout=5000)

        _open_highlight(phone, "Keep this pass")
        phone.click(".top-edit")
        phone.wait_for_selector(".article-body mark.hl", timeout=5000)
        assert urlsplit(phone.url).path == f"/items/{item_id}"

        _open_highlight(phone, "Keep this pass")
        _wait_for_quote(phone, "Keep this pass")
        phone.click("text=Mark as key passage")
        phone.wait_for_selector(".article-body .hl-key-marker", timeout=5000)

        _open_highlight(phone, "Drop this one")
        phone.click("text=Delete highlight")
        phone.wait_for_url(lambda url: urlsplit(url).path == f"/items/{item_id}", timeout=5000)
        _wait_for(lambda: [m["text"] for m in _marked(phone)] == ["Keep this pass"])

        phone.goto(f"{origin}/lists/later")
        phone.goto(f"{article}?from_list=later")
        phone.wait_for_selector(".article-body .hl-key-marker")
        assert phone.locator(".article-body .hl-title-marker").count() == 1
        assert [m["text"] for m in _marked(phone)] == ["Keep this pass"]
        assert phone.inner_text(".sync-state").startswith("Offline · ")

        _go_online(phone, server)
        phone.wait_for_selector(".sync-state", state="hidden")
        _wait_for(
            lambda: [(r["text"], r["section_title"], r["is_key"]) for r in _highlight_rows(tmp_path)]
            == [("Keep this pass", "Part one", 1)],
            timeout=15,
        )
        phone.wait_for_timeout(1000)

        _go_offline(phone, server)
        phone.goto(f"{origin}/lists/later")
        phone.goto(f"{article}?from_list=later")
        phone.wait_for_selector(".article-body .hl-key-marker")
        assert [m["text"] for m in _marked(phone)] == ["Keep this pass"]
        assert phone.locator(".article-body .hl-title-marker").count() == 1


def test_a_title_typed_before_the_page_fills_in_is_kept(phone, monkeypatch, tmp_path):
    # Offline the title page fills in the current title a moment after it
    # opens; it used to overwrite what the reader had started typing.
    with _live_server(monkeypatch, tmp_path) as (origin, server):
        item_id = _saved_article(origin, tmp_path, "typed", "<p>Title me quickly</p>")
        httpx.post(
            f"{origin}/items/{item_id}/highlights",
            data={"start_block": "0", "start_offset": "0", "end_block": "0", "end_offset": "8", "text": "Title me"},
        )
        phone.goto(f"{origin}/settings")
        _wait_until_cached(phone, f"{origin}/offline/highlight-title/section")
        _wait_until_cached(phone, f"{origin}/items/{item_id}")
        _go_offline(phone, server)
        phone.goto(f"{origin}/items/{item_id}?from_list=later")
        # The title page takes a moment to fill itself in, as on a phone.
        phone.add_init_script(
            """if (location.pathname.endsWith("-title")) {
              const real = window.fetch;
              window.fetch = (...args) =>
                new Promise((resolve) => setTimeout(() => resolve(real(...args)), 1500));
            }"""
        )
        _open_highlight(phone, "Title me")
        phone.click("text=Add section title")
        phone.wait_for_selector("h1:has-text('Section title')")
        phone.fill("#highlight-title", "Typed first")
        _wait_for_quote(phone, "Title me")

        assert phone.input_value("#highlight-title") == "Typed first"
