# Music: finding it, auditioning it, building the bed

**No music is included in this skill.** You source it yourself and keep the licence. Free libraries such as Mixkit (Mixkit Stock Music Free License: commercial and YouTube use, no attribution required at the time of writing) work well; always read the current licence on the track page. Keep a `CREDITS.md` in `<MUSIC_LIBRARY>` with track, artist, source URL, licence and where it was used.

## 1. Two kinds of music
- **Intro and payoff moments:** the creator's signature track (the worked example uses a warm deep-house track, ~120–125 BPM, bass-forward). Start it on its best section so it lands early.
- **Body (talking, explaining, screen share): sparse and chill.** Few instruments, low energy, steady, little going on in the voice band. Busy music "distracts the viewer from me explaining" (the author's words). One track per chapter, each change hidden under a chapter card.

## 2. Finding candidates
- Ask before any download: list the tracks (title, artist, URL, licence) and wait for a yes.
- Some music sites expose JSON-LD `"@type": "MusicRecording"` entries (name, genre, artist, duration, file URL) on their genre pages. Parse those rather than the visible grid; naive scraping paired titles with the wrong files.

## 3. Ranking: `scripts/music_rank.py`
Compare each candidate against a track the creator already likes:

```bash
python3 scripts/music_rank.py liked.mp3 cand/*.mp3 --voice voice-10s.wav --reel audition.mp4
```

It measures 60 s of each track:
| Measure | Why |
|---|---|
| **busyness** (onset peaks per second) | busy beds compete with the voice for attention |
| **voice-band share** (energy in 300–3000 Hz) | energy where speech lives masks words, even at low level |
| tempo | keeps the bed close to the vibe of the reference |
| dynamics (spread of 400 ms loudness) | big swells pull focus; steady beds sit under talk |

Pick the top 4–5.

## 4. Auditioning
The creator judges by ear, and Claude can't hear. The `--reel` file plays the reference first, then for each candidate **10 s alone, then 10 s under the creator's voice at the real mix level (music 20 dB under the voice)**. A track that sounds great alone can disappear or clash under talk; the second 10 s is the real test. Ask which ones they like, and note rejections with the reason in the taste profile.

## 5. Building the bed: `scripts/music_bed.py`
Borumi's music layer is exclusive (no overlapping music segments), so a track per chapter means one pre-mixed file. Write a `bed.json` (see the script header): parts with start/end on the current timeline and an offset into each track (use the section the creator liked), mutes under playbacks and montages. Every part is levelled to exactly −41 LUFS (about 20 dB under a −21 LUFS voice), with crossfades at the switches.

Then in Borumi: `import_media`, add one `music` segment at the bed's start, set `enable_looping: false`. Send a short preview export around each switch.

**The bed is placed by fixed time.** After any later cut or untrim, rebuild it and re-place it.

## 6. Final loudness
Borumi's exports land near −20 LUFS. Normalise the final file to −14 LUFS / −1 dBTP with two-pass ffmpeg loudnorm and `-c:v copy` (commands in `borumi-learnings.md` §18).
