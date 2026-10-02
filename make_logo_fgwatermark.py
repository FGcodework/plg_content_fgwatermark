#!/usr/bin/env python3
"""
make_logo_fgwatermark.py

Generates assets/logo.svg and assets/logo.png for plg_content_fgwatermark,
following the FG logo convention:
  - 512x512, squircle corner radius rx=95 (~18.5%, matches the JED banner
    template's .logo-inner frame rounding)
  - navy gradient background #081D32 -> #113758, coral #FF6B4A accent
  - flat shapes only: no drop shadow, no glow, no blur (a baked-in shadow
    leaves a grey halo on non-matching backgrounds; soft effects also turn
    to mush at favicon sizes)

Mark concept: a photo frame with a coral water droplet overlapping its
bottom-right corner, and a "W" framed by viewfinder corner brackets inside
the droplet - "water" + "mark" (and the brackets read as "marked region").

The "W" is drawn as a vector path extracted from DejaVu Sans Bold with
fontTools, so logo.svg is fully portable (no font dependency when viewed
on GitHub or elsewhere).

Usage: python3 make_logo_fgwatermark.py   (needs rsvg-convert on PATH)
Output: logo.svg and logo.png (512x512) in the current directory.
"""

import math
import subprocess

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY_TOP = "#081D32"
NAVY_BOTTOM = "#113758"
CORAL = "#FF6B4A"
CORAL_LIGHT = "#FF9A82"
CARD = "#F4F7FA"
SKY = "#C4DCF0"
SUN = "#FFC94A"
MOUNTAIN_FAR = "#2B6A9E"
MOUNTAIN_MID = "#164569"
MOUNTAIN_DARK = "#0E2C48"


def glyph_path(char, cx, cy, target_width):
    """Vector outline of `char` (DejaVu Sans Bold), centered on (cx, cy)."""
    font = TTFont(FONT_BOLD)
    glyphs = font.getGlyphSet()
    name = font.getBestCmap()[ord(char)]

    bounds = BoundsPen(glyphs)
    glyphs[name].draw(bounds)
    xmin, ymin, xmax, ymax = bounds.bounds

    s = target_width / (xmax - xmin)
    tx = cx - s * (xmin + xmax) / 2
    ty = cy + s * (ymin + ymax) / 2

    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}")
    glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, tx, ty)))
    return pen.getCommands()


def droplet_path(tip, center, radius):
    """Teardrop: sharp tip, slightly concave flanks, round bulb. The flanks
    leave the bulb along its tangent lines (smooth join) and are pulled
    slightly inward near the tip."""
    px, py = tip
    cx, cy = center
    d = cy - py
    theta = math.asin(radius / d)
    tangent_len = math.sqrt(d * d - radius * radius)

    def side(sign):
        dx, dy = sign * math.sin(theta), math.cos(theta)
        tx, ty = px + tangent_len * dx, py + tangent_len * dy
        # control 1: on the line near the tip, nudged toward the axis (concave)
        c1 = (px + 0.32 * tangent_len * dx - sign * 9, py + 0.32 * tangent_len * dy)
        # control 2: on the tangent line just before T (keeps the join smooth)
        c2 = (tx - 0.38 * tangent_len * dx, ty - 0.38 * tangent_len * dy)
        return (tx, ty), c1, c2

    (tr, c1r, c2r) = side(+1)
    (tl, c1l, c2l) = side(-1)

    return (
        f"M{px:.2f},{py:.2f} "
        f"C{c1r[0]:.2f},{c1r[1]:.2f} {c2r[0]:.2f},{c2r[1]:.2f} {tr[0]:.2f},{tr[1]:.2f} "
        f"A{radius},{radius} 0 1 1 {tl[0]:.2f},{tl[1]:.2f} "
        f"C{c2l[0]:.2f},{c2l[1]:.2f} {c1l[0]:.2f},{c1l[1]:.2f} {px:.2f},{py:.2f} Z"
    )


def bracket_paths(cx, cy, half_w, half_h, arm):
    """Four L-shaped viewfinder corners around (cx, cy)."""
    x0, x1 = cx - half_w, cx + half_w
    y0, y1 = cy - half_h, cy + half_h
    return [
        f"M{x0:.1f},{y0 + arm:.1f} L{x0:.1f},{y0:.1f} L{x0 + arm:.1f},{y0:.1f}",
        f"M{x1 - arm:.1f},{y0:.1f} L{x1:.1f},{y0:.1f} L{x1:.1f},{y0 + arm:.1f}",
        f"M{x0:.1f},{y1 - arm:.1f} L{x0:.1f},{y1:.1f} L{x0 + arm:.1f},{y1:.1f}",
        f"M{x1 - arm:.1f},{y1:.1f} L{x1:.1f},{y1:.1f} L{x1:.1f},{y1 - arm:.1f}",
    ]


def build_svg():
    # droplet geometry (bulb bottom-right, overlapping the frame corner)
    bulb_c = (352, 330)
    bulb_r = 86
    tip = (352, 196)
    drop_d = droplet_path(tip, bulb_c, bulb_r)

    w_d = glyph_path("W", bulb_c[0], bulb_c[1] + 3, 54)
    brackets = bracket_paths(bulb_c[0], bulb_c[1] + 2, 49, 43, 19)
    bracket_svg = "\n      ".join(
        f'<path d="{b}"/>' for b in brackets
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{NAVY_TOP}"/>
      <stop offset="100%" stop-color="{NAVY_BOTTOM}"/>
    </linearGradient>
    <clipPath id="squircle">
      <rect x="0" y="0" width="512" height="512" rx="95" ry="95"/>
    </clipPath>
    <clipPath id="scene">
      <rect x="104" y="120" width="256" height="224" rx="20" ry="20"/>
    </clipPath>
  </defs>

  <g clip-path="url(#squircle)">
    <rect x="0" y="0" width="512" height="512" fill="url(#bg)"/>

    <!-- photo frame, slightly tilted -->
    <g transform="rotate(-5 232 232)">
      <rect x="82" y="98" width="300" height="268" rx="36" ry="36" fill="{CARD}"/>
      <g clip-path="url(#scene)">
        <rect x="104" y="120" width="256" height="224" fill="{SKY}"/>
        <circle cx="306" cy="172" r="26" fill="{SUN}"/>
        <polygon points="96,292 168,206 214,236 150,318" fill="{MOUNTAIN_FAR}"/>
        <polygon points="104,310 226,176 372,268 372,330 104,330" fill="{MOUNTAIN_MID}"/>
        <rect x="104" y="288" width="256" height="60" fill="{MOUNTAIN_DARK}"/>
      </g>
    </g>

    <!-- water droplet -->
    <path d="{drop_d}" fill="{CORAL}" stroke="{CARD}" stroke-width="6" stroke-linejoin="round"/>
    <ellipse cx="{bulb_c[0] + 46}" cy="{bulb_c[1] - 52}" rx="8" ry="22"
             transform="rotate(-30 {bulb_c[0] + 46} {bulb_c[1] - 52})" fill="{CORAL_LIGHT}"/>

    <!-- viewfinder brackets + W -->
    <g fill="none" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">
      {bracket_svg}
    </g>
    <path d="{w_d}" fill="#FFFFFF"/>
  </g>
</svg>
"""


if __name__ == "__main__":
    svg = build_svg()
    with open("logo.svg", "w", encoding="utf-8") as fh:
        fh.write(svg)

    subprocess.run(
        ["rsvg-convert", "-w", "512", "-h", "512", "logo.svg", "-o", "logo.png"],
        check=True,
    )
    print("Saved logo.svg and logo.png (512x512)")
