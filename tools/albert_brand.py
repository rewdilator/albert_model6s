"""Albert brand geometry: the "A+" emblem and the "ALBERT" wordmark as 2D outlines.

Pure Python (no bpy / PIL) so the same shapes drive the 3D badges in Blender,
the screen texture and the exported logo PNG/SVG files.

Every glyph is a list of rings ``[(x, y), ...]`` in cap-height units (cap height = 1,
baseline at y = 0).  The first ring of a glyph is its outline (counter-clockwise),
any further rings are holes (clockwise).
"""
import math

# ---------------------------------------------------------------- primitives

def _arc(cx, cy, r, a0, a1, steps):
    """Points on a circular arc from angle a0 to a1 (degrees), inclusive."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
            for i in range(steps + 1)]


def _stadium_hole(x0, y0, y1, x_right, steps):
    """Clockwise counter: flat left side at x0, round right end touching x_right."""
    r = (y1 - y0) / 2.0
    cx, cy = x_right - r, (y0 + y1) / 2.0
    ring = [(x0, y0), (x0, y1)]
    ring += _arc(cx, cy, r, 90, -90, steps)
    return ring


def _circle_intersection(c1, r1, c2, r2):
    """Intersection of two circles with the larger x."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    p, q = (mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d)
    return p if p[0] >= q[0] else q


def signed_area(ring):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]))


def _orient(glyph):
    """Force outline CCW and holes CW."""
    out = []
    for i, ring in enumerate(glyph):
        ccw = signed_area(ring) > 0
        if (i == 0) != ccw:
            ring = ring[::-1]
        out.append(ring)
    return out


def _translate(glyph, dx, dy=0.0, sx=1.0, sy=1.0):
    return [[(x * sx + dx, y * sy + dy) for x, y in ring] for ring in glyph]

# ---------------------------------------------------------------- glyphs

def glyph_A(stroke=0.22, half_width=0.62, apex=0.09, bar=(0.20, 0.36)):
    """Geometric A with a flat apex and a triangular counter. x is centred on 0."""
    slope = (half_width - apex) / 1.0           # x change per unit y on the outer edge
    inner0 = half_width - stroke / math.cos(math.atan(slope))  # inner leg x at the baseline
    ix = lambda y: inner0 - slope * y           # inner edge (right leg) at height y
    b0, b1 = bar
    outline = [(-half_width, 0), (-inner0, 0), (-ix(b0), b0), (ix(b0), b0), (inner0, 0),
               (half_width, 0), (apex, 1), (-apex, 1)]
    top = inner0 / slope                        # where the inner edges meet
    hole = [(-ix(b1), b1), (0.0, top), (ix(b1), b1)]
    return _orient([outline, hole]), (-half_width, half_width)


def glyph_plus(cx, cy, arm=0.24, stroke=0.13):
    a, s = arm, stroke / 2.0
    ring = [(cx - s, cy - a), (cx + s, cy - a), (cx + s, cy - s), (cx + a, cy - s), (cx + a, cy + s),
            (cx + s, cy + s), (cx + s, cy + a), (cx - s, cy + a), (cx - s, cy + s), (cx - a, cy + s),
            (cx - a, cy - s), (cx - s, cy - s)]
    return _orient([ring])


def glyph_L(w, width=0.56):
    return _orient([[(0, 0), (width, 0), (width, w), (w, w), (w, 1), (0, 1)]]), (0, width)


def glyph_E(w, width=0.56, mid=0.50):
    m0, m1 = mid - w / 2, mid + w / 2
    return _orient([[(0, 0), (width, 0), (width, w), (w, w), (w, m0), (width * 0.9, m0), (width * 0.9, m1),
                     (w, m1), (w, 1 - w), (width, 1 - w), (width, 1), (0, 1)]]), (0, width)


def glyph_T(w, width=0.62):
    h = width / 2
    return _orient([[(-w / 2, 0), (w / 2, 0), (w / 2, 1 - w), (h, 1 - w), (h, 1), (-h, 1), (-h, 1 - w),
                     (-w / 2, 1 - w)]]), (-h, h)


def glyph_B(w, steps=16):
    # Bowl radii chosen so the middle bar is exactly one stroke thick: rl + ru = (1 + w) / 2
    rl = (1 + w) / 4 + 0.01                    # lower bowl (slightly larger, as in classic B)
    ru = (1 + w) / 2 - rl
    xu, xl = 0.30, 0.33                        # bowl arc centres (x)
    yl, yu = rl, 1 - ru                        # bowl arc centres (y)
    # the two bowls meet where their outer circles intersect (right-hand point): a clean notch
    ix, iy = _circle_intersection((xl, yl), rl, (xu, yu), ru)
    a_low = math.degrees(math.atan2(iy - yl, ix - xl))
    a_up = math.degrees(math.atan2(iy - yu, ix - xu))
    outline = [(0, 0), (xl, 0)]
    outline += _arc(xl, yl, rl, -90, a_low, steps)[1:]
    outline += _arc(xu, yu, ru, a_up, 90, steps)[1:]
    outline += [(0, 1)]
    # counters concentric with the bowls -> constant stroke all round
    upper = _stadium_hole(w, 1 - 2 * ru + w, 1 - w, xu + ru - w, steps)
    lower = _stadium_hole(w, w, 2 * rl - w, xl + rl - w, steps)
    return _orient([outline, upper, lower]), (0, xl + rl)


