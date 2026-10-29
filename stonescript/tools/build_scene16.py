"""Builds the art for scene 16 (the world looks up).

    python -I build_scene16.py <package dir>

Writes Art16Mouth.txt: the Boiling Mine's mouth at night, the Pushers without their carts, the Stream's far beam,
light trails and steam. The wide shot reuses scene 6's mountain.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_scene1 import Grid, Exporter, frames_of, CHAR, TEX, MIDG, BACK
from build_scene7 import crop

CW, CH = 200, 72
HORIZON = 46
BACK_EDGE, FEET, RAIL, FRONT_EDGE = 47, 51, 52, 55
MOUTH_X = 170                     # the mouth's middle
POST_L, POST_R = 158, 182         # the portal's posts
LINTEL = 42
LAMPS = [(155, 44), (185, 44)]

ROCK = "#1b1f25"
LIT = "#7a8492"
SHADED = "#3a414b"
EDGE = "#8c96a4"
HILL = "#15181c"
HILL_EDGE = "#3a414b"
GROUND = "#16171a"
GROUND_EDGE = "#6a6e74"
STONE = "#4a4e54"
NEAR = "#0e1013"
TIMBER = "#7a5a3c"
TIMBER_DIM = "#4e3a28"
RAILC = "#7c7c7c"
LAMP = "#ffb35c"
BEAM = "#2f6f48"
STEAM = "#6a6e74"


def cliff(y):
    """The cliff's left edge at row y."""
    return int(round(150 - (HORIZON - y) * 0.22 + 1.4 * math.sin(y * 0.7) + 0.8 * math.sin(y * 1.9)))


