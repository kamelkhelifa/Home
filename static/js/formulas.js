/* Formula sheet: KaTeX rendering, live filter (accents and Arabic diacritics ignored) and printing. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var fs = $("[data-fs]");
  if (!fs) return;

  // the same macros as the course pages
  var MACROS = {
    "\\ket": "\\left|#1\\right\\rangle", "\\bra": "\\left\\langle#1\\right|", "\\braket": "\\left\\langle#1\\middle|#2\\right\\rangle",
    "\\expval": "\\left\\langle#1\\right\\rangle", "\\abs": "\\left|#1\\right|", "\\norm": "\\left\\lVert#1\\right\\rVert",
    "\\vb": "\\mathbf{#1}", "\\dv": "\\frac{\\mathrm{d}#1}{\\mathrm{d}#2}", "\\pdv": "\\frac{\\partial#1}{\\partial#2}",
    "\\dd": "\\mathrm{d}", "\\comm": "\\left[#1,#2\\right]", "\\order": "\\mathcal{O}\\left(#1\\right)"
  };
  if (window.renderMathInElement) {
    try {
      window.renderMathInElement(fs, {
        delimiters: [{ left: "\\[", right: "\\]", display: true }, { left: "\\(", right: "\\)", display: false }],
        macros: MACROS, throwOnError: false
      });
    } catch (e) { /* keep the raw LaTeX visible */ }
  }

  var input = $("[data-fs-search]");
  var norm = function (x) { return (x || "").toLowerCase().normalize("NFD").replace(/[̀-ًͯ-ْ]/g, ""); };
  input.addEventListener("input", function () {
    var q = norm(input.value.trim()), any = false;
    $$("[data-fs-block]", fs).forEach(function (blk) {
      var shown = 0;
      $$("[data-fs-item]", blk).forEach(function (it) {
        var ok = !q || norm(it.dataset.text + " " + it.textContent).indexOf(q) >= 0;
        it.hidden = !ok;
        if (ok) shown++;
      });
      blk.hidden = !shown;
      if (shown) any = true;
    });
    $("[data-fs-empty]", fs).hidden = any;
  });

  $$("[data-fs-print]").forEach(function (b) { b.addEventListener("click", function () { print(); }); });
})();
