# runs the package through ssim (offline Stonescript simulator) and prints errors, load per frame and sound cues.
# ssim's folder comes from SSIM_TOOLS or ssim_path.txt
#   cd <ssim's tools folder> && python -I <this file> [frames]
import os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SSIM_TOOLS") or open(os.path.join(HERE, "ssim_path.txt"), encoding="utf-8").readline().strip())
from ssim import Sim, Scenario
PKG = os.path.dirname(HERE)
frames = int(sys.argv[1]) if len(sys.argv) > 1 else 1100
sc = Scenario(loc_id="waterfall", loc_name="Deadwood Waterfall", stars=0, hp=40)
sim = Sim(PKG + r"\Deltahead\Main.txt", sc, search_paths=[PKG])
res = sim.run(frames)
print("parse errors:", res.parse_errors)
errs = res.errors()
print("runtime errors:", len(errs))
seen = collections.OrderedDict()
for e in errs:
    k = str(e)[:220]
    seen[k] = seen.get(k, 0) + 1
for k, n in list(seen.items())[:15]:
    print(f"  x{n}: {k}")
for attr in ("stmt_counts", "statements", "cpu"):
    if hasattr(res, attr):
        print(attr, "available")

stm = [fr.stmts for fr in res]
top = sorted(range(len(stm)), key=lambda i: -stm[i])[:6]
print("statements per frame: max", max(stm), "at frames", [(i, stm[i]) for i in top])
print("median", sorted(stm)[len(stm) // 2])
sounds = [(fr.index, c) for fr in res for c in fr.commands if "play" in str(c) or "ambient" in str(c).lower() or "music" in str(c).lower()]
print("audio events:", len(sounds))
for i, c in sounds[:20]:
    print("  ", i, str(c)[:120])
ui_counts = collections.Counter()
for fr in res:
    for u in fr.ui:
        ui_counts[str(u)[:60].split("(")[0]] += 1
print("ui log kinds:", list(ui_counts.items())[:12])
print("final f =", sim.var("film").__dict__.keys() if hasattr(sim.var("film"), "__dict__") else sim.var("film"))
for fr in res[:3]:
    print("frame", fr.index, "commands", [str(c)[:80] for c in fr.commands][:8])
