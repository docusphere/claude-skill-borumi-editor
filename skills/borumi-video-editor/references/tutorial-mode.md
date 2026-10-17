# Tutorial mode: screen-share videos

Built on a real 22-minute screen-share tutorial (Oct 2026). Rules marked *(tentative)* still need confirming on more edits; when the creator approves or rejects something, update this file with the reason.

## What's different
- The raw material holds talking-head **and** screen footage: either Borumi recorded both as scenes in one project, or a recorder (e.g. Tella) exported camera and screen as two files. For the two-file case, read `borumi-learnings.md` §14 before touching anything.
- Extra visuals (articles, other videos, photos) still come from `broll-sourcing.md`.
- Expect most of the runtime on the screen and less on the face.

## Two views that alternate
| View | Borumi layout | When |
|---|---|---|
| **Face full screen** | `fullscreen` on `camera_1`, fit cover | the intro, opinions, reactions, story, step transitions, the outro and CTA |
| **Screen + face bubble** | custom: screen on the left, full height, ~87 % width; camera in a rounded bubble bottom-right, face tracking auto | whenever something on screen matters |
| Screen full screen | `fullscreen` on `screen_1` | only where the camera file has no face (see §14 of the learnings) |

- **Switch on meaning, not on a timer.** "Look at this", "here", "you can see", "over here", "right here" → screen, even if the creator's own cut had the face there. If the recording at that moment shows something else (another app, a loading screen), cover it with a still of the thing they mean, taken from the same recording a moment later.
- Switch with `transition: instant`, on a jump cut (a segment boundary from the cut pass) or at worst a sentence boundary, so the view change reads as a cut.
- Uneven lengths keep it alive: on the reference edit, 84 views over 16 minutes, a switch every ~10.7 s on average, from 4 to 29 s each.
- Save the view plan as JSON (start, end, view). Trims and untrims break layouts (`borumi-learnings.md` §13) and you'll rebuild from it.

## Editing the screen
- **Highlight the exact thing the creator names.** They say "base layer", "sound effects row", "this button": that element lights up as they say it. This is what makes a screen share feel explained rather than recorded.
- **Zoom into what's being talked about**, not the whole screen: find it from the transcript plus where the cursor is. Keep each zoom inside one screen segment whose frame you checked. Text must be readable on a phone (small text needs 1.8–2.4×).
- **On dark UIs, draw a ring** instead of using `screen_highlight` (it only dims everything else and barely shows). Position math in `borumi-learnings.md` §15.
- **Dictating a prompt:** when the creator speaks a prompt into a voice-dictation box, zoom so the recording indicator and the input are both in frame and highlight them while they speak. Keep the screen on until the dictation really ends (often a key tap and a confirmation sound on the mic), not at the end of the sentence.
- **Cover glitches** (app-switch flashes, spinners, blank loads) with a still from the same recording; paint out burned-in text such as dates with `scripts/patch_still.py`.
- **Explain with the real thing.** When the creator explains how something is built, take their own material apart on screen (an exploded view of a real frame's layers, each tagged as they name it, then collapsing back) rather than a generic diagram.
- **Cut dead time** *(tentative)*: loading, typing long commands, waiting for output. Speed up (2–4×) or cut, and keep a beat of the result appearing. If the creator talks while something loads, keep the talk and speed up only the screen.
- **Never cut a long silence without looking at the screen.** It may be a playback the creator is showing (`borumi-learnings.md` §16).
- **Blur anything private** before placing: API keys, emails, tabs, file names, other people's data.

## Captions
Split per layout (under the screen on screen views, bottom on face views) and none over playbacks or montages with their own speech. Details in `borumi-learnings.md` §17.

## Before recording (tell the creator)
1. Screen at 1440p or 4K, so zooms stay sharp.
2. A clean browser profile; close anything private.
3. Terminal or editor font at least 18 px; a light theme highlights better than dark.
4. Slow mouse moves, pause about 1 s after each click.
5. With a separate recorder, export **camera-only and screen-only files per clip** with no layout baked in, and record system audio if they'll play videos on screen.

## Collect the reps
Log every edit decision to `<WORKSPACE>/<video>/decisions.jsonl`, one JSON object per line:
`{"date": "2026-10-17", "t": "03:12.4", "context": "transcript + waveform/screen facts", "action": "what you did", "verdict": "kept|changed|rejected", "reason": "the creator's words"}`
It's the record of why the edit looks the way it does, and the material for updating the taste profile.
