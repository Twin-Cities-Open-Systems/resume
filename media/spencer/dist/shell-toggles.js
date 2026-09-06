// Shared fontsize + theme toggle behavior, paired with shell-theme.css.
// One real source, not pasted inline into every page.
// Font-size: Gold's own block from .github/bin/render-review.py, verbatim --
// including the 2026-08-30 force-collapse-after-click fix.
(function () {
  var FS_KEY = "tcos-fontsize";
  function applyFontsize(size) {
    document.body.setAttribute("data-fontsize", size);
    document.querySelectorAll(".fontsize-btn").forEach(function (b) {
      b.classList.toggle("active", b.dataset.size === size);
    });
  }
  var savedSize = "m";
  try { savedSize = localStorage.getItem(FS_KEY) || "m"; } catch (e) {}
  applyFontsize(savedSize);
  document.querySelectorAll(".fontsize-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      try { localStorage.setItem(FS_KEY, b.dataset.size); } catch (e) {}
      applyFontsize(b.dataset.size);
      b.blur();
      // Real fix, 2026-08-30: :hover alone keeps .fs-options expanded
      // after a click, since the cursor is still sitting over the
      // widget -- force-collapse it, then let normal hover/focus-within
      // behavior resume once the cursor actually leaves.
      var toggle = b.closest(".fontsize-toggle");
      if (toggle) {
        toggle.classList.add("fs-force-collapsed");
        toggle.addEventListener("mouseleave", function onLeave() {
          toggle.classList.remove("fs-force-collapsed");
          toggle.removeEventListener("mouseleave", onLeave);
        });
      }
    });
  });
})();

(function () {
  // Real bug, found 2026-08-28: this read/wrote dataset.theme, matching
  // this file's own HTML (internally consistent, so it never broke
  // silently the way tcos-www's tc-theme.js did) but not the canonical
  // reference implementation's dataset.themeChoice everywhere else --
  // real, if quieter, drift risk. Aligned to match.
  var KEY = "tcos-theme";
  function apply(theme) {
    if (theme === "auto") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll(".theme-btn").forEach(function (b) {
      b.classList.toggle("active", b.dataset.themeChoice === theme);
    });
  }
  document.addEventListener("DOMContentLoaded", function () {
    apply(localStorage.getItem(KEY) || "auto");
    document.querySelectorAll(".theme-btn").forEach(function (b) {
      b.addEventListener("click", function () {
        localStorage.setItem(KEY, b.dataset.themeChoice);
        apply(b.dataset.themeChoice);
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
// Real fix, 2026-08-28: this used to always go inert on lab for any
// data-cross-site link, on the premise that no *.lab.tcos.us mirror
// existed yet -- true when written, stale since: lab.tcos.us and
// spencer.blog.lab.tcos.us both real and live now (fleet-ops#329 and
// direct verification). Rewrite to the real .tcos.us -> .lab.tcos.us
// swap (same real pattern already used in resume's own blog template)
// instead of assuming no lab target exists.
(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var host = window.location.hostname;
    var onLab = /\.lab\.tcos\.us$/.test(host);

    document.querySelectorAll("a[data-cross-site]").forEach(function (a) {
      if (!onLab) return;
      var url;
      try { url = new URL(a.href); } catch (e) { return; }
      if (/\.lab\.tcos\.us$/.test(url.hostname)) return; // already lab
      url.hostname = url.hostname.replace(/\.tcos\.us$/, ".lab.tcos.us");
      a.href = url.href;
    });

    document.querySelectorAll("[data-host]").forEach(function (el) {
      el.textContent = host;
    });
  });
})();
