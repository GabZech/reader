(() => {
  const registerWorker = async () => {
    if (!("serviceWorker" in navigator)) return;
    try {
      await navigator.serviceWorker.register("/sw.js");
    } catch {
      /* offline cache is best-effort */
    }
  };

  const syncHome = async () => {
    if (location.pathname !== "/") return;
    if (!navigator.onLine) return;
    if (sessionStorage.getItem("reader-synced") === "1") return;
    const status = document.getElementById("sync-status");
    if (status) status.textContent = "Updating";
    sessionStorage.setItem("reader-synced", "1");
    try {
      const response = await fetch("/sync", { method: "POST" });
      if (response.ok) {
        location.reload();
      } else if (status) {
        status.textContent = "Edit";
      }
    } catch {
      if (status) status.textContent = "Edit";
    }
  };

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

    setExpanded(false);
    button.addEventListener("click", () => {
      const isExpanded = extras.every((item) => !item.hidden);
      setExpanded(!isExpanded);
    });
  });

  const toast = document.querySelector(".toast");
  if (toast) {
    setTimeout(() => toast.classList.add("is-hidden"), 5000);
  }

  registerWorker();
  syncHome();
})();
