"""Draws a frame with the game's own ASCII font, the way the game does.

Uses the bold 45 x 82 glyph table, the one the game picks on a 3840 x 2160 screen (an 85 x 26 grid).
Needs font/ next to this (kept out of git, it's the game's): tex_ascii_table_45x82_Bold.png and charmap.json.
"""
import json
import os

import numpy as np
from PIL import Image

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font")
GW, GH = 45, 82                # a glyph's size in the table
COLS, ROWS = 85, 26            # the game's grid on a 3840 x 2160 screen
SCREEN_W, SCREEN_H = 3840, 2160

_masks = None
_charmap = None
_tiles = {}
_unknown = set()


def _load():
    global _masks, _charmap
    if _masks is None:
        atlas = np.asarray(Image.open(os.path.join(FONT_DIR, "tex_ascii_table_45x82_Bold.png")).convert("L"),
                           dtype=np.uint16)
        # glyphs are black on white, so flip them to get the mask
        _masks = (255 - atlas).reshape(16, GH, 16, GW).transpose(0, 2, 1, 3).reshape(256, GH, GW)
        _charmap = json.load(open(os.path.join(FONT_DIR, "charmap.json"), encoding="utf-8"))


def glyph_index(ch):
    """A character's place in the table: its code up to 127, then charmap.json. Unknown ones draw as a space."""
    o = ord(ch)
    if o <= 127:
        return o
    i = _charmap.get(ch, -1)
    if i < 0:
        if ch not in _unknown:
            _unknown.add(ch)
            print("game_font: no glyph for %r (U+%04X), drawn blank" % (ch, o))
        return 32
    return i


def tile(ch, fg, bg):
    """One cell: the glyph in fg over bg."""
    key = (ch, fg, bg)
    t = _tiles.get(key)
    if t is None:
        if len(_tiles) > 60000:
            _tiles.clear()
        m = _masks[glyph_index(ch)][..., None]                     # 0..255
        f = np.array(fg, dtype=np.uint16)
        b = np.array(bg, dtype=np.uint16)
        t = ((b * (255 - m) + f * m) // 255).astype(np.uint8)
        _tiles[key] = t
    return t


def draw(grid):
    """A full 3840 x 2160 RGB screen from rows of [glyph, fg, bg] (from preview_frames.compose), grid centered."""
    _load()
    rows, cols = len(grid), len(grid[0])
    out = np.zeros((SCREEN_H, SCREEN_W, 3), dtype=np.uint8)
    x0 = (SCREEN_W - cols * GW) // 2
    y0 = (SCREEN_H - rows * GH) // 2
    for y, row in enumerate(grid):
        py = y0 + y * GH
        for x, (ch, fg, bg) in enumerate(row):
            if ch in " #" and bg == (0, 0, 0):
                continue
            px = x0 + x * GW
            out[py:py + GH, px:px + GW] = tile(ch if ch != "#" else " ", tuple(fg), tuple(bg))
    return out
