// Shared fontsize + theme toggle behavior, paired with shell-theme.css.
// One real source, not pasted inline into every page.
// Font-size: Gold's own block from .github/bin/render-review.py, verbatim --
// including the 2026-08-30 force-collapse-after-click fix.
(function () {
  var FS_KEY = "tcos-fontsize";
  function applyFontsize(size) {
    document.documentElement.setAttribute("data-fontsize", size);
    document.body.setAttribute("data-fontsize", size);
    if (window.tcosLayout) window.tcosLayout();
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

// Theme: the selector is tcos-app's shell (/js/shell.js, loaded before this
// file), which reads and writes tc-theme. The pre-paint script in each page
// carries an old tcos-theme choice over once.
//
// The way back (tcos-app shell, TC.wayback): a pill that follows the reader
// down a long page and names the page title, plus a jump to the top. Added
// here, once, so no page has to carry its markup.
(function () {
  function run() {
    if (!(window.TC && window.TC.wayback) || document.querySelector("nav.tc-jump")) return;
    var nav = document.createElement("nav");
    nav.className = "tc-jump";
    nav.setAttribute("aria-label", "Back to");
    nav.setAttribute("data-show", "false");
    nav.innerHTML =
      '<button type="button" data-tc-to="group" hidden><span class="tc-jump-l"></span></button>' +
      '<button type="button" data-tc-to="panel" hidden><span class="tc-jump-l"></span></button>' +
      '<button type="button" data-tc-to="top" aria-label="Top of the page">' +
      '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false">' +
      '<path d="M3 10l5-5 5 5M3 4h10" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round"/></svg></button>';
    document.body.appendChild(nav);
    window.TC.wayback.init(nav, { heading: "h1" });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
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

// SYNCED-FROM .github/bin/render-review.py (Gold).

// Links that leave this host open in a new tab; same-site navigation stays
// in place. Operator, 2026-09-06: "most links should open in a new tab".
// Decided at load time from the real href, so authors never annotate.
(function () {
  function run() {
    document.querySelectorAll("a[href]").forEach(function (a) {
      var url;
      try { url = new URL(a.getAttribute("href"), location.href); } catch (e) { return; }
      if (url.protocol !== "http:" && url.protocol !== "https:") return;
      if (url.hostname === location.hostname) return;
      if (!a.target) a.target = "_blank";
      a.rel = (a.rel ? a.rel + " " : "") + "noopener";
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
})();

// Layout tokens from the space actually available, in em -- phone, browser
// zoom and XXL text all collapse the same way (SYNCED-FROM tcos-www site.js).
(function () {
  var COMPACT_EM = 44, NARROW_EM = 26;
  function layout() {
    var root = document.documentElement;
    var px = parseFloat(getComputedStyle(root).fontSize) || 16;
    var em = root.clientWidth / px;
    var tokens = [];
    if (em < COMPACT_EM) tokens.push("compact");
    if (em < NARROW_EM) tokens.push("narrow");
    root.setAttribute("data-layout", tokens.join(" ") || "wide");
  }
  window.tcosLayout = layout;
  var q = new URLSearchParams(location.search).get("fs");
  if (q && /^(s|m|l|xl|xxl)$/.test(q)) { try { localStorage.setItem("tcos-fontsize", q); } catch (e) {} document.documentElement.setAttribute("data-fontsize", q); }
  layout();
  window.addEventListener("resize", layout);
  window.addEventListener("orientationchange", layout);
})();
