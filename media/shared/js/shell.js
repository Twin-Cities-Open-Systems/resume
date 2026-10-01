/* shell.js: the header (menu, text size, theme), flip cards and the way-back pill, on every TCOS web page. OWNED by tcos-app;
 * children copy it, never edit the copy (tcos-app CLAUDE.md, "How a child app inherits").
 *
 * Choices persist in localStorage and are applied before paint by the inline
 * bootstrap in each page's <head>; this file only wires the controls. A
 * browser that blocks storage still works, it just forgets.
 */
(function () {
  "use strict";

  function get(key, fallback) {
    try { return window.localStorage.getItem(key) || fallback; } catch (e) { return fallback; }
  }
  function set(key, value) {
    try { window.localStorage.setItem(key, value); } catch (e) { /* forgets */ }
  }
  function press(group, val, attr) {
    document.querySelectorAll(group).forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset[attr] === val));
    });
  }

  var fs = get("tc-fs", "m");
  document.documentElement.setAttribute("data-fs", fs);
  press(".fontsize-btn", fs, "size");
  document.querySelectorAll(".fontsize-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      var v = b.dataset.size;
      document.documentElement.setAttribute("data-fs", v);
      set("tc-fs", v);
      press(".fontsize-btn", v, "size");
    });
  });

  /* Small screens: fold nav, text size and theme behind one menu button. The button is made
     here, not in each page, so a page needs no markup change and no script leaves it all visible. */
  var top = document.querySelector("header.top");
  if (top && !top.querySelector(".menu-btn")) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "menu-btn";
    btn.setAttribute("aria-label", "Menu");
    btn.setAttribute("aria-expanded", "false");
    btn.textContent = "\u2630";
    var brand = top.querySelector(".brand");
    top.insertBefore(btn, brand ? brand.nextSibling : top.firstChild);
    top.classList.add("tc-menu");
    var shut = function () {
      top.removeAttribute("data-open");
      btn.setAttribute("aria-expanded", "false");
      btn.textContent = "\u2630";
    };
    btn.addEventListener("click", function () {
      var open = !top.hasAttribute("data-open");
      if (!open) { shut(); return; }
      top.setAttribute("data-open", "");
      btn.setAttribute("aria-expanded", "true");
      btn.textContent = "\u2715";
    });
    top.querySelectorAll("nav a").forEach(function (a) { a.addEventListener("click", shut); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && top.hasAttribute("data-open")) { shut(); btn.focus(); }
    });
  }

  /* "auto" removes the stamps entirely, so the page falls back to
     prefers-color-scheme, the unstamped state the CSS is built for. A named
     theme is a light or dark base plus a skin; keep KIND in step with the
     inline bootstrap in each page's <head>. */
  var KIND = { paper: "light", contrast: "light", midnight: "dark", graphite: "dark" };
  function applyTheme(v) {
    var root = document.documentElement;
    if (v === "auto") { root.removeAttribute("data-theme"); root.removeAttribute("data-skin"); return; }
    root.setAttribute("data-theme", KIND[v] || v);
    root.setAttribute("data-skin", v);
  }
  var th = get("tc-theme", "auto");
  var pick = document.querySelector(".theme-select");
  applyTheme(th);
  if (pick) {
    pick.value = th;
    pick.addEventListener("change", function () {
      applyTheme(pick.value);
      set("tc-theme", pick.value);
    });
  }
  /* Flip cards (css/shell.css, "flip card"). TC.flip.set(card, toBack, moveFocus) flips one;
     TC.flip.all(box, toBack) flips every card in a container. Clicks work with no page
     script: a [data-tc-flip] button, the front face, or the back face (unless text is
     selected) flips its card, and [data-tc-flipall="back|front"][data-target=<id>] flips a box. */
  window.TC = window.TC || {};
  var flip = window.TC.flip = {
    set: function (card, toBack, moveFocus) {
      if (!card) { return; }
      card.setAttribute("data-flipped", String(toBack));
      if (moveFocus) {
        var n = card.querySelector(toBack ? ".tc-backq" : ".tc-flipbtn");
        if (n) { n.focus({ preventScroll: true }); }
      }
    },
    all: function (box, toBack) {
      if (!box) { return; }
      Array.prototype.forEach.call(box.querySelectorAll(".tc-flip"), function (c) { flip.set(c, toBack, false); });
    }
  };
  document.addEventListener("click", function (e) {
    var fa = e.target.closest("[data-tc-flipall]");
    if (fa) { flip.all(document.getElementById(fa.getAttribute("data-target")), fa.getAttribute("data-tc-flipall") === "back"); return; }
    var f = e.target.closest("[data-tc-flip]");
    if (!f && !e.target.closest("a, button, input, select, textarea, summary")) {
      f = e.target.closest(".tc-front");
      if (!f && !String(window.getSelection && window.getSelection()).length) { f = e.target.closest(".tc-back"); }
    }
    if (f) { flip.set(f.closest(".tc-flip"), !f.closest(".tc-back"), true); }
  });

  /* The way back (css/shell.css, "way back"). A pill that follows the reader and names
     what is above them: the group they are inside, the section's heading, the top.
       <nav class="tc-jump" data-show="false" aria-label="Back to">
         <button data-tc-to="group" hidden><span class="tc-jump-l"></span></button>
         <button data-tc-to="panel" hidden><span class="tc-jump-l"></span></button>
         <button data-tc-to="top" aria-label="Top of the page">...</button></nav>
     TC.wayback.init(nav, { scope: fn -> the element being read (or null),
       heading: selector inside scope (default "header"), groups: selector for collapsible
       groups (default "[data-tc-collapse]"), strip: extra selector of decoration to leave
       out of a label }). It reads the page as it scrolls and shows only what is out of sight. */
  window.TC.wayback = {
    init: function (nav, opts) {
      if (!nav) { return; }
      opts = opts || {};
      var headSel = opts.heading || "header";
      var groupSel = opts.groups || "[data-tc-collapse]";
      var skip = ".count,.tc-collapse-marker,.chip,[aria-hidden=true]" + (opts.strip ? "," + opts.strip : "");
      var btn = {}, target = {}, HEAD = 76, LINE = 96, queued = false;
      Array.prototype.forEach.call(nav.querySelectorAll("[data-tc-to]"), function (b) { btn[b.getAttribute("data-tc-to")] = b; });
      var words = function (el) {
        var c = el.cloneNode(true);
        Array.prototype.forEach.call(c.querySelectorAll(skip), function (x) { x.remove(); });
        return c.textContent.replace(/\s+/g, " ").trim();
      };
      var within = function (scope) {
        var hit = null;
        Array.prototype.forEach.call(scope.querySelectorAll(groupSel), function (g) {
          var r = g.getBoundingClientRect(), head = g.querySelector("summary, [data-tc-collapse-toggle]");
          if (head && r.top <= LINE && r.bottom > LINE + 60 && head.getBoundingClientRect().bottom < HEAD) { hit = { el: head, label: words(head) }; }
        });
        return hit;
      };
      var update = function () {
        queued = false;
        var scope = opts.scope ? opts.scope() : document.body;
        var on = scope && window.scrollY > 320;
        nav.setAttribute("data-show", String(!!on));
        if (!on) { return; }
        var hd = scope.querySelector(headSel), g = within(scope);
        target.group = g && g.el; target.panel = hd;
        btn.group.hidden = !g || !g.label;
        if (g) { btn.group.querySelector("span").textContent = g.label; }
        btn.panel.hidden = !(hd && hd.getBoundingClientRect().bottom < HEAD);
        if (hd) { btn.panel.querySelector("span").textContent = words(hd.querySelector("h2") || hd); }
        nav.setAttribute("data-has-group", String(!btn.group.hidden));
      };
      var queue = function () { if (!queued) { queued = true; window.requestAnimationFrame(update); } };
      nav.addEventListener("click", function (e) {
        var b = e.target.closest("[data-tc-to]");
        if (!b) { return; }
        var to = b.getAttribute("data-tc-to"), el = target[to];
        var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var y = to === "top" ? 0 : el ? el.getBoundingClientRect().top + window.scrollY - HEAD : null;
        if (y !== null) { window.scrollTo({ top: Math.max(0, y), behavior: still ? "auto" : "smooth" }); }
      });
      window.addEventListener("scroll", queue, { passive: true });
      window.addEventListener("resize", queue);
      document.addEventListener("click", function () { window.setTimeout(queue, 60); });
      queue();
    }
  };
})();
