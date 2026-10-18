# Onboarding v2 — first run, upgrades, and «غيّر إعداداتي»

Run this when `{{DATA_DIR}}/profile.json` is missing or invalid, when it is an older `schema_version` (migration, §4), or when the user asks to change settings («غيّر إعداداتي», «الإعدادات», "settings", `/montage-crew:settings`). The first edit request runs onboarding and then CONTINUES that edit — don't make the user ask twice.
Style of every message: simple MSA (فصحى مبسطة, every dialect understands it), **at most 4 questions per message**, each with a default in brackets. An empty answer or «تمام» accepts the defaults. Answers may come in any dialect or in English. When re-running for «غيّر إعداداتي», the defaults are the CURRENT profile values, and the user may name only the one thing to change («غيّر المقاس إلى 16:9») — then ask only that.

## 0. Detect (automatic, no questions)
Setup has already run (SKILL.md §0 step 0). Copy the `detected` object of `{{PY}} {{SKILL_DIR}}/scripts/setup.py check` (OS, GPU, ffmpeg / Python / Node versions, free disk). Warn once if the work folder's drive has under 10 GB free (a minute of 4K ProRes layers ≈ 3–6 GB). If `setup.py check` still reports something missing, go back to SKILL.md §0 — never ask the profile questions on a broken install.

## 1. Questions

**Message 1 — how you work**
1. «ما برنامج المونتاج الذي تستخدمه؟» → DaVinci Resolve المجاني · Resolve Studio · Premiere Pro · After Effects · CapCut · Final Cut Pro · لا شيء (تستلم الفيديو النهائي جاهزًا). [لا شيء]
   (`editor`: resolve_free · resolve_studio · premiere · after_effects · capcut · final_cut · none. Everyone gets the final MP4; editors also get an importable project — SKILL §1d.)
2. «ما مقاس الفيديو؟» → عمودي 9:16 (ريلز/تيك توك) · أفقي 16:9 (يوتيوب) · الاثنان معًا. [9:16]
3. «هل تصوّر فيديوهاتك بنفسك؟» → نعم، أمام الكاميرا · أسجّل الشاشة · الاثنان (كاميرا + شاشة) · لا أصوّر، عندي فكرة فقط (نصنع الفيديو كاملًا بالموشن). [أمام الكاميرا]
   (`footage`: camera · screen · mixed · none. Any single video can override it: «ما عندي فيديو، الفكرة…».)
4. «طريقة العمل؟» → سريع (وكيل واحد، أسرع وأقل استهلاكًا) · احترافي (فريق كامل من الوكلاء، جودة أعلى ووقت واستهلاك أكثر). [سريع]

**Message 2 — voice and language**
5. «الصوت في الفيديو؟» → صوتك أنت · صوت ذكاء اصطناعي (بمفتاحك الخاص) · موسيقى فقط. [صوتك]
   - AI voice → ask the provider (ElevenLabs default, or OpenAI) and **the NAME of the environment variable** holding the key — never the key itself. Allowed names only: `ELEVENLABS_API_KEY` / `XI_API_KEY` (ElevenLabs), `OPENAI_API_KEY` (OpenAI); any other name (and anything starting `ANTHROPIC_`, `CLAUDE`, `GITHUB_`, `AWS_`, …) is refused. Check it exists without printing it: PowerShell `if ($env:NAME) { 'set' }` / bash `[ -n "${NAME:-}" ] && echo set`. Not set → show how to set it (Windows: `setx NAME "<key>"` then restart Claude Code; macOS/Linux: `export NAME=…` in `~/.zshrc` / `~/.bashrc`) and use "music only" until it exists. Voice id: required for ElevenLabs (from their Voice Library), optional for OpenAI (default `alloy`). The voice is generated only by `scripts/tts.py`; check with the answers just given: `{{PY}} {{SKILL_DIR}}/scripts/tts.py - --out x.wav --provider <provider> --voice <voice id> --dry-run` (expect `key_set: true`; nothing is sent; no voice id for OpenAI → omit `--voice`).
