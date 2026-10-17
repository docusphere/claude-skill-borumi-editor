---
name: borumi-video-editor
description: Use when editing a talking-head, informational or screen-share tutorial YouTube video in the Borumi desktop app through the Borumi MCP tools (mcp__borumi__*). Covers the section map, trimming silences and false starts, the join check on every content cut, the filler and pause pass, auditing every cut on the waveform, face/screen layouts for screen shares, zooms and highlights on what the speaker names, placing B-roll and full-screen cutaways, placing motion-graphic clips from a manifest (made by the motion-graphics skill), graphics behind the speaker, chapter cards, sound effects, slow and punch-in zooms, music beds, captions and transcript fixes, covering glitches and burned-in text, a reviewer-agent pass, export and loudness. Triggers on "edit in Borumi", "edit my video", "trim silences", "cut the false starts", "cut the fillers", "place the B-roll", "place the motion graphics", "manifest is ready", "add zooms", "add sound effects", "add music", "add captions", "export the video", or any Borumi project work.
---

# Editing videos in Borumi

You drive Borumi through its MCP tools (`mcp__borumi__*`). Borumi must be running with **Settings → AI → Enable MCP** turned on. You cannot hear audio, so anything about sound choice and level needs the creator's ears: send short preview exports and ask.

Motion graphics are **not** built here. The companion `motion-graphics` skill (usually run in a separate Claude Code session) renders clips into `<MOTION_OUT>` with a `manifest.md`. Your job is to edit the video and place those clips.

## Setup (placeholders)

This skill uses placeholders instead of fixed paths. Before the first edit, ask the user for these values (or read them from a `config.md` they keep next to this file) and use them wherever they appear below.

| Placeholder | What it is | Example |
|---|---|---|
| `<WORKSPACE>` | Folder where per-video working files live (transcripts, section map, decisions log, exports, scratch) | `~/Videos/editing` |
| `<SFX_LIBRARY>` | Your own pre-levelled sound kit with a README of files, uses and peak offsets (see `references/sound-kit-template.md`). Not included: bring your own licensed sounds. | `~/Sounds/House Kit` |
| `<MUSIC_LIBRARY>` | Your licensed music tracks plus a `CREDITS.md` (see `references/music.md`). Not included. | `~/Music/yt-safe` |
| `<MOTION_OUT>` | Optional. Folder with finished motion-graphic clips and a `manifest.md` (from the `motion-graphics` skill) | `<WORKSPACE>/<video>/motion/out` |
| `<EXPORT_DIR>` | Folder for review and final exports. It must exist before `export_video` | `<WORKSPACE>/<video>/exports` |
| `<SCRIPTS>` | This skill's `scripts/` folder | `~/.claude/skills/borumi-video-editor/scripts` |
| `<BRAND_FONT>` | Optional .ttf used by `page_clip.py` for the source pill (or env `BORUMI_FONT`) | any TTF on disk |

Project IDs and media IDs differ per project. Always look them up with `list_open_projects`, `get_project_overview` and `get_timeline`; never hardcode them.

## Before anything else

1. Call `get_guides` (once per MCP connection, one guide at a time). Borumi's guides define tool semantics and change between versions. Fetch the `exporting` guide before any export.
2. Read `references/borumi-learnings.md`: tool mechanics and gotchas already learned the hard way. **§13 (what ripples on a trim) is mandatory before any cut.**
3. Read `references/edit-style.md`: pacing, zoom spec, rotation rules.
4. Read `references/taste-rules.md`: the creator's taste profile. When a taste rule and a shot list disagree, the taste rule wins.
5. Check `<SFX_LIBRARY>/README.md` for sound files, levels and peak offsets.
6. Re-read the timeline at the start of every session and every transaction. The creator may have edited in the app since your last commit (`base_commit_id` or `duration_ms` changed). Keep their edits; only flag big deletions.

