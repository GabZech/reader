(() => {
  const root = document.querySelector("[data-home-edit]");
  if (!root || !window.homeLayout) return;

  const { loadOrder, loadHidden, save } = window.homeLayout;
  let order = loadOrder();
  let hidden = loadHidden();

  const rows = () => [...root.querySelectorAll("[data-list-id]")];

  const apply = () => {
    const deleted = window.listNames ? window.listNames.loadDeleted() : [];

    order.forEach((id) => {
      const row = root.querySelector(`[data-list-id="${id}"]`);
      if (row) root.appendChild(row);
    });

    rows().forEach((row) => {
      const id = row.getAttribute("data-list-id");
      row.hidden = deleted.includes(id);
    });

    const visible = rows().filter((row) => !row.hidden);
    visible.forEach((row, index) => {
      const id = row.getAttribute("data-list-id");
      const isHidden = hidden.includes(id);
      row.classList.toggle("is-unlisted", isHidden);
      const toggle = row.querySelector("[data-toggle]");
      const up = row.querySelector("[data-up]");
      const down = row.querySelector("[data-down]");
      if (toggle) toggle.textContent = isHidden ? "Hidden" : "On Home";
      if (up) up.disabled = index === 0;
      if (down) down.disabled = index === visible.length - 1;
    });
  };

  root.addEventListener("click", (event) => {
    const button = event.target.closest(".edit-btn");
    if (!button || button.disabled) return;
    const row = button.closest("[data-list-id]");
    if (!row) return;
    const id = row.getAttribute("data-list-id");
    const index = order.indexOf(id);
    if (index < 0) return;

    if (button.hasAttribute("data-toggle")) {
      hidden = hidden.includes(id)
        ? hidden.filter((item) => item !== id)
        : [...hidden, id];
    } else if (button.hasAttribute("data-up") && index > 0) {
      [order[index - 1], order[index]] = [order[index], order[index - 1]];
    } else if (button.hasAttribute("data-down") && index < order.length - 1) {
      [order[index + 1], order[index]] = [order[index], order[index + 1]];
    } else {
      return;
    }

    save(order, hidden);
    apply();
  });

  apply();
})();
