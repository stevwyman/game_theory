(() => {
  const KEY = "game-solver-theme";
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  function getMode() {
    const stored = window.localStorage.getItem(KEY);
    return stored === "light" || stored === "dark" || stored === "auto" ? stored : "auto";
  }

  function resolved(mode) {
    if (mode === "dark") {
      return "dark";
    }
    if (mode === "light") {
      return "light";
    }
    return media.matches ? "dark" : "light";
  }

  function apply(mode) {
    const next = mode === "light" || mode === "dark" || mode === "auto" ? mode : "auto";
    window.localStorage.setItem(KEY, next);
    document.documentElement.classList.toggle("pf-v5-theme-dark", resolved(next) === "dark");
    document.documentElement.dataset.themeMode = next;
    document.querySelectorAll("[data-theme-mode]").forEach((button) => {
      const selected = button.getAttribute("data-theme-mode") === next;
      button.classList.toggle("pf-m-selected", selected);
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  }

  window.GameTheme = { apply, getMode, resolved };
  apply(getMode());
  media.addEventListener("change", () => {
    if (getMode() === "auto") {
      apply("auto");
    }
  });
})();
