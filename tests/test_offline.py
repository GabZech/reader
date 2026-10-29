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

        assert listed == {
            "articles": [
                {
                    "url": f"/items/{item_id}",
                    "images": ["https://img.test/a.png", "/static/b.png"],
                }
            ]
        }


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
