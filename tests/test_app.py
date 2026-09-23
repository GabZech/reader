from __future__ import annotations

import html
import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app import db as dbmod
from app.main import app

FIXTURE = Path(__file__).parent / "fixtures" / "feed.xml"
CAPTURE_BLOG_HTML = (
    Path(__file__).parent / "fixtures" / "capture" / "blog.html"
).read_text(encoding="utf-8")
BLOG_HTML = """<!doctype html>
<html><head>
<link rel="alternate" type="application/rss+xml" href="https://example.test/feed.xml">
</head><body>blog</body></html>
"""
NOT_FEED_HTML = "<html><body>no feed here</body></html>"
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@testchannel"
YOUTUBE_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCtest123"
YOUTUBE_CHANNEL_HTML = f"""<!doctype html>
<html><head>
<link rel="alternate" type="application/rss+xml" href="{YOUTUBE_FEED_URL}">
</head><body>channel</body></html>
"""


def _fetch(url: str, timeout: float = 8.0) -> tuple[str, str]:
    if url.rstrip("/") == "https://example.test/feed.xml":
        return url, FIXTURE.read_text(encoding="utf-8")
    if url.rstrip("/").endswith("/blog"):
        return url, BLOG_HTML
    if url == YOUTUBE_CHANNEL_URL:
        return url, YOUTUBE_CHANNEL_HTML
    if url == YOUTUBE_FEED_URL:
        return url, FIXTURE.read_text(encoding="utf-8")
    return url, NOT_FEED_HTML


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    monkeypatch.delenv("OBSIDIAN_GITHUB_TOKEN", raising=False)
    monkeypatch.setattr("app.ingest.fetch_url", _fetch)
    real_visible = dbmod._visible_items
    frozen = datetime(2026, 8, 20, 12, tzinfo=UTC)

    def visible(conn, slug, now=None, archived=False, read=False):
        return real_visible(conn, slug, now or frozen, archived=archived, read=read)

    monkeypatch.setattr(dbmod, "_visible_items", visible)
    return TestClient(app)


def test_health_reports_ok_and_sha(monkeypatch, tmp_path):
    monkeypatch.setenv("GIT_SHA", "abc1234")
    with _client(monkeypatch, tmp_path) as client:
        response = client.get("/health")
        assert response.json() == {"ok": True, "sha": "abc1234"}


def test_health_sha_defaults_to_dev(monkeypatch, tmp_path):
    monkeypatch.delenv("GIT_SHA", raising=False)
    with _client(monkeypatch, tmp_path) as client:
        assert client.get("/health").json()["sha"] == "dev"


def _add_to_news(client: TestClient, url: str, window: str = "week", backfill: str = "all"):
    added = client.post("/sources/add", data={"url": url})
    assert added.status_code == 200
    assert "This feed currently has" in added.text
    listed = client.post(
        "/sources/add/count",
        data={
            "feed_url": "https://example.test/feed.xml",
            "title": "Fixture news",
            "item_count": "2",
            "backfill": backfill,
        },
    )
    assert listed.status_code == 200
    assert "Choose a list" in listed.text
    windowed = client.post(
        "/sources/add/list",
        data={
            "feed_url": "https://example.test/feed.xml",
            "title": "Fixture news",
            "item_count": "2",
            "backfill": "" if backfill == "all" else backfill,
            "list_slug": "news",
        },
    )
    assert windowed.status_code == 200
    assert "How far back" in windowed.text
    done = client.post(
        "/sources/add/window",
        data={
            "feed_url": "https://example.test/feed.xml",
            "title": "Fixture news",
            "item_count": "2",
            "backfill": "" if backfill == "all" else backfill,
            "list_slug": "news",
            "window": window,
        },
    )
    return done


