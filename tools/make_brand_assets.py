"""Generate Albert logo files and brand the centre-screen texture.

Writes:
  brand/albert_logo.svg, brand/albert_wordmark.svg, brand/albert_lockup.svg
  brand/albert_logo_{white,black}.png, brand/albert_wordmark_{white,black}.png,
  brand/albert_lockup_{white,black}.png   (transparent, for Unity UI / splash screens)
  textures/ev_sedan_screen_d.png           (vehicle card on the touchscreen -> Albert)

Run: python3 tools/make_brand_assets.py   (needs Pillow)
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import albert_brand as ab  # noqa: E402

SS = 4  # supersampling factor


def raster(layers, size, colour, bg=(0, 0, 0, 0)):
    """layers: list of (glyphs, (ox, oy), scale_x, scale_y) in pixels, y up from oy."""
    W, H = size
    img = Image.new("RGBA", (W * SS, H * SS), bg)
    for glyphs, (ox, oy), sx, sy in layers:
        for g in glyphs:
            mask = Image.new("L", img.size, 0)
            d = ImageDraw.Draw(mask)
            for i, ring in enumerate(g):
                d.polygon([((ox + x * sx) * SS, (oy - y * sy) * SS) for x, y in ring], fill=255 if i == 0 else 0)
            img.paste(Image.new("RGBA", img.size, colour), mask=mask)
    return img.resize(size, Image.LANCZOS)


def lockup_layers(cap, word_cap, gap, sx=1.0):
    """A+ above ALBERT, both centred on x = 0; returns layers, width, height."""
    em, (e0, e1) = ab.emblem()
    wm, (w0, w1) = ab.wordmark()
    width = max((e1 - e0) * cap, (w1 - w0) * word_cap) * sx
    height = cap + gap + word_cap
    return [(em, (0, cap), cap * sx, cap), (wm, (0, height), word_cap * sx, word_cap)], width, height


def write_logo_files():
    out = os.path.join(ROOT, "brand")
    os.makedirs(out, exist_ok=True)
    em, eb = ab.emblem()
    wm, wb = ab.wordmark()
    open(os.path.join(out, "albert_logo.svg"), "w").write(ab.to_svg(em, eb))
    open(os.path.join(out, "albert_wordmark.svg"), "w").write(ab.to_svg(wm, wb))

    # lockup SVG: emblem stacked over the wordmark
    layers, lw, lh = lockup_layers(1.0, 0.28, 0.32)
    pad = 0.15
    paths = []
    for glyphs, (ox, oy), sx, sy in layers:
        for g in glyphs:
            d = " ".join("M" + " L".join(f"{ox + x * sx + lw / 2 + pad:.4f},{oy - y * sy + pad:.4f}"
                                          for x, y in ring) + " Z" for ring in g)
            paths.append(f'<path d="{d}"/>')
    open(os.path.join(out, "albert_lockup.svg"), "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {lw + 2 * pad:.4f} {lh + 2 * pad:.4f}">'
        f'<g fill="#111" fill-rule="evenodd">{"".join(paths)}</g></svg>\n')

    for name, col in (("white", (255, 255, 255, 255)), ("black", (17, 17, 17, 255))):
        cap = 600
        W = int((eb[1] - eb[0]) * cap) + 160
        raster([(em, (W / 2, 80 + cap), cap, cap)], (W, cap + 160), col).save(
            os.path.join(out, f"albert_logo_{name}.png"), optimize=True)
        cap = 160
        W = int((wb[1] - wb[0]) * cap) + 120
        raster([(wm, (W / 2, 60 + cap), cap, cap)], (W, cap + 120), col).save(
            os.path.join(out, f"albert_wordmark_{name}.png"), optimize=True)
        layers, lw, lh = lockup_layers(520, 130, 150)
        W, H = int(lw) + 200, int(lh) + 200
        layers = [(g, (W / 2, 100 + oy), sx, sy) for g, (ox, oy), sx, sy in layers]
        raster(layers, (W, H), col).save(os.path.join(out, f"albert_lockup_{name}.png"), optimize=True)


FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _font(size, bold=False):
    from PIL import ImageFont
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def brand_screen():
    """Draw the centre touchscreen UI (textures/ev_sedan_screen_d.png).

    The screen mesh is 0.338 x 0.265 m but maps the full square texture, so the UI is laid
    out on a 1306 x 1024 landscape canvas and squeezed to 1024 x 1024.
    """
    import random
    K = 2                                        # supersampling
    W, H = 1306, 1024
    img = Image.new("RGB", (W * K, H * K), (16, 17, 20))
    d = ImageDraw.Draw(img)
    P = lambda *v: tuple(int(round(x * K)) for x in v)  # noqa: E731
    txt = lambda xy, t, size, fill, bold=False, anchor="la": d.text(P(*xy), t, font=_font(size * K, bold), fill=fill, anchor=anchor)  # noqa: E731
    WHITE, GREY, DIM, BLUE = (236, 238, 242), (150, 154, 162), (88, 92, 100), (62, 138, 255)

    # ---------------- map (right 64 %)
    mx0, my0, mx1, my1 = 470, 0, W, 900
    d.rectangle(P(mx0, my0, mx1, my1), fill=(28, 31, 37))
    rnd = random.Random(7)
    d.polygon([P(*q) for q in [(1030, 0), (1306, 0), (1306, 330), (1180, 300), (1090, 190)]], fill=(24, 40, 62))   # water
    d.rectangle(P(560, 560, 700, 700), fill=(30, 46, 36))                                                    # park
    d.rectangle(P(1120, 620, 1250, 760), fill=(30, 46, 36))
    for _ in range(90):                                                                                      # blocks
        x, y = rnd.uniform(mx0, mx1), rnd.uniform(my0, my1)
        w, h = rnd.uniform(14, 46), rnd.uniform(12, 36)
        d.rectangle(P(x, y, x + w, y + h), fill=(35, 38, 45))
    minor = [((mx0, 120), (mx1, 150)), ((mx0, 330), (mx1, 300)), ((mx0, 520), (mx1, 545)), ((mx0, 760), (mx1, 730)),
             ((560, 0), (575, my1)), ((760, 0), (745, my1)), ((960, 0), (985, my1)), ((1160, 0), (1150, my1)),
             ((470, 860), (900, 420)), ((900, 420), (1306, 60))]
    for a, b in minor:
        d.line(P(*a, *b), fill=(58, 63, 74), width=7 * K)
    major = [((mx0, 430), (mx1, 400)), ((860, 0), (870, my1))]
    for a, b in major:
        d.line(P(*a, *b), fill=(84, 90, 104), width=13 * K)
    txt((1000, 382), "ALBERT AVE", 15, GREY, True)
    txt((600, 160), "Harbour St", 15, GREY)
    txt((600, 500), "Park Ln", 14, GREY)
    route = [(870, 860), (868, 640), (866, 430), (1000, 418), (1150, 405), (1150, 250), (1152, 140)]
    d.line([P(*q) for q in route], fill=(40, 100, 220), width=22 * K, joint="curve")
    d.line([P(*q) for q in route], fill=BLUE, width=14 * K, joint="curve")
    d.ellipse(P(1136, 118, 1168, 150), fill=(235, 70, 60))                                                   # destination
    d.ellipse(P(1145, 127, 1159, 141), fill=WHITE)
    d.polygon([P(*q) for q in [(870, 770), (892, 830), (870, 815), (848, 830)]], fill=WHITE)                # car arrow
    # turn-by-turn card
    d.rounded_rectangle(P(500, 24, 900, 138), radius=18 * K, fill=(22, 24, 28))
    d.polygon([P(*q) for q in [(542, 110), (542, 58), (580, 58), (580, 44), (606, 66), (580, 88), (580, 74),
                               (558, 74), (558, 110)]], fill=WHITE)                                   # turn right
    txt((626, 48), "350 m", 30, WHITE, True)
    txt((626, 90), "Turn right onto Albert Ave", 18, GREY)
    # ETA card
    d.rounded_rectangle(P(930, 790, 1280, 880), radius=18 * K, fill=(22, 24, 28))
    txt((956, 806), "12 min", 28, WHITE, True)
    txt((956, 846), "8.4 km  ·  12:57 arrival", 17, GREY)
    d.rounded_rectangle(P(1196, 812, 1260, 858), radius=12 * K, fill=(200, 55, 50))
    txt((1228, 835), "End", 17, WHITE, True, "mm")

    # ---------------- vehicle panel (left)
    d.rectangle(P(0, 0, 470, 900), fill=(18, 19, 23))
    gears = ["P", "R", "N", "D"]
    for i, g in enumerate(gears):
        txt((40 + i * 40, 30), g, 26, WHITE if g == "P" else DIM, g == "P")
    txt((260, 30), "12:45", 24, WHITE, True)
    txt((370, 30), "21°C", 22, GREY)
    txt((40, 88), "0", 96, WHITE, True)
    txt((40, 196), "km/h", 20, GREY)
    # battery
    d.rounded_rectangle(P(300, 110, 410, 150), radius=6 * K, outline=GREY, width=2 * K)
    d.rectangle(P(410, 122, 418, 138), fill=GREY)
    d.rounded_rectangle(P(305, 115, 305 + 0.82 * 100, 145), radius=4 * K, fill=(76, 200, 110))
    txt((300, 160), "82 %  ·  412 km", 18, GREY)
    # car render
    car_path = os.path.join(ROOT, "brand", "albert_car_render.png")
    if os.path.exists(car_path):
        car = Image.open(car_path).convert("RGBA")
        cw = 400 * K
        car = car.resize((cw, int(car.height * cw / car.width)), Image.LANCZOS)
        img.paste(car, P(35, 270), car)
    # brand lockup + open/close shortcuts under the car
    em, (e0, e1) = ab.emblem()
    wm, (w0, w1) = ab.wordmark()
    logo = raster([(em, (66 * K, 34 * K), 30 * K, 30 * K), (wm, (158 * K, 34 * K), 16 * K, 16 * K)],
                  (470 * K, 50 * K), WHITE + (255,))
    img.paste(logo, P(0, 560), logo)
    for i, label in enumerate(["Frunk", "Trunk", "Lock"]):
        x = 40 + i * 140
        d.rounded_rectangle(P(x, 640, x + 120, 700), radius=14 * K, fill=(34, 36, 42))
        txt((x + 60, 670), label, 18, WHITE, False, "mm")
    # media card
    d.rounded_rectangle(P(24, 730, 446, 880), radius=18 * K, fill=(30, 32, 38))
    d.rounded_rectangle(P(44, 752, 144, 852), radius=10 * K, fill=(62, 138, 255))
    txt((94, 802), "♪", 44, WHITE, True, "mm")
    txt((164, 762), "Albert Radio", 20, WHITE, True)
    txt((164, 796), "Night Drive  ·  Live", 16, GREY)
    d.rounded_rectangle(P(164, 840, 426, 846), radius=3 * K, fill=(60, 63, 70))
    d.rounded_rectangle(P(164, 840, 262, 846), radius=3 * K, fill=WHITE)

    # ---------------- dock
    d.rectangle(P(0, 900, W, H), fill=(10, 10, 12))
    d.line(P(0, 900, W, 900), fill=(40, 42, 48), width=2 * K)
    txt((40, 962), "‹", 38, GREY, False, "lm")
    txt((110, 962), "21.0", 30, WHITE, True, "mm")
    txt((178, 962), "›", 38, GREY, False, "lm")
    icons = [(420, "car"), (530, "phone"), (640, "music"), (750, "apps"), (860, "camera"), (970, "fan")]
    for x, kind in icons:
        c = (x, 962)
        if kind == "car":
            d.rounded_rectangle(P(x - 26, 950, x + 26, 976), radius=8 * K, outline=WHITE, width=3 * K)
            d.line(P(x - 16, 950, x - 10, 938, x + 10, 938, x + 16, 950), fill=WHITE, width=3 * K)
        elif kind == "phone":
            d.rounded_rectangle(P(x - 26, 936, x + 26, 988), radius=12 * K, fill=(76, 200, 110))
            txt(c, "☎", 34, WHITE, False, "mm")
        elif kind == "music":
            txt(c, "♪", 40, WHITE, True, "mm")
        elif kind == "apps":
            for gx in (-12, 12):
                for gy in (-12, 12):
                    d.rounded_rectangle(P(x + gx - 8, 962 + gy - 8, x + gx + 8, 962 + gy + 8), radius=3 * K, fill=WHITE)
        elif kind == "camera":
            d.rounded_rectangle(P(x - 24, 948, x + 24, 980), radius=6 * K, outline=WHITE, width=3 * K)
            d.ellipse(P(x - 9, 955, x + 9, 973), outline=WHITE, width=3 * K)
        elif kind == "fan":
            d.ellipse(P(x - 22, 940, x + 22, 984), outline=(62, 138, 255), width=3 * K)
            d.ellipse(P(x - 5, 957, x + 5, 967), fill=(62, 138, 255))
    d.polygon([P(*q) for q in [(1170, 952), (1182, 952), (1196, 940), (1196, 984), (1182, 972), (1170, 972)]], fill=GREY)
    d.arc(P(1196, 948, 1224, 976), -60, 60, fill=GREY, width=3 * K)

    out = img.resize((1024, 1024), Image.LANCZOS)
    out.save(os.path.join(ROOT, "textures", "ev_sedan_screen_d.png"), optimize=True)


if __name__ == "__main__":
    write_logo_files()
    brand_screen()
    print("brand assets written")
