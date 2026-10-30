"""Renders the film for YouTube at 3840 x 2160, 30 fps, in the game's font, with its sounds mixed in.

The grid is 96 x 30, the height the scenes are laid out for. The game itself only ever shows 25 to 27 rows, so
its 4K grid (85 x 26) cuts off the top and bottom of most scenes.

    python render_4k.py <out.mp4> <audio dir> [first frame] [last frame]

Plays entries/Video.txt till it ends, encoding on the GPU (h264_nvenc). With a first and last frame it renders
just that stretch, without sound.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview_frames as pf
import game_font as gf

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"
ENTRY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entries", "Video.txt")
LIMIT = 30000          # stop here whatever happens
GRID = (96, 30)
SOUND_CMDS = ("play", "ambient.Add", "ambient.Stop", "music.Play", "music.Stop")


def main():
    final = sys.argv[1]
    audio = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    last = int(sys.argv[4]) if len(sys.argv) > 4 else None
    whole = first == 0 and last is None
    gf.use_grid(*GRID)
    pf.SW, pf.SH = GRID
    video = final + ".video.mp4" if (audio and whole) else final
    # converted and tagged as BT.709: untagged, players read 4K as 709 while ffmpeg converts with 601, which
    # shifts the colors
    enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", "%dx%d" % (gf.SCREEN_W, gf.SCREEN_H), "-r", "30", "-i", "-",
                            "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int,"
                            "format=yuv420p",
                            "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "16",
                            "-b:v", "50M", "-maxrate", "100M", "-bufsize", "200M", "-profile:v", "high",
                            "-g", "60", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-color_range", "tv", "-bsf:v",
                            "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1",
                            "-movflags", "+faststart", video],
                           stdin=subprocess.PIPE)
    sim = pf.new_sim(ENTRY)
    events = []
    f = 0
    t0 = time.time()
    while f < LIMIT:
        fr = sim.step()
        for c in fr.commands:
            if isinstance(c, dict) and c.get("cmd") in SOUND_CMDS:
                events.append((f, c))
        if f >= first:
            enc.stdin.write(gf.draw(pf.compose(sim.ui, f / 30.0)).tobytes())
        f += 1
        if last is not None and f > last:
            break
        # stop once the last scene's over (the video entry has its own black after it)
        film = sim.var("film17")
        if film is not None and film.vars.get(sim.interp.key("over")) is True:
            break
        if f % 900 == 0:
            el = time.time() - t0
            print("frame %d (%d:%02d of film), %.0f ms a frame" % (f, f // 1800, (f // 30) % 60, el / max(1, f - first) * 1000),
                  flush=True)
    enc.stdin.close()
    enc.wait()
    if audio and whole:
        import audio_mix
        wav = final + ".wav"
        played, dropped = audio_mix.mix(events, f, audio, FFMPEG, wav)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", video, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "320k", "-shortest", "-movflags", "+faststart", final], check=True)
        os.remove(video)
        os.remove(wav)
        print("sound: %d played, %d the game would drop" % (played, dropped))
    print("wrote %s: %d frames, %d:%02d, %.1f GB" % (final, f - first, (f - first) // 1800, ((f - first) // 30) % 60,
                                                     os.path.getsize(final) / 1e9))


if __name__ == "__main__":
    main()
