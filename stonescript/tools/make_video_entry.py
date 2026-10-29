"""Writes entries/Video.txt, the YouTube video's entry: 3 s of black, then the whole film with Options.video set.

    python make_video_entry.py

The scene chain is copied from Main.txt, so run this again whenever Main changes.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
main = open(os.path.join(HERE, "..", "Deltahead", "Main.txt"), encoding="utf-8").read()
i = main.index("  :?part = 1\n")
j = main.index("    // it ends on the Deltahead and stays there, leave the waterfall to get out\n")
films = "\n".join("var film%d = %s" % (n, "new Deltahead/Scene1" if n == 1 else "null") for n in range(1, 18))
out = """// for the YouTube video only (not in the package): 3 s of black, then the whole film the way Main
// plays it, with the video's own ending. render_4k.py runs it instead of Main. the scene chain is
// copied from Main by make_video_entry.py, so run that again if Main changes

var opt = import Deltahead/Options
var black = 0
""" + films + """
var part = 0

opt.video = true
opt.filmOn = true
?string.Equals(loc.id, "waterfall")
  ?part = 0
    black++
    ?black >= 90
      part = 1
      film1.Update()
""" + main[i:j]
open(os.path.join(HERE, "entries", "Video.txt"), "w", encoding="utf-8", newline="\n").write(out)
print("entries/Video.txt:", len(out.splitlines()), "lines")
