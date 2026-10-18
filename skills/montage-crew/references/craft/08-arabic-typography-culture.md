# Arabic editing scene, typography in motion, dialects, culture

Research base: ~20 Arabic editing tutorials (creators from Iraq, the Gulf, Egypt, the Levant), broadcast lower-third and news typography, the Netflix Arabic Timed Text guide, kashida studies (Khatt Foundation, Alif Type), Adobe RTL notes and Arabic font foundries.

## Fonts by mood (all free unless noted; bundled ones are in `assets/fonts/`)
| Mood | Fonts |
|---|---|
| Premium / editorial / podcast | IBM Plex Sans Arabic, Readex Pro, Thmanyah Sans/Serif (free, not bundled), Amiri for quotes |
| Clean social captions | Cairo Bold/Black, Tajawal, Almarai, Alexandria, Readex Pro |
| Loud hooks / stickers | Lalezar, Changa ExtraBold, Alexandria Black, Cairo Black |
| Storytelling / playful | Marhey, Baloo Bhaijaan 2, Lemonada |
| Heritage / religious | Amiri, Aref Ruqaa (accents only), El Messiri |
Two weights per video: hook phrase Light + key word Black/Bold. Never fake bold with a stroke (it closes the counters of ه ص ق).

## Typography rules
- Sizes (1080×1920): captions 70–95 px Bold; hero words 140–220 px. Arabic looks optically smaller — set mixed English ~10–15 % smaller. For 16:9 (1920×1080) scale by 0.56 (captions 40–54 px, hero 80–120 px).
- 1–3 words per caption line, one line preferred, ≤ 2 lines ever; 5–6 words on a line = wrong. Split at meaning; no orphan word on line 2.
- **Leading 1.3–1.6×** (tall ا ل ك, deep ي ج ع ر) — stacked hero lines collide at Latin leading.
- **No letter-spacing on Arabic. No italics/slant (fake, breaks joins).**
- **Kashida**: one hero word per screen, one kashida per word, allowed positions only — after medial س/ص (and ش ض), or before a final ة ه د ا ل ك; never in Ruqaa, never to justify captions, never on the last letter. Kashida stretch in/out is the signature Arabic animation.
- Mixed scripts: English on its own line (Arabic on top, English smaller below). English inline → bidi bugs (punctuation jumps, order flips): wrap with RLM/LRM (U+200F/U+200E) or write the word in Arabic letters ("ريلز"). Pair families (IBM Plex + Plex Arabic, Readex + Lexend).
- Numerals: one system per video, from `profile.language.digits`. Western digits (90 %, 2026) = modern/tech, the norm for most social creators and always in the Maghreb. Arabic-Indic (٩٠٪ ٢٠٢٦) = formal/heritage/news/government/religious, common in the Gulf and Egypt for formal topics. ٪ with Arabic-Indic, % with Western. Stats always as digits.
- Punctuation: ، ؟ ؛ ; no "?!"; ellipsis …; reels drop full stops, keep ؟ and ! on hero lines.
- Direction: reveals/wipes/slide-ins go right→left; progress bars fill from the right; "next" arrows point left; timelines read RTL.
- Safe zone: phones set to Arabic mirror the IG/TikTok UI (buttons on the LEFT) → keep critical text centred with ≥ 120 px margins both sides, nothing below y 1480, and 190 px clear on both sides for y 700–1480 (measured, craft/09 §3).

## Dialect spelling — one dialect per video, spelled consistently
The profile sets `language.dialect`. Write captions, the written hook and on-screen text in the **creator's own dialect, in its common social spelling** — not MSA, unless the dialect is MSA. Proof-read against what was actually said; never "correct" dialect into MSA. Restore ة and hamzas (أ إ) on hero text — raw auto-captions ("اسرار"، "شويه") look amateur. Shared words keep standard spelling.

