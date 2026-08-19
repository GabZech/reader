(() => {
  if (!window.listNames) return;

  const params = new URLSearchParams(location.search);
  const id = params.get("list") || "news";
  const back = params.get("back") || "news.html";
  const input = document.querySelector(".field");
  const done = document.querySelector("[data-done]");
  const del = document.querySelector("[data-delete]");
  if (!input || !done) return;

  input.value = window.listNames.nameFor(id);
  done.setAttribute("href", back);

  const commit = () => {
    const next = input.value.trim() || window.listNames.DEFAULTS[id] || input.value.trim();
    window.listNames.save(id, next);
  };

  done.addEventListener("click", commit);
  input.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return;
    event.preventDefault();
    commit();
    location.href = back;
  });

  if (del) {
    del.addEventListener("click", () => {
      window.listNames.remove(id);
    });
  }
})();
