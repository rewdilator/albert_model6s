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


def brand_screen():
    """Replace the media card (top-left) with an Albert vehicle card.

    The screen mesh is 0.338 x 0.265 m but maps the full square texture, so artwork is
    squeezed horizontally by 1 / 1.275 to appear with correct proportions in the car.
    """
    path = os.path.join(ROOT, "textures", "ev_sedan_screen_d.png")
    tex = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = 40, 103, 307, 348          # card rectangle in texture pixels
    card_bg = tex.getpixel((x0 + 6, y0 + 6))
    aspect = 0.338 / 0.265
    card = Image.new("RGB", (x1 - x0, y1 - y0), card_bg)
    layers, lw, lh = lockup_layers(78, 17, 34, sx=1 / aspect)
    cw, ch = card.size
    top = (ch - lh) / 2 - 6
    layers = [(g, (cw / 2, top + oy), sx, sy) for g, (ox, oy), sx, sy in layers]
    logo = raster(layers, card.size, (236, 238, 242, 255))
    card.paste(logo, (0, 0), logo)
    # thin accent line + subtle caption bar under the lockup, like a vehicle status card
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((cw / 2 - 26, ch - 34, cw / 2 + 26, ch - 30), radius=2, fill=(74, 144, 245))
    # rounded card corners matching the original UI (radius 10 px)
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=10, fill=255)
    tex.paste(card, (x0, y0), mask)
    tex.save(path, optimize=True)


if __name__ == "__main__":
    write_logo_files()
    brand_screen()
    print("brand assets written")