## References
- **`references/tutorial-mode.md`**: screen-share videos: the two alternating views, switching on meaning ("you can see" = screen), highlighting what's named, zooms, dictation, glitches, captions.
- **`references/fillers.md`**: the filler and pause pass, and the join check for every content cut.
- **`references/music.md`**: sourcing, ranking and auditioning music under the voice, building the bed, final loudness.
- **`references/broll-sourcing.md`**: Claude finds and captures B-roll itself (real pages, other videos' pages, CC photos, stock footage, live proof), with credits.
- **`references/sound-kit-template.md`**: how to build and level your own sound kit.
- **`references/taste-rules.template.md`**: a blank profile for creators starting from scratch.

## Vocabulary (what can be on screen)

| Code | What | Built where |
|---|---|---|
| `FACE` | clean talking head; deliberate breathers for punchlines, emotion, the CTA | here |
| `SCREEN` | screen recording + face bubble (screen shares) | here |
| `ZOOM` | slow push (1.00 → 1.12×, 2–3 s), creep (1.00 → 1.06–1.08× over a sentence), or punch-in (1.4× instant) | here |
| `TXT` | 1–3 big words behind the speaker's head | motion-graphics → placed here |
| `BG` | graphic behind the speaker in the side zones | motion-graphics or here |
| `FS-MG` | full-screen motion graphic (counter, bars, roadmap, chapter card) | motion-graphics → placed here |
| `FS-BR` | full-screen sourced B-roll (real page, photo stack, real footage) | here or motion-graphics |
| `+OVL` | small tag, badge, ring or highlight on top | here |
| SFX / music | sound | here (last stages) |

## Order of work

Run the intro (first ~60 s) through every stage first as a pilot, then go section by section. Commit in sensible chunks (one section or stage at a time) so the creator can review.

0. **Section map.** Export the transcript (`export_transcript`, SRT + md), split it into sections (intro, each body part, outro/CTA) with timestamps, what happens, edit status and flags (missing CTA, tangents, misheard names). Save it to `<WORKSPACE>/<video>/section-map.md` and have the creator confirm it. It's the source of truth; update it after big cuts. Log decisions to `<WORKSPACE>/<video>/decisions.jsonl`.
1. **Cuts.** Trim silences and cut false starts, retakes and tangents. Plan with `detect_speech` + the transcript, then set every OUT/IN on the waveform. **One range per `trim_timeline` call, back to front, targeting every content layer** (`borumi-learnings.md` §13). A retake shows as a repeated phrase at the end of one clip and the start of the next; keep the cleaner take. **Never cut a long silence in a screen share without looking at the screen** (it may be a playback). Every content cut gets the **join check** (`fillers.md`).
2. **Waveform edge audit.** Run `<SCRIPTS>/edge_audit.py` over every audio segment edge, then inspect each flag with `<SCRIPTS>/cut_audit.py`. Fix real problems (half-cut words, stray "uh", leftover sibilants, handling noise).
3. **Filler and pause pass** (`fillers.md`). Present the pause scan as a numbered list; cut only what the creator picks.
4. **After every trim or untrim:** camera vs screen starts still match, the layout track has no gaps, no layout lost its `layer_id`, sound effects after the cut moved by hand.
5. **Export the trimmed transcript** to `<WORKSPACE>/<video>/` (and next to `<MOTION_OUT>`) so anything timed afterwards uses the real edit.
6. **Layouts (screen shares).** Face full screen vs screen + bubble, switched on meaning with instant transitions on jump cuts (`tutorial-mode.md`). Save the view plan as JSON.
7. **B-roll.** Real footage, real pages, real photos (`broll-sourcing.md`). Full-screen cutaways go in as full-canvas overlays. Source pills carry no dates.
8. **Motion graphics.** If `<MOTION_OUT>/manifest.md` exists, place each clip by its **anchor phrase** on your trimmed transcript (raw manifest times are pre-trim hints).
   - Full-screen clips (`FS-*`, `.mp4`): full-canvas `media_overlay`, entrance/exit `instant`.
   - Behind-the-speaker clips (`BG`/`TXT`, `.mov` with alpha): full-canvas `media_overlay` with `behind_subject: {quality: "high"}` (`borumi-learnings.md` §12). On builds without it, use the plate recipe in §3.
9. **Screen zooms and highlights** on the exact thing the speaker names; rings on dark UIs; stills over glitches; patches over burned-in dates (`borumi-learnings.md` §15).
10. **Transitions.** Chapter cards hide the cut inside their fully covered window and stay readable for about 2 s.
11. **SFX.** Whoosh on each switch to a full-screen clip, sound on chapter cards, one card-slide sound for photos, quiet detail sounds, layered frame-matched designs for complex animations. Peak on the switch (file start = switch time − peak offset). Levels in `borumi-learnings.md` §7.
12. **Zooms.** Slow, pure-scale zooms into the screen centre, ending only where the snap-out is hidden; punch-ins on cheeky lines (`edit-style.md`).
13. **Music.** Audition under the voice, then one continuous bed (`<SCRIPTS>/music_bed.py`) on the exclusive music layer, looping off, about −41 LUFS (`music.md`).
14. **Captions.** Fix names first with `correct_media_transcript` (media-time formula in `borumi-learnings.md` §17), split per layout, none over playbacks, style per the taste profile.
15. **Review pass** after each section (below), then **export**: create `<EXPORT_DIR>` first, `export_video` (`best` = 3840×2160 60 fps, slow), then normalise to −14 LUFS with two-pass loudnorm and `-c:v copy` (`borumi-learnings.md` §18).

## Placement rules

- **Anchor every beat to a phrase, never a timestamp.** Clips start ~100 ms before the anchor word.
- **Check scene bounds before adding a take:** `at_ms + duration <= scene end`, or the scene grows and everything after it shifts. Compare `duration_ms` before and after.
- **A full-screen overlay that ends near a camera cut must end at least 50 ms after the cut**, or the old shot flashes. Fix: hold the last frame (`tpad=stop_mode=clone:stop_duration=0.15`) and re-place.
- **Every graphic must fade fully out** before its last frame.
- **Overlays, labels and CTAs stay out of the caption band.**
- **No redundant labels.** Don't label an image with what the speaker is saying at that moment.
- **Rotation:** never the same mode twice in a row, never two full-screens back to back without returning to the face.
- **Never invent numbers.** Only numbers the speaker says, or live ones shown from a real source.

### What to show for a line (first rule that fits)

| If the line... | Show |
|---|---|
| says "you can see", "over here", "right here" in a screen share | the screen + bubble, zoomed and highlighted on what they mean |
| names a UI element while on screen | that element highlighted as the word is said |
| explains how something is built | the real thing taken apart (exploded layers, each tagged as named) |
| says a number that matters | a counter that lands on the spoken number |
| names a person | photo stack (full-screen if a number goes with it, side cards otherwise) |
| names brands or companies | one logo or proof card per name, appearing on the name |
| makes a claim with a source | the real page, scrolled to the line, key line highlighted (`<SCRIPTS>/page_clip.py`) |
| compares two things | side-by-side bars or cards, or countable icons |
| lists things | items appearing one per spoken item (parallel items only) |
| gives the result of things just listed | a connector to an outcome line, not another list item |
| explains a mechanism or flow | a diagram in a side zone behind the speaker |
| describes a behaviour or a feeling | real footage of a person doing it, with a light UI layer |
| claims the creator's own track record | their real channel/page with the top numbers highlighted (live numbers only) |
| has one phrase that sums it up | big text behind the head |
| is funny, cheeky or self-aware | punch-in zoom |
| is a punchline, emotion or the CTA | plain face, maybe a slow push |
| is an emphasis line with nothing to show | zoom push |
| is reflective or personal | zoom creep |

## Review pass (after every section)

1. Export the section, pull 1 fps frames, and give a **separate reviewer agent** the frames, the word timings and the taste profile. It checks: real material on screen, the named thing is highlighted, no spinners, blank screens or app-switch flashes, face bubble clear, no clipped or hidden text, captions out of the way, pacing.
2. Fix what it finds, then run round 2 on fresh frames.
3. Run the audit recipe in `borumi-learnings.md` §10 (zoom ends, overlay ends vs cuts, pop-offs, seams, caption band).
4. Send the creator short clips of every join and every audio change. The reviewer can't hear.

## Verification habits

- Judge visuals from `inspect_timeline` render frames (`save: true`, `quality: "max"`), not raw media: cameras may be mirrored and face-tracked.
- When the creator reports a bug in one place, **audit the whole video** for the same bug and fix every instance.
- Treat timestamps the creator sends as exact; find the cause at frame level before fixing.
- For anything audio, send a 5–10 s preview export. Start with a few sounds and expand once approved.
- If a tool returns `app_not_running` while Borumi is open, relaunch it (`open -a Borumi` on macOS), wait a few seconds and retry.

## Report back

After each stage, in plain words: what you did, what looked off, what the creator needs to listen to or decide, and what the motion session should change.

## Keep this skill sharp

When you learn something new about Borumi (a quirk, a workaround, a failure), add it to `references/borumi-learnings.md` with the date and Borumi version before you finish. New taste preferences go in `references/taste-rules.md` with the creator's reason; style changes go in `references/edit-style.md`.

## Rules

- Never delete or overwrite the user's projects or media without asking. Use a throwaway transaction (`begin_project_edit` / `abort_project_edit`) for experiments.
- Don't edit Borumi's generated workspace config files (`CLAUDE.md`, `.mcp.json`, `.claude/settings.local.json` in the Borumi AI Workspace). Borumi overwrites them.
- Don't delete the creator's own edits without asking, even ones that look like mistakes.
- Ask before any download; use only licensed or free-licensed assets and keep credits.

---

© 2026 Nillard Ltd (company no. 16312961, registered in England and Wales). Licensed under the Nillard Ltd Skills License 1.0 (see `LICENSE` in the repository): use and modify it for your own work, including paid work; don't sell, redistribute or bundle it without written permission.
