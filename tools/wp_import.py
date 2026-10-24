#!/usr/bin/env python3
"""One-off importer: WordPress export (WXR) → cleaned HTML fragments in content/<lang>/.

Usage:  python tools/wp_import.py path/to/export.xml

Each page listed in PAGES is cleaned (inline styles, fonts and WordPress clutter removed,
headings shifted under the page title, internal links rewritten to the new site) and
written to content/<lang>/<key>.html. Uploaded files stay on their WordPress URLs.
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parent.parent
NS = {"wp": "http://wordpress.org/export/1.2/", "content": "http://purl.org/rss/1.0/modules/content/"}

# key → (wp_id, source language). Keys double as output paths.
# Course pages are not imported: each course has its own page built from data/taught/.
PAGES = {
    # Studying
    "studying/physics-manchester": (2667, "en"),
    "studying/medicine-year-1": (6308, "en"),
    "studying/medicine-year-2": (6399, "en"),
    # Resources
    "resources/event2": (158, "en"),
    "resources/feynarts": (3221, "en"),
    "resources/herwig-vbox": (176, "en"),
    "resources/herwig": (5683, "en"),
    "resources/herwig-z-jets": (5694, "en"),
    "resources/moodle": (3664, "en"),
    "resources/physicists-toolkit": (3800, "en"),
    "resources/introduction-to-mathematica": (4618, "en"),
    "resources/charity-projects": (3789, "ar"),
    "resources/local-association": (3793, "ar"),
}

BLOCK = "table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|form|map|area|blockquote|address|math|style|p|h[1-6]|hr|fieldset|legend|section|article|aside|hgroup|header|footer|nav|figure|figcaption|details|menu|summary|iframe|center"
KEEP_ATTRS = {"href", "src", "alt", "colspan", "rowspan", "id", "start", "type"}
LANG_SWITCH = {"عربي", "english", "arabic", "français", "francais", "العربية", "anglais", "en", "ar", "fr", "eng"}


def wpautop(text):
    """Simplified port of WordPress' wpautop: blank lines → paragraphs, newlines → <br>."""
    if not text.strip():
        return ""
    text = re.sub(r"<!--\s*/?wp:.*?-->", "", text)
    pres = []
    text = re.sub(r"<pre[\s\S]*?</pre>", lambda m: pres.append(m.group(0)) or f"\x00{len(pres)-1}\x00", text)
    text = text.replace("\r\n", "\n")
    text = re.sub(rf"(<(?:{BLOCK})[\s/>])", r"\n\n\1", text)
    text = re.sub(rf"(</(?:{BLOCK})>)", r"\1\n\n", text)
    text = re.sub(r"(<hr\s*/?>)", r"\1\n\n", text)
    chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
    out = []
    for c in chunks:
        if re.match(rf"</?(?:{BLOCK}|hr)[\s/>]", c) or c.startswith("\x00"):
            out.append(c)
        else:
            out.append(f"<p>{c}</p>")
    text = "\n".join(out)
    # remaining single newlines inside text become line breaks
    text = re.sub(r"(?<![>\n])\n(?![<\n])", "<br>\n", text)
    text = re.sub(r"(</(?:a|strong|b|em|i|span|sup|sub|code)>)\n(?=[^<\n])", r"\1<br>\n", text)
    text = re.sub(r"(?<=[^>\n])\n(<(?:a|strong|b|em|i|span|sup|sub|code)[\s>])", r"<br>\n\1", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: pres[int(m.group(1))], text)


def build_link_map(items):
    """Map every WordPress slug (last path segment) to its new key."""
    by_id = {wp_id: key.split("@")[0] for key, (wp_id, _) in PAGES.items()}
    slug_map = {}
    for it in items:
        pid = int(it.findtext("wp:post_id", namespaces=NS))
        slug = unquote(it.findtext("wp:post_name", namespaces=NS) or "").lower()
        if pid in by_id and slug:
            slug_map[slug] = by_id[pid]
    # Arabic/French duplicates whose content now lives on another page
    for slug, key in {
        "فيز-321-الفيزياء-الحرارية-و-الإحصائية": "teaching/phys321",
        "فيز-401-ميكانيكا-الكم-1": "teaching/phys401",
        "فيز-402-ميكانيكا-الكم-2": "teaching/phys402",
        "uef223-quantum-mechanics-1": "teaching/uef223",
        "a-physicists-toolkit": "resources/physicists-toolkit",
        "introduction-to-mathematica": "resources/introduction-to-mathematica",
    }.items():
        slug_map[slug] = key
    return slug_map


