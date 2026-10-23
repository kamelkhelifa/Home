/* Kamel Khelifa-Kerfa — site interactions (no dependencies) */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Theme ---------- */
  var themeBtn = document.querySelector("[data-theme-toggle]");
  function currentTheme() {
    if (root.dataset.theme) return root.dataset.theme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
      document.dispatchEvent(new CustomEvent("themechange"));
    });
  }

  /* ---------- Header & mobile menu ---------- */
  var header = document.querySelector("[data-header]");
  function onScroll() { header && header.classList.toggle("is-scrolled", window.scrollY > 12); }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  var menuBtn = document.querySelector("[data-menu-toggle]");
  function setMenu(open) {
    document.body.classList.toggle("menu-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? menuBtn.dataset.labelClose : menuBtn.dataset.labelOpen);
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () { setMenu(!document.body.classList.contains("menu-open")); });
    document.querySelectorAll("[data-nav] a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  /* ---------- Reveal on scroll ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Count-up stats ---------- */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length && "IntersectionObserver" in window && !reduceMotion) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, target = parseInt(el.dataset.count, 10), t0 = null;
        if (isNaN(target)) return;
        co.unobserve(el);
        (function step(ts) {
          if (!t0) t0 = ts;
          var p = Math.min((ts - t0) / 1400, 1);
          el.textContent = Math.round(target * (1 - Math.pow(1 - p, 4)));
          if (p < 1) requestAnimationFrame(step);
        })(performance.now());
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { el.textContent = "0"; co.observe(el); });
  }

  /* ---------- Tabs (teaching archive) ---------- */
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = tabs.length, j = null;
        if (k === "ArrowRight" || k === "ArrowDown") j = (i + 1) % n;
        if (k === "ArrowLeft" || k === "ArrowUp") j = (i - 1 + n) % n;
        if (k === "Home") j = 0;
        if (k === "End") j = n - 1;
        if (j !== null) { e.preventDefault(); select(tabs[j], true); }
      });
    });
    var initial = tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0] || tabs[0];
    if (initial) select(initial);
  });

  /* ---------- Publication search & filters ---------- */
  var pubBox = document.querySelector("[data-pubs]");
  if (pubBox) {
    var controls = document.querySelector("[data-pub-controls]");
    var search = document.querySelector("[data-pub-search]");
    var countEl = document.querySelector("[data-pub-count]");
    var empty = document.querySelector("[data-pub-empty]");
    var filterBtns = document.querySelectorAll("[data-filter]");
    var pubs = Array.prototype.slice.call(pubBox.querySelectorAll(".pub"));
    var groups = pubBox.querySelectorAll("[data-year-group]");
    var filter = "all";
    controls.hidden = false;

    function apply() {
      var q = (search.value || "").trim().toLowerCase();
      var shown = 0;
      pubs.forEach(function (li) {
        var okFilter = filter === "all" ||
          (filter === "proceedings" ? li.dataset.type === "proceedings" : li.dataset.area === filter);
        var ok = okFilter && (!q || li.textContent.toLowerCase().indexOf(q) !== -1);
        li.hidden = !ok;
        if (ok) shown++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector(".pub:not([hidden])"); });
      countEl.textContent = shown + " " + countEl.dataset.of + " " + pubs.length + " " + countEl.dataset.items;
      empty.hidden = shown !== 0;
    }
    filterBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        filter = b.dataset.filter;
        filterBtns.forEach(function (x) { x.classList.toggle("is-on", x === b); x.setAttribute("aria-pressed", String(x === b)); });
        apply();
      });
    });
    search.addEventListener("input", apply);
    apply();
  }

  /* ---------- Table of contents: highlight the current section ---------- */
  var tocLinks = document.querySelectorAll("[data-toc] a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[decodeURIComponent(a.getAttribute("href").slice(1))] = a; });
    var heads = Object.keys(byId).map(function (id) { return document.getElementById(id); }).filter(Boolean);
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.remove("is-active"); });
        var a = byId[en.target.id];
        if (a) a.classList.add("is-active");
      });
    }, { rootMargin: "-15% 0px -70% 0px" });
    heads.forEach(function (h) { spy.observe(h); });
  }

  /* ---------- Hero: animated collider event display ---------- */
  var canvas = document.querySelector("[data-event-display]");
  if (canvas && canvas.getContext) eventDisplay(canvas);

  function eventDisplay(cv) {
    var ctx = cv.getContext("2d");
    var W, H, dpr, cx, cy, R, colors, ev, t0, raf, visible = true;
    var TAU = Math.PI * 2;

    function readColors() {
      var cs = getComputedStyle(root);
      colors = {
        line: cs.getPropertyValue("--canvas-line").trim(),
        a: cs.getPropertyValue("--canvas-track-a").trim(),
        b: cs.getPropertyValue("--canvas-track-b").trim(),
        soft: cs.getPropertyValue("--canvas-soft").trim()
      };
    }
    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (W > 980) { cx = W * 0.73; cy = H * 0.5; R = Math.min(W * 0.27, H * 0.4); }
      else { cx = W * 0.86; cy = H * 0.16; R = Math.max(W * 0.55, 220); }
      if (root.dir === "rtl") cx = W - cx;
    }
    function gauss() { return (Math.random() + Math.random() + Math.random() - 1.5) / 1.5; }

    function makeEvent() {
      var axis = Math.random() * TAU;
      var jets = [
        { phi: axis, e: 0.8 + Math.random() * 0.2 },
        { phi: axis + Math.PI + gauss() * 0.25, e: 0.6 + Math.random() * 0.3 }
      ];
      if (Math.random() < 0.55) jets.push({ phi: axis + Math.PI / 2 + gauss() * 0.9, e: 0.25 + Math.random() * 0.2 });
      var tracks = [], towers = [];
      jets.forEach(function (j, ji) {
        var n = Math.round(9 + j.e * 12);
        for (var i = 0; i < n; i++) {
          var phi = j.phi + gauss() * (0.09 + 0.12 * (1 - j.e));
          var pt = 0.25 + Math.random() * j.e;
          tracks.push({ phi: phi, k: (Math.random() < 0.5 ? -1 : 1) * (0.25 / (pt * R)), len: 1, hard: true, col: ji % 2 ? "b" : "a", w: 0.6 + pt * 1.2 });
        }
        for (var c = 0; c < 7; c++) {
          towers.push({ phi: j.phi + gauss() * 0.14, e: j.e * (0.35 + Math.random() * 0.65), layer: Math.random() < 0.55 ? 0 : 1 });
        }
      });
      for (var s = 0; s < 26; s++) {
        var sp = 0.08 + Math.random() * 0.18;
        tracks.push({ phi: Math.random() * TAU, k: (Math.random() < 0.5 ? -1 : 1) * (0.25 / (sp * R)), len: 0.35 + Math.random() * 0.65, hard: false, col: "soft", w: 0.6 });
      }
      for (var u = 0; u < 14; u++) towers.push({ phi: Math.random() * TAU, e: 0.05 + Math.random() * 0.12, layer: Math.random() < 0.6 ? 0 : 1 });
      return { tracks: tracks, towers: towers, jets: jets };
    }

    function drawDetector() {
      ctx.strokeStyle = colors.line; ctx.lineWidth = 1;
      [0.07, 0.14, 0.22, 0.3, 0.38, 0.46, 0.54].forEach(function (f, i) {
        ctx.setLineDash(i % 2 ? [2, 5] : []);
        ctx.beginPath(); ctx.arc(cx, cy, R * f, 0, TAU); ctx.stroke();
      });
      ctx.setLineDash([]);
      [[0.6, 0.72], [0.76, 0.92]].forEach(function (band) {
        ctx.beginPath(); ctx.arc(cx, cy, R * band[0], 0, TAU); ctx.stroke();
        ctx.beginPath(); ctx.arc(cx, cy, R * band[1], 0, TAU); ctx.stroke();
        for (var i = 0; i < 72; i++) {
          var a = (i / 72) * TAU;
          ctx.beginPath();
          ctx.moveTo(cx + Math.cos(a) * R * band[0], cy + Math.sin(a) * R * band[0]);
          ctx.lineTo(cx + Math.cos(a) * R * band[1], cy + Math.sin(a) * R * band[1]);
          ctx.stroke();
        }
      });
      // muon chambers: octagon
      ctx.beginPath();
      for (var k = 0; k <= 8; k++) {
        var b = (k / 8) * TAU + Math.PI / 8, r = R * 1.02;
        ctx[k ? "lineTo" : "moveTo"](cx + Math.cos(b) * r, cy + Math.sin(b) * r);
      }
      ctx.stroke();
    }

    function drawTrack(tr, frac, alpha) {
      var rMax = R * 0.56 * tr.len, steps = 40, phi = tr.phi, k = tr.k;
      var sMax = rMax * 1.25 * frac;
      var rgb = colors[tr.col];
      ctx.strokeStyle = "rgba(" + rgb + "," + (alpha * (tr.hard ? 0.85 : 0.35)) + ")";
      ctx.lineWidth = tr.w;
      ctx.beginPath(); ctx.moveTo(cx, cy);
      for (var i = 1; i <= steps; i++) {
        var s = (i / steps) * sMax;
        var x = (Math.sin(phi + k * s) - Math.sin(phi)) / k;
        var y = -(Math.cos(phi + k * s) - Math.cos(phi)) / k;
        if (x * x + y * y > rMax * rMax) break;
        ctx.lineTo(cx + x, cy + y);
      }
      ctx.stroke();
    }

    function drawTower(tw, frac, alpha) {
      var band = tw.layer ? [0.76, 0.92] : [0.6, 0.72];
      var r0 = R * band[0], len = R * (band[1] - band[0]) * (0.25 + 0.75 * tw.e) * frac;
      var half = 0.034;
      ctx.fillStyle = "rgba(" + (tw.layer ? colors.a : colors.b) + "," + alpha * (0.25 + tw.e * 0.6) + ")";
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(tw.phi - half) * r0, cy + Math.sin(tw.phi - half) * r0);
      ctx.lineTo(cx + Math.cos(tw.phi - half) * (r0 + len), cy + Math.sin(tw.phi - half) * (r0 + len));
      ctx.lineTo(cx + Math.cos(tw.phi + half) * (r0 + len), cy + Math.sin(tw.phi + half) * (r0 + len));
      ctx.lineTo(cx + Math.cos(tw.phi + half) * r0, cy + Math.sin(tw.phi + half) * r0);
      ctx.closePath(); ctx.fill();
    }

    function drawJetCones(alpha) {
      ev.jets.forEach(function (j, ji) {
        var g = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 0.95);
        var rgb = ji % 2 ? colors.b : colors.a;
        g.addColorStop(0, "rgba(" + rgb + ",0)");
        g.addColorStop(1, "rgba(" + rgb + "," + 0.07 * alpha * j.e + ")");
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, R * 0.95, j.phi - 0.32, j.phi + 0.32); ctx.closePath(); ctx.fill();
      });
    }

    function ease(x) { return 1 - Math.pow(1 - Math.min(Math.max(x, 0), 1), 3); }

    function frame(ts) {
      if (!t0) t0 = ts;
      var t = (ts - t0) / 1000;
      var CYCLE = 6.2;
      if (t > CYCLE) { ev = makeEvent(); t0 = ts; t = 0; }
      render(t);
      raf = visible ? requestAnimationFrame(frame) : null;
    }

    function render(t) {
      ctx.clearRect(0, 0, W, H);
      drawDetector();
      var fadeOut = t === null ? 1 : 1 - ease((t - 5.0) / 1.1);
      var trackFrac = t === null ? 1 : ease(t / 1.2);
      var towerFrac = t === null ? 1 : ease((t - 0.8) / 0.8);
      drawJetCones(fadeOut * towerFrac);
      ev.tracks.forEach(function (tr) { drawTrack(tr, trackFrac, fadeOut); });
      ev.towers.forEach(function (tw) { drawTower(tw, towerFrac, fadeOut); });
      // interaction vertex flash
      var flash = t === null ? 0.5 : Math.max(0.35, 1 - t * 1.5);
      ctx.fillStyle = "rgba(" + colors.a + "," + flash * fadeOut + ")";
      ctx.beginPath(); ctx.arc(cx, cy, 3, 0, TAU); ctx.fill();
    }

    readColors(); resize(); ev = makeEvent();
    window.addEventListener("resize", function () { resize(); if (reduceMotion) render(null); });
    document.addEventListener("themechange", function () { readColors(); if (reduceMotion) render(null); });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () { readColors(); });

    if (reduceMotion) { render(null); return; }

    function start() { if (!raf && visible) raf = requestAnimationFrame(frame); }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { visible = en[0].isIntersecting && !document.hidden; start(); }).observe(cv);
    }
    document.addEventListener("visibilitychange", function () { visible = !document.hidden; if (visible) { t0 = null; start(); } });
    start();
  }
})();
