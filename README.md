# Borumi Video Editor: a Claude Code skill

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill that edits your YouTube videos inside the **Borumi** desktop app. Talking-head videos and screen-share tutorials: cuts, fillers, layouts, B-roll, zooms, sound effects, music, captions and export, with your taste written down as rules it follows every time.

This is the skill from my video on how Claude Code fully edited my YouTube video in Borumi.

**How it works:** Borumi exposes its editing operations through MCP, so Claude Code edits the project directly while you watch every change land on the timeline. Built and tested on two real edits: an 11-minute talking-head video and a 22-minute screen-share tutorial.

**What it does:** section map → cuts with a join check → waveform edge audit → filler and pause pass → face/screen layouts for screen shares → B-roll it finds itself → motion graphics placed by phrase → zooms and highlights on what you name → chapter cards → sound effects → music bed → captions with name fixes → a reviewer-agent pass → export and loudness.

## Setup

| What | Why | How |
|---|---|---|
| Borumi with MCP on | the editor drives Borumi through it | Borumi → Settings → AI → Enable MCP (Borumi must be open) |
| ffmpeg / ffprobe | reading waveforms, building plates, patches, music beds, loudness | `brew install ffmpeg` |
| Python 3 + numpy, Pillow, scipy | the scripts (`scipy` only for the filler pass) | `python3 -m pip install numpy pillow scipy` |
| *optional* mlx-whisper | word timings for motion graphics on Apple Silicon (not used for fillers: it drops "uh") | `python3 -m pip install mlx-whisper` |
| your sound kit and music | Claude places them; you choose and license them | see "Sounds and music" below |


Scripts in `skills/borumi-video-editor/scripts/` (each prints its usage when run without arguments): `cut_audit.py`, `edge_audit.py` (cut audits), `filler_detect.py`, `filler_signature.py`, `filler_edges.py`, `voicefeat.py` (filler pass), `music_rank.py`, `music_bed.py` (music), `page_clip.py` (real-page B-roll), `patch_still.py` (painting out text in a recording).

## The edit order, and why each rule exists

| Step / rule | Why |
|---|---|
| Section map first, confirmed by you | the edit needs one source of truth for what each part of the video is for |
| Intro first as a pilot, then section by section | you approve the style on 60 seconds before it's applied to 20 minutes |
| Cuts set on the waveform, never on transcript times | transcript times drift 0.3–0.5 s and cut words in half |
| Join check on every content cut (read both sentences, 300–600 ms pause, you hear it) | a cut that reads fine in text can still sound broken |
| One range per trim, back to front, every content layer | multi-range trims left gaps in layouts and left pieces behind |
| Check layouts and move sound effects after every trim | layouts open gaps and sound effects don't ripple with trims inside their scene |
| Never cut a long silence in a screen share without looking | the "silence" can be a playback you're showing |
| Filler pass after the cuts, pause list for you to pick from | fillers are personal: some "doubles" are emphasis, some short words only sound like fillers |
| "You can see / over here" switches to the screen | the viewer must see what you point at |
| Highlight exactly what you name on screen | it turns a recording into an explanation |
| Real material over generic graphics | real pages, real footage and your own frames read as proof |
| Source labels without dates | dates make a video look old |
| Graphics behind you with Borumi's `behind_subject` | the native cutout is cleaner and simpler than the old plate workaround |
| Zooms pure-scale into the centre, ending only under a cut or cutaway | Borumi can't ease back out, so the snap must be hidden |
| Punch-ins only on cheeky lines, 2–3 per section | they stop landing if overused |
| Sound effects levelled in LUFS relative to the voice | peak levels lie: short ticks can share a peak with a sweep and sound 10 dB quieter |
| Body music sparse, ranked by busyness and voice-band share, auditioned under the voice | busy music competes with explaining; a track that sounds great alone can clash under talk |
| One pre-mixed music bed, rebuilt after any cut | Borumi's music layer is exclusive and the bed is placed by fixed time |
| Captions split per layout, none over playbacks, names fixed first | the face bubble and burned-in captions collide; misheard product names look careless |
| Reviewer agent on 1 fps frames after each section | a second pair of eyes catches spinners, flashes and hidden text before you do |
| Export with `best`, then normalise to −14 LUFS | `best` is 4K60, and Borumi's exports land near −20 LUFS, quieter than YouTube's target |