def rewrite_href(href, slug_map):
    h = href.strip()
    h = re.sub(r"^http://", "https://", h)
    m = re.match(r"https://(?:khelifak\.wordpress\.com|khelifak\.com)(/[^#?]*)?(?:\?[^#]*)?(#.*)?$", h)
    if not m:
        return h
    path, frag = (m.group(1) or "/"), (m.group(2) or "")
    if path.startswith("/wp-content/uploads/"):
        return "https://khelifak.wordpress.com" + path
    slug = unquote(path.rstrip("/").split("/")[-1]).lower()
    if slug in slug_map:
        return "@@" + slug_map[slug] + frag  # resolved to a relative URL at build time
    top = {
        "": "@@index", "research": "@@research", "studying": "@@studying", "medicine": "@@studying",
        "teaching-2": "@@teaching", "teaching": "@@teaching", "ur": "@@teaching", "iu": "@@teaching",
        "uhbc": "@@teaching", "usthb": "@@teaching", "archive": "@@teaching", "articles": "@@resources",
        "library": "@@resources", "مقالات": "@@resources", "المكتبة": "@@books",
    }
    return top.get(slug, h) + frag


def clean(html, slug_map):
    soup = BeautifulSoup(wpautop(html), "html.parser")

    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(["script", "style", "font", "center", "span", "div", "u"]):
        t.unwrap()
    for t in soup.find_all("b"):
        t.name = "strong"
    for t in soup.find_all("i"):
        t.name = "em"

    # language-switch links ("عربي" / "English") are replaced by the site's own switcher
    for a in soup.find_all("a"):
        if a.get_text(strip=True).lower() in LANG_SWITCH:
            parent = a.parent
            a.decompose()
            if parent and parent.name == "p" and not parent.get_text(strip=True):
                parent.decompose()

    for p in soup.find_all("p"):
        if p.get_text(strip=True).lower() in LANG_SWITCH:
            p.decompose()

    # WordPress "Quick links" blocks: the new layout generates its own table of contents
    for h in soup.find_all(re.compile("^h[1-6]$")):
        if re.match(r"\s*(quick links|روابط سريعة)", h.get_text(), re.I):
            sib = h.find_next_sibling()
            while sib is not None and sib.name in ("ul", "ol", "p", "br") and all(
                (a.get("href") or "").startswith("#") for a in sib.find_all("a")
            ):
                nxt = sib.find_next_sibling()
                sib.decompose()
                sib = nxt
            h.decompose()

    # attributes
    for t in soup.find_all(True):
        attrs = {k: v for k, v in t.attrs.items() if k in KEEP_ATTRS}
        if t.name == "a" and t.get("name") and not attrs.get("id"):
            attrs["id"] = t["name"]
        t.attrs = attrs
        if t.name == "a" and t.get("href"):
            t["href"] = rewrite_href(t["href"], slug_map)
            if not t["href"].startswith(("@@", "#", "mailto:")):
                t["target"] = "_blank"
                t["rel"] = "noopener"
        if t.name == "img":
            if t.get("src"):
                t["src"] = re.sub(r"^http://", "https://", t["src"])
            t["loading"] = "lazy"

    # headings sit under the page title (h1)
    for t in soup.find_all(re.compile("^h[1-6]$")):
        t.name = "h" + str(min(int(t.name[1]) + 1, 6))

    # remove empty elements (repeat to collapse nesting)
    for _ in range(3):
        for t in soup.find_all(["p", "strong", "em", "li", "h2", "h3", "h4", "h5", "h6", "a", "ul", "ol"]):
            if t.name == "a" and t.get("id"):
                continue
            if not t.get_text(strip=True).replace("\xa0", "") and not t.find(["img", "iframe", "table", "a"]):
                t.decompose()
    # strip leading/trailing <br> in blocks, collapse runs of <br>
    for br in soup.find_all("br"):
        prev = br.previous_sibling
        while isinstance(prev, NavigableString) and not prev.strip():
            prev = prev.previous_sibling
        if prev is None or getattr(prev, "name", None) == "br":
            br.decompose()

    # tables scroll horizontally on small screens
    for table in soup.find_all("table"):
        wrap = soup.new_tag("div", attrs={"class": "table-wrap"})
        table.wrap(wrap)

    out = str(soup)
    out = re.sub(r"(&nbsp;|\xa0)+", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def main(path):
    channel = ET.parse(path).getroot().find("channel")
    items = [i for i in channel.findall("item") if i.findtext("wp:post_type", namespaces=NS) in ("page", "post")]
    by_id = {int(i.findtext("wp:post_id", namespaces=NS)): i for i in items}
    slug_map = build_link_map(items)
    for key, (wp_id, lang) in PAGES.items():
        it = by_id[wp_id]
        name = key.split("@")[0]
        html = clean(it.findtext("content:encoded", namespaces=NS) or "", slug_map)
        out = ROOT / "content" / lang / f"{name}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        title = it.findtext("title").replace("&amp;", "&")
        out.write_text(f"<!-- source: {it.findtext('link')} · {title} -->\n" + html, encoding="utf-8")
        print(f"{lang}  {name:42s} {len(html):>7d}  {title}")


if __name__ == "__main__":
    main(sys.argv[1])
