"""Mixes a preview video's sound from the game's own sounds.

audio_dir is the extracted sounds, kept outside the project: audio_wav/, audio_music/ and sfx_map.json (which clips
and pitch each sound id plays). Plays past about five a second get dropped, like the game does.
"""
import json
import os
import subprocess

import numpy as np

RATE = 44100
# the soundscape each ambience id plays
AMBIENT = {
    "ambient_bridge": "bridge_soundscape", "ambient_bronze_gate": "bronze_gate_soundscape",
    "ambient_cave": "remnantof5_soundscape", "ambient_caves": "caves_of_fear_soundscape",
    "ambient_cross_deadwood_wind": "wind_loop", "ambient_crypt": "haunted_crypt_soundscape",
    "ambient_deadwood": "deadewood_canyon_soundscape", "ambient_haunted_gate": "haunted_gate_soundscape",
    "ambient_icy": "icy_ridge_soundscape", "ambient_mines": "boiling_mine_soundscape",
    "ambient_mushroom": "mushroom_forest_soundscape", "ambient_pallas": "pallas_soundscape",
    "ambient_rocky": "rocky_plateau_soundscape", "ambient_temple": "temple_soundscape",
}
# the track each music id plays (the ones the film uses)
MUSIC = {"slave_outro_climb": "SS2202_MinesEnding_climb", "slave_outro_loop": "SS2201_MinesEnding_music_loop",
         "bridge_crossing": "SS7002_BridgeCrossing_new", "icy_ridge_cyan": "SS6416_IcyRidge_Cyan",
         "bronze_guardian_cyan": "SS2299_BronzeGuardian_cyan"}
SFX_GAIN = 0.8
AMBIENT_GAIN = 0.35
MUSIC_GAIN = 0.5


def _load(path, ffmpeg):
    raw = subprocess.run([ffmpeg, "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(RATE), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def mix(events, frames, audio_dir, ffmpeg, out_wav):
    """events are (frame, command) pairs, frames is the video's length. Writes out_wav, returns (played, dropped)."""
    sfx = json.load(open(os.path.join(audio_dir, "sfx_map.json"), encoding="utf-8"))
    n = int(frames / 30 * RATE) + RATE
    track = np.zeros(n, np.float32)
    cache = {}

    def clip(name, sub):
        path = os.path.join(audio_dir, sub, name + ".wav")
        if path not in cache:
            cache[path] = _load(path, ffmpeg) if os.path.exists(path) else None
        return cache[path]

    budget, last, played, dropped = 0.0, 0, 0, 0
    turn = {}
    live = {}
    spans = []
    song, song_at, songs = None, 0, []
    for f, c in events:
        kind = c.get("cmd")
        if kind == "play":
            budget = max(0.0, budget - (f - last) / 30.0)
            last = f
            if budget + 0.2 > 1.0:
                dropped += 1
                continue
            budget += 0.2
            m = sfx.get(c.get("sound"))
            if not m:
                continue
            k = turn.get(c["sound"], 0)
            turn[c["sound"]] = k + 1
            data = clip(m["clips"][k % len(m["clips"])], "audio_wav")
            if data is None:
                continue
            pitch = (c.get("pitch") or 100) / 100.0 * sum(m.get("pitch", [1.0, 1.0])) / 2
            if abs(pitch - 1) > 1e-3:
                data = np.interp(np.arange(0, len(data) - 1, pitch), np.arange(len(data)), data).astype(np.float32)
            s = int(f / 30 * RATE)
            e = min(n, s + len(data))
            track[s:e] += data[:e - s] * SFX_GAIN
            played += 1
        elif kind == "ambient.Add":
            live.setdefault(c.get("id"), f)
        elif kind == "ambient.Stop":
            spans += [(a, f0, f) for a, f0 in live.items()]
            live = {}
        elif kind in ("music.Play", "music.Stop"):
            if song:
                songs.append((song, song_at, f))
            song, song_at = (c.get("id"), f) if kind == "music.Play" else (None, 0)
    spans += [(a, f0, frames) for a, f0 in live.items()]
    if song:
        songs.append((song, song_at, frames))
    for m, f0, f1 in songs:
        data = clip(MUSIC[m], "audio_music") if m in MUSIC else None
        s, e = int(f0 / 30 * RATE), min(n, int(f1 / 30 * RATE))
        if data is None or e <= s:
            continue
        k = min(e - s, RATE)
        ramp = np.ones(e - s, np.float32)
        ramp[-k:] = np.linspace(1, 0, k)
        track[s:e] += np.resize(data, e - s) * ramp * MUSIC_GAIN
    for a, f0, f1 in spans:
        data = clip(AMBIENT[a], "audio_music") if a in AMBIENT else None
        s, e = int(f0 / 30 * RATE), min(n, int(f1 / 30 * RATE))
        if data is None or e <= s:
            continue
        loop = np.resize(data, e - s)
        k = min(e - s, RATE // 2)
        ramp = np.ones(e - s, np.float32)
        ramp[:k] = np.linspace(0, 1, k)
        ramp[-k:] = np.minimum(ramp[-k:], np.linspace(1, 0, k))
        track[s:e] += loop * ramp * AMBIENT_GAIN
    peak = float(np.abs(track).max()) if n else 0.0
    if peak > 0.95:
        track *= 0.95 / peak
    pcm = (np.clip(track, -1, 1) * 32767).astype("<i2")
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-f", "s16le", "-ac", "1", "-ar", str(RATE), "-i", "-",
                    out_wav], input=pcm.tobytes(), check=True)
    return played, dropped
