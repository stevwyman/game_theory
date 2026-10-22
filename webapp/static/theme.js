(function () {
  var storageKey = "theme";

  function preferred() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function storedChoice() {
    try {
      return localStorage.getItem(storageKey) || "auto";
    } catch (error) {
      return "auto";
    }
  }

  function apply(choice) {
    var resolved = choice === "auto" ? preferred() : choice;
    document.documentElement.setAttribute("data-bs-theme", resolved);
    document.documentElement.setAttribute("data-sw-theme", choice);
  }

  function remember(choice) {
    try {
      localStorage.setItem(storageKey, choice);
    } catch (error) {
      /* Private mode can block storage; the choice still applies for this page. */
    }
    apply(choice);
  }

  function markActive(choice) {
    document.querySelectorAll("[data-sw-theme-value]").forEach(function (item) {
      var selected = item.getAttribute("data-sw-theme-value") === choice;
      item.classList.toggle("active", selected);
      item.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    var label = document.getElementById("theme-menu-label");
    if (label) {
      label.textContent = choice.charAt(0).toUpperCase() + choice.slice(1);
    }
  }

  apply(storedChoice());

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
    if (storedChoice() === "auto") {
      apply("auto");
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    var choice = document.documentElement.getAttribute("data-sw-theme") || storedChoice();
    markActive(choice);
    document.querySelectorAll("[data-sw-theme-value]").forEach(function (item) {
      item.addEventListener("click", function () {
        var next = item.getAttribute("data-sw-theme-value");
        remember(next);
        markActive(next);
      });
    });
  });
})();