def glyph_R(w, steps=16):
    r = 0.27
    xu, yu = 0.29, 1 - r
    yb = 1 - 2 * r                             # bottom of the bowl
    lt_x = xu - 0.10                           # leg top-left on the bowl bottom
    lb_x = xu + 0.12                           # leg bottom-left on the baseline
    dx, dy = lb_x - lt_x, -yb
    legw = w / (abs(dy) / math.hypot(dx, dy))  # horizontal width for a stroke of w
    outline = [(0, 0), (w, 0), (w, yb), (lt_x, yb), (lb_x, 0), (lb_x + legw, 0), (lt_x + legw, yb)]
    outline += _arc(xu, yu, r, -90, 90, steps)[1:] if lt_x + legw < xu else _arc(xu, yu, r, -60, 90, steps)
    outline += [(0, 1)]
    hole = _stadium_hole(w, yb + w * 1.05, 1 - w, xu + r - w, steps)
    return _orient([outline, hole]), (0, lb_x + legw)

# ---------------------------------------------------------------- compositions

# ---------------------------------------------------------------- the A+ logo
# Proportions measured from the reference artwork (cap height = 1, baseline y = 0):
# a bold A with a flat apex and a triangular counter, and a "+" overlapping its right
# leg at crossbar height. Each part is a union of convex strokes so the 3D badge can give
# every stroke a faceted (hip-roof) top whose creases meet like a diamond cut.
LOGO_A = dict(foot_out=0.62, foot_in=0.33, apex=0.132, counter_top=0.755, bar=(0.25, 0.46))
LOGO_PLUS = dict(cx=0.258, cy=0.457, arm=0.26, half=0.09)
PLUS_GAP = 0.045          # clearance cut round the "+" in flat (single-colour) versions


def logo_strokes():
    """Convex stroke polygons (CCW) of the logo, un-centred: {"A": [...], "plus": [...]}."""
    a = LOGO_A
    fo, fi, ap, ct = a["foot_out"], a["foot_in"], a["apex"], a["counter_top"]
    k_in = fi / ct                                  # inner-edge x change per unit y
    x_top = -fi + k_in                              # left inner edge extended to y = 1
    left = [(-fo, 0.0), (-fi, 0.0), (x_top, 1.0), (-ap, 1.0)]
    right = [(-x, y) for x, y in left][::-1]
    # crossbar runs between the leg centre lines, so its hidden ends sit under the leg ridges
    centre = lambda y: ((-fo + (fo - ap) * y) + (-fi + k_in * y)) / 2  # noqa: E731
    b0, b1 = a["bar"]
    bar = [(centre(b0), b0), (-centre(b0), b0), (-centre(b1), b1), (centre(b1), b1)]
    p = LOGO_PLUS
    cx, cy, L, t = p["cx"], p["cy"], p["arm"], p["half"]
    horiz = [(cx - L, cy - t), (cx + L, cy - t), (cx + L, cy + t), (cx - L, cy + t)]
    vert = [(cx - t, cy - L), (cx + t, cy - L), (cx + t, cy + L), (cx - t, cy + L)]
    return {"A": [left, right, bar], "plus": [horiz, vert]}


def _logo_centre():
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    st = logo_strokes()
    x0, _, x1, _ = unary_union([Polygon(q) for q in st["A"] + st["plus"]]).bounds
    return (x0 + x1) / 2, (x0 - (x0 + x1) / 2, x1 - (x0 + x1) / 2)


def logo_strokes_centred():
    c, _ = _logo_centre()
    return {k: [[(x - c, y) for x, y in q] for q in v] for k, v in logo_strokes().items()}


def _rings(geom):
    """shapely (Multi)Polygon -> list of glyphs [outline CCW, holes CW]."""
    polys = getattr(geom, "geoms", [geom])
    out = []
    for poly in polys:
        rings = [list(poly.exterior.coords)[:-1]] + [list(h.coords)[:-1] for h in poly.interiors]
        out.append(_orient(rings))
    return out


def logo_outline(part, grow=0.0):
    """Outline of "A" or "plus" (centred), optionally grown with mitred corners, as glyphs."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    geom = unary_union([Polygon(q) for q in logo_strokes_centred()[part]])
    if grow:
        geom = geom.buffer(grow, join_style="mitre", mitre_limit=4.0)
    return _rings(geom)


def emblem():
    """Flat single-colour A+ (the A with a clearance gap cut round the "+").

    Returns (glyphs, (xmin, xmax)) with x centred on the mark, y from 0 to 1.
    """
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    st = logo_strokes_centred()
    a = unary_union([Polygon(q) for q in st["A"]])
    plus = unary_union([Polygon(q) for q in st["plus"]])
    flat = a.difference(plus.buffer(PLUS_GAP, join_style="mitre")).union(plus)
    _, bounds = _logo_centre()
    return _rings(flat), bounds


def wordmark(stroke=0.14, tracking=0.42):
    """ALBERT, centred on x = 0."""
    parts = [glyph_A(stroke=stroke, half_width=0.36, apex=0.055, bar=(0.26, 0.26 + stroke)),
             glyph_L(stroke), glyph_B(stroke), glyph_E(stroke), glyph_R(stroke), glyph_T(stroke)]
    glyphs, x = [], 0.0
    for g, (x0, x1) in parts:
        glyphs.append(_translate(g, x - x0))
        x += (x1 - x0) + tracking
    x -= tracking
    glyphs = [_translate(g, -x / 2) for g in glyphs]
    return glyphs, (-x / 2, x / 2)


def to_svg(glyphs, bounds, height=1.0, pad=0.15, fill="#111"):
    x0, x1 = bounds
    w, h = (x1 - x0) + 2 * pad, height + 2 * pad
    paths = []
    for g in glyphs:
        d = ""
        for ring in g:
            d += "M" + " L".join(f"{x - x0 + pad:.4f},{height - y + pad:.4f}" for x, y in ring) + " Z "
        paths.append(f'<path d="{d.strip()}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.4f} {h:.4f}">'
            f'<g fill="{fill}" fill-rule="evenodd">{"".join(paths)}</g></svg>\n')
