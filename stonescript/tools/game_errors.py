"""Lists the script errors and warnings the game logged while playing the film, each once with a count.

    python -I game_errors.py [log]

Reads the game's current and previous Unity logs, or the log given. Missing sound and music ids show up too.
"""
import collections
import os
import re
import sys

LOGS = os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Martian Rex, Inc_", "Stone Story")


def main():
    paths = sys.argv[1:] or [os.path.join(LOGS, n) for n in ("Player-prev.log", "Player.log")]
    for path in paths:
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        found = collections.Counter()
        for line in text.split("\n"):
            m = re.match(r"(Deltahead/\w+ line \d+: .*)", line)
            if m:
                found[m.group(1).strip()] += 1
            m = re.search(r"No Location found for Key=(\S+)", line)
            if m:
                found["no such sound or music: " + m.group(1)] += 1
        print(f"== {os.path.basename(path)}: {sum(found.values())} logged, {len(found)} different")
        for msg, n in found.most_common():
            print(f"  {n:6d} x {msg}")


if __name__ == "__main__":
    main()