| Meaning | MSA | Iraqi | Gulf | Levantine | Egyptian | Maghrebi | Sudanese | Yemeni |
|---|---|---|---|---|---|---|---|---|
| how | كيف | شلون | شلون / كيف | كيف | إزاي | كيفاش | كيف | كيف |
| what | ماذا / ما | شنو | وش / شنو | شو | إيه | شنو / واش | شنو | إيش / وش |
| now | الآن | هسّه | الحين | هلّق | دلوقتي | دابا / ضرك | هسّي | الحين / دحين |
| a lot / very | كثيرًا / جدًا | هواية / كلش | وايد / واجد | كتير | كتير / أوي | بزاف | شديد / كتير | كثير |
| I want | أريد | أريد (اريد) | أبي / أبغى | بدّي | عايز | بغيت | داير | أشتي |
| there is / isn't | يوجد / لا يوجد | أكو / ماكو | فيه / مافيه | في / ما في | فيه / مفيش | كاين / ماكاينش | في / مافي | فيه / مابش |
| why | لماذا | ليش | ليش | ليش | ليه | علاش | ليه | ليش |
| like this | هكذا | هيچ | جذي / كذا | هيك | كده | هكّا | كدا | كذا |
| letters to keep | — | چ گ | چ (Kuwait), گ | — (ق spoken أ, written ق) | ج spoken /g/, written ج | ڤ ڭ | — | — |

Notes: these are common social spellings — when the creator spells a word their own way in their bio/posts, follow them. "Other" dialects (`dialect_note` in the profile): ask for 5 sample words once at onboarding and keep them in the user's `rules.md`.

### Set words (said between takes) per dialect — the profile list wins
`profile.language.set_words` is authoritative (default «اكشن، كت، نعيد، من جديد»). Typical extras to suggest at onboarding: Gulf «مرة ثانية»; Levantine «كمان مرة، من الأول»; Egyptian «تاني، من الأول، ستوب»; Maghrebi «عاوتاني، من اللول»; MSA «مرة أخرى». English "action / cut / again" are common in every dialect — Whisper may write them in Latin.

