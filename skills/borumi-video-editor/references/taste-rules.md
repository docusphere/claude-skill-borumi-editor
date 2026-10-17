# Taste profile

**This file is yours to edit.** It's the set of defaults the agent follows on every video. When a rule here and a shot list disagree, the rule here wins. Tool mechanics live in `borumi-learnings.md`; this file is about taste.

## How to make it yours
1. Either edit the worked example below (keep what fits, change the numbers, delete the rest), or start from the blank `taste-rules.template.md` and save it over this file.
2. During every edit, each time you approve or reject something, ask Claude to add a row: **the rule, and why, in your own words.** The "Why" column is what lets the agent apply a rule to situations it hasn't seen instead of copying it blindly.
3. Keep rules concrete: numbers (LUFS, seconds, scale), names of sounds and tracks, what you said.

---

# Worked example: the author's profile

These are the rules of the skill's author (Frank, Nillard Ltd), built from his feedback on two real edits in October 2026: an 11-minute talking-head video and a 22-minute screen-share tutorial. Each row records what he asked to change and why, or what he explicitly approved.

## 1. Sound design

| Rule | Why |
|---|---|
| A **soft, smooth whoosh on every switch to a full-screen clip**, peak on the cut, at about −33 LUFS. Nothing on the return to the face. | Approved as-is. Borumi's built-in whooshes sounded "too cartoonish". |
| A **soft whoosh on chapter cards**, peak on the cut hidden inside the card. | Approved. |
| **Detail sounds** (pops, ticks, slides) at about **−36 LUFS on the file, roughly 15 dB under the voice** (voice ≈ −21 LUFS). | At −39 LUFS and dull he couldn't hear them. At −24 to −26 LUFS: "much lower, I can't hear me speak". |
| **Photo cards landing:** **one** short card or paper slide, the same sound for every card. | Rejected soft hits with a treble boost ("some high ping sound") and a heavy paper glide ("like moving a piece of rock"). |
| **Complex animations get a layered sound design matched frame by frame**, mixed into one stereo file: a tick per element appearing (crisp tick layered with a wood tick), a sweep for arrows or paths, a rising, thinning tick ripple for crowds filling in. | "Perfect", "amazing". |
| **Balance layers by short-term loudness, not peak.** In the loudest 100 ms, ticks sit level with or 1–2 dB above the sweep (tick peak ≈ 1.6× sweep peak). | First version: "I can't hear the dots at all, only the arrows". |
| **Pan moving elements with the motion** (equal-power, about −0.8 → +0.8 across the travel). | Got "amazing". |
| **Start with a few sounds, expand once approved.** Send a 5–10 s preview export for every audio change. | "Not too many… start with a few and then add some more." He judges by ear. |
| Use sounds from his own licensed pack, with pre-levelled copies in a kit and a README. | Consistency and licensing. |
| Counters landing don't need a sound by default. | Early rule; later accepted at the quiet level. |

## 2. Music

| Rule | Why |
|---|---|
| **Intro:** his signature track (Deep Urban by Eugenio Mininni, Mixkit: warm deep-house, ~120–125 BPM, bass-forward), from the same section on every video (0:45 in). It pauses under a montage and resumes where it stopped. | "It's the exact vibe I'm looking for." Same section = a recognisable opening. |
| **Body music is sparse and chill:** few instruments, low energy, steady. Punchy deep-house only for the intro and payoff moments. | "We don't want too much going on… that distracts the viewer from me explaining." |
| **One track per chapter**, each change hidden under a chapter card, starting on the section he liked (e.g. Autofahren from 1:40). | He asked to "trim to the favourite part early" and wanted more of the part he liked. |
| Level: **−41 LUFS (≈ 20 dB under the voice)**, silent under playbacks. | "I like the music." |
| **Auditions:** reference first, then each candidate 10 s alone and 10 s under his voice at −20 dB. Candidates ranked by busyness and voice-band share. Offer 4–5. | How every track so far was picked. Under-the-voice is the real test. |
| Rejected: Lo-Fi 04 (Lily J); Hazy After Hours (replaced by more Autofahren). Liked: Autofahren, Smooth Jazz (Francisco Alvear), Focus on Yourself (Eugenio Mininni). | His feedback. |
| Free, YouTube-safe sources only, with a `CREDITS.md`. | Standing rule. |

## 3. Captions

