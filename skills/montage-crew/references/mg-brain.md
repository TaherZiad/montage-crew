# MG brain — from a spoken sentence to a professional motion graphic

Motion graphics are the MOST important layer. The amateur habit is to split the screen and pop words/icons in and out. This file is the decision method that replaces that habit: **every idea gets its own visual, chosen from its meaning, in a layout chosen from its weight.**
Read with: `mg-techniques.md` (the MG-NNN catalogue + recipes), `mg-recipes.md` (the target level: one metaphor per clause, morphs, 3-colour world), `craft/11` §3–4 (layout by meaning, motion from meaning), `craft/09` (soft text, zones). Code: `assets/mg-kit/` (`mg-kit.js`, `mg-kit.css`, `demo.html`).

Defaults this file obeys (unless the brief, the profile or the user's `rules.md` says otherwise): captions of everything the speaker says keep running in every layout (move them to the layout's caption slot, never drop them) · no box/card behind TEXT (UI mocks are images of UI and are fine) · nothing behind the speaker's back except the 1–2 earned text-behind peaks · speaker moves smooth (0.7–1.0 s in-out, never snapped) · SFX few and quiet (~14–20 per reel) · 4K delivery (author at 1080×1920, render `--resolution portrait-4k`) · one colour world, one accent · real numbers only · no imitation of references.

---

