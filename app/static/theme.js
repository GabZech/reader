// Runs before the page draws, so a dark page never flashes light.
(() => {
  if (localStorage.getItem("reader-theme") !== "light") {
    document.documentElement.dataset.theme = "dark";
  }
})();
