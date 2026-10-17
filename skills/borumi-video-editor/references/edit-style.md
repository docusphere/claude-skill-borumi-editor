# Edit style

Defaults for talking-head YouTube videos. Edit these to match your own style; the taste profile (`taste-rules.md`) wins where they disagree.

## Zooms: slow, smooth, never snappy

| Type | Scale | Duration | Easing | Use |
|---|---|---|---|---|
| Push in | 1.00 → 1.12× (max 1.15×) | 2.0–3.0 s | ease-in-out | Emphasis lines. Start on the first word so the zoom peaks on the key word. |
| Creep | 1.00 → 1.06–1.08× | whole sentence (4–8 s) | gentle | Reflective or personal lines |
| Pull out | not available in Borumi | — | — | Borumi snaps back out. Turn "pull out" beats into a creep or plain face. |
| Punch-in | 1.00 → 1.4× | instant | none | Funny, cheeky or self-aware lines (see below) |

- **Pure scale into the exact screen centre.** No XY movement, no face tracking, one continuous move (`focus_point` position 0.5 / 0.5).
- Push length = segment length (`enter_mode: gradual`). One gradual segment per zoom; no push + hold pairs.
- **A zoom may only end under a full-screen clip (~0.1 s after it starts) or on a hard cut.** Otherwise the snap-out shows. No such place before the next behind-the-speaker beat? Don't zoom.
- Hold the zoomed state until that ending point. Leave at least ~4 s between zooms.
- No zooming while a graphic is behind the speaker (it rescales the cutout).
- No whoosh on slow zooms. At most 2–3 soft swells per video, on the biggest moments.

## Pacing

- **Intro (first ~60 s):** a visual change every 3–5 s.
- **Body:** a change every 6–10 s. Never ~15 s with nothing changing.
- About 35–40 % of runtime covered by graphics, B-roll or text.
- **Keep plain face time** for punchlines, emotional lines and the CTA (about 20–30 % of runtime).

## Rotation

- Never the same mode twice in a row (face, zoom, behind-the-speaker, full-screen).
- Never two full-screen cutaways back to back without returning to the face. If a shot list stacks them, turn one into a behind-the-speaker beat.
- Full-screen holds 3–6 s. Longer graphics split full-screen → behind → full-screen.
- Fast lists (names 0.5 s apart) are too fast for full-screens; use cards that build up behind the speaker on one screen.

## Cuts

- Trim silences but keep natural breathing room; the edit shouldn't feel jumpy.
- Cut false starts and retakes; keep the cleaner take.
- Check every cut on the waveform (see `borumi-learnings.md` §6).
- **Every content cut gets the join check** (`fillers.md`): read the two sentences together, 300–600 ms pause at the join, no clipped word, send the creator the join to hear.
- Then the filler and pause pass (`fillers.md`). Cut a held "uh" even when the transcript hides it; never cut a real short word like "a".

## Behind-the-speaker text and graphics

- Partly covered letters are fine if part of each letter stays visible; a fully hidden key letter is not. Scale the text up past the shoulders rather than moving it.
- Build the background plate from frames right around each beat so the light matches that moment (recordings drift as daylight changes).
- Text motion: smooth fade + small rise + blur-in. No hard masks that slice letters.
- Photo beats: about 3 photos per beat, stacked, one dealt in per phrase. Prefer recent and event shots.

## Real-world B-roll

When a line describes something real (a match, a stadium, a city), use actual footage cut like documentary B-roll: hard cuts, slow push on each shot, faded warm grade, film grain, vignette, 2.39 letterbox bars, one tag on the spoken keyword. Free or licensed stock only.

## Order of work

Section map → cuts (+ join check) → waveform edge audit → filler and pause pass → layouts (screen shares) → B-roll → motion graphics (+ background text, tags) → transitions → transition SFX → zooms (+ swells, punch-ins) → music → captions → export → loudness to −14 LUFS. Run the intro through every stage first as a pilot, then go section by section with a reviewer-agent pass after each.

## Punch-in zooms for jokes and cheeky lines

- Slow zooms stay for emphasis. **Funny, cheeky or self-aware lines get a sudden punch-in**: `enter_mode: instant`, about **1.4×** (the top of the usual 1.2–1.4× range; lower looked too soft at 1080p), focus x 0.5 / y 0.42 so the face stays framed.
- Snap in on the punch word, hold through the line, snap back out (`exit_mode: instant`) at the start of the next sentence or on a cut. The snap-out reads as a cut, so it's fine here.
- At most 2–3 per section, or they stop landing. A slow push may run right up to a punch (the push ends where the punch starts).
- No sound on the snap by default; a short hit on the biggest one only after the creator hears a preview.

## Source labels

- Page captures and other sourced clips carry a small source pill: the source only ("YouTube · search", "example.com"), **never a date**, so the video stays timeless. Paint dates out of screenshots and recordings too.
- Keep pills out of the caption band and off the site's own logo (bottom-left above the captions worked best).
