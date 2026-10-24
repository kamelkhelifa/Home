/* Course pages: weekly progress, grade calculator, materials filter, glossary & maths.
   Adapted from TeachWeb's course script. Progress is stored only in the visitor's browser. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var LANG = document.documentElement.lang, RTL = document.documentElement.dir === "rtl";
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("kk:" + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("kk:" + k, JSON.stringify(v)); } catch (e) {} },
    del: function (k) { try { localStorage.removeItem("kk:" + k); } catch (e) {} }
  };
  function setRing(svg, pct) { var c = svg && svg.querySelector(".ring-val"); if (c) c.setAttribute("stroke-dasharray", Math.max(0, Math.min(100, pct)).toFixed(1) + " 100"); }

  // ---------- maths ----------
  var MACROS = {
    "\\ket": "\\left|#1\\right\\rangle", "\\bra": "\\left\\langle#1\\right|", "\\braket": "\\left\\langle#1\\middle|#2\\right\\rangle",
    "\\expval": "\\left\\langle#1\\right\\rangle", "\\abs": "\\left|#1\\right|", "\\norm": "\\left\\lVert#1\\right\\rVert",
    "\\vb": "\\mathbf{#1}", "\\dv": "\\frac{\\mathrm{d}#1}{\\mathrm{d}#2}", "\\pdv": "\\frac{\\partial#1}{\\partial#2}",
    "\\dd": "\\mathrm{d}", "\\comm": "\\left[#1,#2\\right]", "\\order": "\\mathcal{O}\\left(#1\\right)"
  };
  function renderMath(el) {
    if (!window.renderMathInElement) return;
    try {
      window.renderMathInElement(el || document.body, {
        delimiters: [{ left: "\\[", right: "\\]", display: true }, { left: "\\(", right: "\\)", display: false }, { left: "$$", right: "$$", display: true }],
        macros: MACROS, throwOnError: false, ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option", "input"]
      });
    } catch (e) { /* keep the raw LaTeX visible */ }
  }

  var root = $("[data-course]");
  if (root) initCourse(root);

  function initCourse(root) {
    var slug = root.dataset.course;
    $$("[data-print]").forEach(function (b) { b.addEventListener("click", function () { print(); }); });

    // table of contents: highlight the current section
    var links = $$("[data-toc]"), secs = links.map(function (a) { return document.getElementById(a.dataset.toc); });
    function spy() {
      var y = scrollY + innerHeight * 0.3, cur = 0;
      secs.forEach(function (s, i) { if (s && s.offsetTop <= y) cur = i; });
      links.forEach(function (a, i) {
        var on = i === cur;
        if (a.classList.contains("active") !== on) {
          a.classList.toggle("active", on);
          if (on && innerWidth <= 1020) {
            var ul = a.closest(".tw-toc-list");
            ul.scrollLeft += (a.getBoundingClientRect().left + a.offsetWidth / 2) - (ul.getBoundingClientRect().left + ul.clientWidth / 2);
          }
        }
      });
    }
    addEventListener("scroll", spy, { passive: true }); spy();

    // weekly plan: progress ticks
    var boxes = $$("[data-week-done]");
    var done = store.get("weeks:" + slug, []).map(String);
    var nWeeks = boxes.filter(function (b) { return !b.disabled; }).length || 1;
    function syncWeeks() {
      boxes.forEach(function (b) { b.checked = done.indexOf(b.dataset.weekDone) >= 0; b.closest(".week").classList.toggle("done", b.checked); });
      var pct = 100 * done.length / nWeeks;
      setRing($("[data-week-progress] svg"), pct);
      var c = $("[data-week-count]"); if (c) c.textContent = done.length + " / " + nWeeks;
      var wb = $("[data-week-bar]"); if (wb) wb.style.width = pct + "%";
    }
    boxes.forEach(function (b) {
      b.addEventListener("change", function () {
        var w = b.dataset.weekDone;
        done = done.filter(function (x) { return x !== w; }); if (b.checked) done.push(w);
        store.set("weeks:" + slug, done); syncWeeks();
      });
    });
    syncWeeks();
    var reset = $("[data-weeks-reset]");
    if (reset) reset.addEventListener("click", function () { done = []; store.del("weeks:" + slug); syncWeeks(); });

    function setWeek(btn, open) {
      var panel = btn && document.getElementById(btn.getAttribute("aria-controls"));
      if (!panel) return;
      btn.setAttribute("aria-expanded", String(open)); panel.hidden = !open;
    }
    $$(".week-toggle").forEach(function (btn) { btn.addEventListener("click", function () { setWeek(btn, btn.getAttribute("aria-expanded") !== "true"); }); });
    $$("[data-weeks-toggle]").forEach(function (b) { b.addEventListener("click", function () { var o = b.dataset.weeksToggle === "open"; $$(".week-toggle").forEach(function (x) { setWeek(x, o); }); }); });
    function openHash() {
      var m = /^#week-(.+)$/.exec(location.hash); if (!m) return;
      var w = document.getElementById("week-" + m[1]); if (w) setWeek($(".week-toggle", w), true);
    }
    addEventListener("hashchange", openHash); openHash();
    if (!location.hash) {
      var first = $$(".week").filter(function (w) { return !w.classList.contains("done") && $(".week-panel", w); })[0];
      if (first) setWeek($(".week-toggle", first), true);
    }

    // assessment: donut <-> list
    var donut = $(".donut");
    if (donut) $$("[data-seg-hover]").forEach(function (li) {
      var seg = $('[data-seg="' + li.dataset.segHover + '"]');
      li.addEventListener("mouseenter", function () { donut.classList.add("hovering"); seg.classList.add("on"); li.classList.add("on"); });
      li.addEventListener("mouseleave", function () { donut.classList.remove("hovering"); seg.classList.remove("on"); li.classList.remove("on"); });
    });

    // grade calculator
    var calc = $("[data-calc]");
    if (calc) {
      var inputs = $$("input", calc), saved = store.get("calc:" + slug, {});
      inputs.forEach(function (inp, i) { if (saved[i] != null) inp.value = saved[i]; });
      var compute = function () {
        var tot = 0, any = false, s = {};
        inputs.forEach(function (inp, i) {
          var v = parseFloat(inp.value);
          if (!isNaN(v)) { v = Math.max(0, Math.min(100, v)); tot += v * (+inp.dataset.weight) / 100; any = true; s[i] = v; }
        });
        store.set("calc:" + slug, s);
        $("[data-calc-total]", calc).textContent = any ? tot.toFixed(1) : "—";
        $("[data-calc-20]", calc).textContent = any ? (tot / 5).toFixed(2) : "—";
      };
      inputs.forEach(function (inp) { inp.addEventListener("input", compute); }); compute();
    }

    // materials: filter by type and text
    var mgrid = $("[data-mat-grid]");
    if (mgrid) {
      var mType = "", mq = "", mitems = $$("li", mgrid);
      var mApply = function () {
        mitems.forEach(function (li) { li.hidden = !((!mType || li.dataset.type === mType) && (!mq || li.textContent.toLowerCase().indexOf(mq) >= 0)); });
      };
      $$("[data-mat-type]").forEach(function (b) {
        b.addEventListener("click", function () {
          mType = b.dataset.matType;
          $$("[data-mat-type]").forEach(function (x) { x.classList.toggle("is-on", x === b); });
          mApply();
        });
      });
      var ms = $("[data-mat-search]"); if (ms) ms.addEventListener("input", function () { mq = ms.value.trim().toLowerCase(); mApply(); });
    }
  }

  // ---------- glossary: table filter, flashcards, pronunciation ----------
  $$("[data-gloss]").forEach(function (g) {
    var rows = $$("[data-term]", g), search = $("[data-gloss-search]", g), count = $("[data-gloss-count]", g);
    var deck = rows.slice(), idx = 0, card = $("[data-flash-card]", g);
    function visible() { return rows.filter(function (r) { return !r.hidden; }); }
    if (search) search.addEventListener("input", function () {
      var q = (search.value || "").trim().toLowerCase();
      rows.forEach(function (r) { r.hidden = !!q && (r.dataset.en + " " + r.dataset.ar + " " + r.dataset.fr + " " + r.textContent).toLowerCase().indexOf(q) < 0; });
      count.textContent = visible().length; deck = visible(); idx = 0; paint();
    });
    $$("[data-gloss-view]", g).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("[data-gloss-view]", g).forEach(function (x) { x.classList.toggle("is-on", x === b); });
        $$("[data-gloss-pane]", g).forEach(function (p) { p.hidden = p.dataset.glossPane !== b.dataset.glossView; });
        paint();
      });
    });
    var front = LANG === "ar" ? "ar" : LANG === "fr" ? "fr" : "en", back = LANG === "ar" ? "en" : "ar";
    var LBL = { en: "English", ar: "العربية", fr: "Français" };
    function paint() {
      if (!card) return;
      card.classList.remove("flipped");
      var r = deck[idx];
      if (!r) { $("[data-flash-front]", g).textContent = "—"; $("[data-flash-pos]", g).textContent = "0 / 0"; return; }
      var f = $("[data-flash-front]", g), bk = $("[data-flash-back]", g), fl = r.dataset[front] ? front : "en";
      f.textContent = r.dataset[fl]; f.lang = fl;
      var extra = fl === "fr" ? r.dataset.en : r.dataset.fr;
      bk.textContent = r.dataset[back] + (extra ? "  ·  " + extra : ""); bk.lang = back;
      $("[data-flash-lang-front]", g).textContent = LBL[fl];
      $("[data-flash-lang-back]", g).textContent = LBL[back] + (extra ? " · " + LBL[fl === "fr" ? "en" : "fr"] : "");
      var def = $(".g-def", r); $("[data-flash-def]", g).innerHTML = def ? def.innerHTML : "";
      $("[data-flash-pos]", g).textContent = (idx + 1) + " / " + deck.length;
    }
    if (card) {
      card.addEventListener("click", function () { card.classList.toggle("flipped"); });
      $("[data-flash-next]", g).addEventListener("click", function () { if (deck.length) { idx = (idx + 1) % deck.length; paint(); } });
      $("[data-flash-prev]", g).addEventListener("click", function () { if (deck.length) { idx = (idx - 1 + deck.length) % deck.length; paint(); } });
      $("[data-flash-shuffle]", g).addEventListener("click", function () {
        for (var i = deck.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = deck[i]; deck[i] = deck[j]; deck[j] = t; }
        idx = 0; paint();
      });
      $("[data-flash-speak]", g).addEventListener("click", function () { var r = deck[idx]; if (r) speak(r.dataset.en); });
      g.addEventListener("keydown", function (e) {
        if ($('[data-gloss-pane="cards"]', g).hidden || /input|select/i.test(e.target.tagName)) return;
        if (e.key === "ArrowRight") { idx = (idx + (RTL ? -1 : 1) + deck.length) % deck.length; paint(); }
        if (e.key === "ArrowLeft") { idx = (idx + (RTL ? 1 : -1) + deck.length) % deck.length; paint(); }
      });
      paint();
    }
    $$("[data-speak]", g).forEach(function (b) { b.addEventListener("click", function () { speak(b.dataset.speak); }); });
  });

  function speak(text) {
    if (!("speechSynthesis" in window)) return;
    try {
      speechSynthesis.cancel();
      var u = new SpeechSynthesisUtterance(text); u.lang = "en-GB"; u.rate = 0.9;
      var v = speechSynthesis.getVoices().filter(function (v) { return /^en(-|_)/i.test(v.lang); });
      if (v.length) u.voice = v.filter(function (x) { return /GB/i.test(x.lang); })[0] || v[0];
      speechSynthesis.speak(u);
    } catch (e) {}
  }

  window.TW = window.TW || {}; window.TW.speak = speak;   // used by the vocabulary lab in sims.js
  renderMath(document.body);
  // labs re-read colours when the theme changes
  var themeBtn = $("[data-theme-toggle]");
  if (themeBtn) themeBtn.addEventListener("click", function () { setTimeout(function () { document.dispatchEvent(new CustomEvent("tw:theme")); }, 0); });
})();
