from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from lxml.html import fromstring

from app.db import (
    add_source_to_list,
    connect,
    format_when,
    init_db,
    insert_source,
    is_item_in_list,
    item_in_window,
    items_for_list,
)
from app.ingest import (
    _image_candidates,
    _recover_missing_images,
    capture_article,
    ingest_all_sources,
    ingest_xml,
    parse_feed,
)

FIXTURE = Path(__file__).parent / "fixtures" / "feed.xml"
CAPTURE_FIXTURES = Path(__file__).parent / "fixtures" / "capture"
SOURCE_ID = "fixture-rss"


def _source(conn, window: str | None = "week") -> None:
    insert_source(
        conn,
        source_id=SOURCE_ID,
        kind="rss",
        title="RSS",
        feed_url="https://example.test/feed.xml",
        backfill=None,
    )
    add_source_to_list(conn, SOURCE_ID, "news", window)


def test_parse_feed_reads_items():
    entries = parse_feed(FIXTURE.read_text(encoding="utf-8"), SOURCE_ID)
    assert [entry["title"] for entry in entries] == [
        "First fixture item",
        "Second fixture item",
    ]
    assert "Hello from the fixture feed" in entries[0]["body_html"]


def test_ingest_xml_stores_news_items(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    _source(conn)
    result = ingest_xml(conn, FIXTURE.read_text(encoding="utf-8"), SOURCE_ID)
    conn.commit()
    assert result["created"] == 2
    assert result["kept"] == 2
    assert result["feed_total"] == 2
    items = items_for_list(
        conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=UTC)
    )
    assert [row["title"] for row in items] == [
        "First fixture item",
        "Second fixture item",
    ]
    again = ingest_xml(conn, FIXTURE.read_text(encoding="utf-8"), SOURCE_ID)
    assert again["created"] == 0


