(() => {
  const KEY_DELETED = "sourceDeleted";
  const CATALOG = {
    lenny: {
      title: "Lenny's Newsletter",
      byline: "Newsletter · Not on a list",
      items: [
        {
          title: "How to hire a product-minded engineer",
          byline: "Lenny's Newsletter · Today",
          length: "9 min",
        },
        {
          title: "A simple strategy for career growth",
          byline: "Lenny's Newsletter · Yesterday",
          length: "7 min",
        },
      ],
    },
    ft: {
      title: "Financial Times",
      byline: "Newsletter · News (<24h)",
      items: [
        {
          title: "FT morning briefing",
          href: "article.html",
          byline: "Financial Times · Today",
          length: "8 min",
          thumb: true,
        },
      ],
    },
    batch: {
      title: "The Batch",
      byline: "Newsletter · News (<7days)",
      items: [
        {
          title: "The Batch",
          href: "batch.html",
          byline: "DeepLearning.AI · Today",
          length: "6 min",
          thumb: true,
        },
      ],
    },
    stratechery: {
      title: "Stratechery",
      byline: "Newsletter · News (<7days)",
      items: [
        {
          title: "Stratechery",
          byline: "Ben Thompson · Yesterday",
          length: "12 min",
        },
      ],
    },
    veritasium: {
      title: "Veritasium",
      byline: "YouTube · Favourite channels",
      items: [
        {
          title: "The most common mistake in statistics",
          href: "video.html",
          byline: "Veritasium · Today",
          length: "18 min",
          thumb: true,
        },
      ],
    },
    brown: {
      title: "3Blue1Brown",
      byline: "YouTube · Favourite channels",
      items: [
        {
          title: "Attention in neural networks",
          byline: "3Blue1Brown · Yesterday",
          length: "12 min",
          thumb: true,
        },
      ],
    },
  };

  const loadDeleted = () => {
    try {
      const value = JSON.parse(sessionStorage.getItem(KEY_DELETED));
      if (Array.isArray(value)) return value;
    } catch {
      /* keep default */
    }
    return [];
  };

  const remove = (id) => {
    const deleted = loadDeleted();
    if (!deleted.includes(id)) {
      sessionStorage.setItem(KEY_DELETED, JSON.stringify([...deleted, id]));
    }
  };

  const sourceId = () => new URLSearchParams(location.search).get("id") || "lenny";

  const current = () => CATALOG[sourceId()] || CATALOG.lenny;

  const applyDeleted = () => {
    const deleted = loadDeleted();
    document.querySelectorAll("[data-source-id]").forEach((el) => {
      const id = el.getAttribute("data-source-id");
      if (id && deleted.includes(id)) el.hidden = true;
    });
  };

  window.sources = { CATALOG, sourceId, current, remove, applyDeleted };
  applyDeleted();
})();
