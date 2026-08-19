(() => {
  const params = new URLSearchParams(location.search);
  if (params.has("clear")) {
    document.querySelectorAll("a.hl").forEach((el) => {
      el.replaceWith(document.createTextNode(el.textContent));
    });
  }

  const root = document.querySelector("[data-highlight]");
  if (!root) return;

  root.addEventListener("mouseup", () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    const range = selection.getRangeAt(0);
    if (!root.contains(range.commonAncestorContainer)) return;
    try {
      const qs = new URLSearchParams(location.search);
      qs.delete("clear");
      const query = qs.toString();
      const mark = document.createElement("a");
      mark.className = "hl";
      mark.href = query ? `highlight.html?${query}` : "highlight.html";
      range.surroundContents(mark);
    } catch {
      return;
    }
    selection.removeAllRanges();
  });
})();
