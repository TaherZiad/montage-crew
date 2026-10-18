# Caption-style library: 28 styles × 14 colour schemes

A caption style and a colour scheme are picked **for each video**. **Default: CAP-04 Hormozi Punch with SC-02 (white, black stroke, yellow key word)** — the skill's default unless the profile/brief picks another. CAP-01 Soft Phrase is the calm alternative.

| What | Where |
|---|---|
| Module | `assets/captions/caption-styles.js` (motion) + `assets/captions/caption-styles.css` (looks + @font-face) |
| Gallery to choose from | `assets/captions/gallery/index.html` — open it locally in a browser; it renders every style live on a neutral background (CAP numbers and the 14 SC palettes) |
| Gallery project | `assets/captions/gallery/` (`python gen.py` regenerates `index.html`) |
| Fonts (all OFL, `assets/fonts/`) | new: Readex Pro, Rubik, Lalezar, Baloo Bhaijaan 2, Changa, El Messiri, Noto Kufi Arabic, Amiri Bold, Marhey, Lemonada, Almarai XB (+ Reem Kufi was tested and dropped: its «هـ/ه» shapes read badly at caption size) |

## 1. How to call it
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><script src="rtl-kit.js"></script><script src="caption-styles.js"></script>
<style> /* paste caption-styles.css here (HyperFrames check wants @font-face inline) */ </style>
<div id="captions"></div>
<script>
  gsap.defaults({ lazy: false });
  const tl = gsap.timeline({ paused: true });
  const words = WORDS_CUT.words;                       // words_cut.json → [{w, s, e}]
  const captions = [                                   // 2–3 words per line, ≤ 20 letters (craft/09 §2)
    { i: [0, 1, 2] },
    { i: [3, 4, 5], key: 5 },                          // key = the ONE emphasised word (≤ 1 caption in 6)
    { i: [6, 7], key: 7, emoji: "💻" },                // emoji only for CAP-17
  ];
  CS.apply(tl, captions, words, "CAP-08", "SC-04", { root: "#captions", top: 1170 });
  window.__timelines["main"] = tl;
