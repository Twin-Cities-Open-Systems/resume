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

// Real host-aware link/text handling (Spencer, 2026-08-26): "lab links
// should only point to lab stuff and prod to prod" + "remove all
// static content, we don't need nor want it (exception not rule)" --
// no hardcoded domain string lives in any page; every domain-bearing
// bit of text/link is computed from the real window.location.hostname
// at load time.
//
// Real gap this works around: tcos.lab.tcos.us / <oper>.blog.lab.tcos.us
// mirrors were planned (HAProxy reverse-proxy to the real public
// origins) but don't exist yet -- confirmed via DNS, they don't
// resolve. Until they're built, a cross-site link with no real lab
// target goes inert on lab (plain text, no href) instead of silently
// bouncing a lab reviewer out to prod.
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var host = window.location.hostname;
    var onLab = /\.lab\.tcos\.us$/.test(host);

    document.querySelectorAll("a[data-cross-site]").forEach(function (a) {
      if (!onLab) return;
      var span = document.createElement("span");
      span.className = a.className + " link-inert";
      span.textContent = a.textContent + " (prod only)";
      span.title = a.href + " -- no lab mirror yet";
      a.replaceWith(span);
    });

    document.querySelectorAll("[data-host]").forEach(function (el) {
      el.textContent = host;
    });
  });
})();
