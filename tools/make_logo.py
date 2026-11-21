"""Draw the site's logo: three K's for research, teaching and community.

The three K's are the circle: each stem is a third of the ring, and their arms together draw a triangle inscribed in
it; a three-jet event marks the centre and each K's story sits in its corner of the triangle: particle tracks through a lattice
ring (research), an open book and a pen (teaching), a group of people (community).

  python tools/make_logo.py                          # redraw with the cached Arabic name
  python tools/make_logo.py --arabic-font FONT.ttf   # also re-trace the Arabic name from a font

Writes templates/_logo.html (theme colours: the seal and the compact mark), static/img/favicon.svg and
static/img/logo-seal.svg (fixed colours). The seal used to carry the name in English and Arabic round the ring;
it is now the ring alone. The Arabic-name tracing below is kept for reuse (outlines cached in tools/logo_name_ar.txt).
"""
import argparse
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_AR = "كمال خليفة كرفة"
NAME_CACHE = ROOT / "tools/logo_name_ar.txt"
FIXED = {"ink": "#15171c", "maroon": "#8a1538", "gold": "#a87b2f", "paper": "#f6f3ec"}
THEME = {k: f"var(--logo-{k})" for k in FIXED}


def paint(*pairs):
    """Colour attributes: theme colours (CSS variables) share one style attribute, fixed colours are attributes."""
    styles = ";".join(f"{p}:{c}" for p, c in pairs if c.startswith("var("))
    attrs = " ".join(f'{p}="{c}"' for p, c in pairs if not c.startswith("var("))
    return " ".join(x for x in (f'style="{styles}"' if styles else "", attrs) if x)


def pt(x, y, r, deg):
    a = math.radians(deg)
    return x + r * math.cos(a), y + r * math.sin(a)


# ---------------------------------------------------------------- the three K's on a ring
# The three K's make up the circle: each stem is a 120-degree arc of the ring (with a small gap to its neighbours),
# research (maroon) at the upper left, teaching (gold) at the upper right, community (ink) at the bottom. The arms
# of the three K's are the sides of one triangle inscribed in the ring: from the middle of each arc two arms run
# along the triangle's sides and meet the neighbouring K's arms half-way. Inside the triangle, a three-jet event at
# the centre and, in each corner, that K's story.

O, RING, SPAN, GAP_DEG = (50, 50), 38, 120, 3.2     # ring radius; degrees of arc per K; the small gap between K's
ANGLES = {"research": -150, "teaching": -30, "community": 90}     # degrees, clockwise from +x (SVG y is down)
COLOURS = {"research": "maroon", "teaching": "gold", "community": "ink"}
ORDER = ("research", "teaching", "community")
ARM_GAP = 1.3                                           # gap where two neighbouring K's arms meet


def add(a, b, k=1):
    return a[0] + k * b[0], a[1] + k * b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def unit(v):
    n = math.hypot(*v)
    return v[0] / n, v[1] / n


def perp(v):
    return -v[1], v[0]


