#!/usr/bin/env python3
"""Static site builder for Kamel Khelifa-Kerfa's bilingual (English / Arabic) website.

Content:   data/*.yml        structured content, with { en: …, ar: … } for translated text
           content/<lang>/   full pages (course pages, notes, guides, articles) as HTML fragments
Layout:    templates/        Jinja2 templates
Assets:    static/           copied to _site/assets/

English pages are written to _site/, Arabic pages to _site/ar/. All links are relative, so
the site works both on a custom domain and under a GitHub Pages project path.
Run `python build.py` (requires Jinja2, PyYAML and BeautifulSoup).
"""

import datetime as dt
import html
import posixpath
import re
import shutil
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
LANGS = ["en", "ar"]                       # every page; French exists only for courses taught in Algeria
PREFIX = {"en": "", "ar": "ar/", "fr": "fr/"}
LANG_NAMES = {"en": "English", "ar": "العربية", "fr": "Français"}
SECTIONS = ["index", "studying", "teaching", "research", "books", "resources", "404"]

# Pages whose original is Arabic, or that exist as two independent originals.
ARABIC_ORIGINALS = {"teaching/uef223", "teaching/chlef-vibrations-ar", "resources/charity-projects", "resources/local-association"}
BOTH_ORIGINALS = {"teaching/uef131", "teaching/uem123"}


