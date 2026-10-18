# Onboarding — first run, and «غيّر إعداداتي»

Run this when `{{DATA_DIR}}/profile.json` is missing, fails validation, has an older `schema_version`, or the user asks to change settings («غيّر إعداداتي», "settings", «الإعدادات»). The first edit request runs onboarding and then CONTINUES that edit — don't make the user ask twice.

## 0. Detect (automatic, no questions)
Setup has already run (SKILL.md §0 step 0: `setup.py check` → one yes → install). Copy the `detected` object of `{{PY}} {{SKILL_DIR}}/scripts/setup.py check` (JSON, already in profile shape: OS `windows` / `macos`, GPU `cuda` / `apple` / `none`, ffmpeg / Python / Node versions, free disk). Warn once if the work folder's drive has under 10 GB free (a minute of 4K ProRes layers ≈ 3–6 GB). If `setup.py check` still reports something missing, go back to SKILL.md §0 step 0 — don't ask the profile questions on a broken install.

## 1. Questions — plain Arabic (فصحى مبسطة), at most 4 per message, each with a default
Show defaults in brackets; an empty answer or «تمام» accepts the default. When re-running for «غيّر إعداداتي», the defaults are the CURRENT profile values.

**Message 1**
1. «ما برنامج المونتاج الذي تستخدمه؟» → DaVinci Resolve المجاني · Resolve Studio · Premiere Pro · لا شيء (تستلم الفيديو النهائي جاهزًا). [لا شيء]
2. «ما مقاس الفيديو؟» → ريلز/تيك توك عمودي 9:16 · يوتيوب أفقي 16:9 · الاثنان معًا. [9:16]
3. «ما نوع اللقطات عادةً؟» → أنت أمام الكاميرا · تسجيل شاشة · بدون لقطات (فكرة ← نص ← صوت ← موشن). [أمام الكاميرا] — can be overridden per video.
4. «طريقة العمل؟» → سريع (وكيل واحد، أسرع وأقل استهلاكًا) · احترافي (فريق كامل من الوكلاء بالتوازي، جودة أعلى ووقت واستهلاك أكثر). [سريع]

(Keep the questions in simple MSA so every dialect understands them; answers may come in any dialect or in English.)

**Message 2**
5. «الصوت؟» → صوتك أنت · صوت ذكاء اصطناعي (بمفتاحك الخاص) · موسيقى فقط. [صوتك]
   - AI voice → ask the provider (default ElevenLabs) and **the NAME of the environment variable** that holds the key (e.g. `ELEVENLABS_API_KEY`) — never the key itself. Check it exists without printing it: PowerShell `if ($env:NAME) { 'set' }` / bash `[ -n "${NAME:-}" ] && echo set`. Not set → show how to set it (Windows: `setx NAME "<key>"` then restart; macOS: add `export NAME=…` to `~/.zshrc`) and continue with "music only" until it exists. Also ask for a voice id (optional).
6. «ما لهجتك؟» → عراقية · خليجية · شامية · مصرية · مغاربية · سودانية · يمنية · فصحى · غيرها (اكتبها). [فصحى] — "other" → `dialect: "other"` + `dialect_note`, and ask for 5 sample words (how/what/now/a lot/I want) once; save them as a rule in `{{DATA_DIR}}/rules.md`.
7. «عندما تعيد لقطة، هل تقول كلمة معيّنة؟ (مثل: اكشن، كت، نعيد، من جديد)» → show the default list + the dialect's suggestions from `references/craft/08-arabic-typography-culture.md`; the user can add/remove words. [اكشن، كت، نعيد، من جديد]
8. «شكل الأرقام؟» → 123 · ١٢٣. [123]

**Message 3**
9. «هويتك (اختياري)؟» → 3 colours (background / text / accent as hex) · head font + body font (from the bundled list in `assets/fonts/` or a path to a font file) · logo file path · handle / CTA line. Empty = «تُحدَّد لكل فيديو». [فارغ]
10. «أين نعمل، وأين نحفظ الفيديوهات النهائية؟» → work folder [`~/montage-crew-work`] · output folder [`~/Videos/montage-crew`]. The work folder must be an ASCII path (Resolve and some tools fail on Arabic paths) — if the user gives a non-ASCII path, explain and propose an ASCII one.

**Only if editor = Resolve (free or Studio) — one extra question**
11. «هل تريد أن يُبنى المونتاج مباشرة داخل دافنشي وأنت تشاهد وتعدّل (وضع LIVE)؟ يحتاج تثبيت أداة مفتوحة المصدر مرة واحدة.» → لا، أعطني ملف تايملاين أستورده (الأسهل) · نعم، وضع LIVE. [لا]
   - Yes → walk them through `references/resolve/00-control-architecture.md` › B.1 (they install the open-source DaVinci Resolve MCP + console bridge themselves), then ask for the path of that tool's python (`…/venv/Scripts/python.exe` or `…/venv/bin/python`) and its folder → `resolve_live`. Verify with `live.py ping` once Resolve is open; if it fails, save `enabled: false` and tell them LIVE can be switched on later via «غيّر إعداداتي».

## 2. Summary → one yes → save
Show a short Arabic summary table of every answer. On «نعم / تمام / yes»:
1. Write `{{DATA_DIR}}/profile.json` (schema in `{{SKILL_DIR}}/templates/profile.schema.json`, example `templates/profile.example.json`): `schema_version: 1`, ISO `created`/`updated`, the answers, `detected` from step 0. Expand `~` to the absolute home path. Store the API key's env-var NAME only — **never a key value, anywhere** (profile, work folder, logs).
2. Validate: `{{PY}} {{SKILL_DIR}}/scripts/mc_profile.py validate`. Fails → fix and re-validate; never continue with an invalid profile.
3. If missing, copy `{{SKILL_DIR}}/templates/rules.md` → `{{DATA_DIR}}/rules.md` and `templates/scorecard.md` → `{{DATA_DIR}}/scorecard.md`. Never overwrite existing ones (they are the user's history).
4. Create the work and output folders.
5. One line: «حُفظت إعداداتك. يمكنك تغييرها في أي وقت بقول: غيّر إعداداتي» — then continue the edit request that triggered onboarding.

## 3. Broken profile
JSON parse error or validation failure → rename it to `profile.json.bak` (keep older `.bak` files: `profile.json.bak2`, …), tell the user in one line, run onboarding with the old readable values as defaults.

## 4. Per-video overrides
The user can override any setting for one video in the request («هذا الفيديو 16:9»، «هذا تسجيل شاشة»، «اعمل بالوضع الاحترافي هذه المرة») — apply it to that video only; the profile changes only through «غيّر إعداداتي».
