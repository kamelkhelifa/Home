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

O, RING, SPAN, GAP_DEG = (50, 50), 38, 120, 2.6     # ring radius; degrees of arc per K; the small gap between K's
ANGLES = {"research": -150, "teaching": -30, "community": 90}     # degrees, clockwise from +x (SVG y is down)
COLOURS = {"research": "maroon", "teaching": "gold", "community": "ink"}
ORDER = ("research", "teaching", "community")
ARM_GAP = 1.7                                           # gap where two neighbouring K's arms meet


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


def three_jets(c, r=11):
    """A three-jet event at the centre: three slender cones, one per colour, each a solid core inside one soft
    halo. The cones' sides bow outwards a little, as jets of particles do, and end in a round cap."""
    def cone(ang, half, R):
        b0, (x1, y1), (x2, y2) = pt(*O, 1.7, ang), pt(*O, R, ang - half), pt(*O, R, ang + half)
        (q1x, q1y), (q2x, q2y) = pt(*O, R * .55, ang - half * 1.12), pt(*O, R * .55, ang + half * 1.12)
        return (f"M{b0[0]:.2f} {b0[1]:.2f}Q{q1x:.2f} {q1y:.2f} {x1:.2f} {y1:.2f}"
                f"A{R:.2f} {R:.2f} 0 0 1 {x2:.2f} {y2:.2f}Q{q2x:.2f} {q2y:.2f} {b0[0]:.2f} {b0[1]:.2f}Z")
    out = []
    for k, col in enumerate(("maroon", "gold", "ink")):
        ang = -90 + 120 * k
        out.append(f'<path d="{cone(ang, 13, r * .88)}" {paint(("fill", c[col]))} fill-opacity=".2"/>')
        out.append(f'<path d="{cone(ang, 5, r)}" {paint(("fill", c[col]))}/>')
    out.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="1.25" {paint(("fill", c["paper"]), ("stroke", c["ink"]))} stroke-width=".55"/>')
    return "".join(out)


# The three symbols share one drawing language: solid shapes in the K's colour, with details cut out in the paper
# colour, each fitting the same 11-unit circle so they carry the same visual weight.

def arrowhead(p, q, size, color):
    """A small filled arrowhead at the middle of segment p-q, pointing from p to q (fermion-flow arrow)."""
    m, d = add(p, sub(q, p), .5), unit(sub(q, p))
    n = perp(d)
    tip, b1, b2 = add(m, d, size * .65), add(add(m, d, -size * .45), n, size * .55), add(add(m, d, -size * .45), n, -size * .55)
    return f'<polygon points="{fmt([tip, b1, b2])}" {paint(("fill", color))}/>'


def gluon(p, q, loops=3, r=1.05):
    """A curly gluon line from p to q: a prolate cycloid, i.e. the path of a point on a wheel's spoke longer than
    the wheel, which draws `loops` round curls of radius about `r` along the segment."""
    d, L = unit(sub(q, p)), math.hypot(*sub(q, p))
    n = perp(d)
    steps = 40 * loops
    adv = (L - 0) / (2 * math.pi * loops)          # how far the wheel rolls per radian
    pts = []
    for i in range(steps + 1):
        th = 2 * math.pi * loops * i / steps
        ax = adv * th + r * math.sin(th)             # forwards, with a backwards swing that closes each curl
        tr = r * (1 - math.cos(th)) - r             # sideways, centred on the line p-q
        pts.append(add(add(p, d, ax), n, tr * math.sin(math.pi * i / steps) ** .35))   # taper into the ends
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def icon_research(c):
    """A QCD vertex: a quark comes in, radiates a gluon and goes on (fermion-flow arrows on the quark line, a curly
    gluon). This is the Feynman-diagram picture behind soft-gluon resummation and behind the jets at the centre."""
    m = c["maroon"]
    a, v, b, g = (-5.2, 3.2), (0, 1.0), (5.2, 3.2), (0, -6.2)
    return (f'<path d="M{a[0]} {a[1]}L{v[0]} {v[1]}L{b[0]} {b[1]}" fill="none" {paint(("stroke", m))} stroke-width="1" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            + arrowhead(a, v, 2.1, m) + arrowhead(v, b, 2.1, m)
            + f'<path d="{gluon(v, g, 3, .95)}" fill="none" {paint(("stroke", m))} stroke-width=".72" stroke-linecap="round" '
              f'stroke-linejoin="round"/>'
            + f'<circle cx="{v[0]}" cy="{v[1]}" r="1.05" {paint(("fill", m))}/>')