def build_mouth():
    r = random.Random(161)
    back = Grid(CW, CH)
    front = Grid(CW, CH)
    # far hills along the horizon on the left
    for x in range(0, 152):
        top = HORIZON - 3 + 1.6 * math.sin(x * 0.05) + 0.8 * math.sin(x * 0.13 + 2)
        t = int(round(top))
        for y in range(t, HORIZON + 1):
            back.blank(x, y, x, y, HILL)
            if y > t and r.random() < 0.06:
                back.set(x, y, ".", HILL_EDGE)
        nt = int(round(HORIZON - 3 + 1.6 * math.sin((x + 1) * 0.05) + 0.8 * math.sin((x + 1) * 0.13 + 2)))
        back.set(x, t, "_" if nt == t else ("\\" if nt > t else "/"), HILL_EDGE)
    # the mountain's foot: a dark cliff on the right, moonlit edge, strata and cracks
    for y in range(0, HORIZON + 1):
        e = cliff(y)
        for x in range(e, CW):
            back.blank(x, y, x, y, ROCK)
            p = r.random()
            d = x - e
            if d < 3 and p < 0.45:
                back.set(x, y, r.choice(":'`."), LIT)
            elif (y + x // 9) % 6 == 0 and p < 0.35:
                back.set(x, y, r.choice("_-"), SHADED)
            elif p < 0.1:
                back.set(x, y, r.choice(".'`"), SHADED)
        ne = cliff(y + 1) if y < HORIZON else e
        back.set(e, y, "|" if ne == e else ("/" if ne > e else "\\"), EDGE)
    for x0, y0, n in ((162, 6, 7), (176, 14, 9), (190, 3, 8), (168, 26, 6)):
        for k in range(n):
            back.set(x0 + (k % 3 == 2), y0 + k, r.choice("|/"), SHADED)
    # the mouth: timber portal, dark inside, rubble at its sides
    for y in range(LINTEL, FEET + 1):
        for x in range(POST_L + 1, POST_R):
            if y > LINTEL:
                back.blank(x, y, x, y, "#000000")
    back.text(POST_L, LINTEL, "╔" + "═" * (POST_R - POST_L - 1) + "╗", TIMBER)
    for y in range(LINTEL + 1, FEET + 1):
        back.set(POST_L, y, "║", TIMBER)
        back.set(POST_R, y, "║", TIMBER)
    for x in range(POST_L + 3, POST_R - 2, 4):
        back.set(x, LINTEL + 1, "╨", TIMBER_DIM)
    back.text(POST_L - 1, LINTEL - 1, "_" * (POST_R - POST_L + 3), EDGE)
    for x, y in ((POST_L - 3, FEET), (POST_L - 2, FEET - 1), (POST_R + 2, FEET), (POST_R + 3, FEET - 1)):
        back.set(x, y, r.choice("o.,"), STONE)
    # the lanterns either side, on brackets out of the rock
    for lx, ly in LAMPS:
        back.text(lx - 1, ly - 1, " _ ", MIDG)
        back.set(lx - 1, ly, "[", LAMP)
        back.set(lx + 1, ly, "]", LAMP)
        back.blank(lx, ly, lx, ly, "#000000")
        back.set(lx, ly + 1, "¯", MIDG)
        side = 1 if lx < MOUTH_X else -1
        back.set(lx + side * 2, ly - 1, "─", TIMBER_DIM)
    # the ground seen low, rails running into the mouth, scree in front
    for x in range(CW):
        inside = POST_L < x < POST_R
        if x < POST_R + 2:
            for y in range(BACK_EDGE, FRONT_EDGE):
                if not inside or y > FEET:
                    back.blank(x, y, x, y, GROUND)
                    if y not in (RAIL,) and r.random() < 0.06:
                        back.set(x, y, r.choice(".,'`"), TEX)
            if not inside:
                back.set(x, BACK_EDGE, r.choice("_._-") if r.random() < 0.8 else r.choice("o."), GROUND_EDGE)
                if r.random() < 0.05:
                    back.set(x, BACK_EDGE - 1, r.choice(".o"), STONE)
        if x <= MOUTH_X + 8:
            back.set(x, RAIL, "═", RAILC if x < POST_L else BACK)
        for y in range(FRONT_EDGE, CH):
            front.blank(x, y, x, y, NEAR)
            if y > FRONT_EDGE and r.random() < 0.08:
                front.set(x, y, r.choice(".'`,:"), TEX)
        front.set(x, FRONT_EDGE, r.choice("¯¯¯-'") if r.random() < 0.85 else "o", GROUND_EDGE)
    # rocks along the near edge, an old sleeper or two thrown aside
    for x in (12, 37, 61, 79, 104, 131, 146):
        front.rows(x, FRONT_EDGE - 1, [" _ ", "(_)"], STONE)
    for x in (24, 92):
        back.text(x, BACK_EDGE + 1, "═╤═", TIMBER_DIM)
    return back, front


def main():
    pkg = sys.argv[1]
    os.makedirs(pkg, exist_ok=True)
    head = "// Generated by tools/build_scene16.py. Don't edit by hand; change the script and rebuild.\n"
    ex = Exporter(head)
    back, front = build_mouth()
    half = CW // 2
    ex.piece("mouthA", [crop(back, 0, 0, half, CH)])
    ex.piece("mouthB", [crop(back, half, 0, CW - half, CH)])
    ex.value("half", half)
    ex.value("cw", CW)
    ex.value("ch", CH)
    ex.value("horizon", HORIZON)
    ex.value("feet", FEET)
    ex.value("mouthX", MOUTH_X)
    ex.value("postL", POST_L)
    ex.value("lampX", [x for x, _ in LAMPS])
    ex.value("lampY", [y for _, y in LAMPS])
    ex.piece("nearA", [crop(front, 0, 0, half, CH)])
    ex.piece("nearB", [crop(front, half, 0, CW - half, CH)])
    ex.piece("lamp", frames_of([["*"], ["+"], ["*"], ["·"]], LAMP))
    ex.piece("steam", frames_of([["~"], ["-"], ["·"]], STEAM))
    # Pushers facing right: walking (the game's push), standing, shading their eyes to look up
    walk = [["  O", " /¯", legs] for legs in ("/| ", "v| ", " |>", "/ \\")]
    stand = ["  O ", " /| ", "/ \\ "]
    look = ["  O_", " /| ", "/ \\ "]
    ex.piece("body", frames_of(walk + [stand, look], CHAR))
    # the Stream's beam far off over the summit, streaks rising
    beam = []
    for k in range(4):
        rows = []
        for y in range(24):
            ph = (y + k * 2) % 8
            rows.append("|" if ph < 3 else ("'" if ph == 3 else " "))
        beam.append(rows)
    ex.piece("beam", frames_of(beam, BEAM))
    # light trails picked by slope, and the glint where a light passes
    ex.piece("trail", frames_of([["-"], ["~"], ["'"], ["."], ["_"], ["·"]], "#ffffff"))
    ex.piece("spark", frames_of([["*"], ["+"], ["·"]], "#ffffff"))
    size = ex.write(os.path.join(pkg, "Art16Mouth.txt"))
    print(f"Art16Mouth {size} bytes")


if __name__ == "__main__":
    main()