## Caption / keyword styles that work
1 bilingual stack (white Cairo Bold Arabic + yellow English below, chest height) · 2 word-pop karaoke, 1–2 words, active word yellow/brand · 3 editorial explainer: pale-yellow soft font, NO stroke/shadow/glow, darkened paper texture, red hand-drawn circles, yellow marker sweep (pen stroke, multiply, trim path) · 4 glass-panel "new reels style": frosted rounded box + glow line, key word Bold + light sweep, blurred foreground plants for depth, 4K comp → 1080 export for punch-ins · 5 sticker/ticket stamp: heavy display word on a textured label stamping in with overshoot — section titles · 6 news lower-third: offset yellow + white bars slide in, text masked in · 7 text behind the subject · 8 kashida emphasis ("الى بـاب بيـــتك"), key phrase in a pill, red highlight bar, neon trim-path icons.
(Styles 4 and 8 put text in containers — the skill's soft-text default avoids that; use them only when the brief picks them.)

## Animation that keeps letters connected
- Animate per **word** or **line**, never per character (per-character animators and typewriter presets break joins). In HTML: `dir="rtl"`, split on spaces into inline-block word spans, never wrap single letters.
- Safe: RTL clip/mask wipe over a whole word · blur-in + opacity · scale pop from the word's right edge · y-rise per word staggered from the right · marker/highlight bar drawn behind · kashida stretch · 3D extrusion with camera orbit · stroke reveal on outlined calligraphy · shape-grow then mask reveal.
- Unsafe: letter typewriter, random-letters, per-letter scramble/rotation, tracking animations, fake italics.
- Broken/reversed letters come from missing shaping or fonts without Arabic glyphs — always check the rendered frame.

## Culture, tone, hooks, CTAs
- Tone follows the creator's dialect and audience: warm, confident, a bit cheeky familiarity works in most dialects; self-deprecating humour and sarcasm about trends land well. Premium brands: calm, sparse, restraint = prestige.
- Hooks: prohibition ("إياك تنزّل ريل قبل ما…") · shocking stat ("٩٠٪ من…") · bold question with a threat ("تعرف إنك ممكن تخسر…؟") · fortune-teller ("بعد سنة…") · experiment ("جربت ٧ أيام…") · story cold open ("البارحة كنت راح أترك…") · result first. Rewrite every example in the creator's dialect. Hook templates wear out — write fresh.
- CTAs (adapt to the dialect): "راسلنا واتساب"، "الرابط بالبايو"، "شاركه لصديق يحتاجه"، "اكتب لي بالكومنتات"، community plugs. Use the profile's `brand.cta` when set.
- Sensitivities (practitioner knowledge — verify with the creator/client): no music under Quran; never animate sacred text playfully or near feet/shoes · religious mourning periods (e.g. Muharram/Ashura for many audiences) → avoid festive styling, avoid sectarian symbols · "الخليج العربي", correct maps/flags · modest stock for conservative audiences; no alcohol/gambling/dating imagery · Gulf luxury palette cream/gold/deep green/navy — but client brand colours always win · Ramadan/Eid visual language (lanterns, crescent, warm gold) seasonally.
- Order of work that pros report: audio → cuts → colour → B-roll → zooms → captions → transitions → SFX. Open on the strongest shot, cut every mistake/silence, overlays ≤ ~40 % of the frame.

## Idea bank
kashida-stretch reveal on the hook keyword · bilingual stack for diaspora audiences · dialect word-of-the-day explainer · paper + marker explainer · giant stat count-up · "الخطوة ١/٢/٣" ticket stamps · brand name behind the speaker · glass quote cards in 3D orbit · calligraphy stroke-draw of the brand name as outro · lower-third for source/guest · RTL before/after wipe · WhatsApp-chat CTA end card with RTL bubbles · regional map with city pins drawn on · prohibition hook card (red strike on "إياك") · brand-coloured karaoke · Ramadan lantern light sweep · proverb opener in Ruqaa → clean sans · Arabic-Indic countdown for heritage/news · خرافة/حقيقة flip cards · minimal premium (one serif hero sentence, warm grade, no captions) · zoom-out per paragraph + slow push inside · emoji-free premium mode vs emoji-rich street mode · respectful static quote reveal (no music) · dialect slang tooltip glossary · dialect-vs-MSA flip (e.g. «شلون / كيف») as a comedy beat · Arabic sound-word SFX captions («طـاخ»، «ووووب») with comic stretch · comment-reply reel (native comment bubble → answer) · retro ticket title card with barcode/REC marks + whip-blur · karaoke active word with scale pulse 1.0→1.08.

## Amateur tells (Arabic)
disconnected/reversed letters · per-letter animation breaking joins · Latin leading (colliding lines) · tracking or fake italics · kashida everywhere / wrong position / justification · raw auto-captions (missing hamzas, ة→ه, wrong dialect, 5–6-word lines) · mixed numerals, "?!", Latin punctuation · jumping inline English (bidi) · wipes/arrows moving left→right · Arial/Tahoma fallback or 5 fonts · stroke + glow + shadow stacked · text in (mirrored) UI zones · overlays > 40 % · silences/stumbles left, slow first 5 s · ignoring client brand colours, generic grid backgrounds · trending audio that later gets muted · emoji larger than the text.

## Addendum
- **Safe zone reconciled**: IG/TikTok buttons sit on the right (English UI) — exactly where right-aligned Arabic starts — or on the left (mirrored Arabic UI). → **centre-align captions, keep 190 px clear on both sides (y 700–1480) and 440 px at the bottom (craft/09 §3).**
- If letters ever must be split (avoid!), add ZWJ U+200D on the joining side of each fragment so contextual forms survive; use `unicode-bidi: plaintext` per caption; RLM (U+200F) after an inline Latin word before punctuation. Verify in a test render.
- Edit in a 4K comp and deliver 1080×1920 so punch-ins stay sharp; a 1-minute reel usually comes from 4–5 min of raw footage.
- Many creators write «فديو» — dialect spelling reads native, not wrong; fix ة/ه and ى/ي consistently within a video.
- Sensitivities: don't put Qur'anic verses in comedic/meme/glitch layouts; don't use the left hand in food/hospitality inserts; don't parody national symbols.
