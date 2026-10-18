# Soft text, safe/danger zones, SFX doctrine, park & push

Sources: measured analyses of three reference edits — a clean-text reference edit (cinematic, keywords only), an Arabic explainer-board edit, and an editorial-collage edit — plus a safe-zone tutorial and sound/critic reports.

**This file overrides older, conflicting rules in SKILL.md, craft/03, craft/06 and craft/08.**

## 1. Defaults
Each applies unless the brief, the profile or the user's `rules.md` says otherwise.
1. **Soft text only.** Captions, keywords and reference texts get **no box, pill, card, banner, stroke or filled chip**. Legibility comes from placement, a very soft shadow, a soft radial scrim, or a bottom fade.
2. **SFX are the most important layer.** Sound every motion. Leave captions and plain cuts silent.
3. **Safe zone vs danger zone.** Put text only where neither the platform UI nor the face reaches, allowing for the face growing with zooms.
4. **Park the speaker** (shrink and move them into a corner) when a beat needs room for text or images. Do it per video, not always.
5. **Feed images and sources into the story**: cut-outs, photos, UI, logos.
6. **Background replacement only on request** (see §8); otherwise keep the original background.

## 2. Soft caption spec (1080×1920 9:16, 30 fps)

**Base caption**
- **Font:** IBM Plex Sans Arabic 500, or Tajawal Medium, 64–72 px. The glyph block should be 3.4–3.8 % H.
- **Colour:** off-white `#F2F0E8`, never pure white on a warm grade.
- **Line:** one line of 1–4 words (target 2–3), ≤ 20 letters. Use the speaker's dialect spelling (from the profile).
- **Decoration:** none when the backdrop is dark. On a mid backdrop, add a very soft shadow `0 2px 18px rgba(0,0,0,.35)`.
- **Timing:** hard swap on the phrase onset, −1…+2 f. Keep captions back-to-back. No per-word pop or bounce.
  - Optional premium variant (Premium Soft / clean-text reference): a 4–10 f fade/blur-in, blur 8→0, y +8→0.

**Emphasis** (at most 1 caption in 6)
- Either the whole phrase in the video's accent at ≥ 4.5:1 contrast,
- or one word at weight 700, optionally with a kashida. Don't change the size.

**Position (screen-fixed, never zoomed with the footage)**
- Centre y 1170–1270 (61–66 % H), bottom edge ≤ 1350.
- x centred at 540, max width 700 px (x 190–890) because of the button column.

**Legibility fallback.** Check the contrast of the text against the sampled backdrop, then apply in order:
1. Soft radial scrim `rgba(0,0,0,.28)`, blur 60 px, 1.4× the text block.
2. Bottom fade: black 0 → 45 % over the lowest 35 % H.
3. **Never** a pill or card.

**Hide the captions** whenever a hero word, graphic, insert or park layout is on screen. In the last serious or CTA seconds, optionally leave the ending clean.

**Keyword hero** (≤ 1 per 8–10 s)
- Alexandria 800 at 7–9 % H, or the Premium Soft mix: a light word plus a bold word (§9).
- Soft blur-in: 6–10 f `power3.out`, blur 10→0.
- May sit behind the speaker (matte) when it is 1–2 words and the speaker's head overlaps only the bottom 10–25 % of the letters.

**Coverage mode** (choose one per video in `concept.md`)
- (a) **Phrase captions**, explainer-board model: about 50 % of talk time, hidden during graphics.
- (b) **Keywords only**, cinematic, clean-text / Premium Soft model.
- (c) **Designed verbatim** single words, Premium Soft model: one soft word at a time near the chest.

**Arabic typewriter** (hook or lists only)
- Reveal by substrings (whole letters with joining kept), never per letter in separate spans.
- Typing clicks every 60–80 ms.

## 3. Zones (measured, 1080×1920, 9:16)
16:9 (1920×1080): keep text inside x 96–1824, y 54–1026; nothing important in the bottom 140 px (player controls).

