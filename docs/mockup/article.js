(() => {
  const from = new URLSearchParams(location.search).get("from") || "home";
  const dest =
    from === "news"
      ? "news.html"
      : from === "removed"
        ? "news-removed.html"
        : from === "read-batch"
          ? "news-read-batch.html"
          : from === "seen"
            ? "news-seen.html"
            : from === "later"
              ? "read-later.html"
              : from === "archive"
                ? "read-later-archive.html"
                : from === "fav"
                  ? "favourite-channels.html"
                  : "index.html";

  document.querySelectorAll("[data-back]").forEach((link) => {
    link.href = dest;
  });

  document.querySelectorAll("[data-from]").forEach((link) => {
    const url = new URL(link.getAttribute("href"), location.href);
    if (from !== "home") url.searchParams.set("from", from);
    link.setAttribute("href", `${url.pathname.split("/").pop()}${url.search}${url.hash}`);
  });

  const homeTab = document.querySelector('.tab[href="index.html"]');
  const listsTab = document.querySelector('.tab[href="lists.html"]');
  if (homeTab && listsTab && from === "home") {
    homeTab.classList.add("is-active");
    listsTab.classList.remove("is-active");
  }
})();