## Borumi quirks it already knows

Full list with workarounds in `references/borumi-learnings.md`. The big ones: one range per trim; untrims only restore their own edit group and leave layout gaps; sound effects don't ripple within a scene; the music layer is exclusive; media overlays aren't cut by trims; `best` export is 3840×2160 at 60 fps and slow; exports need the `exporting` guide and an existing folder.

## Sounds and music: bring your own

No sound effects or music are included. The author's kit is built from a paid pack whose licence doesn't allow redistribution, so the skill ships a template (`references/sound-kit-template.md`) and the levels that worked, not the files. Music in the worked example comes from Mixkit's free library; the tracks are named and linked, never bundled. Read the current licence of anything you download, keep a `CREDITS.md`, and don't commit your kit or tracks to a public repo.

## Install

```bash
git clone https://github.com/docusphere/claude-skill-borumi-editor.git
cd claude-skill-borumi-editor
bash install.sh
```

This copies the skill into `~/.claude/skills/borumi-video-editor` (it asks before overwriting, and backs up the old copy outside the skills folder). It checks for ffmpeg, Python and the Python packages and prints install hints; it installs nothing itself. Set `CLAUDE_SKILLS_DIR` to install somewhere else.

## Quick start

1. In Borumi: **Settings → AI → Enable MCP**, and open your project.
2. The first time, tell Claude your folders (or write them to `~/.claude/skills/borumi-video-editor/config.md`):

   | Placeholder | What it is |
   |---|---|
   | `<WORKSPACE>` | folder for per-video working files (transcripts, section map, decisions log, scratch) |
   | `<SFX_LIBRARY>` | your own pre-levelled sound kit (see `references/sound-kit-template.md`) |
   | `<MUSIC_LIBRARY>` | your licensed music tracks + `CREDITS.md` (see `references/music.md`) |
   | `<EXPORT_DIR>` | export folder |
   | `<MOTION_OUT>` | optional: finished motion-graphic clips + `manifest.md` from a separate motion-graphics session |
3. Start a new Claude Code session in Borumi's AI workspace folder and say things like:
   - "Edit this video in Borumi. Start with a section map."
   - "Cut the intro, then do the filler pass."
   - "Switch to the screen whenever I say 'you can see' and highlight what I name."
   - "Add sound effects, zooms and music, then captions and export."

## Make the taste profile yours

`references/taste-rules.md` is my own profile as a worked example: sound levels, music, caption style, cut and filler rules, what goes on screen, each with the reason behind it. Keep what fits you and change the rest, or start from the blank `references/taste-rules.template.md`. Every time you approve or reject something during an edit, ask Claude to add a row with your reason. The reasons are what let it apply your taste to situations it hasn't seen.

## Limitations

- Claude can't hear. Sound choice, levels and cut joins need your ears; the skill sends you short preview clips.
- Learned on Borumi 0.31.3–0.32.0. Borumi changes between versions; the skill always reads Borumi's own guides first.
- Some steps use macOS tools (Apple Vision for cutouts in older Borumi builds, `open -a Borumi`). The rest works anywhere ffmpeg and Python run.
- Motion graphics are built by a separate skill; this one places them if you have them and works fine without.

## License

Copyright © 2026 Nillard Ltd (company number 16312961, registered in England and Wales). All rights reserved except as granted in `LICENSE` (Nillard Ltd Skills License 1.0):
- **You can** use and modify the skill for your own work, commercial work included (your monetised channel, client videos). What you make with it is yours.
- **You can't** sell, redistribute, re-upload or bundle the skill (in courses, memberships, marketplaces or other repos) without written permission from Nillard Ltd. To share it, link to this repository.

Not affiliated with or endorsed by Borumi or Anthropic.
