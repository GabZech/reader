// The installed app is a browser of its own: say so, so the Devices page can name it.
try {
  if (window.navigator.standalone || matchMedia("(display-mode: standalone)").matches) {
    document.getElementById("installed").value = "1";
  }
} catch (_) {}
// Nobody is signed in here, so nothing from the library should stay on this phone.
try {
  if (navigator.serviceWorker && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({ type: "forget" });
  }
} catch (_) {}