def _fill_every_home_list(client: TestClient, tmp_path) -> None:
    _add_to_news(client, "https://example.test/feed.xml")
    item_id = _first_item_id(tmp_path)
    client.post(f"/items/{item_id}/later")
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        conn.execute(
            "INSERT INTO item_lists (item_id, list_slug, added_at) VALUES (?, 'fav', ?)",
            (item_id, datetime(2026, 8, 20, tzinfo=UTC).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def test_home_shell(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _fill_every_home_list(client, tmp_path)
        response = client.get("/")
    assert response.status_code == 200
    assert "Home" in response.text
    assert "News" in response.text
    assert "Read later" in response.text
    assert "Favourite channels" in response.text
    assert "Lists" in response.text
    assert "Sources" in response.text


def test_home_has_settings_link(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert 'href="/settings"' in response.text


def test_settings_page_has_theme_toggle(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as client:
        response = client.get("/settings")
    assert response.status_code == 200
    assert "Appearance" in response.text
    assert "theme-toggle" in response.text


def test_settings_page_has_a_read_later_bookmarklet(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as client:
        response = client.get("/settings")
    assert response.status_code == 200
    assert 'href="javascript:' in response.text
    assert "/capture" in response.text
    assert "outerHTML" in response.text


def test_home_hides_lists_with_nothing_unread(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        home = client.get("/")
    assert 'href="/lists/news"' in home.text
    assert 'href="/lists/later"' not in home.text
    assert 'href="/lists/fav"' not in home.text
    assert "all caught up" not in home.text


def test_home_says_all_caught_up_when_every_list_is_empty(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        home = client.get("/")
        edit = client.get("/home/edit")
    assert "You're all caught up." in home.text
    assert "data-list" not in home.text
    assert "Read later" in edit.text
    assert "Favourite channels" in edit.text


def test_home_edit_shows_lists_with_move_boundaries(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.get("/home/edit")
    assert response.status_code == 200
    assert "Home lists" in response.text
    assert response.text.index("News") < response.text.index("Read later")
    assert response.text.index("Read later") < response.text.index("Favourite channels")
    first_moves = response.text.split('action="/home/edit/news/move"')[1]
    assert "disabled" in first_moves.split("</form>")[0]
    last_moves = response.text.split('action="/home/edit/fav/move"')[2]
    assert "disabled" in last_moves.split("</form>")[0]


def test_home_edit_toggle_hides_list_from_home(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _fill_every_home_list(client, tmp_path)
        toggled = client.post("/home/edit/news/toggle", follow_redirects=False)
        assert toggled.status_code == 303
        edit_page = client.get("/home/edit")
        assert "Hidden" in edit_page.text
        home = client.get("/")
        assert 'href="/lists/news"' not in home.text
        client.post("/home/edit/news/toggle")
        home_again = client.get("/")
        assert 'href="/lists/news"' in home_again.text


def test_home_edit_move_reorders_lists(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _fill_every_home_list(client, tmp_path)
        client.post(
            "/home/edit/news/move", data={"direction": "down"}, follow_redirects=False
        )
        edit_page = client.get("/home/edit")
        assert edit_page.text.index("Read later") < edit_page.text.index("News")
        home = client.get("/")
        assert home.text.index("Read later") < home.text.index(">News<")


def test_sources_has_add_source(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        sources = client.get("/sources")
    assert sources.status_code == 200
    assert "Add source" in sources.text
    assert 'href="/sources/add"' in sources.text


def test_empty_paste_stays_on_add(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post("/sources/add", data={"url": "   "})
    assert response.status_code == 200
    assert "Add source" in response.text
    assert "Paste a feed" in response.text


def test_no_feed_says_so(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/sources/add", data={"url": "https://none.example.test/not-a-feed"}
        )
    assert response.status_code == 200
    assert "We could not find a feed." in response.text


def test_add_rss_to_news_from_blog_page(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        done = _add_to_news(client, "https://example.test/blog")
        assert done.status_code == 200
        assert "Fixture news is on News" in done.text
        sources = client.get("/sources")
        assert "Fixture news" in sources.text
        assert "News (&lt;7days)" in sources.text
        news = client.get("/lists/news")
        assert "First fixture item" in news.text
        assert "Second fixture item" in news.text


def test_youtube_channel_url_lands_on_favourite_channels(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        added = client.post("/sources/add", data={"url": YOUTUBE_CHANNEL_URL})
        assert added.status_code == 200
        assert "This feed currently has" in added.text
        client.post(
            "/sources/add/count",
            data={
                "feed_url": YOUTUBE_FEED_URL,
                "title": "Test Channel",
                "item_count": "2",
                "backfill": "all",
            },
        )
        done = client.post(
            "/sources/add/list",
            data={
                "feed_url": YOUTUBE_FEED_URL,
                "title": "Test Channel",
                "item_count": "2",
                "backfill": "",
                "list_slug": "fav",
            },
        )
        assert done.status_code == 200
        assert "is on Favourite channels" in done.text
        sources = client.get("/sources")
        assert "YouTube · Favourite channels" in sources.text


def test_youtube_source_is_included_in_sync(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.post("/sources/add", data={"url": YOUTUBE_CHANNEL_URL})
        client.post(
            "/sources/add/count",
            data={
                "feed_url": YOUTUBE_FEED_URL,
                "title": "Test Channel",
                "item_count": "2",
                "backfill": "all",
            },
        )
        client.post(
            "/sources/add/list",
            data={
                "feed_url": YOUTUBE_FEED_URL,
                "title": "Test Channel",
                "item_count": "2",
                "backfill": "",
                "list_slug": "fav",
            },
        )
        synced = client.post("/sync")
        assert synced.status_code == 200
        assert synced.json()["sources"] == 1


def test_video_url_finds_no_feed(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/sources/add",
            data={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        )
    assert response.status_code == 200
    assert "We could not find a feed." in response.text


def test_sync_includes_unconfigured_mail_result(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post("/sync")
    assert response.status_code == 200
    assert response.json()["mail"] == {"configured": False, "created": 0, "sources": 0}


def _insert_mail_source(tmp_path, source_id, address, title, pending_notice=True):
    conn = dbmod.connect(Path(tmp_path) / "reader.db")
    dbmod.init_db(conn)
    dbmod.insert_source(
        conn,
        source_id=source_id,
        kind="mail",
        title=title,
        feed_url=None,
        backfill=None,
        mail_address=address,
        pending_notice=pending_notice,
    )
    conn.commit()
    conn.close()


def test_sources_notice_dot_shows_and_clears_on_source_open(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _insert_mail_source(tmp_path, "mail-1", "a@newsletter.test", "A Newsletter")

        home = client.get("/")
        assert '<span class="dot" aria-hidden="true"></span>' in home.text

        client.get("/sources")
        home_still = client.get("/")
        assert '<span class="dot" aria-hidden="true"></span>' in home_still.text

        client.get("/sources/mail-1/items")
        home_after = client.get("/")
        assert '<span class="dot" aria-hidden="true"></span>' not in home_after.text


def test_sources_page_groups_by_kind_newest_first_and_highlights_new(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _insert_mail_source(tmp_path, "mail-old", "old@newsletter.test", "Old Newsletter", pending_notice=False)
        _insert_mail_source(tmp_path, "mail-new", "new@newsletter.test", "New Newsletter", pending_notice=True)
        _add_to_news(client, "https://example.test/blog")

        response = client.get("/sources")
        text = response.text
        assert text.index("Newsletter</h2>") < text.index("RSS</h2>")
        assert text.index("New Newsletter") < text.index("Old Newsletter")

        def item_class(source_id: str) -> str:
            marker = f'href="/sources/{source_id}/items"'
            before = text.split(marker)[0]
            return before[before.rindex('<a class="') :]

        assert "is-new" in item_class("mail-new")
        assert "is-new" not in item_class("mail-old")


def test_duplicate_feed_goes_to_existing_source(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        again = client.post(
            "/sources/add",
            data={"url": "https://example.test/blog"},
            follow_redirects=False,
        )
        assert again.status_code == 303
        assert again.headers["location"].startswith("/sources/")
        assert "already=1" in again.headers["location"]
        page = client.get(again.headers["location"])
        assert page.status_code == 200
        assert "Fixture news is already in Sources." in page.text
        assert "Delete source" in page.text
        assert "News (&lt;7days)" in page.text
        sources = client.get("/sources")
        assert sources.text.count("Fixture news") == 1


def test_sync_ingests_added_source(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        synced = client.post("/sync")
        assert synced.status_code == 200
        assert synced.json()["sources"] == 1
        news = client.get("/lists/news")
        assert "First fixture item" in news.text


def test_lists_has_add_list(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        lists = client.get("/lists")
    assert lists.status_code == 200
    assert "Add list" in lists.text
    assert 'href="/lists/add"' in lists.text


def test_empty_list_name_stays_on_add(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post("/lists/add", data={"name": "   "})
    assert response.status_code == 200
    assert "Add list" in response.text
    assert "Name this list." in response.text


def test_create_list_shows_on_lists_and_can_open(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        created = client.post("/lists/add", data={"name": "Weekend"})
        assert created.status_code == 200
        assert "Weekend" in created.text
        assert 'href="/lists/weekend"' in created.text
        opened = client.get("/lists/weekend")
        assert opened.status_code == 200
        assert "<h1>Weekend</h1>" in opened.text
        home = client.get("/")
        assert "Weekend" not in home.text


def test_duplicate_list_name_goes_to_existing(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        again = client.post(
            "/lists/add", data={"name": "News"}, follow_redirects=False
        )
        assert again.status_code == 303
        assert again.headers["location"] == "/lists/news"
        page = client.get("/lists/news")
        assert page.status_code == 200
        assert "<h1>News</h1>" in page.text


def test_list_has_edit(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        created = client.post("/lists/add", data={"name": "Weekend"})
        assert created.status_code == 200
        opened = client.get("/lists/weekend")
        assert 'href="/lists/weekend/edit"' in opened.text


def test_rename_list_updates_name_and_keeps_slug(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.post("/lists/add", data={"name": "Weekend"})
        renamed = client.post("/lists/weekend/edit", data={"name": "Saturday"})
        assert renamed.status_code == 200
        assert "<h1>Saturday</h1>" in renamed.text
        lists = client.get("/lists")
        assert "Saturday" in lists.text
        assert 'href="/lists/weekend"' in lists.text
        home = client.get("/")
        assert "Saturday" not in home.text


def test_empty_rename_stays_on_edit(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.post("/lists/add", data={"name": "Weekend"})
        response = client.post("/lists/weekend/edit", data={"name": "   "})
        assert response.status_code == 200
        assert "<h1>Edit</h1>" in response.text
        opened = client.get("/lists/weekend")
        assert "<h1>Weekend</h1>" in opened.text


def test_duplicate_rename_stays_on_edit(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.post("/lists/add", data={"name": "Weekend"})
        response = client.post("/lists/weekend/edit", data={"name": "News"})
        assert response.status_code == 200
        assert "That name is already used." in response.text
        opened = client.get("/lists/weekend")
        assert "<h1>Weekend</h1>" in opened.text


def test_delete_list_removes_it_and_unlists_sources(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        client.post("/lists/add", data={"name": "Weekend"})
        edit = client.get("/lists/weekend/edit")
        assert "Delete list" in edit.text
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            dbmod.insert_source(
                conn,
                source_id="weekend-feed",
                kind="rss",
                title="Weekend feed",
                feed_url="https://example.test/weekend.xml",
                backfill=None,
            )
            dbmod.add_source_to_list(conn, "weekend-feed", "weekend")
            conn.commit()
        finally:
            conn.close()
        deleted = client.post("/lists/weekend/delete")
        assert deleted.status_code == 200
        lists = client.get("/lists")
        assert 'href="/lists/weekend"' not in lists.text
        gone = client.get("/lists/weekend")
        assert gone.status_code == 404
        home = client.get("/")
        assert "Weekend" not in home.text
        sources = client.get("/sources")
        assert "Weekend feed" in sources.text
        assert "Not on a list" in sources.text


def test_deleting_a_default_list_does_not_bring_it_back(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        deleted = client.post("/lists/fav/delete")
        assert deleted.status_code == 200

        # A later request re-runs init_db; the deleted default list must stay gone.
        lists = client.get("/lists")
        assert "Favourite channels" not in lists.text
        home = client.get("/")
        assert "Favourite channels" not in home.text


def test_deleting_a_list_with_a_read_item_does_not_crash(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        read = client.post(f"/items/{item_id}/read?from_list=news")
        assert read.status_code == 200

        deleted = client.post("/lists/news/delete")
        assert deleted.status_code == 200


def _to_choose_list(client: TestClient, url: str = "https://example.test/feed.xml"):
    added = client.post("/sources/add", data={"url": url})
    assert added.status_code == 200
    listed = client.post(
        "/sources/add/count",
        data={
            "feed_url": "https://example.test/feed.xml",
            "title": "Fixture news",
            "item_count": "2",
            "backfill": "all",
        },
    )
    assert listed.status_code == 200
    assert "Choose a list" in listed.text
    return listed


def test_choose_list_has_later_and_create(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        page = _to_choose_list(client)
        assert "I'll do this later" in page.text
        assert "Create new list" in page.text
        assert "is-apart" in page.text
        assert "Read later" in page.text


def test_ill_do_this_later_leaves_source_unlisted(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _to_choose_list(client)
        done = client.post(
            "/sources/add/list",
            data={
                "feed_url": "https://example.test/feed.xml",
                "title": "Fixture news",
                "item_count": "2",
                "backfill": "",
                "list_slug": "",
            },
        )
        assert done.status_code == 200
        assert "Fixture news is not on a list yet." in done.text
        sources = client.get("/sources")
        assert "Fixture news" in sources.text
        assert "Not on a list" in sources.text


def test_create_new_list_from_add_source_puts_source_on_it(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _to_choose_list(client)
        done = client.post(
            "/sources/add/new-list",
            data={
                "feed_url": "https://example.test/feed.xml",
                "title": "Fixture news",
                "item_count": "2",
                "backfill": "",
                "name": "Weekend",
            },
        )
        assert done.status_code == 200
        assert "Fixture news is on Weekend" in done.text
        sources = client.get("/sources")
        assert "Weekend" in sources.text
        home = client.get("/")
        assert "Weekend" not in home.text


def test_see_items_of_source(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        items = client.get(f"/sources/{source_id}/items")
        assert items.status_code == 200
        assert "First fixture item" in items.text
        assert "Second fixture item" in items.text
        assert "from_source=" in items.text


def test_sources_list_opens_items_by_default_with_settings_link(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        sources = client.get("/sources")
        assert f'href="/sources/{source_id}/items"' in sources.text

        items = client.get(f"/sources/{source_id}/items")
        assert f'href="/sources/{source_id}"' in items.text
        assert "Settings" in items.text

        settings = client.get(f"/sources/{source_id}")
        assert f'href="/sources/{source_id}/items"' in settings.text


def _add_unlisted(client: TestClient, url: str = "https://example.test/feed.xml"):
    _to_choose_list(client, url)
    return client.post(
        "/sources/add/list",
        data={
            "feed_url": "https://example.test/feed.xml",
            "title": "Fixture news",
            "item_count": "2",
            "backfill": "",
            "list_slug": "",
        },
    )


def test_source_screen_offers_add_to_list_when_unlisted(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_unlisted(client)
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        page = client.get(f"/sources/{source_id}")
        assert "Add to a list" in page.text
        assert f'href="/sources/{source_id}/list"' in page.text


def test_list_unlisted_source_from_its_screen(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_unlisted(client)
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        chooser = client.get(f"/sources/{source_id}/list")
        assert "Read later" in chooser.text
        done = client.post(f"/sources/{source_id}/list", data={"list_slug": "later"})
        assert done.status_code == 200
        assert "Saved" in done.text
        assert "Read later" in done.text
        sources = client.get("/sources")
        assert "Read later" in sources.text


def test_list_source_to_news_asks_window(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_unlisted(client)
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        window_page = client.post(
            f"/sources/{source_id}/list", data={"list_slug": "news"}
        )
        assert window_page.status_code == 200
        assert "How far back" in window_page.text
        done = client.post(f"/sources/{source_id}/window", data={"window": "day"})
        assert done.status_code == 200
        assert "News (&lt;24h)" in done.text or "News (<24h)" in done.text


def test_create_new_list_from_source_screen(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_unlisted(client)
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        created = client.post(
            f"/sources/{source_id}/new-list", data={"name": "Weekend"}
        )
        assert created.status_code == 200
        assert "Weekend" in created.text
        lists = client.get("/lists")
        assert "Weekend" in lists.text


def test_remove_source_from_a_list(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        page = client.get(f"/sources/{source_id}")
        assert f'action="/sources/{source_id}/lists/news/remove"' in page.text
        done = client.post(f"/sources/{source_id}/lists/news/remove")
        assert done.status_code == 200
        assert "Not on a list" in done.text
        news = client.get("/lists/news")
        assert "First fixture item" not in news.text


def test_source_can_be_on_more_than_one_list(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        client.post(f"/sources/{source_id}/list", data={"list_slug": "later"})
        page = client.get(f"/sources/{source_id}")
        assert "News" in page.text
        assert "Read later" in page.text
        assert f'action="/sources/{source_id}/lists/news/remove"' in page.text
        assert f'action="/sources/{source_id}/lists/later/remove"' in page.text
        news = client.get("/lists/news")
        assert "First fixture item" in news.text
        later = client.get("/lists/later")
        assert "First fixture item" in later.text
        sources = client.get("/sources")
        assert "On 2 lists" in sources.text
        client.post(f"/sources/{source_id}/lists/later/remove")
        after = client.get(f"/sources/{source_id}")
        assert "Read later" not in after.text
        news_after = client.get("/lists/news")
        assert "First fixture item" in news_after.text


def test_rename_source_updates_name_everywhere(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        renamed = client.post(f"/sources/{source_id}/rename", data={"name": "My News"})
        assert renamed.status_code == 200
        assert "<h1>My News</h1>" in renamed.text
        sources = client.get("/sources")
        assert "My News" in sources.text
        assert "Fixture news" not in sources.text
        items = client.get(f"/sources/{source_id}/items")
        assert "My News" in items.text
        news = client.get("/lists/news")
        assert "My News" in news.text


def test_rename_survives_a_later_sync(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        client.post(f"/sources/{source_id}/rename", data={"name": "My News"})
        synced = client.post("/sync")
        assert synced.status_code == 200
        opened = client.get(f"/sources/{source_id}")
        assert "<h1>My News</h1>" in opened.text


def test_empty_rename_resets_to_auto_title(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        client.post(f"/sources/{source_id}/rename", data={"name": "My News"})
        reset = client.post(f"/sources/{source_id}/rename", data={"name": "   "})
        assert reset.status_code == 200
        assert "<h1>Fixture news</h1>" in reset.text


def test_delete_source_removes_it_and_items(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        gone = client.post(f"/sources/{source_id}/delete")
        assert gone.status_code == 200
        sources = client.get("/sources")
        assert "Fixture news" not in sources.text
        news = client.get("/lists/news")
        assert "First fixture item" not in news.text
        missing = client.get(f"/sources/{source_id}")
        assert missing.status_code == 404


def test_delete_source_with_a_read_item_does_not_crash(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        read = client.post(f"/items/{item_id}/read?from_list=news")
        assert read.status_code == 200

        gone = client.post(f"/sources/{source_id}/delete")
        assert gone.status_code == 200
        missing = client.get(f"/sources/{source_id}")
        assert missing.status_code == 404


def _first_item_id(tmp_path) -> int:
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return dbmod.items_for_list(conn, "news")[0]["id"]
    finally:
        conn.close()


def _get_item_row(tmp_path, item_id):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return dbmod.get_item(conn, item_id)
    finally:
        conn.close()


def _reject_any_export(monkeypatch, message):
    monkeypatch.setenv("OBSIDIAN_GITHUB_TOKEN", "test-token")

    def fail_if_called(method, url, **kwargs):
        raise AssertionError(message)

    monkeypatch.setattr("app.obsidian._request", fail_if_called)


def _record_exports(monkeypatch):
    calls = []

    def fake_export_note(item, highlights, previous_path=None):
        calls.append((item["id"], list(highlights)))
        return {"exported": True, "path": f"Highlights/{item['id']}.md"}

    monkeypatch.setattr("app.main.export_note", fake_export_note)
    return calls


def test_item_page_has_read_later_button(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        page = client.get(f"/items/{item_id}")
        assert page.status_code == 200
        assert "Read later" in page.text


def test_tapping_read_later_adds_item_to_the_list(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        added = client.post(f"/items/{item_id}/later")
        assert added.status_code == 200
        assert "Saved to Read later" in added.text
        later = client.get("/lists/later")
        assert "First fixture item" in later.text


def test_read_later_is_idempotent_on_repeat_taps(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        client.post(f"/items/{item_id}/later")
        later = client.get("/lists/later")
        assert later.text.count("First fixture item") == 1


def test_read_later_on_missing_item_is_404(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post("/items/999999/later")
        assert response.status_code == 404


def test_direct_read_later_membership_ignores_source_window(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml", window="week")
        item_id = _first_item_id(tmp_path)
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            dbmod.init_db(conn)
            conn.execute(
                "UPDATE items SET published_at = ? WHERE id = ?",
                ("2020-01-01T00:00:00+00:00", item_id),
            )
            conn.commit()
        finally:
            conn.close()
        news = client.get("/lists/news")
        assert "First fixture item" not in news.text
        client.post(f"/items/{item_id}/later")
        later = client.get("/lists/later")
        assert "First fixture item" in later.text


def test_later_list_orders_by_when_added_not_published_date(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        first = client.post(
            "/capture",
            data={"url": "https://example.test/first-added", "html": CAPTURE_BLOG_HTML},
        )
        first_id = int(first.json()["item_url"].removeprefix("/items/"))
        second = client.post(
            "/capture",
            data={"url": "https://example.test/second-added", "html": CAPTURE_BLOG_HTML},
        )
        second_id = int(second.json()["item_url"].removeprefix("/items/"))

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            dbmod.init_db(conn)
            # The item added FIRST gets the NEWER published date, and the one
            # added SECOND gets the OLDER one - the opposite of what
            # published-date order would show, so the two orderings disagree
            # and the test actually proves which one the list is using.
            conn.execute(
                "UPDATE items SET published_at = ? WHERE id = ?",
                ("2026-06-01T00:00:00+00:00", first_id),
            )
            conn.execute(
                "UPDATE items SET published_at = ? WHERE id = ?",
                ("2020-01-01T00:00:00+00:00", second_id),
            )
            conn.commit()
        finally:
            conn.close()

        later = client.get("/lists/later")
        first_pos = later.text.find(f"/items/{first_id}")
        second_pos = later.text.find(f"/items/{second_id}")
        assert first_pos != -1
        assert second_pos != -1
        assert second_pos < first_pos


def test_capture_endpoint_saves_a_captured_page_to_read_later(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
        response = client.post("/capture", data={"url": url, "html": CAPTURE_BLOG_HTML})
        assert response.status_code == 200
        body = response.json()
        assert "Hiten Shah" in body["title"]
        assert body["item_url"].startswith("/items/")
        later = client.get("/lists/later")
        assert "Hiten Shah" in later.text
        item_page = client.get(body["item_url"])
        assert "skill library" in item_page.text


def test_capture_endpoint_shows_html_confirmation_for_the_bookmarklet(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
        response = client.post(
            "/capture?format=html",
            data={"url": url, "html": CAPTURE_BLOG_HTML},
        )
        assert response.status_code == 200
        assert "Saved to Read later" in response.text
        assert "Read now" in response.text


def test_capture_endpoint_requires_a_url(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post("/capture", data={"html": CAPTURE_BLOG_HTML})
        assert response.status_code == 400


def test_capture_endpoint_rejects_a_malformed_url_cleanly(monkeypatch, tmp_path):
    # No html given, so this exercises the real server-side fetch (not the
    # fixture-mocked one from _client), which is what actually rejects a
    # url containing a stray control character.
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as client:
        response = client.post(
            "/capture", data={"url": "Some Title\r\nhttps://example.test/article"}
        )
    assert response.status_code == 400


def test_delete_item_removes_it_from_the_list_for_good(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        gone = client.post(f"/items/{item_id}/delete?from_list=news")
        assert gone.status_code == 200
        assert "First fixture item" not in gone.text
        assert "Deleted" in gone.text

        missing = client.get(f"/items/{item_id}")
        assert missing.status_code == 404


def test_delete_item_unknown_id_is_404(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        missing = client.post("/items/999999/delete")
        assert missing.status_code == 404


def test_deleting_an_item_with_a_highlight_does_not_crash(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlighted = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "0",
                "end_block": "0",
                "end_offset": "5",
                "text": "Hello",
            },
        )
        assert highlighted.status_code == 200

        gone = client.post(f"/items/{item_id}/delete?from_list=news")
        assert gone.status_code == 200


def _save_highlight(client, item_id, start_block=0, start_offset=0, end_block=0, end_offset=5, text="Hello"):
    saved = client.post(
        f"/items/{item_id}/highlights",
        data={
            "start_block": str(start_block),
            "start_offset": str(start_offset),
            "end_block": str(end_block),
            "end_offset": str(end_offset),
            "text": text,
        },
    )
    assert saved.status_code == 200
    return saved.json()["id"]


def test_highlight_detail_page_shows_its_text(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlight_id = _save_highlight(client, item_id, text="Hello from the fixture")

        page = client.get(f"/items/{item_id}/highlights/{highlight_id}")
        assert page.status_code == 200
        assert "Hello from the fixture" in page.text
        assert "Add section title" in page.text
        assert "Add subsection title" in page.text
        assert "Delete highlight" in page.text


def test_highlight_detail_unknown_id_is_404(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        missing = client.get(f"/items/{item_id}/highlights/999999")
        assert missing.status_code == 404


def test_setting_a_section_title_persists(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlight_id = _save_highlight(client, item_id)

        saved = client.post(
            f"/items/{item_id}/highlights/{highlight_id}/section-title",
            data={"title": "Money and markets"},
        )
        assert saved.status_code == 200

        page = client.get(f"/items/{item_id}/highlights/{highlight_id}/section-title")
        assert page.status_code == 200
        assert 'value="Money and markets"' in page.text


def test_setting_a_subsection_title_persists(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlight_id = _save_highlight(client, item_id)

        saved = client.post(
            f"/items/{item_id}/highlights/{highlight_id}/subsection-title",
            data={"title": "A closer look"},
        )
        assert saved.status_code == 200

        page = client.get(f"/items/{item_id}/highlights/{highlight_id}/subsection-title")
        assert page.status_code == 200
        assert 'value="A closer look"' in page.text


def test_saving_a_highlight_marks_touched_but_does_not_export_immediately(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _reject_any_export(monkeypatch, "saving a highlight must not export immediately")

        before = _get_item_row(tmp_path, item_id)
        assert before["highlights_touched_at"] is None

        _save_highlight(client, item_id)

        after = _get_item_row(tmp_path, item_id)
        assert after["highlights_touched_at"] is not None
        assert after["highlights_exported_at"] is None


def test_setting_a_title_marks_touched_but_does_not_export_immediately(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlight_id = _save_highlight(client, item_id)
        _reject_any_export(monkeypatch, "setting a title must not export immediately")

        client.post(
            f"/items/{item_id}/highlights/{highlight_id}/section-title",
            data={"title": "Money and markets"},
        )

        after = _get_item_row(tmp_path, item_id)
        assert after["highlights_touched_at"] is not None
        assert after["highlights_exported_at"] is None


def test_deleting_a_highlight_marks_touched_but_does_not_export_immediately(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlight_id = _save_highlight(client, item_id)
        _reject_any_export(monkeypatch, "deleting a highlight must not export immediately")

        client.post(f"/items/{item_id}/highlights/{highlight_id}/delete")

        after = _get_item_row(tmp_path, item_id)
        assert after["highlights_touched_at"] is not None
        assert after["highlights_exported_at"] is None


def test_deleting_a_highlight_removes_it(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        highlight_id = _save_highlight(client, item_id)

        gone = client.post(f"/items/{item_id}/highlights/{highlight_id}/delete")
        assert gone.status_code == 200

        missing = client.get(f"/items/{item_id}/highlights/{highlight_id}")
        assert missing.status_code == 404

        page = client.get(f"/items/{item_id}")
        assert '"id": ' + str(highlight_id) not in page.text


def test_deleting_one_highlight_leaves_anothers_title_untouched(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        first_id = _save_highlight(client, item_id, start_offset=0, end_offset=5)
        second_id = _save_highlight(client, item_id, start_offset=10, end_offset=15)

        client.post(
            f"/items/{item_id}/highlights/{first_id}/section-title",
            data={"title": "First section"},
        )
        client.post(
            f"/items/{item_id}/highlights/{second_id}/section-title",
            data={"title": "Second section"},
        )

        gone = client.post(f"/items/{item_id}/highlights/{first_id}/delete")
        assert gone.status_code == 200

        page = client.get(f"/items/{item_id}/highlights/{second_id}/section-title")
        assert 'value="Second section"' in page.text


def test_delete_item_from_source_items_view_redirects_there(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        gone = client.post(f"/items/{item_id}/delete?from_source={source_id}")
        assert gone.status_code == 200
        assert gone.request.url.path == f"/sources/{source_id}/items"
        assert "First fixture item" not in gone.text
        assert "Deleted" in gone.text

        # And it's actually gone, not just off this one page.
        news = client.get("/lists/news")
        assert "First fixture item" not in news.text


def test_opening_an_item_marks_it_seen_in_list_rows(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        before = client.get("/lists/news")
        assert "is-seen" not in before.text

        client.get(f"/items/{item_id}")

        after = client.get("/lists/news")
        assert "is-seen" in after.text


def test_opening_an_item_twice_keeps_the_first_seen_timestamp(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.get(f"/items/{item_id}")

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            first_seen = conn.execute(
                "SELECT seen_at FROM items WHERE id = ?", (item_id,)
            ).fetchone()["seen_at"]
        finally:
            conn.close()

        client.get(f"/items/{item_id}")

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            second_seen = conn.execute(
                "SELECT seen_at FROM items WHERE id = ?", (item_id,)
            ).fetchone()["seen_at"]
        finally:
            conn.close()

        assert first_seen == second_seen


def test_archive_button_shows_only_once_saved_to_read_later(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        before = client.get(f"/items/{item_id}")
        assert "Archive" not in before.text

        client.post(f"/items/{item_id}/later")
        after = client.get(f"/items/{item_id}")
        assert "Archive" in after.text


def test_archiving_an_item_removes_it_from_read_later_and_home(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
        captured = client.post(
            "/capture", data={"url": url, "html": CAPTURE_BLOG_HTML}
        )
        item_id = int(captured.json()["item_url"].removeprefix("/items/"))

        archived = client.post(f"/items/{item_id}/archive?from_list=later")
        assert archived.status_code == 200
        assert archived.request.url.path == "/lists/later"
        assert "Hiten Shah" not in archived.text
        assert "Archived" in archived.text

        home = client.get("/")
        assert "Hiten Shah" not in home.text


def test_archiving_an_item_keeps_it_saved_to_read_later(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        client.post(f"/items/{item_id}/archive")

        page = client.get(f"/items/{item_id}")
        assert "Saved to Read later" in page.text


def test_archive_on_missing_item_is_404(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        response = client.post("/items/999999/archive")
        assert response.status_code == 404


def test_archiving_exports_once_when_a_highlight_is_pending(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        _save_highlight(client, item_id)
        calls = _record_exports(monkeypatch)

        archived = client.post(f"/items/{item_id}/archive")
        assert archived.status_code == 200

        assert len(calls) == 1
        assert calls[0][0] == item_id
        assert len(calls[0][1]) == 1
        after = _get_item_row(tmp_path, item_id)
        assert after["highlights_exported_at"] is not None


def test_archiving_with_nothing_pending_does_not_export(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        calls = _record_exports(monkeypatch)

        archived = client.post(f"/items/{item_id}/archive")
        assert archived.status_code == 200
        assert calls == []


def test_archiving_again_after_export_does_not_export_a_second_time(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        _save_highlight(client, item_id)
        calls = _record_exports(monkeypatch)

        client.post(f"/items/{item_id}/archive")
        assert len(calls) == 1

        client.post(f"/items/{item_id}/archive")
        assert len(calls) == 1


def test_marking_as_read_exports_once_when_a_highlight_is_pending(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _save_highlight(client, item_id)
        calls = _record_exports(monkeypatch)

        read = client.post(f"/items/{item_id}/read?from_list=news")
        assert read.status_code == 200

        assert len(calls) == 1
        after = _get_item_row(tmp_path, item_id)
        assert after["highlights_exported_at"] is not None


def test_marking_as_read_with_nothing_pending_does_not_export(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        calls = _record_exports(monkeypatch)

        read = client.post(f"/items/{item_id}/read?from_list=news")
        assert read.status_code == 200
        assert calls == []


def test_deleting_an_item_with_a_pending_highlight_exports_once_first(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _save_highlight(client, item_id)
        calls = _record_exports(monkeypatch)

        deleted = client.post(f"/items/{item_id}/delete?from_list=news")
        assert deleted.status_code == 200

        assert len(calls) == 1
        assert calls[0][0] == item_id
        assert len(calls[0][1]) == 1

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            assert dbmod.get_item(conn, item_id) is None
            remaining = conn.execute(
                "SELECT COUNT(*) AS n FROM highlights WHERE item_id = ?", (item_id,)
            ).fetchone()["n"]
        finally:
            conn.close()
        assert remaining == 0


def test_deleting_an_item_with_nothing_pending_does_not_export(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        calls = _record_exports(monkeypatch)

        deleted = client.post(f"/items/{item_id}/delete?from_list=news")
        assert deleted.status_code == 200
        assert calls == []


def _set_body_html(tmp_path, item_id, body_html):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        conn.execute("UPDATE items SET body_html = ? WHERE id = ?", (body_html, item_id))
        conn.commit()
    finally:
        conn.close()


def test_images_in_block_range_collects_urls_from_interior_blocks():
    body = (
        '<p>First</p>'
        '<img src="https://example.test/a.png">'
        '<p>Second</p>'
    )
    assert dbmod.images_in_block_range(body, 0, 2) == ["https://example.test/a.png"]


def test_images_in_block_range_includes_an_image_only_boundary_block():
    # A selection starting or ending on the image itself covers it.
    body = (
        '<p>First</p>'
        '<p><img src="https://example.test/a.png"></p>'
        '<p>Second</p>'
    )
    assert dbmod.images_in_block_range(body, 1, 2) == ["https://example.test/a.png"]
    assert dbmod.images_in_block_range(body, 0, 1) == ["https://example.test/a.png"]


def test_images_in_block_range_skips_an_inline_image_in_a_text_boundary_block():
    # The boundary block is only partly covered, so its inline image may
    # sit outside the selection.
    body = (
        '<p>Before <img src="https://example.test/a.png"> after</p>'
        '<p>Second</p>'
    )
    assert dbmod.images_in_block_range(body, 0, 1) == []


def test_images_in_block_range_collects_a_recovered_image_row_group():
    body = (
        "<p>First</p>"
        '<div class="recovered-image-row">'
        '<img class="recovered-image" src="https://example.test/a.png">'
        '<img class="recovered-image" src="https://example.test/b.png">'
        "</div>"
        "<p>Second</p>"
    )
    assert dbmod.images_in_block_range(body, 0, 2) == [
        "https://example.test/a.png",
        "https://example.test/b.png",
    ]


def test_images_in_block_range_returns_empty_for_missing_body_html():
    assert dbmod.images_in_block_range(None, 0, 2) == []


def test_saving_a_highlight_spanning_an_interior_image_block_stores_its_url(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(
            tmp_path,
            item_id,
            '<p>First</p><img src="https://example.test/a.png"><p>Second</p>',
        )

        highlight_id = _save_highlight(
            client, item_id, start_block=0, start_offset=0, end_block=2, end_offset=5
        )

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            row = dbmod.get_highlight(conn, item_id, highlight_id)
        finally:
            conn.close()
        assert json.loads(row["image_urls"]) == ["https://example.test/a.png"]


def test_saving_a_highlight_that_ends_on_the_image_block_stores_it(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(
            tmp_path,
            item_id,
            '<p>First</p><img src="https://example.test/a.png"><p>Second</p>',
        )

        highlight_id = _save_highlight(
            client, item_id, start_block=0, start_offset=0, end_block=1, end_offset=0
        )

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            row = dbmod.get_highlight(conn, item_id, highlight_id)
        finally:
            conn.close()
        assert json.loads(row["image_urls"]) == ["https://example.test/a.png"]


def test_merging_a_highlight_across_an_image_recomputes_instead_of_concatenating(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _set_body_html(
            tmp_path,
            item_id,
            '<p>First</p><img src="https://example.test/a.png"><p>Second</p>',
        )
        first_id = _save_highlight(
            client, item_id, start_block=0, start_offset=0, end_block=0, end_offset=5
        )

        merged = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "0",
                "end_block": "2",
                "end_offset": "5",
                "text": "the union span",
                "merge_id": str(first_id),
            },
        )
        assert merged.status_code == 200
        merged_id = merged.json()["id"]

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            row = dbmod.get_highlight(conn, item_id, merged_id)
        finally:
            conn.close()
        assert json.loads(row["image_urls"]) == ["https://example.test/a.png"]


def _backdate_touch(tmp_path, item_id, when):
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        conn.execute(
            "UPDATE items SET highlights_touched_at = ? WHERE id = ?",
            (when.isoformat(), item_id),
        )
        conn.commit()
    finally:
        conn.close()


def test_items_due_for_export_needs_a_day_of_no_further_activity(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        _save_highlight(client, item_id)

        now = datetime.now(UTC)
        cutoff = (now - timedelta(days=1)).isoformat()

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            _backdate_touch(tmp_path, item_id, now - timedelta(hours=25))
            due_after_25h = dbmod.items_due_for_export(conn, cutoff)
            assert [row["id"] for row in due_after_25h] == [item_id]

            _backdate_touch(tmp_path, item_id, now - timedelta(hours=2))
            due_after_2h = dbmod.items_due_for_export(conn, cutoff)
            assert due_after_2h == []

            _backdate_touch(tmp_path, item_id, now - timedelta(hours=25))
            dbmod.mark_highlights_exported(conn, item_id)
            conn.commit()
            due_once_exported = dbmod.items_due_for_export(conn, cutoff)
            assert due_once_exported == []
        finally:
            conn.close()


def test_the_daily_export_check_exports_only_what_is_actually_due(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        old_item_id = _first_item_id(tmp_path)
        _save_highlight(client, old_item_id)
        _backdate_touch(tmp_path, old_item_id, datetime.now(UTC) - timedelta(hours=25))

        captured = client.post(
            "/capture",
            data={
                "url": "https://example.test/second-article",
                "html": CAPTURE_BLOG_HTML,
            },
        )
        recent_item_id = int(captured.json()["item_url"].removeprefix("/items/"))
        _save_highlight(client, recent_item_id)

        calls = _record_exports(monkeypatch)
        from app.main import _run_due_exports

        _run_due_exports()

        assert [call[0] for call in calls] == [old_item_id]
        after = _get_item_row(tmp_path, old_item_id)
        assert after["highlights_exported_at"] is not None


def test_delete_button_on_article_page_removes_it_for_good(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        before = client.get(f"/items/{item_id}")
        assert "Delete" in before.text

        client.post(f"/items/{item_id}/later")
        after = client.get(f"/items/{item_id}")
        assert "Delete" in after.text

        gone = client.post(f"/items/{item_id}/delete?from_list=later")
        assert gone.status_code == 200
        missing = client.get(f"/items/{item_id}")
        assert missing.status_code == 404


def test_delete_button_shown_when_opened_from_a_source(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        source_id = dbmod.source_id_for("https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        page = client.get(f"/items/{item_id}?from_source={source_id}")
        assert "Delete" in page.text


def test_read_later_list_shows_library_archive_toggle_with_counts(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")

        library = client.get("/lists/later")
        assert "Library (1)" in library.text
        assert "Archive (0)" in library.text
        assert "First fixture item" in library.text

        client.post(f"/items/{item_id}/archive")

        library_after = client.get("/lists/later")
        assert "Library (0)" in library_after.text
        assert "Archive (1)" in library_after.text
        assert "First fixture item" not in library_after.text

        archive_view = client.get("/lists/later?view=archive")
        assert "First fixture item" in archive_view.text


def test_other_lists_do_not_show_library_archive_toggle(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        news = client.get("/lists/news")
        assert "Library (" not in news.text
        assert "Archive (" not in news.text


def test_later_list_does_not_show_unread_read_toggle(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        later = client.get("/lists/later")
        assert "Unread (" not in later.text
        assert "Read (" not in later.text


def test_mark_as_read_shown_only_when_opened_from_a_non_later_list(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        no_context = client.get(f"/items/{item_id}")
        assert "Mark as read" not in no_context.text

        from_news = client.get(f"/items/{item_id}?from_list=news")
        assert "Mark as read" in from_news.text

        client.post(f"/items/{item_id}/later")
        from_later = client.get(f"/items/{item_id}?from_list=later")
        assert "Mark as read" not in from_later.text


def test_close_from_home_returns_to_home_not_the_list(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        home = client.get("/")
        match = re.search(rf'href="(/items/{item_id}[^"]*)"', home.text)
        assert match, "home should link to the item"

        opened = client.get(match.group(1))
        assert 'href="/">Close</a>' in opened.text


def test_close_from_archive_returns_to_archive_not_library(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        client.post(f"/items/{item_id}/archive?from_list=later")

        archive = client.get("/lists/later?view=archive")
        match = re.search(rf'href="(/items/{item_id}[^"]*)"', archive.text)
        assert match, "archive should link to the item"

        opened = client.get(html.unescape(match.group(1)))
        assert 'href="/lists/later?view=archive">Close</a>' in opened.text

        delete = re.search(r'action="(/items/\d+/delete[^"]*)"', opened.text)
        gone = client.post(html.unescape(delete.group(1)))
        assert str(gone.request.url).endswith("/lists/later?view=archive&flash=Deleted")


def test_close_from_read_tab_returns_to_read_not_unread(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/read?from_list=news")

        read_tab = client.get("/lists/news?view=read")
        match = re.search(rf'href="(/items/{item_id}[^"]*)"', read_tab.text)
        assert match, "read tab should link to the item"

        opened = client.get(html.unescape(match.group(1)))
        assert 'href="/lists/news?view=read">Close</a>' in opened.text


def test_swipe_delete_in_archive_stays_on_archive(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        client.post(f"/items/{item_id}/later")
        client.post(f"/items/{item_id}/archive?from_list=later")

        archive = client.get("/lists/later?view=archive")
        match = re.search(rf'action="(/items/{item_id}/delete[^"]*)"', archive.text)
        gone = client.post(html.unescape(match.group(1)))
        assert str(gone.request.url).endswith("/lists/later?view=archive&flash=Deleted")


def test_marking_read_moves_item_to_read_tab_and_off_home(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        news = client.get("/lists/news")
        assert "Unread (2)" in news.text
        assert "Read (0)" in news.text

        read = client.post(f"/items/{item_id}/read?from_list=news")
        assert read.status_code == 200
        assert read.request.url.path == "/lists/news"
        assert "Read" in read.text

        news_after = client.get("/lists/news")
        assert "Unread (1)" in news_after.text
        assert "Read (1)" in news_after.text
        assert "First fixture item" not in news_after.text

        read_view = client.get("/lists/news?view=read")
        assert "First fixture item" in read_view.text

        home = client.get("/")
        assert "First fixture item" not in home.text


def test_delete_captured_item_clears_its_direct_list_membership(monkeypatch, tmp_path):
    # A captured item reaches Read later through item_lists, not source_lists.
    # Deleting it must clear that row too, or the items.id foreign key from
    # item_lists rejects the delete.
    with _client(monkeypatch, tmp_path) as client:
        url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
        captured = client.post(
            "/capture", data={"url": url, "html": CAPTURE_BLOG_HTML}
        )
        item_id = int(captured.json()["item_url"].removeprefix("/items/"))

        gone = client.post(f"/items/{item_id}/delete?from_list=later")
        assert gone.status_code == 200
        assert "Hiten Shah" not in gone.text

        missing = client.get(f"/items/{item_id}")
        assert missing.status_code == 404


def test_saving_progress_persists_and_resumes_on_reopen(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        saved = client.post(f"/items/{item_id}/progress", data={"index": "4"})
        assert saved.status_code == 200

        page = client.get(f"/items/{item_id}")
        assert page.status_code == 200
        assert 'data-progress-index="4"' in page.text


def test_saving_progress_unknown_item_is_404(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        missing = client.post("/items/999999/progress", data={"index": "1"})
        assert missing.status_code == 404


def test_saving_progress_rejects_a_non_integer_index(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        bad = client.post(f"/items/{item_id}/progress", data={"index": "nope"})
        assert bad.status_code == 400


def test_item_page_has_no_progress_index_when_never_read(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        page = client.get(f"/items/{item_id}")
        assert "data-progress-index" not in page.text


def test_saving_a_highlight_that_spans_two_blocks_persists_and_renders(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)

        saved = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "5",
                "end_block": "1",
                "end_offset": "10",
                "text": "spans two paragraphs",
            },
        )
        assert saved.status_code == 200

        page = client.get(f"/items/{item_id}")
        assert page.status_code == 200
        assert '"start_block": 0' in page.text
        assert '"start_offset": 5' in page.text
        assert '"end_block": 1' in page.text
        assert '"end_offset": 10' in page.text


def test_item_page_has_empty_highlights_when_none_saved(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        page = client.get(f"/items/{item_id}")
        assert page.status_code == 200
        assert 'id="highlights-data">[]</script>' in page.text


def test_saving_highlight_on_unknown_item_is_404(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        missing = client.post(
            "/items/999999/highlights",
            data={
                "start_block": "0",
                "start_offset": "0",
                "end_block": "0",
                "end_offset": "5",
                "text": "nope",
            },
        )
        assert missing.status_code == 404


def test_saving_highlight_rejects_non_integer_offsets(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        bad = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "nope",
                "end_block": "0",
                "end_offset": "5",
                "text": "x",
            },
        )
        assert bad.status_code == 400


def test_saving_highlight_rejects_end_not_after_start(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        bad = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "5",
                "end_block": "0",
                "end_offset": "5",
                "text": "x",
            },
        )
        assert bad.status_code == 400


def test_saving_an_overlapping_highlight_is_rejected(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        first = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "0",
                "end_block": "0",
                "end_offset": "10",
                "text": "first ten chars",
            },
        )
        assert first.status_code == 200

        overlapping = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "5",
                "end_block": "0",
                "end_offset": "15",
                "text": "overlaps the first",
            },
        )
        assert overlapping.status_code == 409


def test_merging_an_overlapping_highlight_replaces_it_with_the_union(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        first_id = _save_highlight(client, item_id, start_offset=0, end_offset=10)

        merged = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "0",
                "end_block": "0",
                "end_offset": "20",
                "text": "the union span",
                "merge_id": str(first_id),
            },
        )
        assert merged.status_code == 200
        merged_id = merged.json()["id"]
        assert merged_id != first_id

        missing = client.get(f"/items/{item_id}/highlights/{first_id}")
        assert missing.status_code == 404

        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            highlights = dbmod.highlights_for_item(conn, item_id)
        finally:
            conn.close()
        assert len(highlights) == 1
        assert highlights[0]["start_offset"] == 0
        assert highlights[0]["end_offset"] == 20


def test_merge_that_shrinks_an_existing_highlight_is_rejected(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        first_id = _save_highlight(client, item_id, start_offset=0, end_offset=10)

        shrinking = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "5",
                "end_block": "0",
                "end_offset": "20",
                "text": "overlaps but does not cover the start",
                "merge_id": str(first_id),
            },
        )
        assert shrinking.status_code == 400

        still_there = client.get(f"/items/{item_id}/highlights/{first_id}")
        assert still_there.status_code == 200


def test_merging_two_highlights_keeps_the_earlier_ones_title(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        early_id = _save_highlight(client, item_id, start_offset=0, end_offset=10)
        client.post(
            f"/items/{item_id}/highlights/{early_id}/section-title",
            data={"title": "Money and markets"},
        )
        later_id = _save_highlight(client, item_id, start_offset=20, end_offset=30)
        client.post(
            f"/items/{item_id}/highlights/{later_id}/section-title",
            data={"title": "Later title"},
        )

        merged = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "0",
                "end_block": "0",
                "end_offset": "30",
                "text": "bridges both",
                "merge_id": [str(early_id), str(later_id)],
            },
        )
        assert merged.status_code == 200
        merged_id = merged.json()["id"]

        page = client.get(f"/items/{item_id}/highlights/{merged_id}/section-title")
        assert 'value="Money and markets"' in page.text


def test_merge_claim_that_does_not_actually_overlap_is_rejected(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        first_id = _save_highlight(client, item_id, start_offset=0, end_offset=10)

        bogus = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "50",
                "end_block": "0",
                "end_offset": "60",
                "text": "does not actually overlap",
                "merge_id": str(first_id),
            },
        )
        assert bogus.status_code == 400

        still_there = client.get(f"/items/{item_id}/highlights/{first_id}")
        assert still_there.status_code == 200


def test_merge_that_omits_a_second_overlapping_highlight_is_rejected(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        _add_to_news(client, "https://example.test/feed.xml")
        item_id = _first_item_id(tmp_path)
        first_id = _save_highlight(client, item_id, start_offset=0, end_offset=10)
        second_id = _save_highlight(client, item_id, start_offset=20, end_offset=30)

        merged = client.post(
            f"/items/{item_id}/highlights",
            data={
                "start_block": "0",
                "start_offset": "5",
                "end_block": "0",
                "end_offset": "25",
                "text": "bridges both but only names one",
                "merge_id": str(first_id),
            },
        )
        assert merged.status_code == 409

        assert client.get(f"/items/{item_id}/highlights/{first_id}").status_code == 200
        assert client.get(f"/items/{item_id}/highlights/{second_id}").status_code == 200
