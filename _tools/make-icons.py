#!/usr/bin/env python3
"""Render the eJukebox Music mark out to real icon files.

The favicon on this site was only ever an inline SVG data: URI in the layout.
That paints instantly, which is why it stays, but Google will not use a
data-URI favicon beside a search result - it wants one at a crawlable URL -
and iOS wants a real 180px tile on an opaque ground or it screenshots the page.

The mark is four equaliser bars, the same geometry as the data URI in
_layouts/default.html, on the site ground #120c11. Ember #ff7a55 for the two
tall middle bars, brass #e6b35c for the two short outer ones.

Run from the repo root:  python _tools/make-icons.py
Writes: assets/favicon.svg, assets/favicon-32.png, assets/apple-touch-icon.png,
        assets/icon-192.png, assets/icon-512.png, favicon.ico
"""

import os
from PIL import Image, ImageDraw

GROUND = "#120c11"
EMBER = "#ff7a55"
BRASS = "#e6b35c"

# x, y, w, h, colour - in the 32x32 viewBox the layout uses.
BARS = [
    (6.0, 18.0, 3.6, 7.0, BRASS),
    (12.0, 12.0, 3.6, 13.0, EMBER),
    (18.0, 7.0, 3.6, 18.0, EMBER),
    (24.0, 15.0, 3.6, 10.0, BRASS),
]

SS = 8  # supersample factor, then downsample with LANCZOS


def render(size, rounded=True, pad=0.0):
    """One icon. pad is extra breathing room as a fraction of the tile."""
    big = size * SS
    im = Image.new("RGB", (big, big), GROUND)
    d = ImageDraw.Draw(im)

    if rounded:
        # Rounded ground on a transparent tile, for the browser tab.
        im = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=7 / 32 * big, fill=GROUND)

    inner = big * (1 - 2 * pad)
    off = big * pad
    k = inner / 32.0
    for x, y, w, h, colour in BARS:
        d.rounded_rectangle(
            [off + x * k, off + y * k, off + (x + w) * k, off + (y + h) * k],
            radius=1.8 * k,
            fill=colour,
        )
    return im.resize((size, size), Image.LANCZOS)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(root, "assets")

    render(32).save(os.path.join(assets, "favicon-32.png"))
    # iOS does not honour transparency and applies its own corner radius,
    # so this one is square, full bleed, with the mark inset.
    render(180, rounded=False, pad=0.16).convert("RGB").save(
        os.path.join(assets, "apple-touch-icon.png")
    )
    render(192).save(os.path.join(assets, "icon-192.png"))
    render(512).save(os.path.join(assets, "icon-512.png"))

    # favicon.ico at the repo root, so the browser default path resolves.
    ico = render(64)
    ico.save(
        os.path.join(root, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )
    print("icons written")


if __name__ == "__main__":
    main()
