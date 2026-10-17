# Borumi learnings: tool mechanics and gotchas

Learned on two real edits: an 11-minute talking-head video (Borumi 0.31.3, 2–5 Oct 2026) and a 22-minute screen-share tutorial (Borumi 0.31.x–0.32.0, 15–17 Oct 2026). Sections 1–11 come from the first, sections 12–19 from the second; where they disagree, the later section wins. Borumi changes between versions, so call `get_guides` first and re-test anything that looks off. Append new findings at the bottom with the date and Borumi version.

Terms used here:
- **FS**: a full-screen clip that replaces the speaker for a few seconds (motion graphic, B-roll, page capture).
- **BG/TXT**: a graphic or text placed *behind* the speaker, with the speaker cut out in front.
- **Plate**: a still of the empty room (speaker removed), used as the background behind BG/TXT graphics.

---

## 1. Transactions and project state

- Edits happen inside a transaction: `begin_project_edit` → changes → `commit_project_edit` (or `abort_project_edit` to throw it away). Use an aborted transaction for experiments.
- **The user may edit in the app between your commits.** `base_commit_id` / timeline hash changes unexpectedly. Re-read the timeline at the start of every transaction, and spot their edits by comparing `base_commit_id` and `duration_ms` with your last commit. Don't delete their edits without asking. Example seen: an app-default 1.3× fast `camera_zoom` appeared across a BG beat that nobody had added through the MCP.
- **`app_not_running`** can be reported while Borumi's processes are still alive (seen after a long idle and during an export). Run `open -a Borumi` (macOS), wait a few seconds, retry. The project stays open and a running export still finishes.
- `export_video` needs an **existing** output folder; a missing one returns `invalid_output_path`.

## 2. Timeline, takes and ripple

