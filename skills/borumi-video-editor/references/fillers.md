# Filler and pause pass

Run it **after the content cuts and before layouts, captions and zooms**, because it ripples everything. On a 22-minute tutorial it made 93 cuts in one pass and removed 58 s, then a second scan found 28 more items for the creator to pick from.

## What counts as a filler
- **"uh" / "um"**: a held vowel, voiced, ≥ 140 ms, with almost no spectral change. Most sit between two words with little or no gap, so silence detection misses them.
- **The speaker's tag words.** Many people end sentences with a tag ("right?", "okay?", "you know?"). Cut it when it's a tag at the end of a sentence or stands alone ("Right."). Keep it when it carries meaning ("the right model"). Find out the creator's tags from the first transcript; on one tutorial a third of all candidates were "right".
- **Quick repeats** ("it it", "that's that's", "I I"): cut the first copy.
- **Stretched real words** ("and…", "so…", a held "I…"): never cut automatically, because they're real words. Put them on a review list, or trim a held word back to its normal length.
- **Intentional doubles stay:** "very very", "super super", "so so", "really really" are emphasis.
- **Never cut a real short word** that sounds like a filler: "a" in "edited a YouTube video". When unsure, keep it.
- **Hidden fillers:** the transcript may leave out a drawn-out "uhh" and show only a gap between words. In any gap ≥ 400 ms, a voiced, steady, low-pitch hump at the speaker's own pitch is a filler. Cut it edge to edge on the waveform.

## Tools
- **Transcript: use Borumi's** (`get_transcript` words + `export_transcript` SRT). It writes "uh/um" out reliably. Whisper large-v3, even with a disfluency prompt, dropped every "uh" and drifted ~0.3 s, so don't use Whisper for this pass.
- `scripts/filler_detect.py`: transcript pass (uh/um, repeats, tag words via `--tags`) plus a signature pass, from a words.json.
- `scripts/filler_signature.py`: learns the speaker's profile (MFCC + spectral flux of the held-vowel core) from the known "uh/um" and scans for unlabelled held vowels. When the transcript already marks fillers, its top hits are usually stretched real words, so treat it as a safety net and a review-list generator.
- `scripts/filler_edges.py`: candidates `[a, b, label]` → cut ranges with edges snapped to the energy valley within ±80 ms of the word boundaries.
- `scripts/edge_audit.py`: flags joins with voiced energy at the cut.
- `scripts/voicefeat.py`: shared features (needs `scipy`).

## Steps
1. Re-export the current timeline audio (`export_audio`; create the output folder first). The creator may have trimmed in the app since your last export.
2. Pull the words with `get_transcript` for the range. Build candidates: for each filler, `a` = end of the previous kept word, `b` = start of the next kept word. Merge neighbours closer than ~150 ms.
3. Run `filler_edges.py`. **Keep the windows narrow**: a ±200 ms search cut into the filler itself and left 60–130 ms of "uh".
4. Apply the ranges **one per `trim_timeline` call, back to front**, targeting every content layer (camera, screen, mic, system sound, and any `camera_2`/`screen_2`). See `borumi-learnings.md` §13 for why. Then compare camera vs screen starts, check the layout track for gaps, and move the sound effects that sit after each cut.
5. Run `edge_audit.py`. In run-on speech about half the joins show voiced energy at the cut. That's expected: render a listening reel of the flagged joins (±1.5 s each, timestamp burned in) for the creator rather than guessing.
6. Report: what was cut, the review list (stretched words), what was kept on purpose.

## Pause scan (second pass)
After the filler pass, measure loudness every 10 ms on the exported timeline audio and list:
- quiet stretches ≥ 0.75 s (suggest trimming to ~0.4 s; mid-sentence pauses first, sentence breaks are taste),
- short, steady, low-pitched sounds (hidden "uhh"),
- written uh/um and doubled words still left.
Skip montages, playbacks, sound effects and anything under intro music. Present it as a numbered table with a 4-second labelled snippet per item in one listening file, recommend a set, and **cut nothing until the creator picks the numbers**. Pauses of 0.60–0.74 s are normal breathing room; leave them unless the creator asks for a tighter pace.

## The join check (every content cut, not just fillers)
1. Write the last kept sentence and the first kept sentence side by side; the conversation must still make sense.
2. Cut on existing clip boundaries when possible (their pauses are already clean).
3. Measure the pause at the join on the waveform: aim for **300–600 ms** at a sentence join, and no clipped word. Don't trust transcript times (they drift 0.3–0.5 s mid-clip).
4. After cutting, re-read the words at the join, then send the creator a short clip of each join to hear.
