(() => {
  if (window.homeLayout) {
    const page = document.querySelector(".page");
    const sections = [...document.querySelectorAll("[data-home-list]")];
    if (page && sections.length) {
      const order = window.homeLayout.loadOrder();
      const hidden = window.homeLayout.loadHidden();
      order.forEach((id) => {
        const section = page.querySelector(`[data-home-list="${id}"]`);
        if (!section) return;
        section.hidden = hidden.includes(id);
        page.appendChild(section);
      });
    }
  }

  const startExpanded = new URLSearchParams(location.search).has("expanded");

  document.querySelectorAll("[data-list]").forEach((section) => {
    const extras = [...section.querySelectorAll(".item.is-more")];
    const button = section.querySelector(".show-more");
    if (!button || extras.length === 0) return;

    const setExpanded = (expanded) => {
      extras.forEach((item) => {
        item.hidden = !expanded;
      });
      button.textContent = expanded ? "Show less" : "Show more";
    };

    setExpanded(startExpanded);

    button.addEventListener("click", () => {
      const isExpanded = extras.every((item) => !item.hidden);
      setExpanded(!isExpanded);
    });
  });
})();
