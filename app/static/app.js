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

  // Home shows three rows per list, the rest behind Show more. Laid out
  // from the rows still present, so a row swiped away lets the next move up.
  const layoutHomeList = (section) => {
    const rows = [...section.querySelectorAll(":scope > .item-swipe, :scope > .item")];
    const button = section.querySelector(".show-more");
    const expanded = section.dataset.expanded === "1";
    rows.forEach((row, index) => {
      row.hidden = !expanded && index >= 3;
    });
    if (button) {
      button.hidden = rows.length <= 3;
      button.textContent = expanded ? "Show less" : "Show more";
    }
  };

  document.querySelectorAll("[data-list]").forEach((section) => {
    const button = section.querySelector(".show-more");
    if (!button) return;
    button.addEventListener("click", () => {
      section.dataset.expanded = section.dataset.expanded === "1" ? "" : "1";
      layoutHomeList(section);
    });
  });

  const initSwipe = () => {
    const rows = document.querySelectorAll(".item-swipe");
    if (rows.length === 0) return;
    const SLIDE = "transform 0.2s ease";

    // A row leaving one tab lands in the other: the active tab's count
    // drops and, when it moved rather than got deleted, the other rises.
    const bumpCounts = (row, moved) => {
      // On Home a row leaves its list whichever way it goes.
      const homeList = row.closest("[data-list]");
      if (homeList) {
        const count = homeList.querySelector(".count");
        if (count) count.textContent = String(Math.max(0, Number(count.textContent) - 1));
        return;
      }
      const tabs = document.querySelectorAll(".actions a");
      tabs.forEach((tab) => {
        const delta = tab.classList.contains("is-active") ? -1 : moved ? 1 : 0;
        if (delta === 0) return;
        tab.textContent = tab.textContent.replace(/\((\d+)\)/, (_, n) => `(${Number(n) + delta})`);
      });
    };

    const post = async (url) => {
      // `manual` keeps the redirect the form routes answer with from being
      // followed: a 303 back to the list is success, and nothing else loads.
      const response = await fetch(url, { method: "POST", redirect: "manual" });
      if (!(response.ok || response.type === "opaqueredirect")) {
        throw new Error(`status ${response.status}`);
      }
    };

    const setX = (row, x, animate) => {
      const link = row.querySelector(".item");
      link.style.transition = animate ? SLIDE : "none";
      link.style.transform = x ? `translateX(${x}px)` : "";
      row.classList.toggle("is-swiping-left", x < 0);
      row.classList.toggle("is-swiping-right", x > 0);
    };

    const removeRow = (row) => {
      row.style.height = `${row.offsetHeight}px`;
      row.classList.add("is-leaving");
      requestAnimationFrame(() => {
        row.style.height = "0px";
        row.style.borderTopColor = "transparent";
      });
      setTimeout(() => {
        const homeList = row.closest("[data-list]");
        row.remove();
        if (!homeList) return;
        const count = homeList.querySelector(".count");
        // Home hides a list with nothing unread; match that without a reload.
        if (count && count.textContent === "0") {
          homeList.remove();
        } else {
          layoutHomeList(homeList);
        }
      }, 220);
    };

    const failed = (row) => {
      setX(row, 0, true);
      delete row.dataset.busy;
      showToast("Couldn't save");
    };

    const runMove = async (row) => {
      row.dataset.busy = "1";
      setX(row, -row.offsetWidth, true);
      try {
        await post(row.dataset.swipeAction);
      } catch {
        failed(row);
        return;
      }
      bumpCounts(row, true);
      removeRow(row);
    };

    const confirmDelete = (row) => {
      row.dataset.busy = "1";
      setX(row, Math.round(row.offsetWidth * 0.4), true);
      const backdrop = document.createElement("div");
      backdrop.className = "swipe-dialog-backdrop";
      backdrop.innerHTML = `
        <div class="swipe-dialog" role="alertdialog" aria-modal="true" aria-labelledby="swipe-dialog-title">
          <div class="swipe-dialog-body">
            <h2 id="swipe-dialog-title">Delete this article?</h2>
            <p></p>
          </div>
          <div class="swipe-dialog-buttons">
            <button type="button">Cancel</button>
            <button type="button">Delete</button>
          </div>
        </div>`;
      backdrop.querySelector("p").textContent =
        `“${row.querySelector(".title").textContent}” will be removed from every list. This can’t be undone.`;
      const [cancel, confirm] = backdrop.querySelectorAll("button");

      const close = () => {
        backdrop.remove();
        document.removeEventListener("keydown", onKey);
      };
      const onCancel = () => {
        close();
        setX(row, 0, true);
        delete row.dataset.busy;
      };
      const onKey = (event) => {
        if (event.key === "Escape") onCancel();
      };

      cancel.addEventListener("click", onCancel);
      backdrop.addEventListener("click", (event) => {
        if (event.target === backdrop) onCancel();
      });
      document.addEventListener("keydown", onKey);
      confirm.addEventListener("click", async () => {
        close();
        try {
          await post(row.dataset.deleteAction);
        } catch {
          failed(row);
          return;
        }
        bumpCounts(row, false);
        removeRow(row);
      });

      document.body.appendChild(backdrop);
      cancel.focus();
    };

    rows.forEach((row) => {
      const link = row.querySelector(".item");
      if (!link) return;
      const canMove = Boolean(row.dataset.swipeAction);
      let startX = 0;
      let startY = 0;
      let dx = 0;
      let dragging = false;
      let deciding = false;
      let justDragged = false;

      const clamp = (value) => {
        const width = row.offsetWidth;
        return Math.max(canMove ? -width : 0, Math.min(width, value));
      };

      // A mouse drag on a link otherwise starts the browser's own link drag,
      // which cancels the pointer mid-swipe.
      link.addEventListener("dragstart", (event) => event.preventDefault());

      link.addEventListener("pointerdown", (event) => {
        if (event.pointerType === "mouse" && event.button !== 0) return;
        if (row.dataset.busy) return;
        startX = event.clientX;
        startY = event.clientY;
        dx = 0;
        dragging = false;
        deciding = true;
      });

      link.addEventListener("pointermove", (event) => {
        if (!deciding && !dragging) return;
        const moveX = event.clientX - startX;
        const moveY = event.clientY - startY;
        if (deciding) {
          if (Math.abs(moveX) < 8 && Math.abs(moveY) < 8) return;
          deciding = false;
          dragging = Math.abs(moveX) > Math.abs(moveY);
          if (dragging) link.setPointerCapture(event.pointerId);
        }
        if (!dragging) return;
        event.preventDefault();
        dx = clamp(moveX);
        setX(row, dx, false);
      });

      const finishDrag = (event) => {
        deciding = false;
        if (!dragging) return;
        dragging = false;
        // A drag release fires a trailing click on this same element; swallow it below.
        justDragged = true;
        const threshold = row.offsetWidth / 3;
        if (event.type === "pointerup" && dx <= -threshold) {
          runMove(row);
        } else if (event.type === "pointerup" && dx >= threshold) {
          confirmDelete(row);
        } else {
          setX(row, 0, true);
        }
      };

      link.addEventListener("pointerup", finishDrag);
      link.addEventListener("pointercancel", finishDrag);

      link.addEventListener("click", (event) => {
        if (justDragged || row.dataset.busy) {
          justDragged = false;
          event.preventDefault();
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

    // Wraps each text node's covered slice in its own <mark>, so a range
    // crossing element boundaries (list items, links, emphasis) never pulls
    // those elements apart or nests block elements inside an inline mark.
    const wrapBlockRange = (block, from, to) => {
      if (to <= from) return [];
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
      const slices = [];
      let pos = 0;
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const len = node.textContent.length;
        const a = Math.max(from - pos, 0);
        const b = Math.min(to - pos, len);
        // Whitespace between list items or table cells is layout, not text.
        const layoutOnly =
          !node.textContent.trim() &&
          node.parentElement.matches("ul, ol, table, thead, tbody, tfoot, tr");
        if (a < b && !layoutOnly) slices.push({ node, a, b });
        pos += len;
        if (pos >= to) break;
      }
      return slices.map(({ node, a, b }) => {
        let target = node;
        if (b < target.textContent.length) target.splitText(b);
        if (a > 0) target = target.splitText(a);
        const mark = document.createElement("mark");
        mark.className = "hl";
        target.before(mark);
        mark.appendChild(target);
        return mark;
      });
    };

    const imagesIn = (block) =>
      block.matches("img") ? [block] : Array.from(block.querySelectorAll("img"));
    const isImageOnly = (block) => !block.textContent.trim() && imagesIn(block).length > 0;

    const wrapHighlight = (
      startBlock,
      startOffset,
      endBlock,
      endOffset,
      highlightId,
      hasTitle = false
    ) => {
      const marks = [];
      for (let b = startBlock; b <= endBlock; b++) {
        const block = blocks[b];
        if (!block) continue;
        const from = b === startBlock ? startOffset : 0;
        const to = b === endBlock ? endOffset : block.textContent.length;
        marks.push(...wrapBlockRange(block, from, to));
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
      // A highlight carrying a section or subsection title gets a small §
      // just before it. The element stays empty (CSS draws the §) so it adds
      // no text: highlights are stored as character offsets into a block.
      if (hasTitle && marks.length > 0) {
        const marker = document.createElement("span");
        marker.className = "hl-title-marker";
        marker.setAttribute("aria-hidden", "true");
        if (highlightId != null) marker.dataset.highlightId = String(highlightId);
        marks[0].before(marker);
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
      wrapHighlight(h.start_block, h.start_offset, h.end_block, h.end_offset, h.id, h.has_title);
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
      body
        .querySelectorAll(`.hl-title-marker[data-highlight-id="${highlightId}"]`)
        .forEach((marker) => marker.remove());
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
      const mark = event.target.closest("mark.hl, .hl-title-marker");
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
          wrapHighlight(
            unionStart[0],
            unionStart[1],
            unionEnd[0],
            unionEnd[1],
            result.id,
            result.has_title
          );
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
  initSwipe();
  initReadingProgress();
  initHighlights();
  initHighlightDetail();
  registerWorker();
  syncHome();
})();
