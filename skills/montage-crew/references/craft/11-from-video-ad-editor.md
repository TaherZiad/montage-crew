# craft/11 — script pass, written hook, layout by meaning, beat sync (ported from video-ad-editor)

Source: video-ad-editor v3.8 (MIT, github.com/majedphotos/video-ad-editor, © 2026 Majed Alzaabi — see NOTICES.md). Only the parts that change the edit itself were ported; its engine (canvas compose / studio / Remotion) is not used — this skill builds overlays in HyperFrames and assembles with `scripts/compose.py` (or Resolve/Premiere via the XML).

## 1. Script pass — before the cut (biggest time saver)
Raw takes contain retakes and **set words** — the words the creator says between takes. The list comes from `profile.language.set_words` (default «اكشن، كت، نعيد، من جديد»; per-dialect suggestions in craft/08). Typical roles: a start word (اكشن), an end word (كت), and a "that take failed" word (نعيد).
```
{{PY}} {{SKILL_DIR}}/scripts/story.py show <work>/raw/words.json
```
- Prints numbered sentences + **RETAKES** (similar sentence within the next 2 → the FIRST is the mistake) + sentences containing a "failed take" word + a ready `--drop` string (retakes + every set word). `story.py` reads the set words from the profile.
- Read the failed-take lines yourself: drop that take up to the set word (and the half take before it when the creator restarts) → `story.py drop <work>/raw/words.json 5 12` prints the ranges → append them to the `--drop` of `jumpcut.py`.
- Whisper may write set words in Latin ("action", "cut") — treat those as set words too.
- Do it BEFORE the beat sheet — every later timing depends on it. Decide yourself; no approval stop.

## 2. Written hook — first 1.6–3 s of every video
A hook sentence ON SCREEN from frame 1 (readable muted, doubles as the cover), while the voice plays under it.
- **Not the first line** — write it from the strongest line (`story.py hooks <work>/cut/words_cut.json` ranks lines and lists the numbers actually said).
- **3–8 words**, max 2 lines («…» breaks the line: idea on top, twist below). ≥ 1 pull device, strongest = 2: number · contrast (… وما / بس) · question (how / why / how much, in the dialect) · curiosity (السبب / الغلطة / محد / الفرق) · reverse command (لا …) · half-sentence story.
- **In the creator's dialect** (`profile.language.dialect`, spelling table in craft/08) — never mix dialects, never switch to MSA unless the dialect is MSA.
- **Never invent**: every number must be in the speech; the promise must be paid inside the video. Digits per the profile, no emoji, no final full stop (؟ and … OK).
- `{{PY}} {{SKILL_DIR}}/scripts/story.py check <work>/cut/words_cut.json "hook 1" "hook 2" "hook 3"` → pick the best one that passes (❌ blocks, ⚠ advice).
- Forms (rewrite in the dialect): number + paradox «3 ساعات باليوم… وما دفعت شي» · awkward question · failure before success · half-sentence story · reverse command «لا تبني موقع قبل هالشي» · curiosity gap «الغلطة اللي كل المبتدئين يسوونها». Common misses: a descriptive title, a hook that burns the answer, exaggeration the creator didn't say.
- Look (soft-text default holds): heavy 800–900 white, soft shadow, no box; the number/key word gets an accent underline sweeping RTL (0.1–0.35 s). Everything visible on frame 0; only a 0.045 s/word settle.
- Duration `0.9 + 0.28 × words` clamped 1.6–3.0 s. **Captions KEEP running under the hook (default: every spoken word is captioned)**; any other graphic waits until it leaves. So the hook sits in the TOP band (9:16: y 290–700) above the face, never in the caption band — two texts must not touch. Face high in frame → shrink the hook, don't move it down onto the captions. 16:9: hook in the upper third, x 96–1824.

## 3. Layout by meaning — decide per sentence: is the FACE or the GRAPHIC more important?
| Moment | Layout | Building block |
|---|---|---|
| emotion · question · promise · hook · CTA | **FULL** face | M/C framings |
| a comment on one graphic | **CARD-DOWN**: graphic top (9:16 y 280–520), captions, speaker below full width | split screen / X-PARK |
| B-roll / big panel / screen recording | **CARD-LOWER**: big card top, small speaker bottom | X-PARK small |
| numbers · list · comparison | **OFF**: speaker gone 4–8 s, whole screen infographic, the voice continues, captions stay | full-screen HyperFrames clip |
- OFF: 1–2× per video, never on the hook or the CTA, back to FULL right after. Vary the layouts — the variation holds attention. Captions never on the face in any layout.
- **Calm pace** (if the user asks for calm or complains about too many cuts): zoom range 1.00–1.06, no framing change before 4 s on the same shot, ≤ 6 layout changes per 30 s, the explanation holds until the idea ends. Hook stays FULL.
- Card crop: a FIXED crop per video starting just above the highest point the head reaches (+1.5 % margin) — never cut the head, never an empty ceiling, no tracking.
- 16:9: CARD-DOWN/LOWER become side-by-side (speaker 40 % one side, graphic 60 % the other; speaker on the side they face away from); OFF stays full frame.
- `footage = screen` (screen recording, no camera): the "face" is the important UI region — FULL = the recording framed on the action; OFF = full-screen infographic; an optional face-cam is a PiP (circle/rect, corner opposite the action).
- `footage = none`: no speaker; layouts alternate kinetic type, full-screen MG and B-roll (craft/03, mg-brain).

