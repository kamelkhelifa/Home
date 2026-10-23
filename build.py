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
LANGS = ["en", "ar"]
PREFIX = {"en": "", "ar": "ar/"}
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


# ---------------------------------------------------------------- build

def build():
    data = {n: load(n) for n in ["site", "i18n", "studying", "teaching", "research", "books", "resources"]}
    site, i18n = data["site"], data["i18n"]

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
    env.filters.update(phys=phys, authors=authors, domain=domain)

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT / "assets")
    if (ROOT / "CNAME").exists():
        shutil.copy(ROOT / "CNAME", OUT / "CNAME")
    (OUT / ".nojekyll").touch()

    def render(template, key, lang, **extra):
        current = out_path(key, lang)
        other = "ar" if lang == "en" else "en"

        def t(value):
            return pick(value, lang)

        def ui(name):
            return Markup(pick(i18n[name], lang))

        def link(target, to_lang=None):
            return relative(out_path(target, to_lang or lang), current)

        def asset(path):
            return relative(path, current)

        ctx = dict(
            data,
            page=key, section=key.split("/")[0], lang=lang, other_lang=other,
            dir="rtl" if lang == "ar" else "ltr",
            t=t, ui=ui, link=link, asset=asset,
            switch_url=link(key, other),
            canonical=f"{site['base_url'].rstrip('/')}/{current.removesuffix('index.html')}",
            alternates={lg: f"{site['base_url'].rstrip('/')}/{out_path(key, lg).removesuffix('index.html')}" for lg in LANGS},
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

    base = site["base_url"].rstrip("/")
    urls = []
    for key in [k for k in SECTIONS if k != "404"] + content_keys:
        links = "".join(
            f'<xhtml:link rel="alternate" hreflang="{lg}" href="{base}/{out_path(key, lg).removesuffix("index.html")}"/>'
            for lg in LANGS
        )
        for lang in LANGS:
            urls.append(f"  <url><loc>{base}/{out_path(key, lang).removesuffix('index.html')}</loc>{links}</url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    print(f"Built {count} pages ({len(LANGS)} languages) into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    build()
