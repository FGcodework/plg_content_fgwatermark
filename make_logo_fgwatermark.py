#!/usr/bin/env python3
"""
make_logo_fgwatermark.py

Generates assets/logo.png (and logo.svg source reference) for
plg_content_fgwatermark, following the FG logo convention:
  - 512x512, squircle corner radius rx=95 (~18.5% - matches the JED banner
    template's .logo-inner frame rounding)
  - navy gradient background #081D32 -> #113758
  - coral #FF6B4A accent
  - flat, no drop shadow on the standalone logo (shadow belongs only in the
    banner, on its own navy bg - a shadow baked into logo.png leaves a grey
    halo on non-matching backgrounds)
  - rendered at 4x supersampling then downsampled (LANCZOS) for clean
    anti-aliased edges without ever applying a blur filter to the alpha
    channel itself

Mark concept: a photo card (small mountain+sun scene, same "generic image"
motif as the plugin's previous icon) with a small circular coral "stamp"
badge overlapping its bottom-right corner - a white ring border and a bold
white "W" inside, slightly rotated for an authentic "rubber stamp applied
at an angle" look. A compact stamp badge reads clearly as "marked/stamped"
even at small sizes (unlike a huge rotated letter spanning the whole card,
which turns illegible/zigzag-looking at this scale), and avoids the old
diagonal-stripe mark's resemblance to a "blocked/prohibited" sign.
"""

from PIL import Image, ImageDraw, ImageFont

SCALE = 4
SIZE = 512 * SCALE

NAVY_TOP = (8, 29, 50)       # #081D32
NAVY_BOTTOM = (17, 55, 88)   # #113758
CORAL = (255, 107, 74)       # #FF6B4A
CARD_BG = (244, 247, 250)    # #F4F7FA
MOUNTAIN_DARK = (14, 44, 72)
MOUNTAIN_LIGHT = (22, 69, 105)
SUN = (255, 201, 74)
WHITE = (255, 255, 255)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CORNER_RADIUS = int(95 * SCALE)


def make_gradient_bg(size):
    base = Image.new("RGB", (size, size), NAVY_TOP)
    px = base.load()
    for y in range(size):
        t = y / (size - 1)
        for x in range(size):
            tx = (x / (size - 1)) * 0.25 + t * 0.75
            r = int(NAVY_TOP[0] + (NAVY_BOTTOM[0] - NAVY_TOP[0]) * tx)
            g = int(NAVY_TOP[1] + (NAVY_BOTTOM[1] - NAVY_TOP[1]) * tx)
            b = int(NAVY_TOP[2] + (NAVY_BOTTOM[2] - NAVY_TOP[2]) * tx)
            px[x, y] = (r, g, b)
    return base


def build_logo():
    bg = make_gradient_bg(SIZE)

    # squircle mask
    mask = Image.new("L", (SIZE, SIZE), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=CORNER_RADIUS, fill=255)

    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0), mask)

    draw = ImageDraw.Draw(canvas)

    # --- Photo card (centered, nudged slightly up-left to leave room for
    # the stamp badge overlapping its bottom-right corner) ---
    card_w, card_h = int(236 * SCALE), int(172 * SCALE)
    card_x = (SIZE - card_w) // 2 - int(14 * SCALE)
    card_y = (SIZE - card_h) // 2 - int(14 * SCALE)
    card_radius = int(16 * SCALE)

    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=card_radius, fill=CARD_BG
    )

    # mountain + sun scene, clipped to the card
    scene = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(scene)
    sun_r = int(19 * SCALE)
    sdraw.ellipse(
        [card_x + card_w - int(68 * SCALE), card_y + int(28 * SCALE) - sun_r,
         card_x + card_w - int(68 * SCALE) + sun_r * 2, card_y + int(28 * SCALE) + sun_r],
        fill=SUN
    )
    sdraw.polygon(
        [
            (card_x, card_y + card_h),
            (card_x + int(86 * SCALE), card_y + int(74 * SCALE)),
            (card_x + int(132 * SCALE), card_y + int(116 * SCALE)),
            (card_x + int(188 * SCALE), card_y + int(46 * SCALE)),
            (card_x + card_w, card_y + card_h),
        ],
        fill=MOUNTAIN_DARK
    )
    sdraw.polygon(
        [
            (card_x, card_y + card_h),
            (card_x + int(58 * SCALE), card_y + int(96 * SCALE)),
            (card_x + int(96 * SCALE), card_y + int(132 * SCALE)),
            (card_x + card_w, card_y + card_h),
        ],
        fill=MOUNTAIN_LIGHT
    )

    card_mask = Image.new("L", (SIZE, SIZE), 0)
    cmdraw = ImageDraw.Draw(card_mask)
    cmdraw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=card_radius, fill=255
    )
    canvas.paste(Image.alpha_composite(canvas.crop((0, 0, SIZE, SIZE)), scene), (0, 0), card_mask)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=card_radius, outline=(11, 35, 56), width=int(4 * SCALE)
    )

    # --- Stamp badge: small coral circle overlapping the card's
    # bottom-right corner, white ring, bold white "W", slightly rotated ---
    stamp_r = int(82 * SCALE)
    stamp_cx = card_x + card_w - int(18 * SCALE)
    stamp_cy = card_y + card_h - int(10 * SCALE)

    stamp_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    stdraw = ImageDraw.Draw(stamp_layer)
    stdraw.ellipse(
        [stamp_cx - stamp_r, stamp_cy - stamp_r, stamp_cx + stamp_r, stamp_cy + stamp_r],
        fill=CORAL
    )
    ring_w = int(6 * SCALE)
    stdraw.ellipse(
        [stamp_cx - stamp_r, stamp_cy - stamp_r, stamp_cx + stamp_r, stamp_cy + stamp_r],
        outline=WHITE, width=ring_w
    )

    w_font = ImageFont.truetype(FONT_BOLD, int(74 * SCALE))
    bbox = stdraw.textbbox((0, 0), "W", font=w_font)
    w_w, w_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    stdraw.text(
        (stamp_cx - w_w / 2 - bbox[0], stamp_cy - w_h / 2 - bbox[1]),
        "W", font=w_font, fill=WHITE
    )

    stamp_layer = stamp_layer.rotate(-12, resample=Image.BICUBIC, center=(stamp_cx, stamp_cy))
    canvas = Image.alpha_composite(canvas, stamp_layer)

    # re-apply squircle mask to keep the outer silhouette crisp
    final = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    final.paste(canvas, (0, 0), mask)

    final = final.resize((512, 512), Image.LANCZOS)
    return final


if __name__ == "__main__":
    logo = build_logo()
    logo.save("logo.png")
    print("Saved logo.png", logo.size)
