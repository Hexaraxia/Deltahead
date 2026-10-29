"""Plays a preview entry in the simulator and logs each frame's screen hash and how many UI calls the script made.

    python -I perf_check.py <entry script> <frames> <out.json>
    python -I perf_check.py --compare <before.json> <after.json>

UI calls (property sets and method calls) are what costs in the game, and it lists the lines making the most.
--compare says whether every frame still looks the same and how the calls changed.
"""
import collections
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview_frames as P

P.SW, P.SH = 80, 30


_dims = {}


def page_size(sheet, frame):
    """How many cells the game walks to draw a frame of an anim: its page's rows by its longest row."""
    if sheet not in _dims:
        _dims[sheet] = [len(rows) * max([len(r) for r in rows] + [0]) for rows, _, _ in P.sheet_pages(sheet)]
    d = _dims[sheet]
    return d[frame % len(d)]


def drawn(uisys):
    """The cells the game walks to draw a frame: every canvas wherever it is, shown or not, and an anim's whole page
    (each layer) only if it and its parents are shown and some of it is on screen."""
    total = [0]

    def walk(c, px, py, hidden):
        hidden = hidden or not P.vis(c)
        p = c.props
        x, y, w, h = px + p.get("x", 0), py + p.get("y", 0), p.get("w", 10), p.get("h", 5)
        if c.TYPE == "Canvas":
            total[0] += max(0, min(w, 100)) * max(0, min(h, 27))
        elif c.TYPE == "Anim" and not hidden and -100 < x < P.SW + 100 and -100 < y < P.SH + 100:
            fr = p.get("frame", 0)
            for s in [c.sheet] + [l.sheet for l in c.layers]:
                total[0] += page_size(s, fr)
        for k in P.kids(c):
            walk(k, x, y, hidden)

    for k in P.kids(uisys.root):
        walk(k, 0, 0, False)
    return total[0]


def record(entry, frames, out):
    sim = P.new_sim(entry)
    calls = [0]
    sites = collections.Counter()
    log = sim.ui.log

    def counted(comp, op, name, value):
        calls[0] += 1
        sites["%s:%s %s %s.%s" % (sim.interp.mod_name, sim.interp.line, op, comp.TYPE, name)] += 1
        return log(comp, op, name, value)

    sim.ui.log = counted
    marks, per, stmts, cells = [], [], [], []
    for fr in range(frames):
        calls[0] = 0
        f = sim.step()
        grid = P.compose(sim.ui, fr / 30.0)
        marks.append(hashlib.md5(repr(grid).encode()).hexdigest()[:16])
        per.append(calls[0])
        stmts.append(f.stmts)
        cells.append(drawn(sim.ui))
    errors = sum(len(fr.errors) for fr in sim.result.frames)
    json.dump({"entry": entry, "marks": marks, "calls": per, "stmts": stmts, "cells": cells, "errors": errors,
               "sites": sites.most_common(40)}, open(out, "w"))
    print(f"{os.path.basename(entry)}: {frames} frames, {errors} errors, calls max {max(per)} mean "
          f"{sum(per) / len(per):.0f}, cells drawn max {max(cells)} mean {sum(cells) / len(cells):.0f}, "
          f"statements max {max(stmts)}")


def compare(a, b):
    a, b = json.load(open(a)), json.load(open(b))
    n = min(len(a["marks"]), len(b["marks"]))
    diff = [i for i in range(n) if a["marks"][i] != b["marks"][i]]
    print(f"{os.path.basename(a['entry'])}: {n} frames, {len(diff)} differ" + (f" (first at {diff[0]})" if diff else ""))
    print(f"  calls a frame: max {max(a['calls'])} -> {max(b['calls'])}, mean {sum(a['calls']) / n:.0f} -> "
          f"{sum(b['calls'][:n]) / n:.0f}; cells drawn: max {max(a['cells'])} -> {max(b['cells'])}, mean "
          f"{sum(a['cells']) / n:.0f} -> {sum(b['cells'][:n]) / n:.0f}; statements max {max(a['stmts'])} -> "
          f"{max(b['stmts'])}; errors {a['errors']} -> {b['errors']}")
    return not diff


if __name__ == "__main__":
    if sys.argv[1] == "--compare":
        ok = compare(sys.argv[2], sys.argv[3])
        sys.exit(0 if ok else 1)
    record(sys.argv[1], int(sys.argv[2]), sys.argv[3])