- Untrimmed, the project timeline matches the stitched raw transcript almost exactly. After a silence trim everything shifts, so **always place by phrase**, never by raw time.
- **A screen take that runs past its scene's end extends the scene and ripples everything after it** (10 ms over was enough to grow the timeline). Takes only accept `at_ms`, so you can't trim one on placement. Before placing, check `at + duration <= scene end`, and pre-trim the clip with ffmpeg if it doesn't fit. Deleting the take (ripple on) undoes the extension. Compare `duration_ms` before and after adding takes.
- **A trim inside a scene does NOT move that scene's later screen takes or layouts.** Overlays, zooms and later scenes shift with the trim, but screen takes and layouts further on in the same scene stay put (a 451 ms trim left a later BG take 451 ms late). After any trim, compare each BG/TXT take's start with its anchor word and `move_timeline_segments` the take and its layout together.
- Scene-attached overlays and zooms **do** shift with a ripple trim. When a trim range touches a BG clip, target the screen and layout layers too.
- **After a ripple delete, also move `sound_effect` segments**, not only same-scene screen takes and layouts (a whoosh stayed put while its full-screen clip moved). Re-check every layer after any ripple: screen takes, layouts, sound effects.
- **No relink.** To swap a re-rendered clip: import the new file, `delete_segments` the old screen take (ripple false), add a new take at the same `at_ms`. **Deleting a screen take also deletes the layout segment over it** (it's source-attached), so re-add the layout and check the layout count.
- To move an overlay, use `move_timeline_segments` with `at_time`; no delete and re-add needed.
- `copy_segments` of a camera segment (`expand_groups: false`) makes an in-sync `camera_2` with no ripple, but it is still a camera layer (see §3).

## 3. Speaker cutout and the behind-the-speaker recipe

What works and what doesn't:
- Background removal works well on a moving graphic: hair, glasses and shirt edges are clean. Weak spot: slight fringing on a fast-moving hand.
- **Edge softness must be 0.** At 0.3 the speaker went semi-transparent and the room showed through.
- **The cutout is computed only after a commit**, about 1–4 min per source media the first time. Until then the preview shows the normal background, so don't judge it before committing. Borumi writes the matte as `<media>.rvm-*.background.mp4` in the project bundle's `medias/` folder; its presence means the cutout is ready. Poll for it before inspecting.
- **Overlays always draw on top of the speaker.** Use overlays for FS cutaways only, never for behind-the-speaker graphics.
- **Camera layers always draw above screen layers**, whatever order a custom layout lists them in. "Later sources render in front" only holds within the same kind.
- The same camera layer listed twice in one layout: the second instance is ignored.
- Swapping a video in as the speaker's background (the "replace" option) did not render; it may only take still images.
- ProRes 4444 `.mov` with alpha imports and plays correctly (it imports as `screen` kind).
- Adding the camera media again as a `screen` take does give room → graphic → cutout, but it rippled the scene to the full media length and needs slipping by the trim offset. Too fragile for many beats.

> **Newer Borumi builds do this natively** (see §12): `media_overlay` with `behind_subject`. Try that first. The plate recipe below is the fallback for older builds or when you need full control of the background.

**Recipe that works (fallback): per-beat baked plate + transparent camera**
1. For each BG/TXT beat, take frames from the source clip around the beat's source range (±2 s, up to ~48 frames).
2. Mask the person in each frame (any person-segmentation model; Apple Vision `VNGeneratePersonSegmentationRequest` in accurate mode worked), dilate the mask by ~31 px.
3. Take the per-pixel median of the visible pixels, then push-pull fill the area that is always covered (it stays under the cutout anyway).
4. **Check the filled centre isn't black** (mean > ~20) before using the plate. One shipped unfilled once.
5. Composite the graphic over the plate into an **opaque** H.264 clip: `ffmpeg -loop 1 -i plate.png -i graphic.mov -filter_complex overlay ... -crf 12 -r 60`.
6. Add it as a screen take: `add_segments` with `take` + `media_id` + `video_kind: screen` at anchor − 100 ms. It lands on `screen_1` with no ripple as long as it fits inside the scene.
7. Add a **2-layer custom layout** over exactly the clip's range: `screen_1` full canvas, then `camera_1` full canvas with background `transparent` (softness 0, quality high). Layout `transition: instant`, because clips carry their own animation.
8. Outside BG/TXT ranges no layout is needed; the plain camera stays as before.

Why per beat: one global plate showed a visible colour and light shift later in the recording (warmer wall, brighter objects), even when a whole-frame mean diff was only 3.5–5/255. Per-beat plates brought seam diffs down to camera-noise level (1.4–5/255 vs. 23–45 before). A tripod camera is required for plates to match.

Alternative (simpler, less robust): import one plate PNG and set it with `update_canvas` background `{type: image}`. The canvas background is project-wide, not per range, and wallpaper can't be restored through the MCP (only in the app).

**Behind-head text**
- Measure the head zone per recording from person masks (one recording: x 760–1270, y ≥ 160 at 1920×1080). Key words placed inside it get hidden.
- Partly covered letters are fine; a fully hidden key letter is not. Fix by scaling the text up past the shoulders or shifting it slightly.
- Side zones are always safe for diagrams and cards.
- Text animation: fade + small rise + blur-in. Hard clip-path masks sliced letters during the rise.

## 4. Camera zooms

- `camera_zoom` renders correctly (1.2× tested). Zoom-in and zoom-out speeds are set separately, and a built-in sound can be attached to either (don't, for slow zooms).
- **`enter_mode: gradual` spans the WHOLE segment.** Segment length = push length; it peaks at the end. A gradual push only reaches ~1.11 of a 1.12 target by its end.
- **There is no slow zoom-out.** A `fast` exit is a snap (< 150 ms). A following 1.00× segment with gradual enter also snaps. Layout `transition: smooth` also completes in < 150 ms.
- **Pure scale only:** `focus_point: {"kind": "position", "x_ratio": 0.5, "y_ratio": 0.5}`. `focus_point: "face"` tracks the face during the push (drift and correction); an off-centre fixed point slides while scaling. The exact centre gave zero pixel shift.
- **No push + hold pairs.** An `instant` hold at the target factor after a gradual push jumps (the push never quite reached it). If the zoom must last until a later cutaway, use one gradual segment over the whole span.
- Zoom timing can't be changed with `update_segments`: delete and re-add.
- **Where a zoom may end (the only two places):**
  1. under a full-screen overlay, ~50–100 ms after it starts (hidden underneath), or
  2. on a hard cut: a trim jump cut or a scene/clip boundary (camera segment edges on `camera_1` in `get_timeline`). The snap then reads as a cut to wide.
- Never end a zoom on plain face or at a BG/TXT start. BG/TXT content fades in over 0.3–0.7 s, so the first frame is plain face and the snap shows (measured as background jumps of 23–45/255). Even a 50 ms gap before a cutaway shows a snap-out frame. No suitable place before the next BG/TXT beat? Don't zoom.
- Never zoom while a BG/TXT clip is up; it rescales the cutout against the graphic. Keep zooms off the first frames of a BG/TXT layout.

## 5. Overlays, cards and cuts

- FS clip: `media_overlay`, position custom 0,0,1,1, entrance/exit `instant`, border radius 0. A default drop shadow is added; harmless at full canvas.
- **An FS overlay that ends near a camera cut must end ≥ 50 ms after the cut.** Ending 0–400 ms before it flashes the outgoing shot (90 ms was noticed). Quick fix: hold the last frame with `tpad=stop_mode=clone:stop_duration=0.15`, then re-place. Audit by listing `camera_1` segment edges against overlay ends.
- **Transition cards must hide the cut** inside their fully covered window, with ≥ 100 ms margin on each side. Example: a card fully covering from +0.34 s to +1.04 s starts at cut − 0.46 s. Starting a card at the cut made the switch visible.
- **Graphics must fully fade before they end.** Check: compare each clip's first and last frame (99th-percentile absolute diff ≤ 4/255 is clean; ~20 means it pops off). Fix without re-rendering the source: apply `[1]format=yuva444p,fade=t=out:st=<dur-0.32>:d=0.3:alpha=1` to the graphic before overlaying the plate.

## 6. Cuts and the waveform

- **The MCP has no waveform tool.** Read the source audio in the project bundle's `medias/` folder with `scripts/cut_audit.py` (10 ms loudness + >4 kHz energy for sibilants).
- Whisper word timestamps are ±50–100 ms. Padding a fixed 150 ms after the last word swallowed the onset of the next word in run-on speech and left an ~80 ms "S" from a false start.
- Rules: OUT in the quiet valley after the last word including its T/S release; IN 20–40 ms before the next onset; for run-on speech find the valley between word energies; after cutting, re-check both sides (tail below about −45 dB, then the next word rises).
- **Full edge audit right after the first trim, before any graphics:** `scripts/edge_audit.py` checks every audio segment edge against each clip's noise floor and flags (a) cuts made while sound is active and (b) stray packets separated from the word by ≥ 40 ms of quiet. One run: 136 edges, 7 flags, 2 real (a half-cut "and" Whisper hadn't transcribed, and a stray "uh"). The rest were breaths, lip clicks, or run-on joins already at their valley. Inspect every flag with `cut_audit.py` and check the script/original transcript before changing anything.
- Order: trim → edge audit + fixes → export transcript → graphics.

## 7. Sound effects

- Built-in sounds (whooosh, whoosh, pop, ding, boom, click, drums, rewind, vinyl) attach to overlays (`enter_sound` / `exit_sound` via `update_segments`), zooms, and layouts (`transition_sound`). `volume: 0` = default level. They can't be previewed through the MCP, and they tended to sound cartoonish.
- Custom audio: `import_media`, then a `sound_effect` segment. `sound_effect` segments don't change scene length.
- **Pre-level the WAV files** instead of guessing Borumi's volume scale. See `sound-kit-template.md`.
- **Measure loudness with ffmpeg's `ebur128` filter, not peak dBFS.** `ffmpeg -i file.wav -af ebur128 -f null -`. With the voice at ≈ −21 LUFS: a bright whoosh at about −33 LUFS is audible; detail sounds (pops, slides, ticks) at about −36 LUFS sit ~15 dB under the voice; −24 to −26 LUFS drowned the voice; dull, low sounds need to be about 10 dB louder than bright ones to be heard (or get a +6 dB shelf at 3 kHz).
- Place each sound so its **peak lands on the switch**: file start = switch time − peak offset (e.g. FS overlay start − 0.17 s for a whoosh peaking at 0.17 s; for a chapter card, peak on the cut hidden inside the card, e.g. card start − 0.65 s for a whoosh peaking at 0.65 s).
- **Photo cards landing:** one short card or paper-slide sound (peak ~0.2 s), the same sound for every card, at the detail level (≈ −36 LUFS). Soft hits with a treble boost read as a "ping"; heavy paper glides sounded like dragging a rock.
- A first quiet version of soft hits (≈ −39 LUFS, dull) was inaudible; a +6 dB shelf at 3 kHz version at ≈ −24 LUFS was audible but too loud; the final level was the `_quiet` variant at ≈ −36 LUFS.
- **Layered designs: balance layers by short-term loudness, not peak.** 10–30 ms ticks had a similar peak to a sweep but averaged 8–12 dB lower, so they vanished when the whole file was lowered. In the loudest 100 ms windows, ticks should sit level with or 1–2 dB above the sweep (a tick peak about 1.6× the sweep peak). Layering a crisp tick with a wood tick gave them body.
- **Pan moving elements with the motion:** equal-power stereo panning from about −0.8 to +0.8 across the travel time; elements on the left get left-panned sounds, on the right right-panned. Compose in numpy as one stereo file and place it at the clip start.

## 8. Music

- Music sits on an **exclusive layer**: no overlapping music segments.
- For several tracks, mix one continuous bed with ffmpeg (`adelay` + `amix normalize=0`, each part with its own fades) and place it as one segment.
- **New music segments default to `enable_looping: true`.** Turn it off.
- A first-pass level of about −41 LUFS (≈ 20 dB under a −21 LUFS voice) was accepted.
- One track per chapter: build the bed so each track change sits under a chapter card (the card's full-cover window hides it). Trim the intro track so its best section lands early.
- Free music sites often list tracks as JSON-LD (`"@type":"MusicRecording"` with name, byArtist, duration, url); parse that instead of scraping the visible grid.

## 9. Captions and transcript

- Proofread the transcript before captions go live; fix **names and brands first** (people, companies, product terms) with `correct_media_transcript`, making only minimal, faithful corrections.
- `captions` segments need `range` placement and real transcripts (proofread first with `get_transcript` → `get_media_transcript` words → `correct_media_transcript`).
- Properties (verified on 0.31.3; check `get_guides` for your version): `position` ("bottom"/"top"/"center"/custom), `paragraph_mode` ("fill"/"single_word"), `text_size`, `text_color`, `future_color`, `background_color`, `highlight_color`, `accent_color`, `casing_mode` ("original"/"uppercase"), `font_families` (array), `bold`, `italic`, `stroke_color`, `stroke_width`. Adjust later with `update_segments`.
- **Example "VHS yellow" style:** text and future colour `{r:255,g:226,b:0,a:255}` (#FFE200), Helvetica, `stroke_width` 4 with a **fully opaque** dark outline (e.g. #191405), `paragraph_mode` "fill", position "bottom", no background or highlight, `text_size` 48.
- **There is no shadow property.** Yellow is hard to read on white graphics. A translucent rounded backing (black at alpha ~70) read as a grey pill on white and was rejected. A fully opaque 4 px outline (5 px looked heavy) plus Borumi's own faint soft shadow worked on both white and dark shots. Keep one style for the whole video.
- Captions occupy roughly y 920–1000 at 1080p. Keep overlays, pills and CTAs above ~y 880 so they never collide (one link pill had to move from y 916 to 780).

## 10. Inspecting and auditing

- `inspect_timeline`: `max_frames` is 8 per call. Use `save: true` + `include_images: false` to measure frames numerically.
- **Audit recipe** (after placing each section):
  1. List zoom ends, overlays, layouts and `camera_1` segment edges.
  2. Each zoom end must be under an FS overlay or on a camera cut.
  3. Each FS overlay end near a cut must be ≥ 50 ms after it.
  4. Sample frames ±30 ms at every layout start and end and compare **local regions** (wall, floor, ceiling crops), never a whole-frame mean. Diff > ~6/255 is a visible pop.
  5. Check first vs. last frame of every graphic for pop-offs.
  6. Re-check BG/TXT takes, layouts and `sound_effect` segments against their anchors after any ripple.
  7. Check no overlay, label or CTA sits in the caption band (below ~y 880 at 1080p).

## 11. Assets and environment

- Real-page FS clips: `scripts/page_clip.py` replays the end of a scroll capture, holds, eases the camera to the line (~1.6–1.8×), and wipes a highlight under the claim with a multiply blend so text stays dark. Use the capture frame that **matches the final screenshot** as `sEnd`; scroll captures ease out slowly, and a frame-diff "scroll stopped" estimate was 3.5 s early.
- Photo beats can be composed straight onto the per-beat plate in PIL (fade + rise + blur), skipping an alpha round trip.
- **CTA proof clip:** record the real landing page live (Playwright screen recording at 1920×1080), then a slow push to the headline and a highlight ring drawn on the signup button. Place it right after the logo/brand reveal.
- **Screenshot redaction:** OCR every text line (macOS Vision `VNRecognizeTextRequest` in a small Swift script that prints bounding boxes), then fill each line horizontally from the empty card background left and right of it (linear interpolation per row + light blur + noise). Vertical fills smear when lines sit close together. Default: remove dates, times, reference and invoice numbers; keep the company name and amount; confirm with the creator.
- Scraped asset lists: parse card by card; naive regex paired titles with the wrong IDs. Some stock sites block scripted downloads behind bot checks; download those manually.
- Free stock video: some items are marked with a restricted licence and their 1080p file returns 403; check the detail page for a free licence first. Scan each clip at 1 fps for objects passing through the foreground.
- Renders and frame extraction fill disks fast (the HyperFrames renderer refuses to render when the disk is nearly full). Keep scratch work on a drive with space. exFAT drives don't support symlinks, and macOS writes `._*` files there (exclude them in rsync and diffs).

---

## 12. Behind-the-speaker, natively (Oct 2026 builds)

- `media_overlay` and `text_overlay` take `properties.behind_subject: {quality: "high"}`. Borumi computes and caches the person mask itself. Import the alpha `.mov`, add a full-canvas `media_overlay` with `behind_subject`, done: no layout segment, no plate.
- Camera clips can be `mirrored: true` with `face_tracking_mode: auto`. Then the raw media is **not** what the viewer sees (things flip sides, framing shifts). Judge graphics against `inspect_timeline` render frames (`save: true`, `quality: "max"`), never raw media frames.
- Borumi's own matte sits next to each camera media in the bundle's `medias/` as `<media>.rvm-md854-ds1000.background.mp4` (854×480, white = person) once a cutout has been used. It gives a clean RGBA cutout for motion graphics without any other segmentation model: `ffmpeg -i cam.png -i matte.png -filter_complex "[1]scale=1920:1080,format=gray[m];[0][m]alphamerge" cutout.png`.
- **Inserting a full-screen video with its own audio (a montage, a playback):** `create_scenes` after the scene, then `add_segments` a `take` of the media at the new scene's start (`video_kind: screen`, `audio_kind: system_sound`). The empty scene grows to the media length and ripples everything after it. `system_sound` keeps it out of the caption transcript.
- `export_transcript` and `export_video` need the `exporting` guide fetched first (`guide_required` otherwise). Fetch guides one at a time: asking for three at once returned `guide_response_too_large`.

## 13. Trimming, untrimming and what ripples (the big one)

Learned the hard way on a long screen-share edit. Re-read this before any cut pass.

- **One range per `trim_timeline` call, back to front.** A 17-range call shifted layouts unevenly and left ~1 s gaps everywhere. (Several ranges in one call are interpreted on the pre-trim timeline and did work on a simple single-camera project, but it isn't safe once there are layouts.) Working from the end of the video backwards means earlier ranges don't move.
- **Target every content layer that exists** in a trim: `target: {type: "layers", layer_ids: [camera_1, camera_2…, screen_1, screen_2…, microphone_1, system_sound_1]}`. A piece that lived on `camera_2` wasn't in the list, didn't move, and ended up 20 s out of place.
- **What follows a trim:** overlays, zooms, highlights and later scenes ripple correctly. **`sound_effect` segments do NOT ripple with a trim inside their scene** (they do follow scene-level shifts from an earlier scene). After every trim, list the sound effects after the cut and move them by the trimmed amount.
- **Layouts are attached to the clips under them.** Trims and untrims stretch, shrink and shift them unevenly, so later layouts end up with **gaps** (0.06–10 s seen). In a gap Borumi shows its default layout: a visible glitch. After every trim or untrim in a section with layouts, check the layout track is contiguous (every end == next start). If not, delete and rebuild from a saved view plan (keep it as JSON and shift it by the net time change).
- After any trim, also scan layout properties for a fullscreen layout that lost its `layer_id` (a blank frame) or one now pointing at an empty layer. Borumi reassigns layer refs while reconciling.
- **`untrim_segments` only restores the segment's own edit group.** Screen segments are a separate group from camera + mic, so untrim the matching screen segment by the same amount in the same call, or the screen falls out of sync. `right_ms` = the gap to the next segment's source start. Untrims also leave screen layouts late (re-check for gaps), and overlays don't always follow (one stayed 220 ms early).
- **Trims inside a stretch with no screen media** (a face-only part of a scene before the screen recording starts) broke every screen layout after it: ends rippled, starts didn't. Fix: delete every screen layout and re-add each one spanning [previous face layout end, next face layout start].
- **Media overlays are not cut by `trim_timeline`.** An overlay just gets shorter and drifts out of sync after the first cut. Anything that must be cut with the talk (a talking-head file someone dropped in as an overlay) must be a `take` instead (see §14).
- **Don't use multi-range `trim_timeline` on a fresh take**: only the first piece survived. Use `split_segments` (`times_ms`) and delete the pieces you don't want.
- **Moving a camera piece can land it on a new layer (`camera_2`).** Borumi then adds an automatic fullscreen layout that replaces every later layout. Keep the view plan so you can rebuild, and point layouts at whatever layer the piece landed on.
- **Rebuilding a layout track:** delete the old layouts (`ripple: false`), then `add_segments` in batches of about 28. Each batch changes the timeline hash, so re-read with `get_timeline` (`layers: ["layout"]`) between batches.
- **The creator's own trims in the app desync independent screen layers too.** At the top of every session compare camera vs screen starts (a changed `base_commit_id` means they edited). Fix by moving every screen segment of the block as one unit with `move_timeline_segments` to the camera's start.
- **The creator adjusts layouts by hand.** Before any rebuild, re-read the live layout track and fold their changes into your saved plan. Never rebuild from an old plan over their edits.

## 14. Screen-share sources (camera + screen as separate files)

Some recorders (e.g. Tella) export the talking head and the screen as two files with identical audio.
- Add the talking-head file as a `take` (`video_kind: camera`, `audio_kind: microphone`) at the screen's `at_ms`, then delete one of the duplicate audio tracks (`expand_groups: false`). Check they really are identical first (audio cross-correlation ≈ 1.0 at lag 0). Borumi's default corner layout then puts the camera bottom-right.
- **The "camera" file isn't always a face.** Wherever the recorder's own layout switched to screen, the camera export holds the screen composite with a small face box baked in. Then a fullscreen-face layout shows the screen, and the bubble shows a screen inside a circle. Before building layouts, scan the camera file (`ffmpeg -vf fps=2,scale=32:18,format=gray`, compare each frame to a known face frame and a known screen frame). In those stretches use the screen fullscreen, never the bubble. Better: ask for **separate camera-only and screen-only exports per clip** before you start.
- **Swapping in clean per-clip exports:** align each clip to the original by audio cross-correlation (8 kHz, a 20 s probe, corr ≥ 0.99 gives the exact offset). Import, add as a take at the END of the timeline, delete its audio (`expand_groups: false`), `split_segments` at the source boundaries of the clips in the slot, delete the unused pieces and the old video in the slot (keep the mic), then `move_timeline_segments` each pair with `destination: {type: "at_time", start_ms}`.
- **Some recorders don't capture system audio.** A video played on screen is then silent unless the speakers bled into the mic (−35 dB, about 13 dB under the voice). Measure before keeping a playback: a silent playback usually gets cut.

## 15. Screen zooms, highlights and covering glitches

- The app on screen changes every few seconds in a cut-together screen share (chat ↔ editor ↔ file). Before each screen zoom, list the `screen_1` segments in its range and keep the zoom inside one segment whose source frame you've checked. Low-quality contact sheets can show the wrong decoded frame; confirm with a single `frames` render.
- When a zoom or highlight runs into a change on the recording (app switch, dialog opening, playback going fullscreen), split at the change and delete the tail. Check source frames at ~0.5 s steps around the end of each zoom.
- **`screen_highlight` barely shows on dark UIs.** It only dims everything else, so dark-on-dark gives no contrast. Add a drawn ring as a transparent `.mov` overlay instead. To place it under a screen zoom: Borumi clamps the focus so the view stays inside the source, view = [f − 0.5/z, f + 0.5/z] after clamping, and canvas x = (source_x − view_x0) · z · w_layout (w_layout = the screen's width share, e.g. 0.8667). Verified to the pixel.
- **Highlights are not clipped to the screen layer.** One that reaches past the zoomed view spills onto the canvas background. Keep zoom × highlight width inside the visible window (a 0.77-wide row needs ≤ 1.25×).
- **Lime/multiply highlights vanish on dark pages:** use a ring there. Small text (prices, counts) needs a real camera move (1.8–2.4× onto the phrase); a 1.07 push leaves it unreadable at 1080p.
- **Covering glitches in a recording** (app-switch flash, loading spinner, blank page): pull a still from the same recording just after the glitch (ffmpeg on the bundle's screen media at that source time) and lay it over as a `media_overlay` at the screen's rectangle with `shadow: null`. Overlays draw above the face bubble, so cut a round hole slightly *inside* the bubble; a bigger hole lets the live screen show through as a "ghost bubble".
- **Text burned into a recording** (a date on a label, a name): if it sits still in the frame, lay a small PNG patch over it at a custom position. `scripts/patch_still.py` builds the patch from a `quality: "max"` saved frame by interpolating each column between the rows just above and below, plus a ~1 px blur. One flat colour leaves a visible block over see-through pills.
- `inspect_timeline` `layer_source` returns `media_unavailable` for the whole range if any frame in it has no media on that layer (e.g. a face-only stretch). Query smaller ranges. Contact sheets: `view: {type: "render"}`, `presentation: "contact_sheet"`, `sampling: {type: "uniform", max_frames: N}`.
- A portrait camera clip can carry black rows at the bottom. A 1.1× `camera_zoom` (instant, focus 0.5/0.46) over the clip fills the frame.

## 16. Cutting a long recording

- **Content cuts in run-on speech** ("code, okay. Third…") need manual edges from a 20 ms loudness profile: OUT just before the removed word's onset, IN in the valley before the kept word. A transcript "word" left at a join can be an alignment remnant; check the waveform before cutting more.
- **Borumi's transcript drifts 0.3–0.5 s mid-clip.** A cut placed by transcript time dropped "So the" before the next sentence; `untrim_segments left_ms` fixed it. Always re-read the words at a join after cutting.
- The mic can decay slowly after a sentence (300–450 ms from word end to floor). For a ~0.35 s pause, cut OUT ~0.3 s after the last loud frame and IN 30 ms before the onset, rather than padding from word ends. A lip click can sit just before an onset; set the IN after it.
- Microphone media may be `.wav` rather than `.mp4`; `edge_audit.py` takes the bundle path and reads both.
- **Never cut a long "silence" in a screen share without looking at the screen.** One deep cut removed three playbacks of a previous video (25 s, 27 s, ~75 s): the speaker was quiet while they played, so speech detection called it dead air. Any silence over ~3 s in a screen section: check the frames first. Lines like "hit play", "watch this", "have a listen", "let me show you" protect what follows until the speaker talks again. Playback audio bleeding into the mic shows up as transcript words in another voice.
- **Handling noise** (a bottle crackling, desk knocks) shows as sustained broadband: > 3 kHz energy ratio 0.6–0.85 and zero-crossing rate 0.5–0.6 for ≥ 300 ms, at speech level. Speech sits at 0.05–0.2 apart from short fricatives. Transcripts don't contain it, so scan segment tails for it.
- **Hidden fillers:** the transcript can leave out a drawn-out "uhh" and show a plain gap between words, and silence detection misses it because it isn't silent. In any transcript gap ≥ 400 ms, a voiced, steady, low-pitch hump (low ZCR, autocorrelation ≥ 0.6, at the speaker's pitch) is a filler. Full method in `fillers.md`.
- Cut planning that works: `detect_speech` silence ranges + transcript blocks for content cuts, then refine each OUT/IN on the source waveform, then `edge_audit.py`, then the join check.

## 17. Captions on a screen-share video

- **Split captions per layout.** On screen layouts use a custom position (x 0.03, y 0.8, w 0.75, h 0.15) so the box centres under the screen and stays clear of the face bubble on the right. On face shots use `bottom`.
- **Leave captions out of every playback, montage or external clip where someone talks.** Those have captions burned in. Find the stretches with a contact sheet, not the transcript.
- **Name fixes with `correct_media_transcript`.** It works in MEDIA time: `media_time = project_time − segment_start + media_range.start`. When a word runs past the segment edge, read `get_media_transcript` for its real bounds. Expect the speech model to mishear product names consistently (e.g. "Cloud/Clone code" for Claude Code); collect the creator's list in the taste profile and fix them all before captions go live.
- Captions have no shadow property. Over white pages a dark translucent box (`background_color` black at alpha ~190, horizontal padding 0.5, vertical 0.3, radius 14, stroke 0) keeps any text colour readable. (An earlier outline-only style, §9, failed on white pages.)

## 18. Music bed and final loudness

- The music layer is exclusive, so build **one bed file** for the body: `scripts/music_bed.py` (parts with offsets, each levelled to exactly −41 LUFS by measuring with ebur128 and applying the gain; loudnorm alone landed 1–2 dB off; 0.75 s crossfades; 0.4 s ramps to silence under playbacks). Import once, place as a `music` segment, turn `enable_looping` off.
- The bed is placed by fixed time: **rebuild it after any later cut** and re-place it.
- An intro track can pause under a montage and resume where it stopped (cut the track at the montage start, continue from that sample after it, 0.4 s ramps).
- Finding tracks: some free music sites carry JSON-LD `MusicRecording` entries (name, genre, artist, duration, file URL) on genre pages but not on "discover" pages. Rank candidates with `scripts/music_rank.py` (see `music.md`).
- **Export:** Borumi's `best` preset exports **3840×2160 at 60 fps** and renders slowly (about 1 % per 10–20 s on a 22-minute video). Its exports land near −20 LUFS integrated. Normalise the final file to YouTube's −14 LUFS with two-pass ffmpeg loudnorm, copying the video stream:
  ```bash
  ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -    # pass 1: read measured_* values
  ffmpeg -i final.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=<..>:measured_TP=<..>:measured_LRA=<..>:measured_thresh=<..>:offset=<..>:linear=true" -c:a aac -b:a 320k final_-14LUFS.mp4
  ```

## 19. Review loop and working habits

- **Reviewer-agent loop:** export the section, pull 1 fps frames, and have a separate agent review them against the taste profile with the word timings (real material, the thing named is highlighted, no spinners or blank screens, face bubble clear, no clipped text, pacing). Fix, then run round 2 on fresh frames. On one tutorial it caught 9 real problems across two sections (a spinner, a ghost bubble, highlights invisible on a dark UI, an app-switch flash). It can't hear audio, so joins and sound still need the creator's ears.
- **Section map first.** After the full recording is in, export the transcript, split it into sections with timestamps, what happens, edit status and flags (missing CTA, tangents, misheard names), and have the creator confirm it. It's the source of truth; update it after big cuts.
- HyperFrames renders frame by frame (seek), so anything started from `tl.call(() => gsap.to(...))` never appears. Put every tween on the timeline itself.
- zsh doesn't word-split `set -- $spec` and expands `$VAR:t` as a modifier; run render loops under bash and write `${VAR}:text=…` in ffmpeg filters.
- The shell may lack macOS Screen Recording permission, so app windows can't be captured from Bash; use `inspect_timeline` frames instead.
- Renders to an external drive can sit for minutes in their final move; the file is complete inside the temporary folder. Wait rather than re-render.
