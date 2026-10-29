"""Rebuilds the generated art and copies the Deltahead package into the game's Stonescript folder.

    python -I tools/install.py

Only the Deltahead folder is written; nothing else in the Stonescript folder is touched.
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(os.path.dirname(HERE), "Deltahead")
GAME = os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Martian Rex, Inc_", "Stone Story",
                    "76561199517219732", "Stonescript", "Deltahead")

for builder in ("build_scene1.py", "build_scene2.py", "build_scene3.py", "build_scene4.py", "build_scene5.py",
                "build_scene6.py", "build_scene7.py", "build_scene8.py", "build_scene9.py", "build_scene10.py", "build_scene11.py", "build_scene12.py", "build_scene13.py", "build_scene14.py", "build_scene15.py", "build_scene16.py", "build_constellation.py", "build_places.py", "build_light16.py", "build_scene17.py", "build_title.py"):
    subprocess.run([sys.executable, "-I", os.path.join(HERE, builder), PKG], check=True)
current = {n for n in os.listdir(PKG) if n.endswith(".txt")}
# anything after an import or new path on its line (like a comment) breaks the file in game ("Incomplete
# parsing") even though the simulator reads it fine
bad = []
for name in sorted(current):
    for i, line in enumerate(open(os.path.join(PKG, name), encoding="utf-8"), 1):
        m = re.match(r"\s*(var )?([\w.]+ = )?(import|new) \S+(.*)$", line.rstrip("\n"))
        if m and m.group(4).strip():
            bad.append(f"{name}:{i}: {line.strip()}")
if bad:
    sys.exit("not installed, the game can't read these lines:\n" + "\n".join(bad))
os.makedirs(GAME, exist_ok=True)
for name in sorted(current):
    shutil.copy2(os.path.join(PKG, name), os.path.join(GAME, name))
    print("installed", name)
# clear out stale files nothing imports
for name in sorted(os.listdir(GAME)):
    if name.endswith(".txt") and name not in current:
        os.remove(os.path.join(GAME, name))
        print("removed old", name)
