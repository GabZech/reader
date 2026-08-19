(() => {
  if (!window.sources) return;

  const id = window.sources.sourceId();
  const source = window.sources.current();
  const qs = `id=${encodeURIComponent(id)}`;

  document.querySelectorAll("[data-source-title]").forEach((el) => {
    el.textContent = source.title;
  });
  document.querySelectorAll("[data-source-byline]").forEach((el) => {
    el.textContent = source.byline;
  });
  const heading = document.querySelector("h1[data-source-title]");
  if (heading) document.title = heading.textContent;

  const itemsLink = document.querySelector("[data-items]");
  if (itemsLink) itemsLink.href = `source-items.html?${qs}`;

  const addLink = document.querySelector("[data-add]");
  if (addLink) addLink.href = `add-choose-list.html?${qs}`;

  const back = document.querySelector("[data-back]");
  if (back) back.href = `source.html?${qs}`;

  const chooseBack = document.querySelector("[data-choose-back]");
  if (chooseBack) chooseBack.href = `add-choose-list.html?${qs}`;

  document.querySelectorAll("a[href]").forEach((link) => {
    const raw = link.getAttribute("href");
    if (!raw || raw.startsWith("#")) return;
    const file = raw.split("?")[0];
    if (!/^add-(window|done|done-fav)\.html$/.test(file)) return;
    const url = new URL(raw, location.href);
    url.searchParams.set("id", id);
    link.setAttribute("href", `${file}${url.search}`);
  });

  const del = document.querySelector("[data-delete]");
  if (del) {
    del.addEventListener("click", () => {
      window.sources.remove(id);
    });
  }

  const list = document.querySelector("[data-source-items]");
  if (list) {
    source.items.forEach((item) => {
      const row = document.createElement(item.href ? "a" : "div");
      row.className = item.thumb ? "item has-thumb" : "item";
      if (item.href) row.href = item.href;
      if (item.thumb) {
        const thumb = document.createElement("span");
        thumb.className = "thumb";
        thumb.setAttribute("aria-hidden", "true");
        row.appendChild(thumb);
      }
      const title = document.createElement("span");
      title.className = "title";
      title.textContent = item.title;
      const sub = document.createElement("span");
      sub.className = "sub";
      sub.innerHTML = `<span class="byline"></span><span class="length"></span>`;
      sub.querySelector(".byline").textContent = item.byline;
      sub.querySelector(".length").textContent = item.length;
      row.appendChild(title);
      row.appendChild(sub);
      list.appendChild(row);
    });
  }
})();