</script>
```
- `scheme` can be an id (`"SC-04"`), an object `{ink, acc, acc2, stk, on}` (for example a client's brand colours), or `null` for the style's default.
- Timing:
  - `t0` defaults to the first onset − 1 f.
  - `t1` defaults to the next caption's `t0`. After a pause longer than 0.6 s, `t1` is the last word's end + 0.35 s.
  - Override either per caption with `t0` / `t1`.
  - To hide captions under a graphic, give `t1` or split the list.
- `tok: ["لـ Claude", …]` overrides how a word is displayed. Pure-ASCII tokens get Montserrat in an LTR-isolated span.
- `opts.top` moves the caption block. The default is top 1170 (centre ≈ 1215), x 190–890, so the 700 px max width is kept. Exceptions: CAP-15 sits at 1100 and CAP-18 at 1300.
- **Seek-safe and Arabic-safe**:
  - Captions are split per word only (never letters).
  - Hidden states come from CSS, and there is no `Math.random` and no `repeat:-1`.
  - CAP-26 needs `rtl-kit.js` (`RK.kashida`).
- Real videos run 2–3 words per caption, which fits one line. The gallery shows all 6 words, so heavy styles wrap to 2 lines. That is why `hyperframes check` reports `content_overlap` for the glyph boxes of wrapped lines in CAP-04/05/12/21. It looks fine in the stills.
- Render the captions as their own alpha layer (`--format mov`), as the captions agent does.

## 2. Picking a style (let the user pick in the gallery `index.html`; else go by topic)
| Video energy / topic | Styles |
|---|---|
| Calm authority, personal brand, premium (Premium Soft grammar) | **01**, 02, 14, 16, 26, 19 |
| Tutorial / educational / explainer | 01, 03, 06, 08, 24, 13 (code/tech lists) |
| Hype, hook-heavy, money/results, challenges | 04, 05, 21, 12, 28 |
| Tech / AI / gaming / night look | 09, 23, 11, 08 |
| Storytelling, emotional, cinematic | 18, 20, 19, 02 |
| Fun, light, youth | 22, 17, 27, 28 |
| One idea per beat, hooks, slow speech | 15, 25 (default: no single karaoke words in full videos, so use 25 only in a hook) |

Rules that still apply to every style:
- Use one style and one scheme per video. Keep them consistent.
- Emphasise ≤ 1 caption in 6.
- Hide the captions while a hero, graphic or park layout is on screen.
- Keep captions silent (no SFX).
- Respect the safe zones.
- CAP-07 is the only one with a box, so it is flagged ⚠. The default soft-text rule (craft/09 §1) forbids it unless the user picks it.

## 3. The 28 styles
Columns:
- **T**: caption entrance.
- **W**: how each word shows up at its onset.
- **H**: the spoken-word highlight.
- **Out**: the exit.
- **Schemes**: the default first, then the 2 alternates.

Shared highlight timing: the colour goes to the accent in 2 f (power1.out) at the onset and back to ink in 3 f at the next onset. The key word stays in the accent.

| # | Name | Font · weight · size | Look | Motion (frames @30) | Schemes | Fits | Arabic notes |
|---|---|---|---|---|---|---|---|
| CAP-01 | **Soft Phrase** (calm alternative) | Plex Arabic 500 · 68 | off-white, soft shadow 0 2 18 .45, no box | T hard swap; W all; H spoken word → acc 2 f, back 3 f; Out hard | SC-01 · SC-04 · SC-06 | everything; the calm, soft look | Plex has the cleanest dialect spelling at small sizes |
| CAP-02 | **Soft Blur-In** (Premium Soft) | Plex 500 · 68 | as 01 | T fade + blur 8→0 + y 8→0, 6 f power3.out; Out blur-fade 4 f power2.in | SC-01 · SC-07 · SC-08 | premium, calm | — |
| CAP-03 | **Karaoke Fill** | Plex 600 · 70 | unspoken words at 42 % ink | W all; H dim → acc 2 f → ink 4 f at next (key stays acc) | SC-02 · SC-01 · SC-04 | podcasts, explainers | dim = ink × .42 (auto) |
| CAP-04 | **Hormozi Punch** | Cairo 900 · 78, key 1.12 em | white, 11 px black stroke (paint-order), yellow key | W pop 1.3→1, 5 f power2.out at onset; H acc | SC-02 · SC-03 · SC-14 | hype, money, hooks | Cairo Black keeps joins under a thick stroke; ≤ 3 words |
| CAP-05 | **Beast Bounce** | Lalezar 400 · 102 | thick stroke 12 + hard 9 px drop, −3° tilt | W pop 0.3→1 back.out(2.4) 5 f; H acc2 (colour-coded) | SC-03 · SC-02 · SC-05 | entertainment, challenges | Lalezar is a display face: 1–3 words max |
| CAP-06 | **Clean Educator** (Ali Abdaal) | Readex Pro 600 · 64 | white, pastel key | T scale .96→1 + fade 6 f power3.out; H pastel acc; Out soft 4 f | SC-09 · SC-11 · SC-12 | educational, B2B | Readex = Lexend for Arabic, high legibility |
| CAP-07 | **Highlight Pill** ⚠ box | Rubik 700 · 70 | accent pill behind the active word, text `--on` | pill fades in, scale .8→1 back.out(1.8) 3 f; out 2 f at next | SC-05 · SC-02 · SC-09 | Submagic/Captions.ai look | off-rule (soft text); pill radius .26 em |
| CAP-08 | **Underline Sweep** | Plex 600 · 68 | 8 px rounded acc bar + glow | bar scaleX 0→1 from the RIGHT 6 f power3.out; fades 3 f at next (key keeps it) | SC-04 · SC-10 · SC-01 | tutorials, tech | bar sweeps R→L (RTL reading) |
| CAP-09 | **Neon Glow** | Alexandria 700 · 70 | white + soft acc halo; key acc2 glowing | T fade+rise 9 f; H text-shadow 0→14/42 px in 3 f + neon flicker 1/.45/1/.7/1 on f1–5 | SC-04 · SC-05 · SC-06 | AI, gaming, night | glow via text-shadow, not filter (keeps edges crisp) |
| CAP-10 | **Outline → Fill** | Alexandria 900 · 74 | 2.5 px outline, hollow | H fills ink (key fills acc) 3 f at onset, stays | SC-12 · SC-02 · SC-06 | bold statements, lists | heavy weight is needed: thin Arabic outlines break at joins |
| CAP-11 | **Gradient Sweep** | Alexandria 800 · 78 | gradient-clipped words, drop-shadow filter | backgroundPosition 0→100 % in 8 f power2.inOut: acc→acc2 enters from the right | SC-05 · SC-10 · SC-11 | trendy, creative | per-word background-clip; never letters |
| CAP-12 | **3D Extrude** | Lalezar 400 · 100 | 7-step acc extrusion + dark base; key acc2 | T pop .7→1 + y 40→0 back.out(1.8) 6 f; H scale 1→1.14 3 f back.out(2), settle 4 f | SC-10 · SC-02 · SC-04 | YouTube-y, playful hooks | extrusion goes down-right; fine with RTL |
| CAP-13 | **Typewriter** | Noto Kufi Arabic 500 · 60 | right-aligned, acc caret | W words appear (display) exactly on onset; caret blinks every 8 f | SC-06 · SC-12 · SC-04 | code, steps, lists | per WORD typing (CapCut letter typing flashes isolated forms); add `typing` SFX only on hooks |
| CAP-14 | **Word Blur-Rise** | Plex 500 · 70 | as 01 | W blur 12→0 + y 14→0 + fade 5 f power3.out per word; H acc | SC-01 · SC-07 · SC-08 | premium storytelling | = RK.wordsIn timing |
| CAP-15 | **Stacked Emphasis** | lead Plex 300 · 56 / key Alexandria 900 · 132 | small lead line + huge key with acc glow | W blur-rise; key 7 f | SC-07 · SC-01 · SC-11 | hero lines, hooks (1 per 8–10 s) | needs `key`; without key it falls back to one line |
| CAP-16 | **Two-Tone Lead** | Plex 300 · 62 + key Alexandria 800 1.4 em | light lead + bold acc key, same line | T soft 6 f; Out soft | SC-08 · SC-13 · SC-09 | authority, calm (Premium Soft light+bold mix) | weight contrast instead of italic |
| CAP-17 | **Emoji Inline** | Almarai 800 · 70 | white, acc highlight, emoji after key | emoji scale 0→1, rot −18→0 back.out(2.2) 6 f at key +2 f | SC-02 · SC-09 · SC-10 | lifestyle, fun | ≤ 1 emoji per caption; Segoe UI Emoji (Windows) |
| CAP-18 | **Cinematic Lower** | El Messiri 600 · 56 | lower (top 1300), gradient hairline above | line scaleX 0→1 12 f power3.out; text fade+rise 9 f; Out soft | SC-07 · SC-12 · SC-08 | documentary, emotional | El Messiri = elegant Naskh-Kufi hybrid |
| CAP-19 | **Ruqaa Script** | Aref Ruqaa 700 · 84 | handwritten feel, acc key | T clip-wipe RIGHT→LEFT 12 f power2.out; Out soft | SC-07 · SC-13 · SC-01 | culture, quotes, emotional | Ruqaa's slant = our «italic»; never slant > 4° |
| CAP-20 | **Editorial Serif** | Amiri 700 · 72 | classic Naskh, acc key | T fade 9 f; Out soft | SC-12 · SC-07 · SC-08 | serious, reflective, quotes | Amiri for classic tone; NOT for Quran (Quran = API text, craft/11 §7) |
| CAP-21 | **Kufi Statement** | Noto Kufi Arabic 800 · 76 | strong geometric, acc key | T slam 1.22→1, 5 f expo.out; H acc | SC-14 · SC-02 · SC-04 | warnings, rules, «لازم» lines | line-height 1.5 (tall Kufi) |
| CAP-22 | **Bubble Pop** | Baloo Bhaijaan 2 800 · 86 | rounded, dark stroke 9 + acc2 drop | W pop .4→1 back.out(2.6) 5 f, rotation ±4°→0 alternating | SC-11 · SC-05 · SC-09 | fun, kids, light | rounded joins survive the stroke |
| CAP-23 | **Glitch RGB** | Changa 700 · 76 | white, acc key | H RGB split 9→0 px (steps 5) + x jitter 7/−5/3/−1/0 over 5 f | SC-04 · SC-05 · SC-06 | tech, hacking, AI | jitter is a fixed sequence (seek-safe) |
| CAP-24 | **Spotlight Focus** | Readex Pro 600 · 70 | others blurred 3 px at 40 % | H active: blur 0, opacity 1, scale 1.08 in 3 f; back in 4 f | SC-01 · SC-04 · SC-10 | podcasts, slow emphasis | — |
| CAP-25 | **One Word** | Alexandria 800 · 112 | one word at a time, centre | W blur-pop 1.25→1, blur 10→0, 4 f; previous word cuts out | SC-12 · SC-02 · SC-05 | hooks only | ⚠ default: not for full videos (single karaoke words) |
| CAP-26 | **Kashida Stretch** | Plex 600 · 70 | acc key whose kashida grows | key: tatweel 0→5 over 12 f power3.out (RK.kashida legal position) | SC-07 · SC-08 · SC-01 | Arabic signature, premium | uniquely Arabic; key words with a joining point only |
| CAP-27 | **Marker Highlight** | Marhey 600 · 72 | hand-drawn highlighter on the key (lower 45 %, acc 78 %) | marker scaleX 0→1 from the RIGHT 8 f power2.out | SC-02 · SC-09 · SC-10 | casual tips, study | the marker is a stroke under the text, not a box |
| CAP-28 | **Retro Offset** | Lemonada 700 · 62 | hard 5 px acc offset shadow, acc2 key | W drop y −46→0 back.out(1.6) 7 f | SC-10 · SC-11 · SC-03 | retro, fun, food | Lemonada is wide: ≤ 3 words |

## 4. The 14 colour schemes (shown in the gallery `index.html`)
In every scheme:
- `ink` is the text colour.
- `acc` is the highlight and key colour.
- `acc2` is the secondary colour (extrude, glow, colour-coding).
- `stk` is used for strokes and dark shadows.
- `on` is the text colour on accent fills.
- `dim` is generated automatically as ink at 42 %.

| ID | Name | ink | acc | acc2 | stk | on | Pairs with |
|---|---|---|---|---|---|---|---|
| SC-01 | Ivory Rose | #F2F0E8 | #FF4D8D | #B45CFF | #120A10 | #FFFFFF | 01 02 14 24 26 |
| SC-02 | Hormozi Gold | #FFFFFF | #FFD400 | #FF8A00 | #000000 | #111111 | 03 04 17 27 |
| SC-03 | Beast Lime | #FFFFFF | #44FF4F | #FF3B3B | #000000 | #0A0A0A | 04 05 28 |
| SC-04 | Neon Blue | #F4F8FF | #3A86FF | #7FD1FF | #050B18 | #FFFFFF | 08 09 23 |
| SC-05 | Cyber Magenta | #FFFFFF | #FF2FA8 | #7B5CFF | #12001A | #FFFFFF | 07 11 22 |
| SC-06 | Teal Eco | #F2FAFF | #3FD7FF | #FF7A59 | #031A24 | #04202B | 13 09 10 |
| SC-07 | Espresso Copper | #F9E2CA | #E09A5C | #C8794A | #1D1011 | #1D1011 | 15 18 19 26 |
| SC-08 | Navy Cream | #F2F2F2 | #D9BFA8 | #9DB8D6 | #00213C | #00213C | 16 20 02 |
| SC-09 | Mint Calm | #FFFFFF | #6BCB77 | #93C5FD | #0B1F12 | #0B1F12 | 06 16 27 |
| SC-10 | Sunset | #FFF6EC | #FF6B3D | #FFC14D | #2A0E05 | #FFFFFF | 12 28 08 |
| SC-11 | Royal Purple | #F5F0FF | #B388FF | #FFD166 | #160A2E | #160A2E | 22 06 15 |
| SC-12 | Mono Editorial | #FFFFFF | #FFE8A3 | #BFC5CC | #000000 | #111111 | 10 20 25 |
| SC-13 | Baghdad Gold | #FFFDF5 | #E6C36A | #2FBF71 | #0E1A12 | #1A1405 | 16 19 |
| SC-14 | Crimson | #FFFFFF | #FF3B47 | #FFB4B9 | #1A0003 | #FFFFFF | 21 04 |

When you choose a scheme:
- Use the client's or the video's own accent if it has one (pass an object).
- Check that the accent reaches ≥ 4.5:1 against the sampled backdrop (craft/09 §2).
- Keep one accent per video (law 5).

## 5. Research behind it
- **Trend:**
  - Word-by-word karaoke and highlight captions are the dominant 2026 format.
  - About 70 % of the top presets use some word-by-word styling. The highlight leads the speech by 50–100 ms; we use −1 f.
  - Sources: [OpusClip presets](https://www.opus.pro/blog/best-caption-presets-styles-boost-retention), [Blitzcut 2026](https://blitzcutai.com/blog/best-caption-style-tiktok).
- **Creator looks:**
  - Hormozi: heavy, yellow key word, black stroke.
  - MrBeast: stroke plus hard drop, spring/bounce, colour-coded words, −3° tilt.
  - Ali Abdaal: clean sans, pastel accent, soft pop-ins.
  - Iman Gadzhi: serif cream with a diffuse shadow, which maps to our CAP-20 and CAP-18.
  - Sources: [ddaverse presets](https://www.ddaverse.com/viral-subtitle-style-generator), [Viralday](https://viralday.app/en/blog/6-caption-styles-beyond-hormozi-that-retain-high-attention), [Submagic template list](https://docs.submagic.co/api-reference/templates) (Hormozi 1–5, Beast, Ali, Iman, Devin…).
- **Tool preset vocabulary we mapped:**
  - VEED: Box Highlight → 07, Karaoke → 03, Impact Pop → 04, Colour Highlight → 01, Drop In → 28, Scale In → 06, Stomp → 21; plus its dynamic styles (Glide, Pulse, Handwritten → 19/27) ([VEED](https://www.veed.io/tools/add-subtitles/animated-subtitles)).
  - Caption tools: glitch → 23, neon pulse → 09, typewriter → 13, bounce → 22 ([videocaptions.ai](https://www.videocaptions.ai/caption-styles)).
  - Emoji punctuation (≤ 1 per line) → 17.
- **Ours, not in those tools:**
  - kashida stretch (26), Ruqaa wipe (19), the two-tone light+bold lead (16), stacked hero (15), spotlight focus (24) and the outline→fill progress (10).
- **Arabic fonts:**
  - Changa: bold, wide, tech.
  - Lalezar and Baloo Bhaijaan 2: display, friendly.
  - Readex Pro: the Arabic member of the Lexend family (legibility) ([Material blog](https://m3.material.io/blog/readex-pro-legibility-arabic-type-design)).
  - All of them are from [Google Fonts](https://fonts.google.com/specimen/Baloo+Bhaijaan+2) under OFL 1.1.
- **Rejected for Arabic:** any per-letter preset (Resolve Follower, CapCut letter typewriter, AE per-character range selectors). They break the joining.
