from __future__ import annotations

from test_service_worker_browser import _live_server, phone  # noqa: F401


def test_the_page_never_scrolls_so_the_tab_bar_cannot_be_dragged_with_it(
    phone, monkeypatch, tmp_path  # noqa: F811
):
    # On an iPhone, fixed elements travel with a scrolling page: the tab bar
    # lifted off the bottom edge. Only an inner container may scroll.
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/sources")
        phone.evaluate("document.querySelector('.page').style.minHeight = '3000px'")
        phone.mouse.move(200, 300)
        phone.mouse.wheel(0, 900)
        phone.wait_for_timeout(300)

        assert phone.evaluate("window.scrollY") == 0
        assert phone.evaluate("document.querySelector('.scroller').scrollTop") > 0
        bar_bottom, height = phone.evaluate(
            "(() => [document.querySelector('.tabbar').getBoundingClientRect().bottom, innerHeight])()"
        )
        assert bar_bottom == height


def test_the_tab_bar_sits_low_with_round_outer_corners(phone, monkeypatch, tmp_path):  # noqa: F811
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/lists")
        corners = phone.evaluate(
            """() => {
              const tabs = [...document.querySelectorAll('.tab')];
              const radius = (el, side) => parseFloat(getComputedStyle(el)[side]);
              return {
                first: radius(tabs[0], 'borderBottomLeftRadius'),
                last: radius(tabs[2], 'borderBottomRightRadius'),
                middle: radius(tabs[1], 'borderBottomLeftRadius'),
              };
            }"""
        )
        assert corners["first"] >= 30 and corners["last"] >= 30
        assert corners["middle"] <= 20


def test_the_side_padding_is_ten_pixels_and_full_width_rows_still_reach_the_edges(
    phone, monkeypatch, tmp_path  # noqa: F811
):
    with _live_server(monkeypatch, tmp_path) as (origin, _server):
        phone.goto(f"{origin}/lists")
        page = phone.evaluate(
            """() => {
              const style = getComputedStyle(document.querySelector('.page'));
              const card = document.querySelector('.list.is-cards a.item').getBoundingClientRect();
              return {left: style.paddingLeft, right: style.paddingRight, cardLeft: card.left, cardRight: innerWidth - card.right};
            }"""
        )
        assert page["left"] == "10px" and page["right"] == "10px"
        assert page["cardLeft"] == 10 and page["cardRight"] == 10

        phone.goto(f"{origin}/lists/news")
        flat = phone.evaluate(
            """() => {
              const box = document.querySelector('.list.is-flat').getBoundingClientRect();
              return {left: box.left, right: innerWidth - box.right};
            }"""
        )
        assert flat["left"] == 0 and flat["right"] == 0