def fmt(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def bar(p, q, w, color):
    n = perp(unit(sub(q, p)))
    return f'<polygon points="{fmt([add(p, n, w / 2), add(q, n, w / 2), add(q, n, -w / 2), add(p, n, -w / 2)])}" {paint(("fill", color))}/>'


def vertex(which, sw):
    """Where a K's arms leave its stem: the middle of its arc, on the inner edge of the stroke."""
    return pt(*O, RING - sw / 2 + .3, ANGLES[which])


def k_arc(which, c, sw=4.2, aw=2.6):
    """One K whose stem is an arc of the ring: a third of the circle (minus a small gap) centred on the K's angle.
    Its two arms run from the middle of the arc along two sides of the inscribed triangle and stop just short of
    the middle of each side, where the neighbouring K's arm comes to meet them."""
    color, ang = c[COLOURS[which]], ANGLES[which]
    half = SPAN / 2 - GAP_DEG / 2
    (x0, y0), (x1, y1) = pt(*O, RING, ang - half), pt(*O, RING, ang + half)
    out = [f'<path d="M{x0:.2f} {y0:.2f}A{RING} {RING} 0 0 1 {x1:.2f} {y1:.2f}" fill="none" {paint(("stroke", color))} stroke-width="{sw}" stroke-linecap="butt"/>']
    v = vertex(which, sw)
    for other in ORDER:
        if other == which:
            continue
        meet = add(v, sub(vertex(other, sw), v), .5)          # the middle of the triangle's side
        end = add(meet, unit(sub(v, meet)), ARM_GAP / 2)
        out.append(bar(v, end, aw, color))
    return "".join(out)


def three_jets(c, r=5.5):
    """A three-jet event at the centre, one jet in each of the three colours."""
    out = []
    for k, col in enumerate(("maroon", "gold", "ink")):
        ang = -90 + 120 * k
        for half, op in ((13, .22), (4.5, 1)):
            x1, y1 = pt(*O, r, ang - half)
            x2, y2 = pt(*O, r, ang + half)
            out.append(f'<path d="M{O[0]} {O[1]}L{x1:.2f} {y1:.2f}A{r} {r} 0 0 1 {x2:.2f} {y2:.2f}Z" {paint(("fill", c[col]))} fill-opacity="{op}"/>')
    out.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="1.1" {paint(("fill", c["paper"]), ("stroke", c["ink"]))} stroke-width=".5"/>')
    return "".join(out)


def symbols(c, k=1.0, rr=23):
    """Each K's story, drawn upright in the triangle's corner between that K's arms: particle tracks through a
    lattice ring (research), an open book with a pen (teaching), a group of people (community). `k` scales the
    icons about their own centres and `rr` is how far from the centre they sit."""
    out = []
    # research: a collision vertex inside a hexagonal lattice cell, its tracks fanning out through the cell
    m = pt(*O, rr, ANGLES["research"]); d = unit(sub(m, O))
    out.append(f'<g transform="translate({m[0]:.2f} {m[1]:.2f}) scale({k}) translate({-m[0]:.2f} {-m[1]:.2f})">')
    for ang in (-28, -14, 0, 14, 28):
        a = math.radians(ang)
        dd = (d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a))
        (x1, y1), (x2, y2) = add(m, dd, .9), add(m, dd, 4.4)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {paint(("stroke", c["maroon"]))} stroke-width=".5" stroke-linecap="round" stroke-opacity=".85"/>')
    hexa = [add(m, (2.3 * math.cos(math.radians(60 * k + 30)), 2.6 * math.sin(math.radians(60 * k + 30)))) for k in range(6)]
    out.append(f'<polygon points="{fmt(hexa)}" fill="none" {paint(("stroke", c["maroon"]))} stroke-width=".6" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{m[0]:.2f}" cy="{m[1]:.2f}" r=".75" {paint(("fill", c["maroon"]))}/></g>')
    # teaching: an open book and a pen
    bx, by = pt(*O, rr, ANGLES["teaching"])
    out.append(f'<g transform="translate({bx:.2f} {by:.2f}) scale({k}) translate({-bx:.2f} {-by:.2f})">')
    out.append(f'<path d="M{bx:.2f} {by + 2.2:.2f}C{bx - 1.4:.2f} {by + 1.2:.2f} {bx - 3.2:.2f} {by + 1.2:.2f} {bx - 4.6:.2f} {by + 1.7:.2f}V{by - 1.9:.2f}'
               f'C{bx - 3.2:.2f} {by - 2.4:.2f} {bx - 1.4:.2f} {by - 2.4:.2f} {bx:.2f} {by - 1.5:.2f}Z'
               f'M{bx:.2f} {by + 2.2:.2f}C{bx + 1.4:.2f} {by + 1.2:.2f} {bx + 3.2:.2f} {by + 1.2:.2f} {bx + 4.6:.2f} {by + 1.7:.2f}V{by - 1.9:.2f}'
               f'C{bx + 3.2:.2f} {by - 2.4:.2f} {bx + 1.4:.2f} {by - 2.4:.2f} {bx:.2f} {by - 1.5:.2f}Z" fill="none" {paint(("stroke", c["gold"]))} stroke-width=".6" stroke-linejoin="round"/>')
    out.append(f'<g transform="translate({bx - .6:.2f} {by - 3.0:.2f}) rotate(-35)"><rect x="-3.2" y="-.5" width="5" height="1" rx=".3" {paint(("fill", c["gold"]))}/>'
               f'<path d="M1.8 -.5L3.5 0L1.8 .5Z" {paint(("fill", c["ink"]))}/></g></g>')
    # community: three people
    x0, y0 = pt(*O, rr, ANGLES["community"])
    out.append(f'<g transform="translate({x0:.2f} {y0:.2f}) scale({k}) translate({-x0:.2f} {-y0:.2f})">')
    ink = paint(("fill", c["ink"]))
    for dx, r, dy in ((-3, .95, .6), (0, 1.15, 0), (3, .95, .6)):
        out.append(f'<circle cx="{x0 + dx:.2f}" cy="{y0 + dy - 1.9:.2f}" r="{r}" {ink}/>'
                   f'<path d="M{x0 + dx - 1.7 * r:.2f} {y0 + dy + 1.9:.2f}C{x0 + dx - 1.7 * r:.2f} {y0 + dy - .3:.2f} {x0 + dx + 1.7 * r:.2f} {y0 + dy - .3:.2f} {x0 + dx + 1.7 * r:.2f} {y0 + dy + 1.9:.2f}Z" {ink}/>')
    out.append("</g>")
    return "".join(out)


def emblem(c, detailed=True):
    """The whole mark: the three K's whose stems make up the ring and whose arms make the triangle, the jets at the
    centre and each K's story in its corner. The compact version (seen at 40 px or so) has heavier strokes and
    slightly larger icons and jets."""
    if detailed:
        return "".join(k_arc(w, c) for w in ORDER) + three_jets(c, 7.5) + symbols(c, 1.2, 23)
    return "".join(k_arc(w, c, 5.2, 3.2) for w in ORDER) + three_jets(c, 8.5) + symbols(c, 1.35, 22.5)


