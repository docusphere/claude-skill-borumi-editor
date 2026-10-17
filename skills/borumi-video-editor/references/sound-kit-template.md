# Building a sound kit ("House Kit")

A house kit is a small folder of pre-levelled sound effects with a README that says what each file is for and where its peak sits. The agent reads the README to pick and place sounds, so you get the same sound for the same job across every video, and Borumi needs no volume tweaks.

Set `<SFX_LIBRARY>` in `SKILL.md` to this folder.

## 1. Folder layout

```
<SFX_LIBRARY>/
  README.md                       the table below + licence notes
  fs-whoosh_soft.wav              switch to a full-screen clip
  chapter-whoosh_soft.wav         chapter cards
  photo-slide_short_quiet.wav     photo cards landing
  pop-soft_quiet.wav              cards / phones popping in
  counter-land_quiet.wav          a counter landing on its number
  <clip-id>_design.wav            one-off layered designs for specific animations
```

Name files by **job**, not by the source pack's file name, so the agent can find them. Add `_quiet` / `_quieter` suffixes for level variants and note which one is in use.

## 2. README columns

| File | Source | Use | Peak at |
|---|---|---|---|
| fs-whoosh_soft.wav | `<pack> / Whooshes / <original file>.wav`, peak −18 dBFS, ≈ −33 LUFS | switch to any full-screen clip | 0.17 s → place at overlay start − 0.17 s |
| chapter-whoosh_soft.wav | `<pack> / Whooshes / <original file>.wav`, peak −17 dBFS | chapter cards | 0.65 s → place so the peak lands on the cut inside the card |
| photo-slide_short_quiet.wav | `<pack> / Foley / <original file>.wav`, ≈ −36 LUFS | photo cards sliding onto the stack | ~0.20 s |
| ... | | | |

- **Source:** pack name and original path, so you can go back to the original. Keep the pack's licence file next to it.
- **Use:** the job it does. One sound per job keeps the edit consistent.
- **Peak at:** seconds from file start to the loudest moment. The agent places the file at `switch time − peak`.
- Add a dated notes line under the table whenever you change a level or reject a sound, with the reason.

## 3. Pre-levelling with ffmpeg

Convert to 48 kHz stereo and normalise, so Borumi plays everything at its default volume:

```bash
# measure integrated loudness (LUFS) and true peak
ffmpeg -hide_banner -i in.wav -af ebur128=peak=true -f null - 2>&1 | tail -12

# trim, convert and set a peak level (e.g. -18 dBFS)
ffmpeg -i in.wav -t 0.8 -ar 48000 -ac 2 -af "volume=<gain>dB" out.wav

# make a quieter variant (-12 dB)
ffmpeg -i out.wav -af "volume=-12dB" out_quiet.wav

# brighten a dull hit so it cuts through the voice (+6 dB shelf at 3 kHz)
ffmpeg -i in.wav -af "highshelf=f=3000:g=6" out_bright.wav

# find the peak offset (seconds) with numpy
ffmpeg -loglevel error -i out.wav -ac 1 -ar 48000 -f s16le - | \
  python3 -c "import sys,numpy as n;a=n.frombuffer(sys.stdin.buffer.read(),n.int16);print(abs(a).argmax()/48000)"
```

Judge levels by **LUFS (`ebur128`), not peak dBFS**. Short ticks can share a peak with a sweep and still sound 8–12 dB quieter.

## 4. Recommended levels (voice at ≈ −21 LUFS)

| Sound | Level on the file | Notes |
|---|---|---|
| Bright whoosh on full-screen switches | ≈ −33 LUFS | clearly audible, not distracting |
| Detail sounds (pops, slides, ticks, counters) | ≈ −36 LUFS (~15 dB under the voice) | −24 to −26 LUFS drowned the voice |
| Dull or low hits | ~10 dB louder than bright sounds, or add a 3 kHz shelf | otherwise inaudible |
| Layered animation designs | ≈ −44 LUFS overall was approved for one design | balance layers by short-term loudness |
| Music bed | ≈ −41 LUFS (~20 dB under the voice) | first pass; adjust by ear |

These are starting points from one creator's ears. Send short preview exports and adjust.

## 5. Layered designs

For complex animations, build one stereo file per clip in numpy or a DAW: a tick per element appearing, a sweep for paths, a ripple for groups filling in, each frame-matched to the animation. Balance by short-term loudness (ticks level with or 1–2 dB above the sweep in the loudest 100 ms) and pan moving elements with equal-power panning. Place the file at the clip start.

## 6. Licensing

**No sounds are included in this skill.** Build your own kit from sounds you hold a licence for: a purchased pack, or free libraries whose licence allows commercial use (Mixkit's sound effects licence allowed this at the time of writing; check the current terms). Most paid packs let you use the sounds in your videos but **not redistribute the files**, so never commit your kit to a public repo. Keep the licence text in the kit and a source column in the README.

The levels and peak offsets in this file are from the author's own kit, which is built from a paid pack and can't be shared; use them as starting points for yours.