def icon_teaching(c):
    """An open book: two solid leaves whose top edges curve down into the spine, lines of text cut out of the pages
    in the paper colour, and the cover's edge showing as a thin curve underneath."""
    g, paper = c["gold"], c["paper"]
    leaf = "M-.35 3.0C-1.9 2.1 -3.7 1.9 -5.5 2.4V-2.9C-3.7 -3.4 -1.9 -3.2 -.35 -2.2Z"
    out = [f'<path d="{leaf}" {paint(("fill", g))}/>', f'<path d="{leaf}" transform="scale(-1 1)" {paint(("fill", g))}/>']
    for side in (-1, 1):
        for y, w in ((-1.55, 3.35), (-.3, 3.35), (.95, 2.3)):
            x0 = side * 1.3
            out.append(f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + side * w:.2f}" y2="{y - .34:.2f}" {paint(("stroke", paper))} '
                       f'stroke-width=".46" stroke-linecap="round"/>')
    out.append(f'<path d="M-5.5 3.15C-3.5 2.65 -1.6 2.95 0 3.8C1.6 2.95 3.5 2.65 5.5 3.15" fill="none" {paint(("stroke", g))} '
               f'stroke-width=".62" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def icon_community(c):
    """People together: two behind, one in front. The front figure is outlined in the paper colour so the three
    read as separate people; the group is wider at the top, matching the shape of the triangle's lower corner."""
    ink, paper = c["ink"], c["paper"]

    def person(cx, cy, r, extra=""):
        """A head of radius r centred at (cx, cy) above rounded shoulders."""
        w, top, base = 2.0 * r, cy + 1.45 * r, cy + 3.55 * r
        body = (f"M{cx - w:.2f} {base:.2f}C{cx - w:.2f} {top + .2 * r:.2f} {cx - .62 * w:.2f} {top:.2f} {cx:.2f} {top:.2f}"
                f"C{cx + .62 * w:.2f} {top:.2f} {cx + w:.2f} {top + .2 * r:.2f} {cx + w:.2f} {base:.2f}"
                f"Q{cx:.2f} {base + .35 * r:.2f} {cx - w:.2f} {base:.2f}Z")
        return (f'<path d="{body}" {paint(("fill", ink))}{extra}/>'
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" {paint(("fill", ink))}{extra}/>')
    back = "".join(f'<g fill-opacity=".55">{person(dx, -3.3, 1.2)}</g>' for dx in (-3.0, 3.0))
    clip = f' {paint(("stroke", paper))} stroke-width=".7" stroke-linejoin="round"'
    return back + person(0, -.6, 1.5, clip)


# Where each story sits: on its corner's bisector, about where the largest circle that fits between that corner's
# two arms is centred, nudged by eye (`dy`) because the icons are not round; `k` evens out their visual weight.
PLACE = {"research": dict(k=1.0, dy=1.1), "teaching": dict(k=1.02, dy=1.2), "community": dict(k=1.08, dy=-1.2)}


def symbols(c, k=1.0, rr=19):
    """Each K's story, upright in the triangle's corner between that K's arms. `k` scales all three icons and `rr`
    is how far from the centre they sit."""
    out = []
    for which, draw in (("research", icon_research), ("teaching", icon_teaching), ("community", icon_community)):
        x, y = pt(*O, rr, ANGLES[which])
        pl = PLACE[which]
        out.append(f'<g transform="translate({x:.2f} {y + pl["dy"]:.2f}) scale({k * pl["k"]:.3f})">{draw(c)}</g>')
    return "".join(out)


def emblem(c, detailed=True):
    """The whole mark: the three K's whose stems make up the ring and whose arms make the triangle, the jets at the
    centre and each K's story in its corner. The compact version (seen at 40 px or so) has heavier strokes and
    slightly larger icons and jets."""
    if detailed:
        return "".join(k_arc(w, c) for w in ORDER) + three_jets(c, 12.5) + symbols(c, 1.0, 19.5)
    return "".join(k_arc(w, c, 5.2, 3.2) for w in ORDER) + three_jets(c, 13) + symbols(c, 1.0, 19.5)


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
