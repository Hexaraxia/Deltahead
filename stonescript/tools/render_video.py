# renders the film to an MP4 the way preview_frames.py draws it. needs Pillow and ffmpeg (C:\ffmpeg)
#   python -I render_video.py <out.mp4> [screen width] [screen height] [entry script] [audio dir] [start frame] [stop frame]
# default is 80x30 (about a maximized game window) and Deltahead/Main. sounds get captioned under the picture,
# and with a folder of the game's sounds (see audio_mix.py) you hear them too
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview_frames as pf
from PIL import Image, ImageDraw, ImageFont

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"
BAND = 40
TAIL = 60            # frames to keep after the scene ends (the "watch it again" hint)
LIMIT = 12000        # stop here whatever happens
NAMES = {
    "controller_whip_attack": "whip swing", "controller_whip_hit": "whip crack", "slave_npc": "Pusher talking",
    "first_controller": "Controller shouting", "bomb_cart_move": "rumble", "fire_geyser": "geyser",
    "stone_throw_hit": "rock impact", "mushroom_boss_fat_slam": "heavy slam",
}


def cue(c):
    """A caption for one command, or None if it makes no sound."""
    c = c if isinstance(c, dict) else {}
    kind = c.get("cmd")
    if kind == "play":
        return "♪ " + NAMES.get(c.get("sound"), str(c.get("sound")).replace("_", " "))
    if kind == "ambient.Add":
        return "ambience: " + str(c.get("id")).replace("_", " ")
    if kind == "music.Play":
        return "music: " + str(c.get("id")).replace("_", " ")
    return None


def main():
    out = sys.argv[1]
    pf.SW = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    pf.SH = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    entry = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None
    audio = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != "-" else None
    start = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    stop = int(sys.argv[7]) if len(sys.argv) > 7 else None
    final, out = out, (out + ".video.mp4" if audio else out)
    w, h = pf.SW * pf.CW, pf.SH * pf.CHH + BAND
    small = ImageFont.truetype(r"C:\Windows\Fonts\CascadiaMono.ttf", 16)
    sim = pf.new_sim(entry)
    enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{w}x{h}", "-r", "30", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-crf", "20", "-preset", "medium", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    shown = []           # (frame, caption)
    events = []          # (frame, command) for the audio mix
    end = None
    f = 0
    while f < LIMIT:
        fr = sim.step()
        for c in fr.commands:
            label = cue(c)
            if label:
                shown.append((f, label))
            if isinstance(c, dict) and c.get("cmd") in ("play", "ambient.Add", "ambient.Stop", "music.Play",
                                                         "music.Stop"):
                events.append((f, c))
        # over when every scene says it's over
        scenes = [v for v in sim.interp.main.vars.values() if hasattr(v, "vars") and sim.interp.key("over") in v.vars]
        if end is None and scenes and all(s.vars[sim.interp.key("over")] is True for s in scenes):
            end = f + TAIL
        if f < start:
            f += 1
            continue
        frame = Image.new("RGB", (w, h), (0, 0, 0))
        frame.paste(pf.render(sim.ui, f / 30.0), (0, 0))
        d = ImageDraw.Draw(frame)
        d.line([(0, h - BAND), (w, h - BAND)], fill=(40, 40, 40))
        d.text((10, h - BAND / 2), f"{f // 1800}:{(f // 30) % 60:02d}.{(f % 30) * 10 // 30}", fill=(110, 110, 110),
               font=small, anchor="lm")
        live = [lab for (s, lab) in shown if f - s < 45][-3:]
        d.text((w - 10, h - BAND / 2), "   ".join(live), fill=(200, 170, 100), font=small, anchor="rm")
        enc.stdin.write(frame.tobytes())
        f += 1
        if (end is not None and f >= end) or (stop is not None and f >= stop):
            break
    enc.stdin.close()
    enc.wait()
    if audio:
        import audio_mix
        wav = final + ".wav"
        played, dropped = audio_mix.mix(events, f, audio, FFMPEG, wav)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", out, "-ss", f"{start / 30:.3f}", "-i", wav,
                        "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "160k", "-shortest", "-movflags", "+faststart", final], check=True)
        os.remove(out)
        os.remove(wav)
        print(f"sound: {played} played, {dropped} the game would drop")
    print(f"wrote {final}: {f - start} frames, {(f - start) / 30:.1f} s, {os.path.getsize(final) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
