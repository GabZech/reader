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
                "url": f"/items/{item_id}",
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

        urls = [a["url"] for a in client.get("/offline/articles").json()["articles"]]

        assert urls == [f"/items/{kept}"]


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