| Rule | Why |
|---|---|
| **Style:** yellow text (#FFE200), Helvetica Neue, size 48, sentence case, no word highlighting, on a **dark translucent box** (black at alpha 190, padding 0.5 / 0.3, radius 14, no stroke). | He asked for "professional, minimalist, old VHS tape yellow captions". An outline-only version became unreadable over white pages; the box fixed it. |
| **Split per layout** on screen shares: centred under the screen on screen views, bottom on face views. | Keeps them clear of the face bubble. |
| **No captions over playbacks, montages or external clips** where someone talks. | They have captions burned in; doubled captions look broken. |
| **Proofread before captions go live.** His usual mishearings: Cloud/Clone/Cloco → Claude (Code); Burumi/Burubi/Forumi → Borumi; Tela → Tella; CapCon → CapCut; "scale" → skill; "police" → polished. | Wrong product names on screen look careless. |
| Nothing else sits in the caption band (pills, labels, CTAs stay above ~y 880 at 1080p). | A link pill collided with captions. |

## 4. Cuts, transitions, timing

| Rule | Why |
|---|---|
| **Every content cut gets the join check:** read the two sentences together, 300–600 ms pause, no clipped word, send him the join. | "This is the most important." The first trial caught a cut that dropped "So the" because transcript timing drifted. |
| **Fillers:** cut uh/um, his tag "right?", quick repeats and hidden held "uhh"s. Keep "very very", "super super" (emphasis) and real short words ("edited **a** YouTube video"). | He flagged a hidden "uhh" himself, and a cut "a" that broke the sentence. |
| **Long pauses:** trim pauses ≥ 0.75 s to ~0.4 s, mid-sentence ones first; he picks from a numbered list. | Approved the recommended set from a 28-item scan. |
| **A full-screen clip near a cut must end at least 50 ms after the cut.** | Ending 60–140 ms before left a flash of the old shot ("the cut was a bit loose"). |
| **Chapter cards readable for about 2 s.** | "Doesn't give the user the time to read." |
| **Every graphic fades fully out before it ends.** | 11 clips were popping off while still visible. |
| **Zooms:** slow pure-scale into the screen centre, one continuous move; end only on a hard cut or under a full-screen clip. | "I just want a simple zoom… doesn't change the XY axis." |
| **Punch-ins (1.4×, instant) on funny or cheeky lines**, 2–3 per section max. | He chose the top of the 1.2–1.4× range; a softer punch looked too weak at 1080p. |
| When a bug shows up in one place, **audit the whole video** for it. | He appreciated the sweep. |

## 5. What goes on screen

| Rule | Why |
|---|---|
| **Real material over motion graphics:** real pages scrolled to the line with a highlight, real clips, real people. | "Less motion graphics… more real examples." |
| **Highlight exactly what he names** on a screen share ("base layer", "sound effects row" lights up as he says it). | Called it the best part ("you are the goats"). |
| **Explain with his real material:** take a real frame apart into its layers (exploded view, each layer tagged as he names it), then put it back together. | Same praise. Generic diagrams read as filler. |
| **"You can see / over here / right here" means the screen**, even if his cut had his face there. | He flagged a "you can see the result over here" shown on his face. |
| **Show the dictation:** when he dictates a prompt, the recording indicator and the input are zoomed and highlighted until the dictation really ends. | Viewers should see his words turn into the prompt. |
| **Source pills carry no dates.** | He wants videos to stay timeless. |
| **When the line describes a behaviour or feeling, show a person doing it**, with a light UI layer on top. | Words or abstract cards read as filler there. |
| **Lists hold parallel items only.** A result is an outcome line with a connector, not one more card. | "It seems like an extra option." |
| **Show cause before effect**, even when he says the effect first. | "Show 'enjoy it' first, and then 'get good faster'." |
| **Track record:** his channel → Popular tab → top view counts highlighted → him in a top video with its real view count. | "Emphasise the videos that perform really well." |
| **Objects look like the real thing; lines visibly attach** to what they connect. | A flat "TV" was rejected; "make the lines actually touch the phone". |
| **Never invent numbers or earnings.** Only numbers he says or live ones on screen. | An untrue claim had to be cut. |
| **No redundant labels.** Don't tag an image with what he's saying at that moment. | The voice already says it. |
| **No spinners, blank loads or app-switch flashes** on screen; cover them with a still from the same recording. | The reviewer pass flags these every time. |
| Real-world footage gets a documentary grade (faded warm, grain, vignette, 2.39 bars, slow push). | "Professional documentaries" look. |
| **Opener:** his face in the normal background for the first words, then a **full-screen** graphic, then a **hard cut** back to him. | Chosen over keeping the cutout on a white backdrop for the whole opener: the full-screen gives the scene change and room for bigger cards. |
| **CTA proof:** after the logo reveal, a live recording of the real landing page with a slow push to the headline and a ring on the signup button. | "So viewers see it is legit and clickable" (his idea). |
| **Comparisons as countable icons** ($ coins popping in one by one) rather than bars. | "Instead of a bar… dollar icons appearing one after another." |
| **Screenshots with private data get redacted** (dates, times, reference and invoice numbers), keeping the company name and amount. Confirm with him. | Proof without leaking details. |

## 6. Visual style
- House style: **Apple-clean** (light ground, Geist, one accent highlight, fade + rise + blur). On the tutorial a **sketch** style (cream tags, mono labels, drawn ink, orange accent) for tags and rings.
- His real taste is **Vox paper collage**, used as an intro cold open; Apple-clean after. Build one sample beat first for anything new.

## 7. Working with him
- He dictates by voice: ask in plain prose, not multiple-choice prompts.
- Say "intro", not "hook".
- Timestamps he sends are exact; find the cause at frame level before fixing.
- He edits in Borumi himself between sessions. Re-read the live timeline every session, keep his edits, and only flag big deletions.
- After each section, run the reviewer-agent pass before showing him, and send short clips for anything he has to hear.
