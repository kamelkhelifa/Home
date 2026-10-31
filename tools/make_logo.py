"""Draw the site's logo: three K's for research, teaching and community.

Research: a QCD jet, a gluon (theory), a lattice ending in a hexagonal ring (materials) and a mesh of points
(computation). Teaching: a digital pen and a circuit trace. Community: a voice carrying outward and people
linked arm in arm. The K's sit at the corners of a triangle.

  python tools/make_logo.py                          # redraw with the cached Arabic name
  python tools/make_logo.py --arabic-font FONT.ttf   # also re-trace the Arabic name from a font

Writes templates/_logo.html (theme colours: the seal and the compact mark), static/img/favicon.svg and
static/img/logo-seal.svg (fixed colours). The Arabic name is set in Khalid Art Bold; its outlines are cached in
tools/logo_name_ar.txt, so the font file itself is never needed by the site or published.
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


# ---------------------------------------------------------------- the three K's (each in a 36 x 44 box)

VX, VY, UP, DN = 6.2, 23, -50, 46     # the point where the arms meet, and the arms' directions


def stem(c):
    ink = paint(("fill", c["ink"]))
    return (f'<rect x="2" y="2" width="4.2" height="40" {ink}/>'
            f'<rect x="-1" y="1.3" width="10.2" height="1.4" rx=".4" {ink}/>'
            f'<rect x="-1" y="41.3" width="10.2" height="1.4" rx=".4" {ink}/>')


def cone(c, r, d, half, col, op):
    x1, y1 = pt(VX, VY, r, d - half)
    x2, y2 = pt(VX, VY, r, d + half)
    return f'<path d="M{VX} {VY}L{x1:.2f} {y1:.2f}A{r} {r} 0 0 1 {x2:.2f} {y2:.2f}Z" {paint(("fill", c[col]))} fill-opacity="{op}"/>'


def vertex(c):
    return f'<circle cx="{VX}" cy="{VY}" r="1.5" {paint(("fill", c["paper"]), ("stroke", c["ink"]))} stroke-width=".7"/>'


def k_research(c):
    s = []
    for i in range(5):                                   # computation: a mesh of points
        for j in range(6):
            s.append(f'<circle cx="{12 + i * 5}" cy="{6 + j * 6.5}" r=".38" {paint(("fill", c["ink"]))} fill-opacity=".22"/>')
    s.append(stem(c))
    s.append(cone(c, 25, UP, 11, "maroon", .2))           # a QCD jet: cone, tracks and core
    for d in (UP - 7, UP - 2.5, UP + 2.5, UP + 7):
        x, y = pt(VX, VY, 24, d)
        s.append(f'<line x1="{VX}" y1="{VY}" x2="{x:.2f}" y2="{y:.2f}" {paint(("stroke", c["maroon"]))} stroke-width=".55" stroke-opacity=".8"/>')
    s.append(cone(c, 25, UP, 4, "maroon", 1))
    hx, hy = pt(VX, VY, 22, DN)                           # materials: a bond with atoms, ending in a hexagonal ring
    hexpts = [pt(hx, hy, 3.4, DN + 30 + 60 * k) for k in range(6)]
    ex, ey = pt(VX, VY, 22 - 3.4 * math.cos(math.radians(30)), DN)
    gold = paint(("stroke", c["gold"]))
    s.append(f'<line x1="{VX}" y1="{VY}" x2="{ex:.2f}" y2="{ey:.2f}" {gold} stroke-width="1.6" stroke-linecap="round"/>')
    s.append('<polygon points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in hexpts) + f'" fill="none" {gold} stroke-width="1.3" stroke-linejoin="round"/>')
    for x, y in hexpts:
        s.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r=".8" {paint(("fill", c["gold"]))}/>')
    for k, r in enumerate((7, 12.5)):
        x, y = pt(VX, VY, r, DN)
        s.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2" {paint(("fill", c["gold" if k == 0 else "paper"]), ("stroke", c["gold"]))} stroke-width="1"/>')
    path = [f"M{VX} {VY}"]                               # theory: a gluon, as in a Feynman diagram
    L, n = 15, 6
    for k in range(n):
        a0, a1 = VX + L * k / n, VX + L * (k + 1) / n
        path.append(f"C{a0 + .6:.2f} {VY - 2.6:.2f} {a1 + .9:.2f} {VY - 2.6:.2f} {a1 - .6:.2f} {VY:.2f} S{a1 + .3:.2f} {VY + 1.6:.2f} {a1:.2f} {VY:.2f}")
    s.append(f'<path d="{"".join(path)}" fill="none" {paint(("stroke", c["ink"]))} stroke-width=".55" stroke-opacity=".7" transform="rotate(2 {VX} {VY})"/>')
    s.append(vertex(c))
    return "".join(s)


def k_teaching(c):
    s = [stem(c)]
    L, w = 24, 2.3                                        # a digital pen
    s.append(f'<g transform="translate({VX} {VY}) rotate({UP})"><path d="M0 {-w / 2}L{L - 5} {-w / 2}L{L - 5} {w / 2}L0 {w / 2}Z" {paint(("fill", c["gold"]))}/>'
             f'<rect x="{L - 8}" y="{-w / 2}" width="1.4" height="{w}" {paint(("fill", c["ink"]))} fill-opacity=".55"/>'
             f'<path d="M{L - 5} {-w / 2}L{L} 0L{L - 5} {w / 2}Z" {paint(("fill", c["ink"]))}/><circle cx="{L - 1.6}" cy="0" r=".45" {paint(("fill", c["paper"]))}/>'
             f'<line x1="3" y1="0" x2="{L - 9}" y2="0" {paint(("stroke", c["paper"]))} stroke-width=".35" stroke-opacity=".7"/></g>')
    pts = [(VX, VY), (VX + 5, VY + 5), (VX + 5, VY + 9), (VX + 11, VY + 15), (VX + 16, VY + 15), (VX + 21, VY + 20)]   # a circuit trace
    m = paint(("stroke", c["maroon"]))
    s.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" {m} stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>')
    for (x, y), (bx, by) in ((pts[2], (VX + 9.5, VY + 9)), (pts[4], (VX + 16, VY + 10))):
        s.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx:.1f}" y2="{by:.1f}" {m} stroke-width=".8"/>'
                 f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="1" {paint(("fill", c["paper"]), ("stroke", c["maroon"]))} stroke-width=".7"/>')
    ex, ey = pts[-1]
    s.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2" {paint(("fill", c["maroon"]))}/><circle cx="{ex:.1f}" cy="{ey:.1f}" r=".8" {paint(("fill", c["paper"]))}/>')
    s.append(vertex(c))
    return "".join(s)


def k_community(c):
    s = [stem(c)]
    m = paint(("stroke", c["maroon"]))
    x2, y2 = pt(VX, VY, 13, UP)                           # a voice carrying outward
    s.append(f'<line x1="{VX}" y1="{VY}" x2="{x2:.2f}" y2="{y2:.2f}" {m} stroke-width="2.2" stroke-linecap="round"/>')
    for k, r in enumerate((15.5, 20, 24.5)):
        a1, b1 = pt(VX, VY, r, UP - 14 + k * 2)
        a2, b2 = pt(VX, VY, r, UP + 14 - k * 2)
        s.append(f'<path d="M{a1:.2f} {b1:.2f}A{r} {r} 0 0 1 {a2:.2f} {b2:.2f}" fill="none" {m} stroke-width="{1.9 - k * .4:.2f}" stroke-linecap="round" stroke-opacity="{1 - k * .2:.2f}"/>')
    ex, ey = pt(VX, VY, 14.5, DN)                         # the arm leads to a group of people (outreach)
    s.append(f'<line x1="{VX}" y1="{VY}" x2="{ex:.2f}" y2="{ey:.2f}" {paint(("stroke", c["gold"]))} stroke-width="2.2" stroke-linecap="round"/>')
    gx, gy = pt(VX, VY, 21.5, DN)
    g, pp = paint(("fill", c["gold"])), paint(("stroke", c["paper"]))
    for dx, dy, sc in ((-3.6, -1.2, .8), (3.6, -1.2, .8), (0, 0, 1)):   # two behind, one in front
        x, y = gx + dx, gy + dy
        s.append(f'<g transform="translate({x:.2f} {y:.2f}) scale({sc})"><circle cx="0" cy="-3.4" r="1.9" {g} {pp} stroke-width=".6"/>'
                 f'<path d="M-3.4 3C-3.4 -1.2 3.4 -1.2 3.4 3Z" {g} {pp} stroke-width=".6"/></g>')
    s.append(vertex(c))
    return "".join(s)


def k_simple(c, arm1, arm2):
    """The compact K: the stem and two plain arms, for the header and the browser tab."""
    x1, y1 = pt(VX, VY, 24, UP)
    x2, y2 = pt(VX, VY, 24, DN)
    return (stem(c) + f'<line x1="{VX}" y1="{VY}" x2="{x1:.2f}" y2="{y1:.2f}" {paint(("stroke", c[arm1]))} stroke-width="3.6" stroke-linecap="round"/>'
            f'<line x1="{VX}" y1="{VY}" x2="{x2:.2f}" y2="{y2:.2f}" {paint(("stroke", c[arm2]))} stroke-width="3.6" stroke-linecap="round"/>')


def place(art, x, y, sc):
    return f'<g transform="translate({x} {y}) scale({sc}) translate(-18 -22)">{art}</g>'


def triangle(c, detailed=True):
    ks = (k_research(c), k_teaching(c), k_community(c)) if detailed else \
         (k_simple(c, "maroon", "gold"), k_simple(c, "gold", "maroon"), k_simple(c, "maroon", "maroon"))
    sc = .78 if detailed else .86
    spots = ((50, 28), (30, 66), (70, 66)) if detailed else ((50, 27), (29, 68), (71, 68))
    return "".join(place(k, x, y, sc) for k, (x, y) in zip(ks, spots))


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
    m = paint(("stroke", c["maroon"]))
    return "".join([
        f'<circle cx="50" cy="50" r="48.5" fill="none" {m} stroke-width="1.2"/>',
        f'<circle cx="50" cy="50" r="46.6" fill="none" {m} stroke-width=".4" stroke-opacity=".7"/>',
        f'<circle cx="50" cy="50" r="35" fill="none" {paint(("stroke", c["ink"]))} stroke-width=".5" stroke-opacity=".45"/>',
        f'<defs><path id="{uid}-t" d="M10.8 50A39.2 39.2 0 0 1 89.2 50"/></defs>',
        f'<text font-family="Fraunces, Georgia, serif" font-size="6.4" letter-spacing="1.3" direction="ltr" {paint(("fill", c["ink"]))}>'
        f'<textPath href="#{uid}-t" startOffset="50%" text-anchor="middle">KAMEL KHELIFA-KERFA</textPath></text>',
        f'<path d="{arabic_on_arc(50, 50, 44, 6.9)}" {paint(("fill", c["ink"]))}/>',
        f'<circle cx="8.6" cy="50" r="1.2" {paint(("fill", c["gold"]))}/><circle cx="91.4" cy="50" r="1.2" {paint(("fill", c["gold"]))}/>',
        f'<g transform="translate(50 49) scale(.69) translate(-50 -50)">{triangle(c)}</g>',
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arabic-font", help="re-trace the Arabic name from this font (Khalid Art Bold)")
    if (font := ap.parse_args().arabic_font):
        trace_arabic(font)
    macros = f'''{{# Generated by tools/make_logo.py: edit that script, not this file. #}}
{{% macro mark(cls="brand-mark") -%}}
<svg class="logo {{{{ cls }}}}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">{triangle(THEME, detailed=False)}</svg>
{{%- endmacro %}}

{{% macro seal(cls="brand-seal", uid="seal") -%}}
<svg class="logo {{{{ cls }}}}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">{seal(THEME, "{{{{ uid }}}}")}</svg>
{{%- endmacro %}}
'''
    (ROOT / "templates/_logo.html").write_text(macros.replace("{{{{ uid }}}}", "{{ uid }}"), encoding="utf-8")
    (ROOT / "static/img/favicon.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{FIXED["paper"]}"/>'
        f'<g transform="translate(50 50) scale(1.08) translate(-50 -48)">{triangle(FIXED, detailed=False)}</g></svg>\n', encoding="utf-8")
    (ROOT / "static/img/logo-seal.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{seal(FIXED, "seal")}</svg>\n', encoding="utf-8")
    print("wrote templates/_logo.html, static/img/favicon.svg and static/img/logo-seal.svg")


if __name__ == "__main__":
    main()
