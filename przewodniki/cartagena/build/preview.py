# -*- coding: utf-8 -*-
"""Podgląd map w PNG (tylko do kontroli składu, nie wchodzi do książki)."""
import os
import sys

import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/mapy"
os.makedirs(OUT, exist_ok=True)
for n in (1, 2, 3, 4):
    src = os.path.join(HERE, f"maps/mapa{n}.svg")
    dst = os.path.join(OUT, f"mapa{n}.png")
    cairosvg.svg2png(url=src, write_to=dst, scale=2.0)
    print(dst)
