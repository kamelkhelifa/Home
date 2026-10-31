"""Draw the site's logo: three K's for research, teaching and community.

The K's stems form a triangle and their arms meet inside it; a three-jet event marks the centre. In the seal
each K also holds its story: particle tracks and a lattice ring (research), an open book and a pen (teaching), a
group of people (community).

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


# ---------------------------------------------------------------- the three K's
# The K's stems are the sides of a triangle; from the middle of each stem two arms reach inwards and meet the
# neighbouring K's arms. Research (maroon) on the left, teaching (gold) on the right, community (ink) as the base.
# Where the three meet, at the centre, a three-jet event in their three colours.

O, R, T, GAP = (50, 52), 38, .38, 1.6


def add(a, b, k=1):
    return a[0] + k * b[0], a[1] + k * b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def unit(v):
    n = math.hypot(*v)
    return v[0] / n, v[1] / n


def perp(v):
    return -v[1], v[0]


def turn(p, deg):
    a, (x, y) = math.radians(deg), sub(p, O)
    return O[0] + x * math.cos(a) - y * math.sin(a), O[1] + x * math.sin(a) + y * math.cos(a)


TOP = (O[0], O[1] - R)
LEFT, RIGHT = turn(TOP, -120), turn(TOP, 120)
P_TOP, P_LEFT, P_RIGHT = (add(O, sub(X, O), T) for X in (TOP, LEFT, RIGHT))   # where neighbouring arms meet
MID = {"research": add(LEFT, sub(TOP, LEFT), .5), "teaching": add(RIGHT, sub(TOP, RIGHT), .5), "community": add(LEFT, sub(RIGHT, LEFT), .5)}


def bar(p, q, w, color):
    n = perp(unit(sub(q, p)))
    pts = [add(p, n, w / 2), add(q, n, w / 2), add(q, n, -w / 2), add(p, n, -w / 2)]
    return f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in pts)}" {paint(("fill", color))}/>'


def k_letter(s0, s1, arm_to, color, sw=4.2, aw=2.5):
    """One K: a serif stem along a side of the triangle, and two arms of equal weight from its middle."""
    a, b = add(s0, sub(s1, s0), .15), add(s0, sub(s1, s0), .85)
    mid, n = add(s0, sub(s1, s0), .5), perp(unit(sub(s1, s0)))
    out = [bar(a, b, sw, color)] + [bar(add(e, n, -sw), add(e, n, sw), 1.2, color) for e in (a, b)]
    for q in arm_to:
        end = add(q, unit(sub(mid, q)), GAP)
        nn = perp(unit(sub(q, mid)))
        out += [bar(mid, end, aw, color), bar(add(end, nn, -aw * .95), add(end, nn, aw * .95), .9, color)]
    return "".join(out)


def three_jets(c):
    out = []
    for k, col in enumerate(("maroon", "gold", "ink")):
        ang = -90 + 120 * k
        for half, op in ((13, .22), (4.5, 1)):
            x1, y1 = pt(*O, 6.5, ang - half)
            x2, y2 = pt(*O, 6.5, ang + half)
            out.append(f'<path d="M{O[0]} {O[1]}L{x1:.2f} {y1:.2f}A6.5 6.5 0 0 1 {x2:.2f} {y2:.2f}Z" {paint(("fill", c[col]))} fill-opacity="{op}"/>')
    out.append(f'<circle cx="{O[0]}" cy="{O[1]}" r=".9" {paint(("fill", c["paper"]), ("stroke", c["ink"]))} stroke-width=".45"/>')
    return "".join(out)


def symbols(c):
    """Each K's story, drawn between its arms."""
    out = []
    m = MID["research"]                                   # research: particle tracks from the K's vertex, a lattice ring
    d = unit(sub(O, m))
    for ang in (-24, -12, 0, 12, 24):
        a = math.radians(ang)
        dd = (d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a))
        (x1, y1), (x2, y2) = add(m, dd, 2.2), add(m, dd, 7.5)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {paint(("stroke", c["maroon"]))} stroke-width=".42" stroke-linecap="round" stroke-opacity=".85"/>')
    h = add(m, sub(O, m), .62)
    ring = [add(h, (1.5 * math.cos(math.radians(60 * k)), 1.5 * math.sin(math.radians(60 * k)))) for k in range(6)]
    out.append('<polygon points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in ring) + f'" fill="none" {paint(("stroke", c["maroon"]))} stroke-width=".5"/>')
    bx, by = add(MID["teaching"], sub(O, MID["teaching"]), .5)   # teaching: an open book and a pen
    out.append(f'<path d="M{bx:.2f} {by + 1.6:.2f}C{bx - 1.2:.2f} {by + .8:.2f} {bx - 2.8:.2f} {by + .8:.2f} {bx - 4:.2f} {by + 1.2:.2f}V{by - 1.6:.2f}'
               f'C{bx - 2.8:.2f} {by - 2:.2f} {bx - 1.2:.2f} {by - 2:.2f} {bx:.2f} {by - 1.2:.2f}Z'
               f'M{bx:.2f} {by + 1.6:.2f}C{bx + 1.2:.2f} {by + .8:.2f} {bx + 2.8:.2f} {by + .8:.2f} {bx + 4:.2f} {by + 1.2:.2f}V{by - 1.6:.2f}'
               f'C{bx + 2.8:.2f} {by - 2:.2f} {bx + 1.2:.2f} {by - 2:.2f} {bx:.2f} {by - 1.2:.2f}Z" fill="none" {paint(("stroke", c["gold"]))} stroke-width=".55" stroke-linejoin="round"/>')
    out.append(f'<g transform="translate({bx + .6:.2f} {by - 3.2:.2f}) rotate(-35)"><rect x="-3" y="-.45" width="4.6" height=".9" {paint(("fill", c["gold"]))}/>'
               f'<path d="M1.6 -.45L3.2 0L1.6 .45Z" {paint(("fill", c["ink"]))}/></g>')
    x0, y0 = add(MID["community"], sub(O, MID["community"]), .45)   # community: a group of people
    ink = paint(("fill", c["ink"]))
    for dx, r, dy in ((-2.6, .85, .5), (0, 1, 0), (2.6, .85, .5)):
        out.append(f'<circle cx="{x0 + dx:.2f}" cy="{y0 + dy - 1.6:.2f}" r="{r}" {ink}/>'
                   f'<path d="M{x0 + dx - 1.7 * r:.2f} {y0 + dy + 1.6:.2f}C{x0 + dx - 1.7 * r:.2f} {y0 + dy - .3:.2f} {x0 + dx + 1.7 * r:.2f} {y0 + dy - .3:.2f} {x0 + dx + 1.7 * r:.2f} {y0 + dy + 1.6:.2f}Z" {ink}/>')
    return "".join(out)


def triangle(c, detailed=True):
    out = (k_letter(LEFT, TOP, (P_TOP, P_LEFT), c["maroon"])          # research
           + k_letter(RIGHT, TOP, (P_TOP, P_RIGHT), c["gold"])        # teaching
           + k_letter(LEFT, RIGHT, (P_LEFT, P_RIGHT), c["ink"])       # community
           + three_jets(c))
    return out + (symbols(c) if detailed else "")


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
                f'<defs><path id="{uid}-t" d="M10.8 50A39.2 39.2 0 0 1 89.2 50"/></defs>',
        f'<text font-family="Fraunces, Georgia, serif" font-size="6.4" letter-spacing="1.3" direction="ltr" {paint(("fill", c["ink"]))}>'
        f'<textPath href="#{uid}-t" startOffset="50%" text-anchor="middle">KAMEL KHELIFA-KERFA</textPath></text>',
        f'<path d="{arabic_on_arc(50, 50, 44, 6.9)}" {paint(("fill", c["ink"]))}/>',
        f'<circle cx="8.6" cy="50" r="1.2" {paint(("fill", c["gold"]))}/><circle cx="91.4" cy="50" r="1.2" {paint(("fill", c["gold"]))}/>',
        f'<g transform="translate(50 50) scale(.78) translate(-50 -46.9)">{triangle(c)}</g>',
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arabic-font", help="re-trace the Arabic name from this font (Khalid Art Bold)")
    if (font := ap.parse_args().arabic_font):
        trace_arabic(font)
    macros = f'''{{# Generated by tools/make_logo.py: edit that script, not this file. #}}
{{% macro mark(cls="brand-mark") -%}}
<svg class="logo {{{{ cls }}}}" viewBox="0 0 100 100" aria-hidden="true" focusable="false"><g transform="translate(50 50) scale(1.12) translate(-50 -46.9)">{triangle(THEME, detailed=False)}</g></svg>
{{%- endmacro %}}

{{% macro seal(cls="brand-seal", uid="seal") -%}}
<svg class="logo {{{{ cls }}}}" viewBox="0 0 100 100" aria-hidden="true" focusable="false">{seal(THEME, "{{{{ uid }}}}")}</svg>
{{%- endmacro %}}
'''
    (ROOT / "templates/_logo.html").write_text(macros.replace("{{{{ uid }}}}", "{{ uid }}"), encoding="utf-8")
    (ROOT / "static/img/favicon.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{FIXED["paper"]}"/>'
        f'<g transform="translate(50 50) scale(1.12) translate(-50 -46.9)">{triangle(FIXED, detailed=False)}</g></svg>\n', encoding="utf-8")
    (ROOT / "static/img/logo-seal.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">{seal(FIXED, "seal")}</svg>\n', encoding="utf-8")
    print("wrote templates/_logo.html, static/img/favicon.svg and static/img/logo-seal.svg")


if __name__ == "__main__":
    main()
