// Shared fontsize + theme toggle behavior, paired with shell-theme.css.
// One real source, not pasted inline into every page.
(function () {
  var KEY = "tcos-fontsize";
  function apply(size) {
    document.body.setAttribute("data-fontsize", size);
    document.querySelectorAll(".fontsize-btn").forEach(function (b) {
      b.classList.toggle("active", b.dataset.size === size);
    });
  }
  document.addEventListener("DOMContentLoaded", function () {
    apply(localStorage.getItem(KEY) || "m");
    document.querySelectorAll(".fontsize-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        localStorage.setItem(KEY, b.dataset.size);
        apply(b.dataset.size);
      });
    });
  });
})();

(function () {
  var KEY = "tcos-theme";
  function apply(theme) {
    if (theme === "auto") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll(".theme-btn").forEach(function (b) {
      b.classList.toggle("active", b.dataset.theme === theme);
    });
  }
  document.addEventListener("DOMContentLoaded", function () {
    apply(localStorage.getItem(KEY) || "auto");
    document.querySelectorAll(".theme-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        localStorage.setItem(KEY, b.dataset.theme);
        apply(b.dataset.theme);
      });
    });
  });
})();
