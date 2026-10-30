from __future__ import annotations

from test_app import CAPTURE_BLOG_HTML, _client, _get_item_row, _set_body_html

from app import main as mainmod


def _capture(client, slug: str) -> int:
    response = client.post(
        "/capture", data={"url": f"https://blog.test/{slug}", "html": CAPTURE_BLOG_HTML}
    )
    assert response.status_code == 200
    return response.json()["item_id"]


def test_offline_articles_lists_the_read_later_library_with_its_images(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        item_id = _capture(client, "one")
        _set_body_html(
            tmp_path,
            item_id,
            '<p>Text</p><p><img src="https://img.test/a.png"></p><img src="/static/b.png">',
        )

        listed = client.get("/offline/articles").json()

        assert listed["articles"] == [
            {
                "urls": [
                    f"/items/{item_id}?from_list=later",
                    f"/items/{item_id}?from_list=later&from_home=1",
                ],
                "images": ["https://img.test/a.png", "/static/b.png"],
            }
        ]


def test_offline_articles_names_home_and_every_list_to_refresh(monkeypatch, tmp_path):
    # Read Later's articles are no use offline if the list leading to them
    # never got stored.
    with _client(monkeypatch, tmp_path) as client:
        client.post("/lists/add", data={"name": "Essays"})

        pages = client.get("/offline/articles").json()["pages"]

        assert pages[:2] == ["/", "/lists"]
        assert "/lists/later" in pages
        assert "/lists/news" in pages
        assert "/lists/essays" in pages


def test_offline_articles_leaves_out_the_archive(monkeypatch, tmp_path):
    with _client(monkeypatch, tmp_path) as client:
        kept = _capture(client, "kept")
        archived = _capture(client, "archived")
        assert client.post(f"/items/{archived}/archive", follow_redirects=False).status_code == 303

        urls = [a["urls"][0] for a in client.get("/offline/articles").json()["articles"]]

        assert urls == [f"/items/{kept}?from_list=later"]


def test_offline_articles_caps_the_images_but_keeps_every_article(monkeypatch, tmp_path):
    monkeypatch.setattr(mainmod, "OFFLINE_IMAGE_CAP", 3)
    with _client(monkeypatch, tmp_path) as client:
        first = _capture(client, "first")
        second = _capture(client, "second")
        for item_id in (first, second):
            _set_body_html(
                tmp_path,
                item_id,
                "".join(f'<img src="https://img.test/{item_id}-{n}.png">' for n in range(2)),
            )

        articles = client.get("/offline/articles").json()["articles"]

        assert len(articles) == 2
        assert sum(len(a["images"]) for a in articles) == 3


def test_a_prefetched_article_is_not_marked_seen(monkeypatch, tmp_path):
    # Downloading Read Later in the background must not grey out titles the
    # reader has never opened.
    with _client(monkeypatch, tmp_path) as client:
        item_id = _capture(client, "unseen")

        page = client.get(f"/items/{item_id}", headers={"X-Reader-Prefetch": "1"})

        assert page.status_code == 200
        assert _get_item_row(tmp_path, item_id)["seen_at"] is None
        client.get(f"/items/{item_id}")
        assert _get_item_row(tmp_path, item_id)["seen_at"] is not None


def _highlight_rows(tmp_path):
    from app import db as dbmod

    conn = dbmod.connect(tmp_path / "reader.db")
    try:
        return conn.execute("SELECT * FROM highlights ORDER BY id").fetchall()
    finally:
        conn.close()


def _post_highlight(client, item_id, start, end, text, merge_ids=()):
    return client.post(
        f"/items/{item_id}/highlights",
        data={
            "start_block": "0",
            "start_offset": str(start),
            "end_block": "0",
            "end_offset": str(end),
            "text": text,
            "merge_id": [str(m) for m in merge_ids],
        },
    )


def test_sending_the_same_highlight_again_returns_the_one_already_saved(
    monkeypatch, tmp_path
):
    # A phone that sent a queued highlight but lost the reply sends it again.
    with _client(monkeypatch, tmp_path) as client:
        item_id = _capture(client, "twice")
        _set_body_html(tmp_path, item_id, "<p>A sentence worth keeping twice over</p>")
        first = _post_highlight(client, item_id, 0, 10, "A sentence")
        client.post(f"/items/{item_id}/highlights/{first.json()['id']}/key")

        again = _post_highlight(client, item_id, 0, 10, "A sentence")

        assert again.status_code == 200
        assert again.json() == {**first.json(), "is_key": True}
        assert len(_highlight_rows(tmp_path)) == 1


def test_resending_a_merge_that_already_went_through_returns_the_merged_highlight(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        item_id = _capture(client, "merge-twice")
        _set_body_html(tmp_path, item_id, "<p>A sentence worth keeping twice over</p>")
        small = _post_highlight(client, item_id, 0, 5, "A sen").json()["id"]
        merged = _post_highlight(client, item_id, 0, 10, "A sentence", [small])

        again = _post_highlight(client, item_id, 0, 10, "A sentence", [small])

        assert again.status_code == 200
        assert again.json()["id"] == merged.json()["id"]
        assert len(_highlight_rows(tmp_path)) == 1


def test_a_merge_naming_a_highlight_deleted_elsewhere_still_saves(monkeypatch, tmp_path):
    # Highlighted over an older highlight offline, while another device
    # deleted that older one.
    with _client(monkeypatch, tmp_path) as client:
        item_id = _capture(client, "gone")
        _set_body_html(tmp_path, item_id, "<p>A sentence worth keeping twice over</p>")
        older = _post_highlight(client, item_id, 0, 5, "A sen").json()["id"]
        client.post(f"/items/{item_id}/highlights/{older}/delete")

        saved = _post_highlight(client, item_id, 0, 10, "A sentence", [older])

        assert saved.status_code == 200
        assert [row["text"] for row in _highlight_rows(tmp_path)] == ["A sentence"]


def test_the_article_page_carries_each_highlights_text_and_titles_safely(
    monkeypatch, tmp_path
):
    # The phone builds a highlight's page offline from the stored article.
    import json
    import re

    with _client(monkeypatch, tmp_path) as client:
        item_id = _capture(client, "carries")
        _set_body_html(tmp_path, item_id, "<p>Ends here &lt;/script&gt; and more</p>")
        hid = _post_highlight(client, item_id, 0, 19, "Ends here </script>").json()["id"]
        client.post(
            f"/items/{item_id}/highlights/{hid}/section-title", data={"title": "Part one"}
        )

        page = client.get(f"/items/{item_id}").text

        raw = re.search(
            r'<script type="application/json" id="highlights-data">(.*?)</script>', page, re.DOTALL
        ).group(1)
        [carried] = json.loads(raw)
        assert carried["text"] == "Ends here </script>"
        assert carried["section_title"] == "Part one"
        assert carried["subsection_title"] is None


def test_offline_highlight_page_templates_are_downloaded_with_the_lists(
    monkeypatch, tmp_path
):
    with _client(monkeypatch, tmp_path) as client:
        pages = client.get("/offline/articles").json()["pages"]
        for path in (
            "/offline/highlight",
            "/offline/highlight-title/section",
            "/offline/highlight-title/subsection",
        ):
            assert path in pages
            shell = client.get(path)
            assert shell.status_code == 200
            assert "data-offline-shell" in shell.text


def _news_item(client, tmp_path):
    from test_app import _add_to_news, _first_item_id

    _add_to_news(client, "https://example.test/feed.xml")
    return _first_item_id(tmp_path)


def test_offline_articles_also_names_each_lists_second_tab(monkeypatch, tmp_path):
    # An item moved to Read or Archive while offline has to land on a tab
    # that is already stored.
    with _client(monkeypatch, tmp_path) as client:
        pages = client.get("/offline/articles").json()["pages"]

        assert "/lists/later?view=archive" in pages
        assert "/lists/news?view=read" in pages
        assert "/lists/later?view=read" not in pages
        assert "/lists/news?view=archive" not in pages


def test_list_rows_say_which_item_and_list_they_are(monkeypatch, tmp_path):
    # app.js finds a row by these when it applies what was done offline.
    with _client(monkeypatch, tmp_path) as client:
        item_id = _news_item(client, tmp_path)

        page = client.get("/lists/news").text
        home = client.get("/").text

        assert f'data-item-id="{item_id}"' in page
        assert 'data-list-slug="news"' in page
        assert f'data-item-id="{item_id}"' in home
        assert '<section class="list" data-list="news"' in home


def test_the_article_page_carries_what_its_buttons_do_offline(monkeypatch, tmp_path):
    import json
    import re

    with _client(monkeypatch, tmp_path) as client:
        item_id = _news_item(client, tmp_path)
        client.post(f"/items/{item_id}/later")

        page = client.get(f"/items/{item_id}?from_list=news").text

        moves = [json.loads(m) for m in re.findall(r"data-move='([^']*)'", page)]
        by_action = {m["action"]: m for m in moves}
        assert by_action["read"]["list"] == "news"
        assert by_action["read"]["then"] == "/lists/news?flash=Read"
        assert by_action["archive"]["list"] == "later"
        assert by_action["archive"]["then"] == "/lists/news?flash=Archived"
        assert by_action["later"]["then"] == f"/items/{item_id}?from_list=news"
        assert by_action["read"]["url"] == f"/items/{item_id}/read?from_list=news"
        assert by_action["later"]["url"] == f"/items/{item_id}/later?from_list=news"
        # Saving to Read later offline unlocks Archive, so it carries that move.
        assert by_action["later"]["archive"] == by_action["archive"]
        # The row each button's item becomes on the tab it lands on.
        templates = dict(
            re.findall(r'<template id="(moved-row-\w+)">(.*?)</template>', page, re.DOTALL)
        )
        read_row = templates["moved-row-read"]
        assert f'data-swipe-action="/items/{item_id}/unread?from_list=news"' in read_row
        assert f'href="/items/{item_id}?from_list=news&view=read"' in read_row
        archive_row = templates["moved-row-archive"]
        assert f'data-swipe-action="/items/{item_id}/unarchive"' in archive_row
        later_row = templates["moved-row-later"]
        assert f'data-swipe-action="/items/{item_id}/archive?from_list=later"' in later_row


def test_an_article_opened_outside_a_list_has_no_mark_as_read_move(monkeypatch, tmp_path):
    import json
    import re

    with _client(monkeypatch, tmp_path) as client:
        item_id = _news_item(client, tmp_path)

        page = client.get(f"/items/{item_id}").text

        actions = {json.loads(m)["action"] for m in re.findall(r"data-move='([^']*)'", page)}
        assert "moved-row-read" not in page
        assert "act-read" not in page
        assert actions == {"later"}


def test_offline_articles_names_settings_sources_and_each_sources_and_lists_pages(
    monkeypatch, tmp_path
):
    # What a reader opens without a connection beyond the lists: Settings,
    # Sources, every source's items and its own page, and each list's editor.
    from app import db as dbmod

    with _client(monkeypatch, tmp_path) as client:
        _news_item(client, tmp_path)
        conn = dbmod.connect(tmp_path / "reader.db")
        try:
            source_id = conn.execute(
                "SELECT id FROM sources WHERE id != 'captured'"
            ).fetchone()["id"]
        finally:
            conn.close()

        pages = client.get("/offline/articles").json()["pages"]

        for path in (
            "/settings",
            "/sources",
            f"/sources/{source_id}/items",
            f"/sources/{source_id}",
            "/lists/news/edit",
            "/lists/later/edit",
        ):
            assert path in pages
        # Adding things and the like need the server, so are not stored.
        assert "/sources/add" not in pages
        assert "/lists/add" not in pages