6. «ما لهجتك؟» → عراقية · خليجية · شامية · مصرية · مغاربية · سودانية · يمنية · فصحى · غيرها (اكتبها). [فصحى] — "other" → `dialect: "other"` + `dialect_note`, and ask once for 5 sample words (كيف / ماذا / الآن / كثيرًا / أريد); save them as a rule in `{{DATA_DIR}}/rules.md` (they are the user's own words).
7. «عندما تعيد لقطة، هل تقول كلمة معيّنة؟ (مثل: اكشن، كت، نعيد، من جديد)» → the default list + the dialect's suggestions from `references/craft/08-arabic-typography-culture.md`; the user can add/remove words. [اكشن، كت، نعيد، من جديد]
8. «شكل الأرقام؟» → 123 · ١٢٣. [123]

**Message 3 — the styles you like**
Show the built-in cards as ONE compact list (slug + its one-line look from `{{SKILL_DIR}}/styles/INDEX.md`, 12 lines) and the caption gallery path: `{{SKILL_DIR}}/assets/captions/gallery/index.html` (absolute path; «افتحه في المتصفح لترى 28 شكلًا للترجمة»).
9. «أي الأساليب تعجبك؟ اختر من 1 إلى 3 (أو: اختر أنت حسب كل فيديو)» [اختر أنت — premium-soft for talking heads]
10. «شكل الترجمة (الكابشن)؟» → الافتراضي · اختر رقمًا من المعرض (CAP-01…CAP-28 ولون SC-01…SC-14). [CAP-04 + SC-02]
11. «إيقاع الحركة؟» → ناعم (smooth) · سريع وحاد (snappy) · فاخر وهادئ (premium). [ناعم]
12. «هل هناك صانع محتوى أو فيديوهات يعجبك أسلوبها؟ أرسل روابط أو ملفات (اختياري) — أتعلّم أسلوبها بعد الإعداد.» [لا]
   (→ `style_prefs.looks`, `caption_style`, `caption_scheme`, `motion_personality`, `liked_refs`. `default_style` stays null unless the user names one style for every video.)

**Message 4 — brand and folders**
13. «هل عندك هوية بصرية (براند)؟» → نعم (شعار / ألوان / خطوط / دليل هوية / موقع / منشورات سابقة) · لا، حدّدها لكل فيديو · لا، اقترح لي هوية. [لا، لكل فيديو]
   - Yes → after this message run the import flow in `references/brand.md` (asks only what is missing, copies files into `{{DATA_DIR}}/brand/`, `brand.py import`).
   - «اقترح لي هوية» → `references/brand.md` › No brand yet (one proposal + 2 alternatives, saved only on yes).
   - No → `brand.has_brand = false`; derived per video.
14. «أين نعمل، وأين نحفظ الفيديوهات النهائية؟» → work folder [`~/montage-crew-work`] · output folder [`~/Videos/montage-crew`]. The work folder must be an ASCII path (Resolve and some tools fail on Arabic paths) — if the user gives a non-ASCII path, explain and propose an ASCII one.

**Only if editor = Resolve (free or Studio) — one extra question**
15. «هل تريد أن يُبنى المونتاج مباشرة داخل دافنشي وأنت تشاهد (وضع LIVE)؟ يحتاج تثبيت أداة مفتوحة المصدر مرة واحدة.» → لا، أعطني ملف تايملاين أستورده (الأسهل) · نعم، وضع LIVE. [لا]
   - Yes → walk them through `references/resolve/00-control-architecture.md` › B.1 (they install the open-source DaVinci Resolve MCP + console bridge themselves), then ask for that tool's python path and folder → `resolve_live`. Verify with `live.py ping` once Resolve is open; if it fails, save `enabled: false` and say LIVE can be switched on later via «غيّر إعداداتي».

## 2. Summary → one yes → save
Show a short Arabic summary table of every answer (brand: name + 3 colour swatches as hex + fonts + logo file name). On «نعم / تمام / yes»:
1. Write `{{DATA_DIR}}/profile.json` (schema `{{SKILL_DIR}}/templates/profile.schema.json`, example `templates/profile.example.json`): `schema_version: 2`, ISO `created`/`updated`, the answers, `detected` from step 0. Expand `~` to the absolute home path. The brand block is written by `brand.py` (it mirrors `brand/brand.json`) — don't hand-edit it. A brand imported during this onboarding was saved before the profile existed → run `{{PY}} {{SKILL_DIR}}/scripts/brand.py sync` right after writing the profile. Store the API key's env-var NAME only — **never a key value, anywhere** (profile, work folder, logs).
2. Validate: `{{PY}} {{SKILL_DIR}}/scripts/mc_profile.py validate`. Fails → fix and re-validate; never continue with an invalid profile.
3. If missing, copy `{{SKILL_DIR}}/templates/rules.md` → `{{DATA_DIR}}/rules.md` and `templates/scorecard.md` → `{{DATA_DIR}}/scorecard.md`. Never overwrite existing ones (they are the user's history).
4. Create the work and output folders.
5. One line: «حُفظت إعداداتك. يمكنك تغييرها في أي وقت بقول: غيّر إعداداتي».
6. `liked_refs` not empty → one line: «أتعلّم أسلوب الروابط التي أرسلتها الآن؟ (حوالي 10–20 دقيقة لكل رابط)» — yes → `references/learn.md` for each (it asks before saving each style); no → they stay in the profile for later («تعلّم من الروابط التي أعجبتني»).
7. Continue the edit request that triggered onboarding (if any).

## 3. Broken profile
JSON parse error or validation failure → rename it to `profile.json.bak` (keep older `.bak` files: `profile.json.bak2`, …), tell the user in one line, run onboarding with the old readable values as defaults.

## 4. Upgrade from v1 (ask only what is new)
`schema_version` 1 → `{{PY}} {{SKILL_DIR}}/scripts/mc_profile.py migrate` (keeps every value, backup `profile.v1.json`), and read the `ask` list in migrate's own JSON output → the fields still unset or reset during migration (usually `style_prefs.looks`, `style_prefs.caption_style`, `style_prefs.motion_personality`, and `brand.has_brand` when the v1 brand was empty). Ask ONLY those questions (from Message 3 / question 13 above), in one message, after one line: «أضفنا في الإصدار الثاني اختيار الأساليب والهوية البصرية — سؤالان أو ثلاثة فقط.» A v1 brand with colours/logo path → offer once to copy it into the brand kit (`brand.py import --logo <old path> --colors …`) so it no longer breaks if the file moves. Then §2 steps 2–7.

## 5. Per-video overrides
Any setting can change for one video in the request («هذا الفيديو 16:9»، «هذا تسجيل شاشة»، «ما عندي فيديو، عندي فكرة»، «بستايل neon-blue»، «اعمل بالوضع الاحترافي هذه المرة») — apply it to that video only; the profile changes only through «غيّر إعداداتي» / `/montage-crew:settings`.
