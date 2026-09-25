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
    waist = 2 * rl                             # top of the lower bowl
    t0 = math.degrees(math.asin(max(-1.0, (waist - yu) / ru)))
    outline = [(0, 0), (xl, 0)]
    outline += _arc(xl, yl, rl, -90, 90, steps)[1:]
    outline += _arc(xu, yu, ru, t0, 90, steps)
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

def emblem():
    """The A+ mark. Returns (glyphs, (xmin, xmax)) with x centred on the mark."""
    a, _ = glyph_A()
    plus = glyph_plus(0.86, 0.76)
    glyphs = [a, plus]
    xmin, xmax = -0.62, 0.86 + 0.24
    c = (xmin + xmax) / 2
    glyphs = [_translate(g, -c) for g in glyphs]
    return glyphs, (xmin - c, xmax - c)


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
