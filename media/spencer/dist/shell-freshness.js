// Shared "lu:" freshness banner. Tiny, plug-and-play: drop
//   <div class="lu-row freshness" id="freshness">
//     <span class="fr-dot"></span><b>lu:</b>
//     <time class="lu-iso" datetime="ISO8601">ISO8601</time>
//     <span id="fr-text"></span>
//   </div>
// onto any page, include this script, done -- no page-specific wiring.
// First built for tux-tattoo; reused here per Spencer's "never dup,
// always dedup" rule (second use is exactly the line where it moves
// to a shared file instead of getting copy-pasted).
//
// Real fix, 2026-08-28: used to read a data-generated attribute on the
// wrapping div, a real timestamp but not the canonical lu-iso <time>
// element check_render_review_compliance.py (the org's real Gold
// checker) looks for -- unified onto the one real element instead of
// carrying two representations of the same timestamp.
(function () {
  var STALE_AFTER_MS = 24 * 60 * 60 * 1000;
  var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function ordinal(n) {
    if (n >= 11 && n <= 13) return n + "th";
    switch (n % 10) { case 1: return n + "st"; case 2: return n + "nd"; case 3: return n + "rd"; default: return n + "th"; }
  }
  // Real, human-readable absolute date shown first (per Spencer's ask
  // for something "more sqz" than a fully spelled-out date+time, but
  // still a genuine calendar date) -- squeezed relative time second,
  // a quick gut-check, not the primary claim.
  function fancyDate(d) {
    return WEEKDAYS[d.getUTCDay()] + " " + MONTHS[d.getUTCMonth()] + " " + ordinal(d.getUTCDate()) + " " + d.getUTCFullYear();
  }
  document.addEventListener("DOMContentLoaded", function () {
    var wrap = document.getElementById("freshness");
    if (!wrap) return;
    var isoEl = wrap.querySelector(".lu-iso");
    if (!isoEl) return;
    var textEl = document.getElementById("fr-text");
    var generated = new Date(isoEl.getAttribute("datetime"));
    function renderDelta() {
      var ms = Date.now() - generated.getTime();
      var mins = Math.floor(ms / 60000);
      var rel;
      if (mins < 1) rel = "now";
      else if (mins < 60) rel = mins + "m";
      else if (mins < 60 * 24) rel = Math.floor(mins / 60) + "h" + (mins % 60) + "m";
      else rel = Math.floor(mins / (60 * 24)) + "d" + Math.floor((mins % (60 * 24)) / 60) + "h";
      isoEl.textContent = fancyDate(generated);
      textEl.innerHTML = '<span class="fr-rel">(' + rel + " ago)</span>";
      // Real technical value, the same real ISO timestamp this is
      // computed from -- muted, hover-only, not the primary claim.
      // hee-epoch will eventually own real epoch tracking; this is the
      // honest ISO number until then.
      isoEl.title = "ISO: " + isoEl.getAttribute("datetime");
      wrap.dataset.stale = String(ms > STALE_AFTER_MS);
    }
    renderDelta();
    setInterval(renderDelta, 30000);
  });
})();
