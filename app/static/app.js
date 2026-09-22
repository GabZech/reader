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

  const initHighlights = () => {
    const body = document.querySelector(".article-body[data-highlight-action]");
    if (!body) return;
    const blocks = Array.from(body.children);
    if (blocks.length === 0) return;
    const saveUrl = body.dataset.highlightAction;

    const pointAtOffset = (block, offset) => {
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
      let pos = 0;
      let node = walker.nextNode();
      let last = null;
      while (node) {
        const len = node.textContent.length;
        if (pos + len >= offset) return { node, offset: offset - pos };
        pos += len;
        last = node;
        node = walker.nextNode();
      }
      return last ? { node: last, offset: last.textContent.length } : null;
    };

    const wrapBlockRange = (block, from, to) => {
      if (to <= from) return null;
      const start = pointAtOffset(block, from);
      const end = pointAtOffset(block, to);
      if (!start || !end) return null;
      const range = document.createRange();
      range.setStart(start.node, start.offset);
      range.setEnd(end.node, end.offset);
      try {
        const mark = document.createElement("mark");
        mark.className = "hl";
        mark.appendChild(range.extractContents());
        range.insertNode(mark);
        return mark;
      } catch {
        /* leave the text unwrapped rather than corrupt the DOM */
        return null;
      }
    };

    const imagesIn = (block) =>
      block.matches("img") ? [block] : Array.from(block.querySelectorAll("img"));
    const isImageOnly = (block) => !block.textContent.trim() && imagesIn(block).length > 0;

    const wrapHighlight = (startBlock, startOffset, endBlock, endOffset, highlightId) => {
      const marks = [];
      for (let b = startBlock; b <= endBlock; b++) {
        const block = blocks[b];
        if (!block) continue;
        const from = b === startBlock ? startOffset : 0;
        const to = b === endBlock ? endOffset : block.textContent.length;
        const mark = wrapBlockRange(block, from, to);
        if (mark) marks.push(mark);
        // Images have no text to wrap. Outline the ones the highlight
        // covers, by the same rule the server stores and exports them
        // (`images_in_block_range` in app/db.py).
        if ((b > startBlock && b < endBlock) || isImageOnly(block)) {
          imagesIn(block).forEach((img) => {
            img.classList.add("hl-image");
            if (highlightId != null) img.dataset.highlightId = String(highlightId);
          });
        }
      }
      if (highlightId != null) {
        marks.forEach((mark) => {
          mark.dataset.highlightId = String(highlightId);
        });
      }
      return marks;
    };

    const blockIndexOf = (node) => {
      let el = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
      while (el && el.parentElement !== body) el = el.parentElement;
      return el ? blocks.indexOf(el) : -1;
    };

    const charOffsetWithinBlock = (block, container, offsetInContainer) => {
      const range = document.createRange();
      range.selectNodeContents(block);
      range.setEnd(container, offsetInContainer);
      return range.toString().length;
    };

    const dataEl = document.getElementById("highlights-data");
    let saved = [];
    try {
      saved = dataEl ? JSON.parse(dataEl.textContent || "[]") : [];
    } catch {
      saved = [];
    }
    saved.forEach((h) => {
      wrapHighlight(h.start_block, h.start_offset, h.end_block, h.end_offset, h.id);
    });
    // Live record of what's on the page, kept in sync as saves/merges
    // happen so a second overlapping selection in the same visit (before
    // any reload) still detects correctly.
    const known = saved.map((h) => ({ ...h }));

    // Tuple-less-than for [block, offset] points, matching the server's
    // own (block, offset) comparisons.
    const pointBefore = (a, b) => a[0] < b[0] || (a[0] === b[0] && a[1] < b[1]);

    const textForSpan = (startBlock, startOffset, endBlock, endOffset) => {
      const start = pointAtOffset(blocks[startBlock], startOffset);
      const end = pointAtOffset(blocks[endBlock], endOffset);
      if (!start || !end) return "";
      const range = document.createRange();
      range.setStart(start.node, start.offset);
      range.setEnd(end.node, end.offset);
      return range.toString();
    };

    const unwrapHighlight = (highlightId) => {
      body.querySelectorAll(`mark.hl[data-highlight-id="${highlightId}"]`).forEach((mark) => {
        const parent = mark.parentNode;
        while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
        parent.removeChild(mark);
        parent.normalize();
      });
      body.querySelectorAll(`img.hl-image[data-highlight-id="${highlightId}"]`).forEach((img) => {
        img.classList.remove("hl-image");
        delete img.dataset.highlightId;
      });
    };

    body.addEventListener("click", (event) => {
      const mark = event.target.closest("mark.hl");
      if (!mark || !mark.dataset.highlightId) return;
      location.href = `${location.pathname}/highlights/${mark.dataset.highlightId}`;
    });

    const handleFinishedSelection = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) return;
      const range = selection.getRangeAt(0);
      if (!body.contains(range.commonAncestorContainer)) return;
      const text = range.toString();
      if (!text.trim()) return;

      let startBlock = blockIndexOf(range.startContainer);
      let endBlock = blockIndexOf(range.endContainer);
      if (startBlock < 0 || endBlock < 0) return;
      let startOffset = charOffsetWithinBlock(
        blocks[startBlock],
        range.startContainer,
        range.startOffset
      );
      let endOffset = charOffsetWithinBlock(
        blocks[endBlock],
        range.endContainer,
        range.endOffset
      );
      selection.removeAllRanges();

      // A boundary in an image-only block counts as covering its image
      // (see `images_in_block_range` in app/db.py). A browser often puts a
      // selection's end at the very start of the next block, touching an
      // image without covering it: move such a boundary onto the
      // neighbouring text so the image stays out.
      const touchesOnly = (block) =>
        isImageOnly(block) && !imagesIn(block).some((img) => range.intersectsNode(img));
      if (endBlock > startBlock && touchesOnly(blocks[endBlock])) {
        endBlock -= 1;
        endOffset = blocks[endBlock].textContent.length;
      }
      if (startBlock < endBlock && touchesOnly(blocks[startBlock])) {
        startBlock += 1;
        startOffset = 0;
      }

      const newStart = [startBlock, startOffset];
      const newEnd = [endBlock, endOffset];
      const overlapping = known.filter(
        (h) =>
          pointBefore(newStart, [h.end_block, h.end_offset]) &&
          pointBefore([h.start_block, h.start_offset], newEnd)
      );

      let unionStart = newStart;
      let unionEnd = newEnd;
      overlapping.forEach((h) => {
        const hStart = [h.start_block, h.start_offset];
        const hEnd = [h.end_block, h.end_offset];
        if (pointBefore(hStart, unionStart)) unionStart = hStart;
        if (pointBefore(unionEnd, hEnd)) unionEnd = hEnd;
      });

      const finalText = overlapping.length
        ? textForSpan(unionStart[0], unionStart[1], unionEnd[0], unionEnd[1])
        : text;
      if (!finalText.trim()) return;

      const data = new URLSearchParams({
        start_block: String(unionStart[0]),
        start_offset: String(unionStart[1]),
        end_block: String(unionEnd[0]),
        end_offset: String(unionEnd[1]),
        text: finalText,
      });
      overlapping.forEach((h) => data.append("merge_id", String(h.id)));

      // The DOM is only touched once the server confirms the save: no
      // optimistic mark, so a rejected or failed save leaves the page
      // exactly as it was instead of showing a phantom, unsaved highlight.
      fetch(saveUrl, { method: "POST", body: data })
        .then((r) => (r.ok ? r.json() : null))
        .then((result) => {
          if (!result) return;
          overlapping.forEach((h) => unwrapHighlight(h.id));
          wrapHighlight(unionStart[0], unionStart[1], unionEnd[0], unionEnd[1], result.id);
          const mergedIds = new Set(overlapping.map((h) => h.id));
          for (let i = known.length - 1; i >= 0; i--) {
            if (mergedIds.has(known[i].id)) known.splice(i, 1);
          }
          known.push({
            id: result.id,
            start_block: unionStart[0],
            start_offset: unionStart[1],
            end_block: unionEnd[0],
            end_offset: unionEnd[1],
          });
        })
        .catch(() => {});
    };

    // mouseup covers a fresh press-and-drag selection. On a touch device,
    // refining a selection with the system's drag handles never fires
    // mouseup on the page at all, so selectionchange (debounced until the
    // selection stops moving) is the only signal that works for both.
    body.addEventListener("mouseup", handleFinishedSelection);

    // Dragging a native selection handle slowly (aiming precisely, pausing
    // to reposition a finger) can easily pause longer than the debounce
    // below, which would finalize and mutate the DOM mid-drag — visibly
    // disrupting the OS's own handle UI and leaving only a partial
    // highlight. Tracking whether a touch is actually still down and
    // holding off until it lifts avoids finalizing while the gesture is
    // still in progress, regardless of how long a mid-drag pause lasts.
    let touchActive = false;
    let selectionTimer = null;
    document.addEventListener(
      "touchstart",
      () => {
        touchActive = true;
      },
      { passive: true }
    );
    const onTouchEnd = () => {
      touchActive = false;
      clearTimeout(selectionTimer);
      handleFinishedSelection();
    };
    document.addEventListener("touchend", onTouchEnd, { passive: true });
    document.addEventListener("touchcancel", onTouchEnd, { passive: true });

    document.addEventListener("selectionchange", () => {
      clearTimeout(selectionTimer);
      selectionTimer = setTimeout(() => {
        if (touchActive) return; // still dragging; touchend will finalize
        handleFinishedSelection();
      }, 400);
    });
  };

  const initHighlightDetail = () => {
    const button = document.getElementById("copy-highlight");
    if (!button) return;
    button.addEventListener("click", () => {
      const text = button.dataset.copyText || "";
      navigator.clipboard?.writeText(text)
        .then(() => showToast("Copied"))
        .catch(() => {});
    });
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
  initHighlights();
  initHighlightDetail();
  registerWorker();
  syncHome();
})();
