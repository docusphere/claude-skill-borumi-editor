# B-roll sourcing: Claude finds and captures it

The speaker records themselves (and their screen, in Borumi). **Every other visual is found and captured by Claude.** Do it right after the shot list is approved, before placing anything.

## What to look for, per line
| The line… | Go find | Capture as |
|---|---|---|
| cites a stat, study or quote | the original article or report | real page scrolled to the line, key line highlighted (`scripts/page_clip.py`) |
| mentions a person's public statement or talk | their YouTube video or interview | a short screen recording of the video page playing (browser automation, e.g. Playwright), with the title and channel visible |
| names a person | CC-licensed photos (Wikimedia Commons first) | photo stack or side cards; face-centred crop |
| names a company, product or platform | its real website or app page | page recording with a slow push to the relevant part |
| describes people doing something (cooking, gaming, filming) | free stock footage (check the licence: commercial use + YouTube allowed) | full-screen cutaway, 1.5–3 s |
| shows the speaker's own proof (channel stats, earnings, results) | the live page, signed in by the speaker | page recording; never type in their credentials yourself, they sign in |

## How to capture
- **Pages:** `scripts/page_clip.py <url> "<line to highlight>" <out.mp4>` scrolls to the line, eases in and highlights it. Check the result frame by frame for cookie banners and pop-ups; decline non-essential cookies.
- **Other people's YouTube videos:** record the video page playing in the browser for 3–6 s. Don't download the video file (that breaks YouTube's terms). Keep it short, show the source on screen, and credit it in the description.
- **Photos:** Wikimedia Commons CC BY / CC BY-SA / public domain. Save each one with a row in `CREDITS.md`: file, source URL, author, licence.
- **Ask before any download.** List what you want (URL, author, licence, size) and wait for a yes.
- **Page captures that worked:** Playwright at 1600×900 with `device_scale_factor: 2` (crisp at 1080p), phrase rectangles from DOM text ranges for the highlight, the highlight inside the same zoomed container as the screenshot so they move together. On cookie walls click "Reject all" (match the button text). Some social sites render posts blank without a login; a public search page often shows the same point.
- **Source pills carry no date** ("anthropic.com", "YouTube · search"), so the video stays timeless.

## Rules
- Real material over mockups: a real page, a real person, real footage beats an illustration. **Never AI-generate a real person** or a fake screenshot of a real brand.
- Only numbers the speaker says, or live numbers from the real source on screen. Never earnings claims they didn't make.
- Blur or crop anything private: emails, API keys, dates on payments, other people's names in DMs (OCR + fill; see borumi-learnings.md).
- Every source goes into the description credits block when you publish.