## 0. What "professional" means here (research distilled)
- **Motion carries information, never decoration** (the Vox rule: "every animated element answers a question the narration just raised"). If a graphic only repeats the spoken words, it is a caption — delete it.
- **One metaphor per idea, held consistently** — clarity beats cleverness; never two metaphors for one idea; familiar objects over obscure ones (explainer-studio practice: Kurzgesagt/School of Motion storyboard the metaphor and the transition FIRST, then design).
- **Transitions are designed**, not effects: match cut / morph / zoom-through / cut-on-action (School of Motion's six essentials). The best transition turns the old metaphor INTO the next one (target-level reference reel A: ~10 morphs in 46 s).
- **Restraint and rhythm**: Apple-style — few elements, physical easing, deliberate anchor points; Fireship-style tech pace — a visual change every ~2 s, code/UI rebuilt live, one joke-beat per reel.
- **Layout is a beat, not a mode** (measured on finished Arabic reels): a PiP/park lasts 2.5–3.5 s, a takeover 1.1–4 s, then back to the speaker's face.

---

## 1. The method — 7 steps per sentence (do it for every line of `words_cut.json`)

| Step | Question | Output |
|---|---|---|
| 1. **Sentence** | What is the ONE idea? Where is the hit word (the noun/verb/number that carries it)? | idea in ≤ 6 words + hit word + its timestamp |
| 2. **Meaning type** | Which of the 22 types in §2 is it? | type id (T01…T22) |
| 3. **Visual metaphor** | "What object IS this sentence?" Climb the ladder (§3): literal proof → rebuilt UI → data form → metaphor object → symbol. Brainstorm 3, keep the clearest. Can it MORPH from the previous beat's object? | object + how it behaves (its verb) |
| 4. **Layout mode** | Is the speaker's FACE or the IDEA more important right now? Weight + duration → mode (§4 rules). | L-id + enter/exit style |
| 5. **Technique** | How does the object move to show the verb? | 1 hero MG-NNN + ≤ 1 support MG-NNN |
| 6. **Assets** | What must exist: logo, real UI, icon (one family), photo, 3D, SFX? | asset list → `asset-sourcing.md` |
| 7. **Timing** | Build starts 0–10 f before the hit word; the hit lands ON it; hold ≥ 1.2 s after completion; exit ≈ 70 % of the entrance or morph into the next beat. | t_in, t_hit, t_out, transition to next |

Output = one beat-sheet row (format §8). Then sanity pass over the whole reel (§5 pacing, §6 variety) before building.

**The verb test.** The object must DO what the sentence says: "يبني" → it assembles; "يسرّب" → it leaks; "يسرّع" → it speeds; "يحمي" → it closes/locks; "يتعلم" → it fills; "يربط" → lines connect; "يختصر" → steps collapse into one. A static icon that just appears fails the verb test.

---

## 2. Lookup table — meaning type → visual → layout → technique

Cue words: MSA first, dialect variants after « / » — adapt to the profile's dialect. Layout ids in §4, technique ids in `mg-techniques.md`.

| # | Meaning type | Cue words (examples) | Visual forms (pick one, invent better) | Default layout | Hero techniques |
|---|---|---|---|---|---|
| T01 | **Number / stat** | رقم، ٪، ألف، مليون، ضعف | odometer slam on the word · stat in giant type with unit kashida · ring fills | SPLIT or TAKEOVER (1.5–2.5 s) | MG-051, MG-052, MG-055 |
| T02 | **Part of whole / ratio** | من كل، نصف / نص، ربع، معظم / أغلب | waffle 100 cells (N light) · donut · cup filling to a line · crowd of dots, N in accent | SPLIT / TAKEOVER | MG-058, MG-055, MG-047 |
| T03 | **Trend / growth / drop** | زاد، ارتفع / صعد، انخفض / نزل / طاح، كبر | line draws + area · stairs · arrow climbs and breaks · plant/bar grows | SPLIT | MG-054, MG-053 |
| T04 | **Comparison A vs B** | أفضل من / أحسن من، الفرق، بدلاً من / بدل، مقابل | split versus panels (loser desaturates) · scale tips · two circles by size · before/after slider | TAKEOVER split-2 / SIDE | MG-078, MG-079, MG-052 |
| T05 | **Ranking / list of tools** | أولاً / أول، ثانياً / ثاني، أفضل 5، أدوات | orbit/wheel of logos → hero → dock · podium · bar race · flipping stack | SPLIT stage (whole list) | MG-076, MG-056, MG-034 |
| T06 | **Process / steps / how-to** | تفتح… ثم / بعدين… فيظهر / وتطلع | node flow with travelling dot · numbered path drawn · assembly line · timeline playhead | SPLIT / TAKEOVER | MG-075, MG-019, MG-060 |
| T07 | **Cause → effect** | لأن، فـ، أصبح / صار، يجعل / يخلي | dominoes · gear turns gear · A → arrow wipe → B · chain reaction ripple | SPLIT | MG-075, MG-021, MG-028 |
| T08 | **Time / speed / duration** | ثوانٍ، دقيقة، ساعات، بسرعة، يوم | clock sweep · countdown · progress bar racing · speed lines/motion trail · calendar flip | PiP or SPLIT | MG-059, MG-060, MG-041 |
| T09 | **Place / scale of world** | في بلدنا، العالم، كل الدول | map zoom + pin drop · route draw · globe with arcs · ripples from a point | TAKEOVER (map wants the full frame) | MG-061, MG-062, MG-063 |
| T10 | **Product / tool / app** | Claude، Cursor، Lovable، الأداة | rebuilt UI (prompt bar, chat, editor, browser) live · app tile bounce + 3 feature icons · phone mock | SPLIT or DEVICE | MG-064…MG-072 |
| T11 | **Action on screen / demo** | تكتب، تضغط، تنسخ، تفتح | the creator's screen recording in split, zoom into the field · cursor path + click ripple · typing | SPLIT (recording) / OTS | MG-069, MG-070, MG-037 |
| T12 | **Build / create / generate** | يصنع لك / يسوّيلك، يبني، يُنشئ موقعاً / يطلع موقع | prompt → site assembles block by block · city rises from a pill (reference reel A) · skeleton → content | TAKEOVER 2–3 s or SPLIT | MG-066, MG-073, MG-033 |
| T13 | **Abstract concept** | فكرة، ذكاء، فهم، سياق، ذاكرة | symbol object (brain of nodes, lightbulb from a dot, context = stack of cards) · 3D object · particle form | TAKEOVER short / PiP | MG-043, MG-045, MG-013 |
| T14 | **Danger / security / mistake** | خطر، اختراق، يسرّب، خطأ / غلط، انتبه | lock/shield builds then cracks · red glitch · leaked key flying out of code · warning gauge to red · strike | SPLIT / TAKEOVER | MG-084, MG-048, MG-012, MG-057 |
| T15 | **Protection / fix / solution** | تحمي، الحل، تُصلح / تصلّح | shield closes around the object · broken line re-joins · checklist ticks · green pass sweep | SPLIT | MG-013, MG-020, MG-085 |
| T16 | **Contrast / negation / myth** | ليس / مو / مش، لا، لكن / بس، بالعكس، الجميع يظن | struck word → replaced word · flip card (myth / truth) · colour-world flip | FULL face + type, or TAKEOVER 1 s | MG-012, MG-010, MG-086 |
| T17 | **Emotion / stakes / story** | تعبت، خفت، فرحت، صدمة | NO graphic — face, smooth push-in, grade/colour shift, silence; at most a single word behind the speaker | FULL | MG-087, MG-089 |
| T18 | **Question / hook / curiosity** | كيف؟ / إزاي؟، لماذا؟ / ليش؟، هل تعلم؟ / تعرف إيه؟ | written hook top band · silhouette/blurred "?" reveal · pixelated card that clears on the answer | FULL (hook) | MG-001, MG-031 |
| T19 | **Money / cost / free** | مال / فلوس، مجاني، اشتراك، دولار | price tags struck → $0 · coins stack · invoice prints · subscriptions scatter away | SPLIT / TAKEOVER | MG-012, MG-051, MG-047 |
| T20 | **Many things / overload** | كثير جداً / كتير أوي، فوضى | icon swarm / particle storm → converge to one (simplify) · tab explosion | TAKEOVER | MG-045, MG-046 |
| T21 | **Definition / term** | يعني، هذا اسمه، المصطلح | term set big (kashida) + one-line meaning; ghost word behind; dictionary card (UI) | PiP corner | MG-003, MG-002 |
| T22 | **CTA / follow / save** | احفظ، تابع، علّق | button pressed by cursor + ripple · comment bubble types the keyword | FULL (face) | MG-071, MG-070 |

**Niche metaphor bank (AI tools / Claude / vibe coding / building sites & apps / prompts / security)** — starting points, invent per video:
| Idea | Metaphor objects |
|---|---|
| prompt | prompt bar typing (real), a key in a lock, a recipe card, a remote control, a wish slip into a machine |
| context / memory | stack of cards sliding into a head/box, a window that widens, a backpack filling, a shelf |
| tokens / limit | fuel gauge, hourglass, a ruler that runs out, bricks counted |
| model / AI "thinking" | node network lighting in waves, a brain made of code lines, orbiting particles condensing |
| agent / automation | robot arm on an assembly line, dominoes, gears, a to-do list ticking itself |
| skills / plugins / MCP | puzzle pieces clicking into a core, cartridges into a console, plugs into a hub (hub-and-spoke) |
| vibe coding | voice/waveform → code lines → live site (morph chain), a DJ deck mixing UI blocks |
| build a website | wireframe draws → blocks drop in → colour fills → browser chrome closes around it |
| app | phone frame, screens sliding in like cards, tap ripples |
| bug / error | red glitch slice, a crack running through UI, a beetle walking across code |
| security / API key leak | key literally flies out of the editor into a crowd; vault door; shield closing; padlock snapping |
| speed / productivity | hours on a clock collapsing to minutes, motion trails, before/after timeline lengths |
| free vs paid | price tags struck and falling, $0 slam |
| learning curve | stairs/mountain path with a dot climbing |
| copy-paste templates | clone wall (one card multiplies), stamp |

---

## 3. Metaphor ladder (step 3) — climb only as far as needed
1. **Literal proof** — the real thing (the creator's screen recording, the real app UI rebuilt, the real logo). Always best for T10–T12: proof beats metaphor.
2. **Data form** — number/ratio/trend/comparison → chart family (T01–T05).
3. **Diagram** — process/cause/system → nodes, arrows, flows (T06–T07).
4. **Metaphor object** — the concept as a physical thing that behaves (T13–T15, T19–T20).
5. **Symbol / type** — when nothing visual helps: kinetic type with ONE accent word, or nothing (T16–T18).

Rules: brainstorm 3 per sentence, choose the one a 14-year-old gets in 0.5 s · never repeat a scene across videos · if the previous beat's object can morph into this one, prefer that (continuity = premium) · one metaphor per idea for the whole reel (if "context = cards" once, it stays cards).

---

## 4. Layout modes (step 4)

Geometry is in 1080×1920 px (9:16), presets live in `MG.LAYOUTS` (`assets/mg-kit/mg-kit.js`). 16:9 (1920×1080): keep text inside x 96–1824, y 54–1026; nothing important in the bottom 140 px (player controls). **Architecture**: not every editor can keyframe the speaker's picture reliably (Resolve free has no keyframe API), so any beat where the speaker's picture moves/shrinks is an **MG segment**: one HyperFrames composition that contains the footage (untimed `.mg-spk` wrapper + `<video data-start data-media-start>` of the locked A-roll composite — the speaker on the background plate if one is used) plus the MG world, rendered **opaque** and laid on the track above the A-roll for exactly its range (enter and exit at layout `full` = frame-identical seam). Captions stay their own layer above. Matte layers inside HyperFrames: WebM VP9 alpha (`ffmpeg -c:v libvpx-vp9 -pix_fmt yuva420p -auto-alt-ref 0`), not ProRes. Overlay-only beats (speaker unchanged) stay alpha ProRes as before.

| Mode | Look | Use when | Duration | Enter / exit (smooth) | Caption slot |
|---|---|---|---|---|---|
| **L-FULL** (face) | speaker full frame, MG only in safe bands (top band y 290–700, chest band) | hook, emotion, opinion, promise, CTA, punchline, any line where the speaker's expression is the message | any | punch/push 1.00↔1.07, 0.9 s inOut | default (y 1170–1270) |
| **L-SPLIT-TOP** (`split-top`) | speaker top half (face ≈ y 480), MG stage bottom half 960–1480 | the workhorse: lists, demos, UI, charts while the speaker keeps talking; screen recordings | 3–12 s (a whole list section) | `frameTo` 0.8 s power3.inOut; stage rises from below 12 f expo.out; exit reverse or morph | on the seam y ≈ 900–960 (soft, over the bottom of the speaker's frame) |
| **L-SPLIT-BOTTOM** (`split-bottom`) | MG top, speaker bottom (chin < 1480) | the visual is "above" (sky/map/headline object), or to alternate with split-top for variety | 3–8 s | same | top of the speaker's half, y ≈ 1000 |
| **L-SIDE** (`side-right`) | speaker right half full height, content left (RTL: the speaker is read first) | vertical objects (phone, ranking column, code), two-thing comparisons with the speaker as one side | 3–6 s | slide 0.8 s; content column from the left edge | under the speaker's half, centred x 810 |
| **L-PIP-CIRCLE** (`circle-bl/br/tl/tr/center`) | speaker in a 320–400 px circle + accent ring, MG owns the frame | MG needs the whole frame but the speaker's reaction still matters (data, maps, UI walk-through) | 2.5–6 s | 0.8 s shrink; ring draws 10 f after it lands; exit: circle grows back to full 0.8 s | top band y 300–420 if circle is low, or beside the circle |
| **L-PIP-CARD** (`card-bl/br/top`) | speaker in a rounded card (radius 44–48) | same as circle but the speaker gestures (hands matter), or "reacting to their own content" | 2.5–6 s | 0.8 s; soft drop shadow, no border card | beside/above card |
| **L-STAGE-CARD** (`stage-card`) | speaker as a big card floating on the MG world (grid, glow), objects orbit/pin around it | chapter starts, "me + 3 tools" moments, intros; zoom-out reveal | 2–4 s | camera pulls back 0.9 s (speaker 1 → 0.75), world fades/draws in | below card y 1330 |
| **L-DEVICE** (`device-phone` + `MG.ui.phone`) | speaker inside a phone/browser/monitor frame | the topic is the platform itself («على تيك توك…»، «في موقعك»), or a meta joke | 2–3 s | frame scales in around the speaker 14 f, footage settles into the screen | under device |
| **L-TAKEOVER** (stage over the speaker) | full-frame MG explainer, the voice continues | the 2–4 strongest ideas: a metaphor that needs the whole frame, a map, a big number, a morph chain | 1.1–3 s (max 4 s) | designed transition 6–10 f: wipe with accent edge bar, iris from an element, push, blur-whip, or the speaker's frame shrinks to a dot (`dot`) and the world takes over | bottom caption line y 1400–1470 (reference reel A position), never overlapping the hero |
| **L-WORLD** (speaker cut out in front of an MG world) | the speaker's matte composited over an animated MG environment (grid world, floating UI, giant type) | hero intro, "I build with these tools" brag beats, climax | 2–5 s, ≤ 2× per reel | world builds behind; respects "nothing behind the speaker's back": only type/abstract world, no busy cards | default |
| **L-BEHIND** (text behind) | giant word/numeral between plate and matte | earned peak: hook or climax word only | 1–2.5 s, ≤ 2× per reel | slam/drop + push 1.00→1.06 | hidden for that word only |
| **L-OTS** (over-the-shoulder screen) | the screen recording in perspective as if on the monitor beside the speaker, then zoom INTO it (dynamic zoom) | demos where the transition "into the screen" sells it | 2–4 s inside, then back | zoom-through 0.9 s expo.inOut into the screen → split/full recording | default |
| **L-BROLL** (cutaway) | full-frame B-roll/AI scene/stock clip | situations, places, emotions that need real images; hide a bad jump cut | 1–2.5 s | hard cut on a word or match cut | default |

### Choosing (decision rules, in order)
1. Hook (0–3 s), emotional line, opinion, CTA → **L-FULL**. Never a takeover on the hook or CTA.
2. The creator shows a screen recording → **L-SPLIT-TOP** (recording bottom, zoom into the typed field, out on the result).
3. The idea is a SET (list, steps, tools, comparison rows) lasting > 4 s → one **L-SPLIT** section for the whole set; the stage changes per item (morph/swap), the speaker's frame does not jump per item (only a gentle 1.00↔1.07 zoom per item).
4. The idea needs the whole frame (map, big morph, big number, particle convergence, a metaphor reveal) and is ≤ 3 s → **L-TAKEOVER**.
5. The idea needs most of the frame but the speaker's reaction matters (walk-through, before/after, data they comment on) → **L-PIP-CIRCLE/CARD**.
6. The idea IS a platform/device → **L-DEVICE**. A chapter start / intro of 3–5 things → **L-STAGE-CARD** or **L-WORLD**.
7. Small support visual only (icon, logo, one number) → stay **L-FULL**, put it in the top band / beside the head.

### Pacing rules (how long, how often)
- **Face budget**: the speaker's face (L-FULL or ≥ split size) on screen ≥ 55 % of the reel; the speaker visible (any size) ≥ 85 %.
- **Takeover**: 1.1–3 s each, 4 s absolute max, 2–4 per 60 s, never two in a row without ≥ 2 s of the face between, never on hook/CTA, never on an emotional line.
- **PiP/park**: 2.5–6 s; return to FULL or SPLIT after it.
- **Split section**: up to ~12 s if the stage changes every 2–4 s; if the stage is static > 4 s, change something (new item, zoom, morph).
- **Layout changes**: ≤ 6 per 30 s (calm mode: ≤ 4); never the same mode change twice in a row (e.g. FULL→PIP→FULL→PIP is fine only if the PiP corner/shape differs or a takeover is between).
- **Visual change every 2–4 s**, new idea every 3–7 s, a breather (clean face, no MG) every 8–12 s.
- **Mode transitions**: the speaker's frame always moves smooth (0.7–1.0 s, power3/expo inOut). MG-to-MG transitions are short and designed (6–10 f). Each mode change gets ONE soft SFX (air whoosh on the move) — not every item.

### Entering / exiting — the smooth grammar
- FULL → SPLIT/PIP: `MG.frameTo(tl, spk, t, 'split-top'|'circle-bl', {dur:.8})`; the stage/world is ALREADY there underneath (it appears as the speaker shrinks — no second animation needed); first MG object enters 4–8 f after the speaker lands.
- FULL → TAKEOVER: `MG.takeover(tl, stage, t, {style:'wipe'|'iris'|'push'|'blur-whip'})`, or shrink the speaker to `dot` then iris out of that dot (best "the speaker hands over to the idea" move).
- TAKEOVER → FULL: `MG.giveBack(...)` the same style continuing direction, or the takeover's last object MORPHS into the speaker's PiP frame (e.g. a circle in the MG becomes the circle the speaker appears in) → `frameTo 'full'`.
- Between two MG beats in the same mode: morph cut (MG-033, MG-013) > match cut (MG-035) > wipe with edge bar (MG-025) > blur-whip (MG-032). Max 1 plain cut per section.

---

## 5. Timing on the words (step 7)
- Visual starts 0–10 f before the clause's first word; the **hit** (slam, morph completion, cell lights, counter ends) lands ON the hit word (±2 f). Counters: `dur` ends at the number word's start.
- Hold ≥ 1.2 s after completion; ~1.3 words/s reading pace for on-stage headlines (words 18–36 f apart, reference reel A).
- Exits 70 % of the entrance, or no exit: morph into the next object.
- SFX: on the moves that matter (mode change, hero hit, morph landing, click). Silence 0.5 s before the key line.

## 6. Variety & quality pass (whole reel, before building)
- Count techniques: no hero technique used > 2× per reel; no two consecutive beats with the same layout AND the same technique family.
- Colour: 3-colour world (dark / light / ONE accent); flip the takeover background between beats (never same twice in a row).
- Every beat passes the verb test and the "would a muted viewer get it?" test.
- Zones (9:16): nothing in IG UI (top 290 / bottom 1480 / right rail x > 950 for y 1100–1650); PiP circles and cards obey the same. 16:9: see §4.
- Amateur tells to kill: pop-in/pop-out icons with no verb, graphics that repeat the spoken words, a split screen with a static image for 6 s, three reads at once, a different transition every time, linear motion, PiP that snaps.

---

## 7. Ten worked examples (tech / AI tools / business)

Lines are in MSA; adapt to the profile's dialect.

**1. «Claude Code يستطيع أن يبني لك موقعاً كاملاً من جملة واحدة»** (T12 build)
Metaphor: a sentence becomes a site. Layout: L-SPLIT-TOP → L-TAKEOVER 2.2 s. Technique: prompt bar types the sentence (MG-066) → cursor clicks send (MG-070) → iris from the send button (MG-028) into a takeover where wireframe lines draw (MG-019) and blocks drop in (MG-073) inside browser chrome (MG-064) on «موقعاً كاملاً». Hit = blocks finish on «كاملاً». Assets: none external (rebuilt UI), Claude logo small in the bar. SFX: typing (soft), click, one rise→pop on the reveal. Exit: browser shrinks into a circle → the speaker's PiP (morph) → full.

**2. «70٪ من المشاريع الصغيرة تستخدم الذكاء الاصطناعي بشكل خاطئ»** (T02 + T14) — only if the speaker said 70.
Layout: L-TAKEOVER 2.0 s (dark). Waffle 100 cells (MG-058); 70 light accent-red on «70٪», a red glitch sweep across them on «خاطئ» (MG-048). Headline «تستخدمه بشكل خاطئ» with «خاطئ» in accent. Give back with wipe; on the face the speaker adds the next line.

**3. «أول أداة: frontend-design، تجعل تصميمك احترافياً»** (T05 list item)
Layout: L-SPLIT-TOP for the whole list. Stage: orbit of 5 tool bubbles (MG-076) → item 1 swells to hero «01» + name (MG-007 roll for the name) → a plain grey card MORPHS into a polished card (MG-033) on «احترافياً» → hero docks to a header strip for the next item. Gentle 1.00→1.07 zoom on the speaker per item.

**4. «لا تضع مفتاح الـAPI داخل الكود»** (T14 security)
Layout: L-SPLIT-TOP. Editor mock types `const key = "sk-…"` (MG-067); on «داخل الكود» the key line glows red; the key token detaches and flies out of the window into a crowd of tiny figures/dots (MG-021 travel + MG-045 particles); padlock icon snaps open. Then on the fix line: the key slides into a `.env` vault icon and a shield closes (MG-013 morph). SFX: glitch soft on the leak, click on the lock.

**5. «الفرق بين ChatGPT وClaude في البرمجة»** (T04 comparison)
Layout: L-TAKEOVER split-2 (top/bottom halves, 2.5 s) or L-SIDE with the speaker as narrator. Two editor panels typing the same task; one finishes first, a progress bar race (MG-060) on «الفرق»; loser desaturates (MG-079). Only claims the speaker actually makes.

**6. «اشتغلت عليه 3 ساعات… والأداة أنجزته في 5 دقائق»** (T08 time)
Layout: L-PIP-CIRCLE (speaker reacting) 3 s. Clock face sweeps 3 hours fast (MG-059) then COLLAPSES (scale squash) into a small 5-minute timer that slams on «5 دقائق» (MG-051 counter). SFX: clock tick run → stop → one hit.

**7. «الأمر (البرومبت) مثل الوصفة، كلما كان دقيقاً كانت النتيجة أفضل»** (T13 abstract via analogy)
Layout: L-TAKEOVER 2.5 s (cream world). A recipe card (prompt) whose lines tick in; on «دقيقاً» more ingredient lines draw; a plate/result on the right goes from blurry blob to crisp UI card (MG-033 blob→card morph + blur sharpen). The analogy object stays the same if the idea comes back later.

**8. «MCP يربط Claude بكل أدواتك»** (T13 + T05 hub)
Layout: L-STAGE-CARD (speaker card centre) 3 s. Hub-and-spoke: tool logos at the rim, lines draw from the speaker's card/Claude logo to each (MG-075 + MG-020), each logo lights when the line reaches it, one pulse travels around (MG-021). On «كل» all connect at once with a soft ripple.

**9. «إذا لم تفهم الكود، ستقع في مشكلة»** (T16 warning, emotional)
Layout: L-FULL. No object. Smooth push 1.00→1.07 over the sentence, grade cools slightly, «مشكلة» as the single accent word in the caption; optionally a red vignette breath 15 % (MG-089). Restraint is the technique here.

**10. «احفظ المقطع لترجع إليه وتجرّب»** (T22 CTA)
Layout: L-FULL. Save icon (bookmark) builds from a line draw (MG-019), cursor presses it (MG-070) with ripple on «احفظ», bookmark fills accent. Hold 1.5 s, clean end.

---

## 8. Beat-sheet row (what the brain hands to the build)
```
B07 | 12.40–15.10 | «لا تضع مفتاح الـAPI داخل الكود» | T14 | key leaks out of code
    | L-SPLIT-TOP (enter 12.30 frameTo .8s) | hero MG-067 editor typing → MG-021 key travel + MG-045 swarm | support MG-084 padlock
    | hit «الكود» 13.92 | assets: none (rebuilt) + lock icon (same family) | SFX: glitch_soft @13.92
    | exit: morph key → vault (B08) | captions: seam slot y 930
```
Build: `assets/mg-kit/demo.html` shows split → circle PiP → wipe takeover with morph → give back, all seek-safe.

Sources: School of Motion — six essential transitions, match cuts, Explainer Camp; Vox style deconstruction (earnedits.com); Kurzgesagt production process (10.studio); metaphor selection rules (animotionsstudio.com); split vs PiP use (directai.app); Fireship pacing (engineerscodex); open-video-edit layout presets (github.com/kevinbadi/open-video-edit); 2025–26 motion trends (liquid glass, collage, hybrid 2D/3D); plus the skill's own measured research (`mg-recipes.md`, `craft/03`, `craft/11`).
