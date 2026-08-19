(() => {
  const KEY = "listNames";
  const KEY_DELETED = "listDeleted";
  const DEFAULTS = {
    news: "News",
    later: "Read later",
    fav: "Favourite channels",
  };

  const load = () => {
    try {
      const value = JSON.parse(sessionStorage.getItem(KEY));
      if (value && typeof value === "object") return { ...DEFAULTS, ...value };
    } catch {
      /* keep default */
    }
    return { ...DEFAULTS };
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

  const nameFor = (id) => load()[id] || DEFAULTS[id] || "";

  const save = (id, name) => {
    const next = load();
    next[id] = name;
    sessionStorage.setItem(KEY, JSON.stringify(next));
  };

  const remove = (id) => {
    const deleted = loadDeleted();
    if (!deleted.includes(id)) {
      sessionStorage.setItem(KEY_DELETED, JSON.stringify([...deleted, id]));
    }
    if (window.homeLayout) {
      const order = window.homeLayout.loadOrder().filter((item) => item !== id);
      const hidden = window.homeLayout.loadHidden().filter((item) => item !== id);
      window.homeLayout.save(order, hidden);
    }
  };

  const apply = () => {
    const names = load();
    const deleted = loadDeleted();
    document.querySelectorAll("[data-list-title]").forEach((el) => {
      const id = el.getAttribute("data-list-title");
      if (id && names[id]) el.textContent = names[id];
    });
    document.querySelectorAll("[data-list-id], [data-home-list]").forEach((el) => {
      const id = el.getAttribute("data-list-id") || el.getAttribute("data-home-list");
      if (id && deleted.includes(id)) el.hidden = true;
    });
    const heading = document.querySelector("h1[data-list-title]");
    if (heading) document.title = heading.textContent;
  };

  window.listNames = { DEFAULTS, load, loadDeleted, nameFor, save, remove, apply };
  apply();
})();
