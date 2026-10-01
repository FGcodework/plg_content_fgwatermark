#!/usr/bin/env python3
"""
make_banner_fgwatermark.py

Generates the JED submission banner (1200x525) for plg_content_fgwatermark,
following the established FG series banner convention:
  - navy gradient background (#081D32 -> #113758) with soft blurred
    decorative circles
  - icon badge (rounded-square navy tile) top-left, reusing the plugin's own
    assets/logo.png, with a "{Type} plugin" caption centered below it
  - right side: title ("FG" in coral #FF6B4A + rest of name in white bold),
    an italic white subtitle/tagline, a thin coral divider, then a bulleted
    feature list (coral dot + bold white headline + lighter description)
  - text rendered via PIL using the bundled DejaVu Sans TTF files directly
    (deterministic glyphs, no system-font substitution risk)

Usage: python3 make_banner_fgwatermark.py
Output: banner.png (1200x525) next to this script.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 1200, 525

# Sampled from the reference fgremovegenerator banner - lighter/bluer than a
# pure top-to-bottom navy fade, blended mostly left-to-right.
GRAD_TL = (12, 47, 80)
GRAD_BR = (39, 81, 119)

CORAL = (255, 107, 74)       # #FF6B4A
WHITE = (255, 255, 255)
LIGHT_GRAY_BLUE = (168, 188, 209)

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"

LOGO_PATH = "assets/logo.png"


def make_gradient_bg():
    base = Image.new("RGB", (W, H), GRAD_TL)
    px = base.load()
    for y in range(H):
        ty = y / (H - 1)
        for x in range(W):
            tx = x / (W - 1)
            t = tx * 0.75 + ty * 0.25
            r = int(GRAD_TL[0] + (GRAD_BR[0] - GRAD_TL[0]) * t)
            g = int(GRAD_TL[1] + (GRAD_BR[1] - GRAD_TL[1]) * t)
            b = int(GRAD_TL[2] + (GRAD_BR[2] - GRAD_TL[2]) * t)
            px[x, y] = (r, g, b)
    return base


def add_blurred_circles(base):
    """Soft, subtle white glows only - no coral blobs, kept low-opacity and
    heavily blurred so they read as gentle ambient light, not shapes."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    circles = [
        (980, 470, 260, (255, 255, 255, 16)),
        (230, 470, 220, (255, 255, 255, 12)),
        (1050, 60, 200, (255, 255, 255, 10)),
    ]

    for cx, cy, r, color in circles:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    overlay = overlay.filter(ImageFilter.GaussianBlur(90))
    base = base.convert("RGBA")
    base = Image.alpha_composite(base, overlay)
    return base.convert("RGB")


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[1]


def draw_caption_centered(draw, cx, y, text, font, fill):
    w, h, top = text_size(draw, text, font)
    draw.text((cx - w / 2, y - top), text, font=font, fill=fill)


def paste_icon_badge(base, tile_y):
    icon_size = 220
    tile_x = 70
    tile_y = int(round(tile_y))

    # crisper, more visible offset shadow (a "layered card" look, matching
    # the reference banner rather than a heavily-blurred soft glow)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle(
        [tile_x + 16, tile_y + 18, tile_x + icon_size + 16, tile_y + icon_size + 18],
        radius=44, fill=(0, 0, 0, 130)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    base = base.convert("RGBA")
    base = Image.alpha_composite(base, shadow)

    logo = Image.open(LOGO_PATH).convert("RGBA").resize((icon_size, icon_size), Image.LANCZOS)
    base.alpha_composite(logo, (tile_x, tile_y))

    return base.convert("RGB"), tile_x, icon_size


def build_banner():
    base = make_gradient_bg()
    base = add_blurred_circles(base)

    probe = ImageDraw.Draw(base)

    # --- Fonts ---
    title_font = ImageFont.truetype(FONT_BOLD, 68)
    tagline_font = ImageFont.truetype(FONT_ITALIC, 27)
    headline_font = ImageFont.truetype(FONT_BOLD, 25)
    desc_font = ImageFont.truetype(FONT_REGULAR, 20)
    caption_font = ImageFont.truetype(FONT_BOLD, 22)

    content_x = 360
    features = [
        ("Image & text watermarks", "Logo overlay, text overlay, or both - positioned and styled independently"),
        ("SVG logo support", "Rasterized automatically via Imagick - no manual PNG conversion needed"),
        ("Cached & atomic writes", "Nothing re-rendered per page load; source images are never modified"),
        ("Native Joomla 4/5/6", "PSR-4, DI service provider, SubscriberInterface architecture"),
    ]

    # --- Measure the right-hand text block so it can be vertically centered ---
    _, title_h, _ = text_size(probe, "FG Watermark", title_font)
    _, tagline_h, _ = text_size(probe, "Ag", tagline_font)
    row_h = 68
    _, desc_h, _ = text_size(probe, "Ag", desc_font)

    gap_title_tagline = 24
    gap_tagline_divider = 26
    gap_divider_bullets = 34

    text_block_h = (
        title_h + gap_title_tagline + tagline_h + gap_tagline_divider + 3
        + gap_divider_bullets + row_h * (len(features) - 1) + 32 + desc_h
    )
    text_top = (H - text_block_h) / 2

    # --- Measure the icon block so it can be vertically centered too ---
    icon_size = 220
    gap_icon_caption = 26
    _, caption_h, _ = text_size(probe, "Ag", caption_font)
    icon_block_h = icon_size + gap_icon_caption + caption_h
    icon_top = (H - icon_block_h) / 2

    # --- Icon + caption ---
    base, tile_x, icon_size = paste_icon_badge(base, icon_top)
    draw = ImageDraw.Draw(base)
    draw_caption_centered(
        draw, tile_x + icon_size / 2, icon_top + icon_size + gap_icon_caption,
        "Content Plugin", caption_font, LIGHT_GRAY_BLUE
    )

    # --- Title ---
    title_y = text_top
    fg_text = "FG"
    rest_text = " Watermark"
    _, _, title_top = text_size(draw, "FG Watermark", title_font)
    draw.text((content_x, title_y - title_top), fg_text, font=title_font, fill=CORAL)
    fg_w, _, _ = text_size(draw, fg_text, title_font)
    draw.text((content_x + fg_w, title_y - title_top), rest_text, font=title_font, fill=WHITE)

    # --- Tagline ---
    tagline_y = title_y + title_h + gap_title_tagline
    _, _, tagline_top = text_size(draw, "Ag", tagline_font)
    draw.text(
        (content_x, tagline_y - tagline_top),
        "Automatic image & text watermarking for Joomla articles",
        font=tagline_font, fill=WHITE
    )

    # --- Divider ---
    divider_y = tagline_y + tagline_h + gap_tagline_divider
    draw.line([(content_x, divider_y), (1140, divider_y)], fill=CORAL, width=3)

    # --- Feature bullets ---
    dot_r = 6
    bullet_y = divider_y + 3 + gap_divider_bullets

    for headline, desc in features:
        dot_cy = bullet_y + 14
        draw.ellipse(
            [content_x, dot_cy - dot_r, content_x + dot_r * 2, dot_cy + dot_r],
            fill=CORAL
        )
        text_x = content_x + dot_r * 2 + 18
        draw.text((text_x, bullet_y), headline, font=headline_font, fill=WHITE)
        draw.text((text_x, bullet_y + 32), desc, font=desc_font, fill=LIGHT_GRAY_BLUE)
        bullet_y += row_h

    return base


if __name__ == "__main__":
    banner = build_banner()
    banner.save("banner.png")
    print("Saved banner.png", banner.size)
