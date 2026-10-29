# runs one entry script through ssim and prints errors, load and sounds (sim_check.py does the same for Main)
#   cd <ssim's tools folder> && python -I <this file> <entry script> [frames]
# ssim's folder comes from SSIM_TOOLS or ssim_path.txt, same as preview_frames.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SSIM_TOOLS") or open(os.path.join(HERE, "ssim_path.txt"), encoding="utf-8").readline().strip())
from ssim import Sim, Scenario
PKG = os.path.dirname(HERE)
entry = sys.argv[1]
frames = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
sc = Scenario(loc_id="waterfall", loc_name="Deadwood Waterfall", stars=0, hp=40)
sc.set("screen.w", 80)
sc.set("screen.h", 30)
sim = Sim(entry, sc, search_paths=[PKG])
res = sim.run(frames)
print("parse errors:", res.parse_errors)
errs = res.errors()
print("runtime errors:", len(errs))
for e in errs[:8]:
    print("  ", str(e)[:300])
stm = [fr.stmts for fr in res]
print("statements per frame: max", max(stm), "median", sorted(stm)[len(stm) // 2])
for fr in res:
    for c in fr.commands:
        if isinstance(c, dict) and c.get("cmd") in ("play", "ambient.Add", "music.Play"):
            print("  ", fr.index, c.get("cmd"), c.get("sound") or c.get("id"), c.get("pitch", ""))