| Zone | Rule |
|---|---|
| Platform top | nothing above y 290 |
| Platform bottom | nothing below y 1480 (description/username area) |
| Sides | 120 px clear everywhere; between y 700 and 1480, keep 190 px on **both** sides (the like/comment/share column, mirrored on Arabic phones) |
| Text box | x 120–960 for y 290–700; x 190–890 for y 700–1480 |
| Hook/title band | y 300–520 (only if the head leaves room, e.g. WIDE/park) |
| Eye line | frame so the eyes land at y 670–800; anchor punch-ins at the eyes |
| Captions | centre y 1170–1270, bottom edge ≤ 1350 |
| **Face danger** | the face box for this shot, grown by the shot's zoom: `face' = anchor + z·(face − anchor)`, + 40 px. Text sitting at the chin in the wide shot lands on the face after a 118 % punch |
| **Zoom crop** | for zoom z at anchor (ax, ay), the visible footage is x ∈ [ax−ax/z, ax+(1080−ax)/z], y ∈ [ay−ay/z, ay+(1920−ay)/z]. At 118 % on the eyes this crops 82 / 82 / 102 / 191 px (L/R/T/B); at 150 % on the centre, 180 px each side. Only **pinned** elements (baked into the footage, text-behind, tracked labels) need this; overlay tracks are not zoomed |
| Pinned safe core | for a 130 % punch: x 20–80 %, y 17–68 % |
| Cover / grid | the grid crop keeps the centre 3:4 (y 240–1680); older 4:5 keeps y 285–1635 and 1:1 keeps y 420–1500. Cover title and face go inside x 120–960, y 420–1250, and the title is ≥ 110 px tall |

**Tool:** `scripts/zones.py speaker.mov shots.json out/`. It draws the per-shot head danger after that shot's framing, the platform bands and the largest safe rectangles as a red/green sheet. Every graphic must sit inside its shot's safe rectangle.

## 4. SFX doctrine
1. **Sound what moves:** slides, grows, whips, animated zooms and pushes, parks and shrinks, transitions, pops of images/cards, and number counters.
2. **Silence:** captions, word reveals, hard cuts and static reframes.
3. **Hook:**
   - Leave an air pocket of 0.4–0.6 s (bed down to about −40 LUFS-M), then one low boom 0…+1 f on the first keyword.
   - The bed sits at −11…−14 dB under the voice during the hook, then drops to −30…−35 dB, or stops.
4. **Section change:** a small crack on the flash frame, then the sub hit (`impact_sub`) on the first frame of the new shot. Mute the bed 3–15 f before it.
5. **Animated zoom/push:** a low boom (100–500 Hz, 0.5–0.9 s decay) starting 0–4 f **before** the move.
6. **Whoosh length ≈ tween length (±15 %).** Peak on the fastest frame. Vary the whoosh files so no two consecutive ones are the same.
7. **Pops and clicks:** land on the element's max-scale frame (+0…+3 f), in descending pitch/level on repeats.
8. **Ending:**
   - Cut the bed **on a picture cut** 1.5–3 s before the end, so the last line is dry.
   - An optional sting pre-laps the cut to black by 5–6 f.
9. **Levels vs voice:**
   - whoosh −10…−14 dB; pop/click −12…−18; impact −3…0 in a gap or −8 under a word; riser ramps to −8 at its peak;
   - bed −18…−24 (hook −11…−14); room tone −25…−35.
10. **Library:** the bundled CC0 SFX library `assets/sfx/` (see its `manifest.json`, which gives `peak_time_s`). Clip start = hit − peak_time_s.

## 5. X-PARK: shrink the speaker

**When**
- A 2.5–3.5 s beat where the speaker lists ≥ 3 items, cites a source, or shows a thing.
- Cut to a different framing before it.
- Emotional lines stay full-frame.

**Build:** `scripts/park.py in.mp4 out.mp4 T0 DUR S XT YT`, an ffmpeg pre-render with a smoothstep ease.
- Background: a blurred copy of the same frame. With a replaced background, prefer the plate: composite the speaker layer scaled over the plate instead.
- DUR 0.5–0.6 s. Reverse the ease to exit, or hard-cut back.

| Preset | S | XT, YT | Freed area |
|---|---|---|---|
| Park bottom-right | 0.55 | 432, 442 | text column x 6–38 % W, y 12–75 % (face lands at about 28–35 % H) |
| Park top | 0.55 | 243, 110 | lower band 60–76 % H (captions off) |
| Corner cam | 0.34 | 650, 1000 | whole frame for UI/image |

- **Captions** are off during the park. Text and images in the freed area are soft (no cards). Rounded corners or a soft shadow on the parked video are allowed only as a HyperFrames overlay. No border card.
- **SFX:** a low air whoosh stretched to DUR, starting on the first motion frame. Silent on a hard-cut exit.
- **With the speaker matte** (background replaced), X-PARK can also be done in the editor by scaling the speaker track over the plate (in Resolve: Zoom 0.55 with Anchor Point at the bottom-right corner — a hard reframe).

## 6. X-PUSH: an eased animated push-in, pre-rendered
- ffmpeg: `scale=w='2*trunc(1080*(1+A*E)/2)':h=-2:eval=frame,crop=1080:1920:x='(iw-1080)/2':y='(ih-1920)*0.33'`, where E is smoothstep over 14–18 f and A is 0.12–0.28. The anchor factor 0.33 keeps the eyes on their line.
- Use it into inserts or for emphasis, with a riser peaking on the cut or a low boom 0–4 f before.
- Captions must be a separate overlay, never burned in.
- `scripts/push.py` wraps this. If jitter shows, upscale ×2 first.

## 7. Idea → edit grammar (pick ONE per video in `concept.md`)

| Grammar | Pattern | Fits |
|---|---|---|
| **Chapter looks** (clean-text reference edit) | one look per sentence (grade and type change), with a loud transition between looks (a 13-frame strobe W1/A1/W1/B1/W1, film burn, glitch) and calm inside each chapter | short cinematic 20–40 s |
| **Explainer board** (Arabic explainer reference edit) | one insert per example the speaker lists, on one flat board colour, UI mockups and nodes popping on the spoken noun; board whips 4–5 f + deblur 6 f; about 28 % of runtime in cutaways | educational 60–140 s |
| **Editorial collage** | one metaphor object (grayscale cut-out) plus one phrase every 1–2 s; paper texture, one big colour disc, crop marks | hooks, intros, manifesto lines |
| **Premium Soft** (§9) | soft single words, a light+bold keyword mix, one accent, floating photo cards, light streaks, glow numbers behind the speaker | personal-brand and authority videos; **default grammar for talking-head videos** |

## 8. Background replacement — only on request
- Keep the original background unless the user asks. The user either names/gives a plate (their own photo or video) or describes a look; for a described look, find a real photo on Pexels/Unsplash (use the browser if a site blocks curl) or generate one.
- Build: `scripts/room.py` (room plate) or `scripts/wall.py` (plain/graphic wall) → flip so the practical light sits on the speaker's key side, lens blur 8–12 px, wall 1–2 stops under the face, grain → `scripts/matte.py --rgba-in --bg plate.png` (light wrap ≤ 0.12, radius ≤ 6 px; edges from RVM fgr; no edge blur/halo; QA the fastest hand frames at 100 % on grey + green).

## 9. PREMIUM SOFT — the default grammar for talking-head videos
Two text levels, never on screen together:
- **Karaoke word**: every spoken word, 1–2 at a time, IBM Plex Sans Arabic 500 ~66 px, #F2F0E8, soft shadow only, on the chest band (screen-fixed), instant swap at word start −1 f.
- **Hero phrase** (1–3 per shot, replaces the karaoke word): small light lead-in (Plex Arabic Light or **Aref Ruqaa** — Ruqaa's natural slant = our "italic"; Google Fonts) ~74 px + huge bold keyword (Alexandria 900, 118–135 px, kashida instead of italic) partly (30–50 %) **behind the speaker's head** (matte), a second bold line in front of the chest — face framed between the two lines; hero blocks sit on the RIGHT (mirrored). Never slant Arabic > 4°, never split letters.
Emphasis = size/weight/Ruqaa + moving gradient (accent → deep accent → plum, sweep 36 f, blink off on f4/6/8 at settle) or a strike-through bar (12 px, #DC3429, draws R→L 8 f, word then fades out 7 f blur 12, sinks 14 px).
Graphics are OBJECTS IN THE SCENE, depth-sorted with the speaker's cut-out: a "16x"-style lit sign on the wall (silver extruded → yellow fill rises bottom-up 28 f), logo/trophy resting on the speaker's palm (tracked), a ring of cards orbiting the speaker, floating photo cards (radius 22, soft shadow, ±5 px float, glow-in 5 f, pairs 6 f apart, exit through a 3 f glow + 1 f white). Pinned to wall/head while the camera drifts (replay camera drift on a wrapper or Fusion Tracker — free).
Everything enters/exits through LIGHT: white glow, orange flare streak (3 stacked strokes glow/colour/core, draws 90 f, tail erases, dot follows the head), orbit rings (scale 2.2→1 over 15 f, ~90°/s, rings 2 f apart). Light passes render on BLACK and go to the editor with Screen composite (baked glow on alpha turns grey).
Motions: whip-slide keyword 220 px from the right 4 f expo.out + horizontal blur 60→0 over 5 f; drop-in phrase y −64→0 15 f expo.out + blur 10→0 7 f, then drift down 18 px during hold.
Cuts 1–7 f: white flash (brightness ×3.2 over 2 f), whip (directional blur 120 px 4 f), defocus jump (blur 18 over 4 f, cut, 3 f back) — adjustment clip over the cut so graphics blur too. Sound: whoosh 0.2–0.6 s before + sub boom ±1 f on the cut; an SFX on almost every graphic event; music ~12 dB under voice with ~2.5 dB ducking.
Camera: gimbal drift/push, shots ~4.3 s. For locked-off shots fake it with a slow push 1.00→1.05 per shot (X-PUSH or DynamicZoom) and the park/punch ladder.
Layer order (timeline tracks, bottom → top): plate → behind-graphics → light-behind (Screen) → speaker matte → front-graphics → light-front (Screen) → transition adjustment clips.
