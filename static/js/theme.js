/**
 * DateMe — theme.js
 * Handles dark / light mode toggle.
 * Persists preference in localStorage.
 */

(function () {
  "use strict";

  const KEY = "dateme_theme";
  const DEFAULT = "dark";

  /* Apply a theme immediately (no flash) */
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(KEY, theme);
    updateButton(theme);
  }

  /* Update the toggle button label/icon */
  function updateButton(theme) {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    if (theme === "dark") {
      btn.innerHTML = '<span class="icon">☀️</span> Light Mode';
      btn.title = "Switch to light mode";
    } else {
      btn.innerHTML = '<span class="icon">🌙</span> Dark Mode';
      btn.title = "Switch to dark mode";
    }
  }

  /* Toggle between dark and light */
  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || DEFAULT;
    applyTheme(current === "dark" ? "light" : "dark");
  }

  /* On page load: restore saved preference (or system preference) */
  function init() {
    const saved = localStorage.getItem(KEY);
    let theme;
    if (saved) {
      theme = saved;
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
      theme = "light";
    } else {
      theme = DEFAULT;
    }
    applyTheme(theme);

    /* Wire up the button once DOM is ready */
    document.addEventListener("DOMContentLoaded", function () {
      const btn = document.getElementById("themeToggle");
      if (btn) {
        btn.addEventListener("click", toggleTheme);
        updateButton(theme); // ensure label matches
      }
    });
  }

  /* Run as early as possible to avoid flash */
  init();
})();