## 4. Motion from meaning — the graphic is PROOF of the word, not decoration
| The speaker says (examples) | Info type | Form (examples, invent more) |
|---|---|---|
| «4 من كل 100» | part of whole | 100-icon grid, 4 light up · dots gather |
| «النص تقريباً» / 38 % | ratio | donut fills · cup fills to the line · bar splits |
| «زادت / نزلت» | trend | line draws + filled area · arrow climbs and breaks · stairs |
| «أكثر من / أقل» | comparison | two bars · scale tips · two circles by size |
| «الأول، الثاني…» | ranking | bar race · podium · flipping list |
| «تصوّر ← ترفع ← تنشر» | process | step timeline · chained arrows · editor timeline with playhead |
| «بـ3 ثواني / كل يوم» | time | clock sweep · countdown · flipping calendar |
| a country or city name | place | simple map + pin drop · ripples from a point |
| «100 ألف / مليون» | money / big number | odometer that SLAMS on the word · stacked coins · printed invoice |
| «لأن / فصار» | cause → effect | dominoes · gear turns gear · chain breaks |
| «خطأ / خلل» | problem | glitch + cracks · ✕ slams · screen goes dark |
| strong quote | message | kashida kinetic type · word stretches · text behind the speaker |
Rules: one hero component + ≤ 1 support (grids only in CARD-LOWER/OFF) · the HIT lands on the spoken word (counter `dur` ends on the number word's start; shake + burst + SFX on that same frame) · **real numbers only** · every component holds ≥ 1.2 s after it completes · brainstorm 3 ideas per sentence, never the same scene in two videos.
SFX per visual event (categories in `assets/sfx/manifest.json`): element enters → whoosh/soft · counter runs → ticks accelerating then spacing out · number slams → thud + sub · before a reveal → riser ending ON it · card pops → pop · button/icon → click · typing → keys · highlight → shimmer · error → glitch. **Silence is a tool**: mute everything 0.5 s before the key line. ≤ 15 events/min (a tick run counts as one).

## 5. On the beat — `scripts/beat.py`
```
{{PY}} {{SKILL_DIR}}/scripts/beat.py music.mp3 --out beats.json [--click] [--bpm 128] [--offset 1.2] [--grid]
```
→ `bpm, beats, accents, downbeats, drops, energy, onsets`. `--click` writes the song + a tick per beat: listen when a cut "doesn't sit".
- B-roll montage / music section / music-only videos: cut on `beats` (or on `onsets` when the song isn't on a fixed grid — pro editors cut on the audible hit, ~70 % within 40 ms). Place cut points on the nearest frame to the beat.
- Accents get the bigger effect (zoom punch, whip/wipe transition); `drops` = the biggest moment of the video. Off-beat cuts get NO transition — a hard cut beats an effect that exposes it.
- Never the same effect (or family) twice in a row; intensity follows the section energy (`0.35 + 0.65 × energy`); talking parts only light zoom/shake on the bed.
- Flashes/inverts ≤ 3 per second (WCAG 2.3.1), strobe only on explicit request.

## 6. QA additions (numbers first, eyes on ONE sheet)
- `{{PY}} {{SKILL_DIR}}/scripts/overlay_check.py overlays.mov --zones <work>/picture/zones/zones.json` — checks what was actually RENDERED: bright opaque overlay pixels (text/icons) inside the platform UI or the speaker's head per shot. Exit 3 = breach, lists time ranges. Skip `--zones` for text-behind-speaker layers.
- Sync: `{{PY}} {{SKILL_DIR}}/scripts/transcribe.py final.mp4 --model small --out final_words.json` → `story.py sync <work>/cut/words_cut.json final_words.json` — every sentence start within 0.1 s.
- Visual: `{{PY}} {{SKILL_DIR}}/scripts/sheet.py final.mp4 sheet.jpg t1 … t6` — read the one sheet, not frames one by one (8 separate preview images ≈ 900 k characters of context).
- Deliverables beside the final: `story.py srt <work>/cut/words_cut.json <out>/<name>` → `.srt` (YouTube/LinkedIn) + `.txt` (full speech for the post caption).
- Token budget: one command per stage (extract audio + transcribe + frames together, in the background); `grep -n` / `tail -5` instead of reading whole files; references only when needed.

## 7. Culture / type additions
- **Quran verbatim from a source, never typed**: copy via API (`api.quran.com` → `text_imlaei`, or `api.alquran.cloud`), compare letters with a second source before rendering. Imlaei with tashkeel reads clearer than Uthmani; Uthmani look = `Amiri Quran`. Anything that isn't the ayah (قال الله تعالى، the surah name) in the video's normal font. No music under Quran (decision 19).
- Kashida: «لا» never splits; the tatweel goes AFTER a letter's tashkeel, never between the letter and its mark (`assets/rtl-kit.js kashida()` enforces both; test: `scripts/test_kashida.js`). Digits never stretch.

## 8. Gotchas
- **iPhone HDR** (HLG/PQ) converted naively = washed-out creamy image that reads as an unwanted grade → `jumpcut.py` detects it and tone-maps to bt709 (and tags every cut bt709).
- **Long files** (a full episode): Whisper drops minutes and hallucinates channel-outro phrases («اشتركوا في القناة») → transcribe in ~20 s chunks cut at silences; don't transcribe and render at the same time (everything ×2–3 slower).
- ffmpeg `drawtext` is missing in some builds → stamp text with PIL (`sheet.py` does).

## Not taken (and why)
Their canvas engine, studio timeline and Remotion screen · text-behind-person and cut styles (Mac Vision only — this skill has `matte.py`) · their default cream/clay theme · paid AI scenes via fal.ai (offer only if the user wants it, with their own key in an env var).
