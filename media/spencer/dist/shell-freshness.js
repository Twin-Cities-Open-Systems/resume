// Shared "lu:" freshness banner. Tiny, plug-and-play: drop
//   <div class="freshness" id="freshness" data-generated="ISO8601">
//     <span class="fr-dot"></span><span id="fr-text"></span>
//   </div>
// onto any page, include this script, done -- no page-specific wiring.
// First built for tux-tattoo; reused here per Spencer's "never dup,
// always dedup" rule (second use is exactly the line where it moves
// to a shared file instead of getting copy-pasted).
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
    var textEl = document.getElementById("fr-text");
    var generated = new Date(wrap.dataset.generated);
    function renderDelta() {
      var ms = Date.now() - generated.getTime();
      var mins = Math.floor(ms / 60000);
      var rel;
      if (mins < 1) rel = "now";
      else if (mins < 60) rel = mins + "m";
      else if (mins < 60 * 24) rel = Math.floor(mins / 60) + "h" + (mins % 60) + "m";
      else rel = Math.floor(mins / (60 * 24)) + "d" + Math.floor((mins % (60 * 24)) / 60) + "h";
      textEl.innerHTML = "lu: " + fancyDate(generated) + ' <span class="fr-rel">(' + rel + " ago)</span>";
      // Real technical value, same one this is computed from (the
      // wire-format data-generated attribute) -- muted, hover-only,
      // not the primary claim. hee-epoch will eventually own real
      // epoch tracking; this is the honest ISO number until then.
      textEl.title = "ISO: " + wrap.dataset.generated;
      wrap.dataset.stale = String(ms > STALE_AFTER_MS);
    }
    renderDelta();
    setInterval(renderDelta, 30000);
  });
})();