# ---------------------------------------------------------------- the Arabic name, bent along the seal

def trace_arabic(font_path):
    """Shape the name with HarfBuzz and return its outlines (font units, y down, baseline at 0) and width."""
    import uharfbuzz as hb
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    font = hb.Font(hb.Face(hb.Blob.from_file_path(str(font_path))))
    buf = hb.Buffer()
    buf.add_str(NAME_AR)
    buf.guess_segment_properties()
    hb.shape(font, buf, {})
    tt = TTFont(str(font_path))
    glyphs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    rec, x = RecordingPen(), 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs[order[info.codepoint]].draw(TransformPen(rec, (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)))
        x += pos.x_advance
    lines = [f"width {x}", f"em {tt['head'].unitsPerEm}"]
    for op, args in rec.value:
        lines.append(op + " " + " ".join(f"{px:.1f},{py:.1f}" for px, py in args))
    NAME_CACHE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def arabic_on_arc(cx, cy, radius, size):
    """The cached outlines bent along the bottom of a circle: baseline on `radius`, letters upright, read right to left."""
    rows = NAME_CACHE.read_text(encoding="utf-8").split("\n")
    width, em = float(rows[0].split()[1]), float(rows[1].split()[1])
    s = size / em
    half = width * s / 2 / radius                         # half the arc the name spans, in radians

    def warp(px, py):
        theta = math.pi / 2 + half - px * s / radius      # left end of the text on the left of the bottom
        r = radius + py * s                               # glyph y is negative upwards: towards the centre
        return cx + r * math.cos(theta), cy + r * math.sin(theta)

    out, cur = [], None
    for row in rows[2:]:
        if not row:
            continue
        op, *rest = row.split(" ")
        pts = [tuple(map(float, p.split(","))) for p in rest if p]
        if op == "moveTo":
            cur = pts[0]
            out.append("M%.2f %.2f" % warp(*cur))
        elif op == "lineTo":
            (x1, y1), (x0, y0) = pts[0], cur
            for k in range(1, 5):                         # subdivide, so long strokes follow the arc
                out.append("L%.2f %.2f" % warp(x0 + (x1 - x0) * k / 4, y0 + (y1 - y0) * k / 4))
            cur = pts[0]
        elif op == "qCurveTo":                            # TrueType: implied on-curve points between off-curve ones
            offs, end = pts[:-1], pts[-1]
            for i, off in enumerate(offs):
                on = end if i == len(offs) - 1 else ((off[0] + offs[i + 1][0]) / 2, (off[1] + offs[i + 1][1]) / 2)
                out.append("Q%.2f %.2f %.2f %.2f" % (*warp(*off), *warp(*on)))
                cur = on
        elif op == "curveTo":
            out.append("C" + " ".join("%.2f %.2f" % warp(*p) for p in pts))
            cur = pts[-1]
        elif op in ("closePath", "endPath"):
            out.append("Z")
    return "".join(out)


# ---------------------------------------------------------------- assemblies

def seal(c, uid):
    """The large version used on the home page and in the footer: the ring alone, with the full detail inside."""
    return f'<g transform="translate(50 50) scale(1.2) translate(-50 -50)">{emblem(c)}</g>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arabic-font", help="re-trace the Arabic name from this font (Khalid Art Bold)")
    if (font := ap.parse_args().arabic_font):
        trace_arabic(font)
    macros = f'''{{# Generated by tools/make_logo.py: edit that script, not this file. #}}
{{% macro mark(cls="brand-mark") -%}}
<svg class="logo {{{{ cls }}}}" viewBox="0 0 100 100" aria-hidden="true" focusable="false"><g transform="translate(50 50) scale(1.18) translate(-50 -50)">{emblem(THEME, detailed=False)}</g></svg>
{{%- endmacro %}}

{{% macro seal(cls="brand-seal", uid="seal") -%}}
<svg class="logo {{{{ cls }}}}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">{seal(THEME, "{{{{ uid }}}}")}</svg>
{{%- endmacro %}}
'''
    (ROOT / "templates/_logo.html").write_text(macros.replace("{{{{ uid }}}}", "{{ uid }}"), encoding="utf-8")
    (ROOT / "static/img/favicon.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{FIXED["paper"]}"/>'
        f'<g transform="translate(50 50) scale(1.18) translate(-50 -50)">{emblem(FIXED, detailed=False)}</g></svg>\n', encoding="utf-8")
    (ROOT / "static/img/logo-seal.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{seal(FIXED, "seal")}</svg>\n', encoding="utf-8")
    print("wrote templates/_logo.html, static/img/favicon.svg and static/img/logo-seal.svg")


if __name__ == "__main__":
    main()
