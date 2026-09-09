from __future__ import annotations

from datetime import datetime, timezone
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
    monkeypatch.setattr("app.ingest.fetch_url", _fetch)
    real_visible = dbmod._visible_items
    frozen = datetime(2026, 8, 20, 12, tzinfo=timezone.utc)

    def visible(conn, slug, now=None):
        return real_visible(conn, slug, now or frozen)

    monkeypatch.setattr(dbmod, "_visible_items", visible)
    return TestClient(app)


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


def test_home_shell(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    with TestClient(app) as client:
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
        listed = client.post(
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


def _first_item_id(tmp_path) -> int:
    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return dbmod.items_for_list(conn, "news")[0]["id"]
    finally:
        conn.close()


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
