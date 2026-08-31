#!/usr/bin/env python
"""Rebuild the two derivative image sets from assets/img.

GitHub Pages builds this site server-side with the whitelisted plugins only -
no Actions, no build step - so the small copies cannot be generated at deploy
time. They are generated here and committed with the sources.

    assets/img/640/<stem>.webp    640px-wide copy of anything wider. pic.html
                                  offers it through srcset, so a phone stops
                                  downloading the full desktop file.
    assets/img/thumb/<stem>.webp  copy scaled so its SHORT side is 96px, for
                                  chip-sized slots. This site has none yet, so
                                  THUMBS below is empty and no thumbs are made.

Run it from the repo root after adding, replacing or removing an image:

    python _tools/make-derivatives.py

Sources are never modified. Existing derivatives are overwritten. Every image
wider than 640px gets a 640 copy whether or not a page uses it yet, so adding
a photo to a page can never leave a srcset candidate pointing at nothing.
Needs Pillow: python -m pip install pillow
"""
import os
from PIL import Image

# Stems rendered at chip size, which are the only ones small enough to want a
# 96px source. ejukebox.music has no such slot - the sibling ejukebox.tv does.
THUMBS = []

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, 'assets', 'img')


def build(mode, stems):
    if not stems:
        print('assets/img/%s: nothing to do' % mode)
        return
    out = os.path.join(SRC, mode)
    os.makedirs(out, exist_ok=True)
    made = 0
    for stem in stems:
        path = os.path.join(SRC, stem + '.webp')
        if not os.path.exists(path):
            print('  missing source, skipped: ' + stem)
            continue
        im = Image.open(path).convert('RGB')
        w, h = im.size
        scale = 640.0 / w if mode == '640' else 96.0 / min(w, h)
        if scale >= 1:
            continue
        im.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                  Image.LANCZOS).save(os.path.join(out, stem + '.webp'),
                                      'WEBP', quality=80, method=6)
        made += 1
    print('assets/img/%s: %d files' % (mode, made))


everything = sorted(f[:-5] for f in os.listdir(SRC) if f.endswith('.webp'))
build('640', everything)
build('thumb', [s for s in THUMBS if s in everything])
