(() => {
  const KEY_ORDER = "homeOrder";
  const KEY_HIDDEN = "homeHidden";
  const DEFAULT_ORDER = ["news", "later", "fav"];

  const loadOrder = () => {
    try {
      const value = JSON.parse(sessionStorage.getItem(KEY_ORDER));
      if (Array.isArray(value) && value.length) return value;
    } catch {
      /* keep default */
    }
    return [...DEFAULT_ORDER];
  };

  const loadHidden = () => {
    try {
      const value = JSON.parse(sessionStorage.getItem(KEY_HIDDEN));
      if (Array.isArray(value)) return value;
    } catch {
      /* keep default */
    }
    return [];
  };

  const save = (order, hidden) => {
    sessionStorage.setItem(KEY_ORDER, JSON.stringify(order));
    sessionStorage.setItem(KEY_HIDDEN, JSON.stringify(hidden));
  };

  window.homeLayout = { loadOrder, loadHidden, save, DEFAULT_ORDER };
})();
