/* Visitors page: visit counts from GoatCounter's public counter, by section, course and language.
   Each path is asked for once; paths nobody has visited yet answer 404 and count as 0. */
(function () {
  "use strict";
  var page = document.querySelector("[data-visits-page]");
  if (!page || !page.dataset.endpoint) return;
  var data = JSON.parse(page.querySelector("[data-visit-paths]").textContent);
  var AR = page.dataset.lang === "ar";
  var fmt = new Intl.NumberFormat("en");
  var cache = {};

  function count(path) {
    if (!cache[path]) {
      cache[path] = fetch(page.dataset.endpoint + encodeURIComponent(path) + ".json")
        .then(function (r) { return r.status === 404 ? { count: "0" } : (r.ok ? r.json() : Promise.reject(r.status)); })
        .then(function (j) { return parseInt(String(j.count).replace(/[^0-9]/g, ""), 10) || 0; });
    }
    return cache[path];
  }
  function sum(paths) {
    // a few requests at a time, to be gentle with the counter
    var i = 0, total = 0;
    function next() {
      if (i >= paths.length) return Promise.resolve(total);
      var batch = paths.slice(i, i += 6);
      return Promise.all(batch.map(count)).then(function (ns) { ns.forEach(function (n) { total += n; }); return next(); });
    }
    return next();
  }
  function countUp(el, n) {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || n < 20) { el.textContent = fmt.format(n); return; }
    var t0 = performance.now(), dur = 1100;
    (function step(t) {
      var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt.format(Math.round(n * e));
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }

  function bars(kind, rows, total, limit) {
    var list = page.querySelector('[data-bars="' + kind + '"]');
    rows = rows.filter(function (r) { return r.n > 0; }).sort(function (a, b) { return b.n - a.n; }).slice(0, limit);
    var max = rows.length ? rows[0].n : 1;
    list.innerHTML = "";
    rows.forEach(function (r) {
      var li = document.createElement("li");
      var share = total ? Math.round(100 * r.n / total) : 0;
      li.className = "vbar";
      li.tabIndex = 0;
      li.innerHTML = '<span class="vbar-name"></span><span class="vbar-sub"></span>' +
        '<span class="vbar-track"><span class="vbar-fill"></span></span><span class="vbar-val"></span>' +
        '<span class="vbar-tip" role="tooltip"></span>';
      li.querySelector(".vbar-name").textContent = r.label;
      li.querySelector(".vbar-sub").textContent = r.sub || "";
      li.querySelector(".vbar-val").textContent = fmt.format(r.n);
      li.querySelector(".vbar-tip").textContent = fmt.format(r.n) + " · " + share + "% " + page.dataset.share;
      li.querySelector(".vbar-fill").style.width = Math.max(1.5, 100 * r.n / max) + "%";
      list.appendChild(li);
    });
    list.closest(".visits-card").hidden = !rows.length;
  }

  page.dataset.share = page.dataset.shareLabel || "";
  count("TOTAL").then(function (total) {
    countUp(page.querySelector("[data-total]"), total);
    return Promise.all([
      Promise.all(data.sections.map(function (s) { return sum(s.paths).then(function (n) { return { label: s.label[AR ? "ar" : "en"] || s.label.en, n: n }; }); })),
      Promise.all(data.courses.map(function (c) { return sum(c.paths).then(function (n) { return { label: AR ? c.label_ar : c.label, sub: AR ? c.uni_ar : c.uni, n: n }; }); })),
      Promise.all(Object.keys(data.langs).map(function (lg) { return sum(data.langs[lg]).then(function (n) { return [lg, n]; }); }))
    ]).then(function (res) {
      var tracked = res[0].reduce(function (a, r) { return a + r.n; }, 0) || total;
      bars("sections", res[0], tracked, 10);
      bars("courses", res[1], tracked, 10);
      res[2].forEach(function (p) { var dd = page.querySelector('[data-lang-total="' + p[0] + '"]'); if (dd) dd.textContent = fmt.format(p[1]); });
    });
  }).catch(function () {
    page.querySelector("[data-visits-error]").hidden = false;
    page.querySelector("[data-total]").textContent = "—";
  });
})();
