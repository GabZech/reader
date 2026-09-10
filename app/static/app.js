(() => {
  const THEME_COLOR = { light: "#fafaf9", dark: "#1c1917" };

  const initThemeToggle = () => {
    const button = document.querySelector(".theme-toggle");
    const meta = document.querySelector('meta[name="theme-color"]');

    const apply = (theme) => {
      document.documentElement.dataset.theme = theme;
      if (button) button.textContent = theme === "dark" ? "Light" : "Dark";
      if (meta) meta.setAttribute("content", THEME_COLOR[theme]);
    };

    apply(document.documentElement.dataset.theme === "dark" ? "dark" : "light");

    if (button) {
      button.addEventListener("click", () => {
        const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        localStorage.setItem("reader-theme", next);
        apply(next);
      });
    }
  };

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

  const initSwipeToDelete = () => {
    const OPEN_X = -88; // 5.5rem at the default 16px root font-size, matches .item-delete-btn width
    const THRESHOLD = OPEN_X / 2;
    let openRow = null;

    const closeRow = (row) => {
      row.classList.remove("is-open");
      if (openRow === row) openRow = null;
    };

    document.querySelectorAll(".item-swipe").forEach((row) => {
      const link = row.querySelector(".item");
      if (!link) return;
      let startX = 0;
      let startY = 0;
      let dragging = false;
      let deciding = false;
      let justDragged = false;

      link.addEventListener("pointerdown", (event) => {
        if (event.pointerType === "mouse" && event.button !== 0) return;
        startX = event.clientX;
        startY = event.clientY;
        dragging = false;
        deciding = true;
      });

      link.addEventListener("pointermove", (event) => {
        if (!deciding && !dragging) return;
        const dx = event.clientX - startX;
        const dy = event.clientY - startY;
        if (deciding) {
          if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
          deciding = false;
          dragging = Math.abs(dx) > Math.abs(dy);
          if (dragging) link.setPointerCapture(event.pointerId);
        }
        if (!dragging) return;
        event.preventDefault();
        const base = row.classList.contains("is-open") ? OPEN_X : 0;
        const next = Math.min(0, Math.max(OPEN_X, base + dx));
        link.style.transition = "none";
        link.style.transform = `translateX(${next}px)`;
      });

      const finishDrag = (event) => {
        deciding = false;
        if (!dragging) return;
        dragging = false;
        // A drag release fires a trailing click on this same element; swallow it below.
        justDragged = true;
        link.style.transition = "";
        link.style.transform = "";
        const base = row.classList.contains("is-open") ? OPEN_X : 0;
        const dx = event.clientX - startX;
        const next = Math.min(0, Math.max(OPEN_X, base + dx));
        if (next < THRESHOLD) {
          if (openRow && openRow !== row) closeRow(openRow);
          row.classList.add("is-open");
          openRow = row;
        } else {
          closeRow(row);
        }
      };

      link.addEventListener("pointerup", finishDrag);
      link.addEventListener("pointercancel", finishDrag);

      link.addEventListener("click", (event) => {
        if (justDragged) {
          justDragged = false;
          event.preventDefault();
          return;
        }
        if (row.classList.contains("is-open")) {
          event.preventDefault();
          closeRow(row);
        }
      });
    });
  };

  const initReadingProgress = () => {
    const body = document.querySelector(".article-body[data-progress-action]");
    if (!body) return;
    const blocks = Array.from(body.children);
    if (blocks.length === 0) return;
    const saveUrl = body.dataset.progressAction;

    let currentIndex = -1;
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              currentIndex = blocks.indexOf(entry.target);
            }
          });
        },
        { rootMargin: "0px 0px -85% 0px" }
      );
      blocks.forEach((block) => observer.observe(block));
    }

    const sendProgress = () => {
      if (currentIndex < 0) return;
      const data = new URLSearchParams({ index: String(currentIndex) });
      try {
        navigator.sendBeacon(saveUrl, data);
      } catch {
        fetch(saveUrl, { method: "POST", body: data, keepalive: true }).catch(() => {});
      }
    };

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "hidden") sendProgress();
    });
    window.addEventListener("pagehide", sendProgress);

    const resumeIndex = parseInt(body.dataset.progressIndex || "", 10);
    if (Number.isInteger(resumeIndex) && resumeIndex >= 2 && blocks[resumeIndex]) {
      window.addEventListener("load", () => {
        const target = blocks[resumeIndex];
        target.classList.add("is-resume");
        target.scrollIntoView({ block: "start" });
        showToast("Resumed");
      });
    }
  };

  const showToast = (text) => {
    const el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    el.textContent = text;
    document.body.appendChild(el);
    setTimeout(() => el.classList.add("is-hidden"), 5000);
    setTimeout(() => el.remove(), 5600);
  };

  const toast = document.querySelector(".toast");
  if (toast) {
    if (window.history && window.history.replaceState) {
      const url = new URL(location.href);
      if (url.searchParams.has("flash")) {
        url.searchParams.delete("flash");
        window.history.replaceState({}, "", url);
      }
    }
    setTimeout(() => toast.classList.add("is-hidden"), 5000);
  }

  initThemeToggle();
  initSwipeToDelete();
  initReadingProgress();
  registerWorker();
  syncHome();
})();
