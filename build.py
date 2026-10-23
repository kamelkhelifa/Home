#!/usr/bin/env python3
"""Static site builder for Kamel Khelifa-Kerfa's academic website.

Content lives in data/*.yml, layout in templates/, assets in static/.
Run `python build.py` to generate the site into _site/ (requires Jinja2 + PyYAML).
"""

import datetime as dt
import html
import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
PAGES = ["index", "studying", "teaching", "research", "books", "resources", "404"]


def load(name):
    with open(ROOT / "data" / f"{name}.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


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
    if host in {"sites.google.com", "youtube.com"} and path:
        return host + path.replace("/view", "")
    return host


def build():
    site = load("site")
    studying = load("studying")
    teaching = load("teaching")
    research = load("research")
    books = load("books")
    resources = load("resources")

    pubs = research["publications"]
    years = sorted({p["year"] for p in pubs}, reverse=True)
    site["stats"] = [
        {"value": sum(p["type"] == "journal" for p in pubs), "label": "Journal articles"},
        {"value": sum(p["type"] == "proceedings" for p in pubs), "label": "Proceedings"},
        {"value": len(research["talks"]), "label": "Talks & posters"},
        {"value": len(research["grants"]), "label": "Funded grants"},
        {"value": dt.date.today().year - 2013, "suffix": "+", "label": "Years teaching"},
    ]
    site["portrait"] = next(
        (f"assets/img/{p.name}" for p in (ROOT / "static/img").glob("portrait.*")), None
    )
    site["cv"] = "assets/files/CV.pdf" if (ROOT / "static/files/CV.pdf").exists() else None
    site["year"] = dt.date.today().year

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(phys=phys, authors=authors, domain=domain)

    ctx = dict(
        site=site,
        studying=studying,
        teaching=teaching,
        research=research,
        books=books,
        resources=resources,
        pub_years=years,
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT / "assets")
    for extra in ["CNAME"]:
        if (ROOT / extra).exists():
            shutil.copy(ROOT / extra, OUT / extra)
    (OUT / ".nojekyll").touch()

    for page in PAGES:
        tpl = env.get_template(f"{page}.html")
        (OUT / f"{page}.html").write_text(tpl.render(page=page, **ctx), encoding="utf-8")

    base = site["base_url"].rstrip("/")
    urls = "\n".join(
        f"  <url><loc>{base}/{'' if p == 'index' else p + '.html'}</loc></url>"
        for p in PAGES
        if p != "404"
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    print(f"Built {len(PAGES)} pages into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    build()