def test_ingest_xml_keeps_only_latest_five_when_limited(tmp_path):
    items_xml = "\n".join(
        f"""
        <item>
          <title>Item {n}</title>
          <link>https://example.test/news/{n}</link>
          <guid>https://example.test/news/{n}</guid>
          <pubDate>Wed, {n:02d} Aug 2026 08:00:00 +0000</pubDate>
          <description>&lt;p&gt;Body {n}&lt;/p&gt;</description>
        </item>
        """
        for n in range(1, 8)
    )
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0"><channel>
      <title>Many</title>
      {items_xml}
    </channel></rss>"""
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    _source(conn, window=None)
    result = ingest_xml(conn, xml, SOURCE_ID, limit=5)
    conn.commit()
    assert result["feed_total"] == 7
    assert result["kept"] == 5
    titles = [
        row["title"]
        for row in items_for_list(
            conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=UTC)
        )
    ]
    assert titles == ["Item 7", "Item 6", "Item 5", "Item 4", "Item 3"]


def test_ingest_all_sources_skips_a_source_that_fails_to_fetch(monkeypatch, tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    _source(conn)
    insert_source(
        conn,
        source_id="broken-rss",
        kind="rss",
        title="Broken",
        feed_url="https://broken.test/feed.xml",
        backfill=None,
    )
    add_source_to_list(conn, "broken-rss", "news", "week")

    def flaky_fetch_url(url: str, timeout: float = 8.0):
        if url == "https://broken.test/feed.xml":
            raise RuntimeError("feed host is down")
        return url, FIXTURE.read_text(encoding="utf-8")

    monkeypatch.setattr("app.ingest.fetch_url", flaky_fetch_url)

    result = ingest_all_sources(conn)
    conn.commit()

    assert result["sources"] == 2
    assert result["failed"] == 1
    assert result["created"] == 2
    titles = [
        row["title"]
        for row in items_for_list(
            conn, "news", now=datetime(2026, 8, 20, 12, tzinfo=UTC)
        )
    ]
    assert titles == ["First fixture item", "Second fixture item"]


def test_item_in_window_day_and_week():
    now = datetime(2026, 8, 20, 12, tzinfo=UTC)
    assert item_in_window("day", "2026-08-20T08:00:00+00:00", now)
    assert not item_in_window("day", "2026-08-19T08:00:00+00:00", now)
    assert item_in_window("week", "2026-08-14T08:00:00+00:00", now)
    assert not item_in_window("week", "2026-08-12T08:00:00+00:00", now)
    assert item_in_window(None, "2026-01-01T00:00:00+00:00", now)


def test_format_when_today_and_date():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
    assert format_when("2026-08-20T08:00:00+00:00", now) == "Today"
    assert format_when("2026-08-19T08:00:00+00:00", now) == "Yesterday"
    assert format_when("2026-08-17T08:00:00+00:00", now) == "17/08/26"


def _capture_fixture(name: str) -> str:
    return (CAPTURE_FIXTURES / name).read_text(encoding="utf-8")


def test_capture_article_cleans_a_real_page_and_adds_it_to_read_later(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
    item_id, title = capture_article(conn, url, html=_capture_fixture("blog.html"))
    conn.commit()
    assert "Hiten Shah" in title
    assert is_item_in_list(conn, item_id, "later")
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["url"] == url
    assert "skill library" in item["body_html"]
    assert item["word_count"] > 0


def test_capture_article_keeps_an_inline_body_image(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://example.test/with-an-image"
    html = """
    <html><head><title>An Article With A Picture</title></head>
    <body><article>
    <p>An opening paragraph with enough real words in it for trafilatura to
    treat this page as an actual article worth extracting in the first place.</p>
    <img src="https://example.test/diagram.png" alt="A diagram">
    <p>A closing paragraph, again with enough real words in it for trafilatura
    to treat this page as an actual article worth extracting in the first place.</p>
    </article></body></html>
    """
    item_id, title = capture_article(conn, url, html=html)
    conn.commit()
    assert title == "An Article With A Picture"
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert 'src="https://example.test/diagram.png"' in item["body_html"]


def test_capture_article_keeps_whole_paragraph_bold_in_an_interview(tmp_path):
    # trafilatura strips a <strong> that wraps an entire paragraph's text
    # (treating it as noise rather than emphasis), which loses the
    # question/answer distinction in an interview transcript where every
    # interviewer question is a fully-bold paragraph and every answer isn't.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://example.test/an-interview"
    html = """
    <html><head><title>An Interview About Technofascism</title></head>
    <body><article>
    <p>An opening paragraph with enough real words in it for trafilatura to
    treat this page as an actual article worth extracting in the first place.</p>
    <p><strong>How does artificial intelligence pave the way for
    technofascism in your view, and why does it matter so much right now?</strong></p>
    <p>Artificial intelligence concentrates power in ways we have not fully
    reckoned with yet, and that concentration is what makes it dangerous.</p>
    <p><strong>What role do the big platforms play in that concentration of
    power across the technology industry as a whole?</strong></p>
    <p>The big platforms control the infrastructure that everything else
    depends on, which gives them leverage far beyond their market share.</p>
    </article></body></html>
    """
    item_id, _title = capture_article(conn, url, html=html)
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    body = item["body_html"]
    assert "<strong>How does artificial intelligence" in body
    assert "<strong>What role do the big platforms" in body
    assert "<strong>Artificial intelligence concentrates power" not in body
    assert "<strong>The big platforms control" not in body


def test_capture_article_keeps_whole_paragraph_italics(tmp_path):
    # Same trafilatura behaviour as the bold case above, but for <em>/<i> -
    # an editor's note or aside rendered fully italic in the source.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://example.test/an-editors-note"
    html = """
    <html><head><title>An Article With An Editor's Note</title></head>
    <body><article>
    <p>An opening paragraph with enough real words in it for trafilatura to
    treat this page as an actual article worth extracting in the first place.</p>
    <p><em>Editor's note: this interview has been edited for length and
    clarity before publication, as is standard practice for transcripts.</em></p>
    <p>A closing paragraph, again with enough real words in it for trafilatura
    to treat this page as an actual article worth extracting in the first place.</p>
    </article></body></html>
    """
    item_id, _title = capture_article(conn, url, html=html)
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    body = item["body_html"]
    assert "<em>Editor's note: this interview has been edited" in body


def test_capture_article_keeps_a_fully_bold_faq_list_item(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://example.test/an-faq"
    html = """
    <html><head><title>A Frequently Asked Questions Page</title></head>
    <body><article>
    <p>An opening paragraph with enough real words in it for trafilatura to
    treat this page as an actual article worth extracting in the first place.</p>
    <ul>
    <li><strong>What is the first frequently asked question about this
    topic that readers keep bringing up in their messages?</strong></li>
    <li>Plain answer text for the first FAQ item that explains things in
    enough detail to read as real content here on this page.</li>
    </ul>
    </article></body></html>
    """
    item_id, _title = capture_article(conn, url, html=html)
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    body = item["body_html"]
    assert "<li><strong>What is the first frequently asked question" in body
    assert "<strong>Plain answer text" not in body


def test_capture_article_keeps_a_fully_bold_pull_quote(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://example.test/a-pull-quote"
    html = """
    <html><head><title>An Article With A Pull Quote</title></head>
    <body><article>
    <p>An opening paragraph with enough real words in it for trafilatura to
    treat this page as an actual article worth extracting in the first place.</p>
    <blockquote><strong>This is a fully bold pull quote taken directly from
    later in the interview to highlight one especially striking point.</strong></blockquote>
    <p>A closing paragraph, again with enough real words in it for trafilatura
    to treat this page as an actual article worth extracting in the first place.</p>
    </article></body></html>
    """
    item_id, _title = capture_article(conn, url, html=html)
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    body = item["body_html"]
    assert "<blockquote><strong>This is a fully bold pull quote" in body


def test_capture_article_prefers_the_real_headline_for_an_x_article(tmp_path):
    # The client caught this: X's long-form Article format sets a real
    # headline in og:description (matching an on-page <h1>), which the
    # first version of this fix ignored in favor of synthesizing one from
    # body text - producing a much worse title than was actually available.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/seanlinehan/status/2091955290552078418"
    html = """
    <html><head>
    <title>Sean Linehan on X: &quot;https://t.co/aoqzeekmmv&quot; / X</title>
    <meta property="og:title" content="Sean Linehan (@seanlinehan) on X">
    <meta name="twitter:title" content="Sean Linehan (@seanlinehan) on X">
    <meta property="og:description" content="The Economics of the Intelligence Frontier">
    </head>
    <body><article>
    <h1>The Economics of the Intelligence Frontier</h1>
    <p>There is a lot of hand-wringing right now over whether frontier model
    companies are going to make it when open competitors commoditize their
    capabilities.</p>
    </article></body></html>
    """
    item_id, title = capture_article(conn, url, html=html)
    conn.commit()
    assert title == "The Economics of the Intelligence Frontier"
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["title"] == title


def test_capture_article_prefers_the_real_headline_for_a_localized_x_article(tmp_path):
    # The client caught this: X localizes its "Name (@handle) on X"
    # boilerplate to the viewer's language ("en X" in Spanish), and the
    # English-only match left that boilerplate as the captured title.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/JayaGup10/status/2101799427145183571"
    html = """
    <html><head>
    <title>Jaya Gupta en X: &quot;https://t.co/WkxtRUiScu&quot; / X</title>
    <meta property="og:title" content="Jaya Gupta (@JayaGup10) en X">
    <meta name="twitter:title" content="Jaya Gupta (@JayaGup10) en X">
    <meta property="og:description" content="The Great Unbundling of Intelligence">
    </head>
    <body><article>
    <p>For most of the last decade, intelligence came bundled with the
    software that delivered it, and that bundle is now coming apart.</p>
    </article></body></html>
    """
    item_id, title = capture_article(conn, url, html=html)
    conn.commit()
    assert title == "The Great Unbundling of Intelligence"
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["title"] == title


def test_capture_article_spots_x_boilerplate_by_the_handle_not_the_wording(tmp_path):
    # Some languages reorder X's boilerplate entirely (Japanese puts the
    # name mid-sentence), so it is recognised by the post author's own
    # handle from the URL rather than by any fixed wording around it.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/JayaGup10/status/2101799427145183571"
    html = """
    <html><head>
    <meta property="og:title" content="X上のJaya Gupta（@JayaGup10）さん">
    <meta property="og:description" content="The Great Unbundling of Intelligence">
    </head>
    <body><article>
    <p>For most of the last decade, intelligence came bundled with the
    software that delivered it, and that bundle is now coming apart.</p>
    </article></body></html>
    """
    _item_id, title = capture_article(conn, url, html=html)
    conn.commit()
    assert title == "The Great Unbundling of Intelligence"


def test_capture_article_synthesizes_a_title_for_an_x_post_without_a_headline(tmp_path):
    # A plain tweet/thread with no og:description headline falls back to a
    # title synthesized from the post's own opening text.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/seanlinehan/status/2091955290552078418"
    html = """
    <html><head>
    <title>Sean Linehan on X: &quot;https://t.co/aoqzeekmmv&quot; / X</title>
    <meta property="og:title" content="Sean Linehan (@seanlinehan) on X">
    <meta name="twitter:title" content="Sean Linehan (@seanlinehan) on X">
    </head>
    <body><article>
    <p>There is a lot of hand-wringing right now over whether frontier model
    companies are going to make it when open competitors commoditize their
    capabilities. I think it is entirely plausible that frontier model
    companies wind up among the biggest companies on Earth while most of
    the tasks their models perform become commodities.</p>
    </article></body></html>
    """
    item_id, title = capture_article(conn, url, html=html)
    conn.commit()
    assert title == (
        "There is a lot of hand-wringing right now over whether frontier "
        "model companies are going to make it when open competitors "
        "commoditize their capabilities."
    )
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["title"] == title


def test_capture_article_keeps_a_normal_x_title_alone_when_no_pattern_matches(tmp_path):
    # A guard against over-triggering: only the exact generic pattern
    # should be replaced, not any title that happens to contain "on X".
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/someuser/status/1"
    html = """
    <html><head>
    <title>A genuinely specific headline someone wrote</title>
    <meta property="og:title" content="A genuinely specific headline someone wrote">
    </head>
    <body><article>
    <p>Body text that should not matter here since the title is already
    a real one, not the generic X site boilerplate this fix targets.</p>
    </article></body></html>
    """
    _item_id, title = capture_article(conn, url, html=html)
    conn.commit()
    assert title == "A genuinely specific headline someone wrote"


def test_capture_article_embeds_a_table_image_trafilatura_still_drops(tmp_path):
    # Uses the real page that surfaced this bug rather than a hand-built
    # snippet: a minimal synthetic reproduction of the same table shape
    # turned out to sit right on the edge of trafilatura's internal scoring
    # and flipped pass/fail across separate runs depending on the process's
    # hash seed. The real page's actual structure fails this deterministically.
    #
    # The hoist rewrite alone does not recover this specific page's images -
    # deeper investigation found trafilatura drops this content regardless of
    # tag shape, not just tables - so embedding the image directly from its
    # original URL is the real safety net here, not the rewrite.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://vitalik.eth.limo/general/2023/11/27/techno_optimism.html"
    item_id, title = capture_article(
        conn, url, html=_capture_fixture("vitalik_techno_optimism.html")
    )
    conn.commit()
    assert title == "My techno-optimism"
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    body = item["body_html"]
    assert 'class="recovered-image"' in body
    assert (
        'src="https://vitalik.eth.limo/images/techno_optimism/path1.png"' in body
    )
    # Regression: the recovered images must land near their real position in
    # the article, not all get dumped together at the very end. A first pass
    # at this positioned every single one at the end, because the anchor
    # text search required an exact whitespace match while the captured body
    # keeps the source's own line-wrapped newlines inside each paragraph.
    tail = body[-400:]
    assert tail.count("recovered-image") < 6
    # Regression: every real content image the source page references must
    # be accounted for, kept or flagged - not just the ones sitting inside a
    # table. The client caught a version that only checked table images and
    # silently lost the other 22 of this article's 28.
    image_names = [
        "0chan", "bensinger", "carbonvote", "civprogress", "dacc", "dacc_2",
        "defensetypes", "differential", "genfill", "helpfulnote2",
        "life_expectancy", "medbook", "meme", "mindpaths", "path1", "path2",
        "path3", "poll1", "poll2", "poll3", "pollution", "samback",
        "scamblock", "smog", "switzerland", "techtrajectory", "temperature",
        "viewpoints",
    ]
    for name in image_names:
        assert f"{name}.png" in body, f"{name}.png missing entirely, not even flagged"


def test_capture_article_keeps_images_on_a_page_split_into_many_text_blocks(tmp_path):
    # The client caught this on a Squarespace post: its text is split across
    # a dozen separate blocks, so the busiest single block held only 14 of
    # the page's 40 paragraphs, and the images sat in sibling blocks outside
    # it. Trafilatura dropped all five charts, and the safety net never saw
    # them either, since it only looked inside that one text block.
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.tobyord.com/writing/swarm-scaling"
    item_id, _title = capture_article(
        conn, url, html=_capture_fixture("tobyord_swarm_scaling.html")
    )
    conn.commit()
    body = conn.execute("SELECT body_html FROM items WHERE id = ?", (item_id,)).fetchone()[0]
    image_names = [
        "SEC-Bench+Pro+%28Multi-Agent%29.png", "SEC-Bench+%28log+scale%29",
        "Swarm+Scaling.png", "Inference+scaling+of+Stokes+model+vs+Astra.png",
        "o3-GPT5+SWE+diff.png",
    ]
    for name in image_names:
        assert name in body, f"{name} missing entirely, not even flagged"
    # Each lands next to its own paragraph, not all piled up at the end.
    assert body[-600:].count("recovered-image") < 2


def test_recover_missing_images_is_a_no_op_when_the_image_is_already_there():
    body = '<p>Intro.</p><img src="https://example.test/pic.png"><p>Outro.</p>'
    flagged = _recover_missing_images(body, [("https://example.test/pic.png", "Intro.", 1)])
    assert flagged == body


def test_recover_missing_images_inserts_right_after_its_anchor_paragraph():
    body = (
        "<p>An opening paragraph that ends right here, giving the flag a"
        " landmark to anchor against.</p><h2>Next section</h2>"
    )
    anchor = "landmark to anchor against."
    flagged = _recover_missing_images(body, [("https://example.test/pic.png", anchor, 1)])
    assert flagged == (
        "<p>An opening paragraph that ends right here, giving the flag a"
        " landmark to anchor against.</p>"
        '<img class="recovered-image" src="https://example.test/pic.png" alt="">'
        "<h2>Next section</h2>"
    )


def test_recover_missing_images_appends_at_the_end_when_its_anchor_is_also_gone():
    body = "<p>All that is left of the article.</p>"
    flagged = _recover_missing_images(
        body, [("https://example.test/pic.png", "text nowhere in body", 1)]
    )
    assert flagged == (
        "<p>All that is left of the article.</p>"
        '<img class="recovered-image" src="https://example.test/pic.png" alt="">'
    )


def test_recover_missing_images_groups_a_shared_row_into_one_flex_row():
    # The client caught this: three images that were originally a 3-column
    # table row got recovered as three separate stacked blocks instead of
    # staying side by side.
    body = "<p>Landmark paragraph ending right here.</p>"
    anchor = "Landmark paragraph ending right here."
    candidates = [
        ("https://example.test/a.png", anchor, 42),
        ("https://example.test/b.png", anchor, 42),
        ("https://example.test/c.png", anchor, 42),
    ]
    flagged = _recover_missing_images(body, candidates)
    assert flagged == (
        "<p>Landmark paragraph ending right here.</p>"
        '<div class="recovered-image-row">'
        '<img class="recovered-image" src="https://example.test/a.png" alt="">'
        '<img class="recovered-image" src="https://example.test/b.png" alt="">'
        '<img class="recovered-image" src="https://example.test/c.png" alt="">'
        "</div>"
    )


def test_image_candidates_covers_standalone_images_not_just_tables():
    # The client caught this: an earlier version only ever looked inside
    # tables for candidates, so a standalone <img> that trafilatura drops
    # for its own unrelated reasons was silently lost with no flag at all.
    html = """
    <html><body><div id="doc">
    <p>An opening paragraph with enough real words in it to anchor on later,
    thirty-some characters and then some more to be sure.</p>
    <img src="https://example.test/standalone.png">
    <p>A closing paragraph with enough real words in it to anchor on later,
    thirty-some characters and then some more to be sure as well.</p>
    </div></body></html>
    """
    tree = fromstring(html)
    candidates = _image_candidates(tree, "https://example.test/article")
    assert ("https://example.test/standalone.png", candidates[0][1], candidates[0][2]) in candidates


def test_image_candidates_ignores_a_lazy_load_placeholder():
    html = """
    <html><body><div id="doc">
    <p>An opening paragraph with enough real words in it to anchor on later,
    thirty-some characters and then some more to be sure.</p>
    <img src="data:image/svg+xml,%3Csvg%20viewBox='0 0 0 0'%3E%3C/svg%3E"
         data-src="https://example.test/real.png">
    <p>A closing paragraph with enough real words in it to anchor on later,
    thirty-some characters and then some more to be sure as well.</p>
    </div></body></html>
    """
    tree = fromstring(html)
    candidates = _image_candidates(tree, "https://example.test/article")
    urls = [url for url, _anchor, _row in candidates]
    assert urls == ["https://example.test/real.png"]


def test_image_candidates_gives_same_row_images_the_same_row_key():
    html = """
    <html><body><div id="doc">
    <p>An opening paragraph with enough real words in it to anchor on later,
    thirty-some characters and then some more to be sure.</p>
    <table><tr>
    <td><img src="https://example.test/left.png"></td>
    <td><img src="https://example.test/right.png"></td>
    </tr></table>
    <p>A closing paragraph with enough real words in it to anchor on later,
    thirty-some characters and then some more to be sure as well.</p>
    </div></body></html>
    """
    tree = fromstring(html)
    candidates = _image_candidates(tree, "https://example.test/article")
    row_keys = {row for _url, _anchor, row in candidates}
    assert len(row_keys) == 1


def test_capture_article_leaves_an_imageless_table_untouched(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://example.test/with-a-data-table"
    html = """
    <html><head><title>A Real Data Table</title></head>
    <body><article>
    <p>An opening paragraph with enough real words in it for trafilatura to
    treat this page as an actual article worth extracting in the first place.</p>
    <table>
    <tr><td>Pros</td><td>Cons</td></tr>
    <tr><td>Fast</td><td>Expensive</td></tr>
    </table>
    <p>A closing paragraph, again with enough real words in it for trafilatura
    to treat this page as an actual article worth extracting in the first place.</p>
    </article></body></html>
    """
    item_id, _title = capture_article(conn, url, html=html)
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    body = item["body_html"]
    assert "<table>" in body
    assert "Pros" in body
    assert "Expensive" in body


def test_capture_article_falls_back_to_a_server_fetch_when_given_no_html(
    monkeypatch, tmp_path
):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://dataproducts.substack.com/p/the-shift-left-manifesto-v2"
    monkeypatch.setattr(
        "app.ingest.fetch_url", lambda u, timeout=8.0: (u, _capture_fixture("substack.html"))
    )
    item_id, title = capture_article(conn, url)
    conn.commit()
    assert "Shift Left" in title
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert item["word_count"] > 0


def test_capture_article_still_saves_a_link_it_cannot_clean(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.nexojornal.com.br/colunistas/2026/09/02/paywalled"
    item_id, title = capture_article(conn, url, html=_capture_fixture("paywalled.html"))
    conn.commit()
    assert title and title != url
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    assert not item["body_html"]
    assert is_item_in_list(conn, item_id, "later")


def test_capture_article_does_not_crash_on_a_javascript_only_page(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://x.com/seanlinehan/status/2091955290552078418/"
    item_id, title = capture_article(conn, url, html=_capture_fixture("js_shell.html"))
    conn.commit()
    assert title
    assert is_item_in_list(conn, item_id, "later")


def test_capture_article_is_idempotent_per_url(tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    url = "https://www.explainx.ai/blog/hiten-shah-ai-skill-library-company-strategy-2026"
    first_id, _ = capture_article(conn, url, html=_capture_fixture("blog.html"))
    second_id, _ = capture_article(conn, url, html=_capture_fixture("blog.html"))
    conn.commit()
    assert first_id == second_id
    count = conn.execute("SELECT COUNT(*) AS n FROM items WHERE url = ?", (url,)).fetchone()
    assert count["n"] == 1
