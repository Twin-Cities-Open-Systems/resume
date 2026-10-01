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
       out of a label }). It reads the page as it scrolls and shows only what is out of sight.
     It also adds a "link here" anchor (no markup needed): its href is always a link to the
     section the reader is in -- the nearest heading, card or [id] above the reading line --
     so it can be opened, dragged or right-click copied, and a click copies that URL and puts
     it in the address bar without moving the page. A heading with no id gets one from its
     text (the same text gives the same id on every load, so the link survives a reload). */
  window.TC.wayback = {
    init: function (nav, opts) {
      if (!nav) { return; }
      opts = opts || {};
      var headSel = opts.heading || "header";
      var groupSel = opts.groups || "[data-tc-collapse]";
      var skip = ".count,.tc-collapse-marker,.chip,[aria-hidden=true]" + (opts.strip ? "," + opts.strip : "");
      var btn = {}, target = {}, HEAD = 76, LINE = 96, queued = false;
      if (!nav.querySelector('[data-tc-to="here"]')) {
        var a = document.createElement("a");
        a.setAttribute("data-tc-to", "here");
        a.className = "tc-jump-here";
        a.hidden = true;
        a.href = "#";
        a.innerHTML = '<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false">' +
          '<path d="M6.5 9.5l3-3M7 4.5l1.2-1.2a2.6 2.6 0 0 1 3.7 3.7L10.7 8.2M9 11.5l-1.2 1.2a2.6 2.6 0 0 1-3.7-3.7L5.3 7.8" ' +
          'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>' +
          '<span class="tc-jump-said" aria-live="polite"></span>';
        var topb = nav.querySelector('[data-tc-to="top"]');
        nav.insertBefore(a, topb || null);
      }
      Array.prototype.forEach.call(nav.querySelectorAll("[data-tc-to]"), function (b) { btn[b.getAttribute("data-tc-to")] = b; });
      var slug = function (t) {
        return t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) || "section";
      };
      // An id for a heading that has none, from its own words; a clash takes -2, -3 ...
      var idFor = function (el) {
        if (el.id) { return el.id; }
        var base = slug(words(el)), id = base, n = 2;
        while (document.getElementById(id)) { id = base + "-" + n++; }
        el.id = id;
        return id;
      };
      var anchorSel = "h2, h3, h4, " + groupSel + ", section[id], article[id]";
      // The section being read: the last anchor candidate whose top is above the reading line.
      var here = function (scope) {
        var hit = null;
        Array.prototype.forEach.call(scope.querySelectorAll(anchorSel), function (el) {
          if (el.closest(".tc-jump") || el.offsetParent === null) { return; }
          if (el.getBoundingClientRect().top <= LINE + 8) { hit = el; }
        });
        if (!hit) { return null; }
        // A card or section is named by its heading, and linked by its own id when it has one.
        var head = hit.matches("h2, h3, h4") ? hit : hit.querySelector("summary, [data-tc-collapse-toggle], h2, h3, h4");
        var el = hit.id ? hit : (head || hit);
        return { el: el, label: words(head || hit) };
      };
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
      // Every heading in the scope gets its id now, in document order, so a clash is numbered
      // the same way on every load and a copied link still lands after a reload.
      var idSel = "h2, h3, h4, summary, [data-tc-collapse-toggle]";
      Array.prototype.forEach.call(((opts.scope && opts.scope()) || document.body).querySelectorAll(idSel), function (h) {
        if (!h.closest(".tc-jump")) { idFor(h); }
      });
      // A link that arrived before those ids existed found nothing to scroll to, and one that
      // did may sit under the sticky header: put the target just below it.
      if (location.hash.length > 1) {
        var go = document.getElementById(decodeURIComponent(location.hash.slice(1)));
        if (go && Math.abs(go.getBoundingClientRect().top - HEAD) > 4) {
          window.scrollTo(0, go.getBoundingClientRect().top + window.scrollY - HEAD);
        }
      }
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
        var h = here(scope);
        btn.here.hidden = !h;
        if (h) {
          var url = location.href.split("#")[0] + "#" + idFor(h.el);
          if (btn.here.href !== url) { btn.here.href = url; }
          btn.here.setAttribute("aria-label", "Link to this section: " + h.label);
          btn.here.title = "Copy a link to: " + h.label;
        }
      };
      // The clipboard API first; it refuses without focus or permission, so the old
      // select-and-copy is the fallback for a refusal too, not only for its absence.
      var legacy = function (text) {
        var t = document.createElement("textarea");
        t.value = text; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
        document.body.appendChild(t); t.select();
        var ok = false;
        try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
        t.remove();
        return ok ? Promise.resolve() : Promise.reject(new Error("copy refused"));
      };
      var copy = function (text) {
        if (navigator.clipboard && window.isSecureContext) {
          return navigator.clipboard.writeText(text).catch(function () { return legacy(text); });
        }
        return legacy(text);
      };
      var said = null;
      btn.here.addEventListener("click", function (e) {
        // A modified click opens the link the browser's way; a plain one copies it in place.
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) { return; }
        e.preventDefault();
        var url = btn.here.href, out = btn.here.querySelector(".tc-jump-said");
        try { history.replaceState(history.state, "", url); } catch (err) { /* file:// */ }
        var say = function (msg) {
          out.textContent = msg;
          btn.here.setAttribute("data-said", "");
          window.clearTimeout(said);
          said = window.setTimeout(function () { out.textContent = ""; btn.here.removeAttribute("data-said"); }, 1800);
        };
        copy(url).then(function () { say("Link copied"); }, function () { say("Link in the address bar"); });
      });
      var queue = function () { if (!queued) { queued = true; window.requestAnimationFrame(update); } };
      nav.addEventListener("click", function (e) {
        var b = e.target.closest("[data-tc-to]");
        if (!b || b.getAttribute("data-tc-to") === "here") { return; }
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