def load(name):
    with open(ROOT / "data" / f"{name}.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pick(value, lang):
    """Return the `lang` variant of a { en: …, ar: … } value; plain values pass through."""
    if isinstance(value, dict) and ("en" in value or "ar" in value):
        return value.get(lang, value.get("en"))
    return value


# Typeset common physics notation in plain-text titles (escapes first, so it is safe).
PHYS_RULES = [
    (r"\bkt\b", "k<sub>t</sub>"),
    (r"\bNc\b", "N<sub>c</sub>"),
    (r"\bpT\b", "p<sub>T</sub>"),
    (r"e\+e−", "e<sup>+</sup>e<sup>−</sup>"),
    (r"\bpp to WW\b", "pp → WW"),
]


def phys(text):
    out = html.escape(str(text), quote=False)
    for pattern, repl in PHYS_RULES:
        out = re.sub(pattern, repl, out)
    return Markup(out)


def authors(text, me="K. Khelifa-Kerfa"):
    out = html.escape(str(text), quote=False)
    return Markup(out.replace(me, f'<strong class="me">{me}</strong>'))


def domain(url):
    m = re.match(r"https?://(?:www\.)?([^/]+)(/[^?#]*)?", url or "")
    if not m:
        return ""
    host, path = m.group(1), (m.group(2) or "").rstrip("/")
    if host in {"sites.google.com", "youtube.com", "t.me", "twitter.com"} and path:
        return host + path.replace("/view", "")
    return host


def out_path(key, lang):
    """Site-relative output path of a page key ('index', 'teaching', 'teaching/phys321')."""
    return f"{PREFIX[lang]}{key}.html"


def relative(target, current):
    """Relative URL from the page at `current` to the site path `target`."""
    rel = posixpath.relpath(target, posixpath.dirname(current) or ".")
    return rel


# ---------------------------------------------------------------- courses taught (data/taught/)

LINEBREAK_SPACING = re.compile(r"\\\\\[\s*-?[\d.]+\s*(?:mm|cm|pt|em|ex)\s*\]")
MATH = re.compile(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", re.S)
ARABIC = re.compile(r"[\u0600-\u06FF]")
BLOCK_TAG = re.compile(r"^\s*<(p|ul|ol|div|table|pre|h\d|blockquote|figure)\b", re.I)
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"]
EDITOR_ONLY = ("pending", "notes", "sources")   # never published (see COURSE_FORMAT.md)


def tidy(v):
    """Clean course text for KaTeX: drop `\\\\[2mm]` spacing and escape < > inside maths."""
    if isinstance(v, str):
        v = LINEBREAK_SPACING.sub(r"\\\\ ", v)
        return MATH.sub(lambda m: m.group(0).replace("<", "&lt;").replace(">", "&gt;"), v)
    if isinstance(v, dict):
        return {k: tidy(x) for k, x in v.items()}
    if isinstance(v, list):
        return [tidy(x) for x in v]
    return v


def paragraphs(text):
    """Blank-line separated text → <p> paragraphs (HTML blocks are left alone)."""
    if text is None:
        return Markup("")
    out = []
    for block in re.split(r"\n\s*\n", str(text).strip()):
        block = block.strip()
        if block:
            out.append(block if BLOCK_TAG.match(block) else f"<p>{' '.join(l.strip() for l in block.splitlines())}</p>")
    return Markup("\n".join(out))


def ltr(s):
    """Keep numeric ranges such as 2019–2020 in reading order inside Arabic text."""
    s = str(s or "")
    return Markup(html.escape(s)) if ARABIC.search(s) else Markup(f'<bdi dir="ltr">{html.escape(s)}</bdi>')


def pct(w):
    return int(w) if float(w).is_integer() else w


def load_courses():
    """Universities (display order) with their courses, ready for the templates."""
    companions = load("companions")
    # Safety net: a file held back (`pending:`) in any course is never published, in any course.
    withheld = set()
    for f in (ROOT / "data" / "taught").glob("*/*.yml"):
        with open(f, encoding="utf-8") as fh:
            withheld |= {p.get("url") for p in (yaml.safe_load(fh).get("pending") or []) if p.get("url")}
    unis = []
    for u in load("universities"):
        u["langs"] = LANGS + (["fr"] if u.get("french") else [])
        courses = []
        for f in sorted((ROOT / "data" / "taught" / u["id"]).glob("*.yml")):
            with open(f, encoding="utf-8") as fh:
                c = tidy(yaml.safe_load(fh))
            for k in EDITOR_ONLY:
                c.pop(k, None)
            comp = companions.get(c.get("companion")) or {}
            c.setdefault("sims", list(comp.get("sims") or []))
            c.setdefault("glossary", comp.get("glossary") or [])
            c["materials"] = [m for m in c.get("materials") or [] if m.get("url") not in withheld]
            c["exams"] = [e for e in c.get("exams") or [] if not ({e.get("paper"), e.get("solution")} & withheld)]
            c.setdefault("taught", [])
            c["n_materials"] = len(c["materials"]) + len(c["exams"])
            h = c.get("hours") or {}
            total = sum(h.get(k, 0) or 0 for k in ("lecture", "tutorial", "lab"))
            c["contact_hours"] = pct(total) if total else 0
            weights = [a.get("weight") for a in c.get("assessment") or []]
            c["weights_ok"] = bool(weights) and all(isinstance(w, (int, float)) for w in weights) and abs(sum(weights) - 100) < 1e-6
            for i, w in enumerate(c.get("schedule") or []):
                if w.get("week") in (None, ""):          # a chapter plan without weeks: number it I, II, III…
                    w["week"] = ROMAN[i] if i < len(ROMAN) else str(i + 1)
                w["wid"] = re.sub(r"[^\w-]", "", str(w["week"]).replace("–", "-")) or str(i + 1)
                w["numeric"] = str(w["week"])[:1].isdigit()
            c["prerequisites_text"] = c.pop("prerequisites", None)
            c["uni"] = u
            c["key"] = f"{u['id']}/{c['slug']}"
            c["page"] = f"teaching/{u['id']}/{c['slug']}"
            courses.append(c)
        courses.sort(key=lambda c: (c.get("order", 999), c["slug"]))
        u["courses"] = courses
        unis.append(u)
    return unis


# ---------------------------------------------------------------- content pages

def collect_page_meta(studying, teaching, resources):
    """Titles, breadcrumbs and chips for every page in content/, gathered from the data files."""
    meta = {}
    for track in studying["tracks"]:
        for p in track.get("pages", []):
            meta[p["page"]] = {"title": p["title"], "section": "studying", "parent": track["title"], "chips": [track["place"]]}
    for uni in teaching["archive"]:
        for c in uni["courses"]:
            if c.get("page"):
                chips = [uni["short"]]
                if c.get("year"):
                    chips.append(c["year"])
                if c.get("taught_in"):
                    chips.append({"i18n": f"taught_in_{c['taught_in']}"})
                meta[c["page"]] = {"title": c["title"], "code": c.get("code"), "section": "teaching", "parent": uni["institution"], "chips": chips}
    for group in resources["groups"]:
        for it in group["items"]:
            if it.get("page"):
                meta[it["page"]] = {"title": it["label"], "section": "resources", "parent": group["title"], "chips": [it.get("kind")] if it.get("kind") else []}
    return meta


def original_language(key):
    if (ROOT / "content" / "fr" / f"{key}.html").exists():
        return "fr"
    if key in BOTH_ORIGINALS:
        return None
    return "ar" if key in ARABIC_ORIGINALS else "en"


LANG_SWITCH_WORDS = {"english", "عربي", "français", "francais", "en", "ar", "fr"}


def render_fragment(key, lang, current):
    """Load a content fragment, resolve @@links, build a table of contents."""
    raw = (ROOT / "content" / lang / f"{key}.html").read_text(encoding="utf-8")
    raw = re.sub(r"^<!--.*?-->\s*", "", raw, flags=re.S)
    soup = BeautifulSoup(raw, "html.parser")

    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h.startswith("@@"):
            target, _, frag = h[2:].partition("#")
            a["href"] = relative(out_path(target, lang), current) + (f"#{frag}" if frag else "")
    # leftover "English عربي" switch paragraphs from WordPress
    for p in soup.find_all("p"):
        words = p.get_text(" ", strip=True).lower().split()
        if words and all(w in LANG_SWITCH_WORDS for w in words):
            p.decompose()

    seen, toc = set(), []
    for el in soup.find_all(id=True):
        if el["id"] in seen:
            del el["id"]
        else:
            seen.add(el["id"])
    for i, h in enumerate(soup.find_all("h2"), 1):
        if not h.get("id"):
            h["id"] = f"s{i}"
            while h["id"] in seen:
                h["id"] += "-"
            seen.add(h["id"])
        toc.append({"id": h["id"], "text": h.get_text(" ", strip=True)})
    for table in soup.find_all("table"):
        if table.find("th") is None:
            first = table.find("tr")
            if first and len(first.find_all("td")) > 1 and all(td.find(["strong"]) for td in first.find_all("td") if td.get_text(strip=True)):
                for td in first.find_all("td"):
                    td.name = "th"
    for img in soup.find_all("img"):
        img["loading"] = "lazy"
        img["decoding"] = "async"
    return Markup(str(soup)), toc


# ---------------------------------------------------------------- formula sheet (data/formulas.yml)

FORMULAS_PAGE = "resources/formulas"


def load_formulas():
    f = load("formulas")
    for sec in f["sections"]:
        for it in sec["items"]:
            # stack the formulas of one item (separated by \qquad) on separate lines, so they fit two printed columns;
            # long lines are also split at ",\quad"
            parts = []
            for p in re.split(r"\\qquad", it["tex"]):
                parts += re.split(r",\s*\\quad\s*", p) if len(p) > 90 else [p]
            parts = [x.strip().rstrip(",") for x in parts if x.strip()]
            it["tex"] = parts[0] if len(parts) == 1 else "\\begin{aligned}&" + " \\\\ &".join(parts) + "\\end{aligned}"
    return f


# ---------------------------------------------------------------- build

def build():
    data = {n: load(n) for n in ["site", "i18n", "studying", "teaching", "research", "books", "resources"]}
    site, i18n = data["site"], data["i18n"]
    course_ui = load("course_ui")
    formulas = load_formulas()
    unis = load_courses()
    courses = {c["page"]: c for u in unis for c in u["courses"]}
    page_langs = {c["page"]: c["uni"]["langs"] for c in courses.values()}
    for uni in data["teaching"]["archive"] + [{"courses": data["teaching"]["current"]["courses"]}]:
        for item in uni["courses"]:
            if item.get("course") and f"teaching/{item['course']}" not in courses:
                raise SystemExit(f"data/teaching.yml links to a course that does not exist: {item['course']}")

    pubs = data["research"]["publications"]
    years = sorted({p["year"] for p in pubs}, reverse=True)
    stats = [
        {"value": sum(p["type"] == "journal" for p in pubs), "label": {"en": "Journal articles", "ar": "مقالات محكّمة"}},
        {"value": sum(p["type"] == "proceedings" for p in pubs), "label": {"en": "Proceedings", "ar": "أعمال مؤتمرات"}},
        {"value": len(data["research"]["talks"]), "label": {"en": "Talks & posters", "ar": "مداخلات وملصقات"}},
        {"value": len(data["research"]["grants"]), "label": {"en": "Funded grants", "ar": "مشاريع ممولة"}},
        {"value": dt.date.today().year - 2013, "suffix": "+", "label": {"en": "Years teaching", "ar": "سنة في التدريس"}},
    ]
    portrait = next((f"assets/img/{p.name}" for p in (ROOT / "static/img").glob("portrait.*")), None)
    cv = "assets/files/CV.pdf" if (ROOT / "static/files/CV.pdf").exists() else None
    page_meta = collect_page_meta(data["studying"], data["teaching"], data["resources"])
    content_keys = sorted(p.relative_to(ROOT / "content/en").with_suffix("").as_posix() for p in (ROOT / "content/en").rglob("*.html"))
    missing = [k for k in content_keys if k not in page_meta]
    if missing:
        raise SystemExit(f"Pages without an entry in the data files: {missing}")

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(phys=phys, authors=authors, domain=domain, para=paragraphs, ltr=ltr, pct=pct)

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT / "assets")
    if (ROOT / "CNAME").exists():
        shutil.copy(ROOT / "CNAME", OUT / "CNAME")
    (OUT / ".nojekyll").touch()

    def render(template, key, lang, langs=LANGS, **extra):
        current = out_path(key, lang)
        other = "ar" if lang == "en" else "en"

        def t(value):
            return pick(value, lang)

        def ui(name):
            return Markup(pick(i18n[name], lang))

        def link(target, to_lang=None):
            to_lang = to_lang or lang
            if to_lang not in page_langs.get(target, LANGS):   # French exists only for some course pages
                to_lang = "en"
            return relative(out_path(target, to_lang), current)

        def cui(name):
            return pick(course_ui["ui"][name], lang)

        def cui_has(name):
            return name in course_ui["ui"]

        def asset(path):
            return relative(path, current)

        ctx = dict(
            data,
            page=key, section=key.split("/")[0], lang=lang, other_lang=other,
            dir="rtl" if lang == "ar" else "ltr",
            t=t, ui=ui, link=link, asset=asset, cui=cui, cui_has=cui_has,
            labels=course_ui, unis=unis, page_langs_all=langs,
            switch_url=link(key, other),
            switches=[{"lang": lg, "name": LANG_NAMES[lg], "url": relative(out_path(key, lg), current)} for lg in langs if lg != lang],
            canonical=f"{site['base_url'].rstrip('/')}/{current.removesuffix('index.html')}",
            alternates={lg: f"{site['base_url'].rstrip('/')}/{out_path(key, lg).removesuffix('index.html')}" for lg in langs},
            stats=stats, pub_years=years, portrait=portrait, cv=cv, year=dt.date.today().year,
            **extra,
        )
        html_out = env.get_template(template).render(**ctx)
        dest = OUT / current
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")

    count = 0
    for lang in LANGS:
        for key in SECTIONS:
            render(f"{key}.html", key, lang)
            count += 1
        for key in content_keys:
            body, toc = render_fragment(key, lang, out_path(key, lang))
            orig = original_language(key)
            render("doc.html", key, lang, doc=page_meta[key], body=body, toc=toc,
                   translated_from=orig if orig and orig != lang else None)
            count += 1
        render("formulas.html", FORMULAS_PAGE, lang, formulas=formulas)
        count += 1
    for key, c in courses.items():
        for lang in c["uni"]["langs"]:
            render("course.html", key, lang, langs=c["uni"]["langs"], c=c)
            count += 1

    base = site["base_url"].rstrip("/")
    urls = []
    for key in [k for k in SECTIONS if k != "404"] + content_keys + [FORMULAS_PAGE] + list(courses):
        langs = page_langs.get(key, LANGS)
        links = "".join(
            f'<xhtml:link rel="alternate" hreflang="{lg}" href="{base}/{out_path(key, lg).removesuffix("index.html")}"/>'
            for lg in langs
        )
        for lang in langs:
            urls.append(f"  <url><loc>{base}/{out_path(key, lang).removesuffix('index.html')}</loc>{links}</url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8",
    )
    if site.get("launched"):
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    else:  # pre-launch: pages carry a noindex tag; robots.txt itself only counts on a custom domain
        (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    print(f"Built {count} pages ({len(courses)} course pages, French for Algerian courses) into {OUT.relative_to(ROOT)}/"
          + ("" if site.get("launched") else "  [pre-launch: hidden from search engines]"))


if __name__ == "__main__":
    build()
