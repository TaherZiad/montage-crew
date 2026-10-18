# سجل الإصدارات — Changelog

كل التغييرات المهمة في montage-crew مسجلة هنا. أرقام الإصدارات تتبع نظام [SemVer](https://semver.org/).
All notable changes are listed here. Versions follow [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-10-13

أول إصدار عام. First public release.

### الجديد

- مهارة مونتاج عربية لـ Claude Code تعمل على Windows و macOS.
- أسئلة إعداد في أول تشغيل: برنامج المونتاج، والصيغة، ونوع المادة، والصوت، واللهجة، والهوية البصرية، وطريقة العمل، والمجلدات. وأمر «غيّر إعداداتي» لتعديلها لاحقاً.
- فحص تلقائي للمتطلبات قبل أي سؤال (ffmpeg و Python و Node وكرت الشاشة والمساحة)، مع أمر التثبيت الدقيق لكل ما ينقص.
- وضعان للعمل: **سريع** (Claude وحده) و **احترافي** (فريق من 9 وكلاء `mc-*` بالتوازي).
- ثلاثة أنواع مادة: تصوير أمام الكاميرا، وتسجيل شاشة، وبدون تصوير (سكربت ← صوت ← موشن).
- ثلاث صيغ: 9:16 و 16:9 والاثنتان معاً.
- تسليم `final.mp4` دائماً، مع `.srt` و `.txt` وصورة غلاف، ومستوى صوت −14 LUFS.
- ملف تايملاين `timeline.xml` لمستخدمي DaVinci Resolve و Premiere Pro، مع كل الطبقات على مسارات منفصلة.
- وضع Resolve المباشر الاختياري عبر جسر davinci-resolve-mcp الذي يثبّته المستخدم بنفسه.
- دعم اللهجات: العراقية، والخليجية، والشامية، والمصرية، والمغاربية، والسودانية، واليمنية، والفصحى، وأي لهجة أخرى يصفها المستخدم، مع كلمات الإعادة الخاصة به.
- حلقة تعلّم: كل ملاحظة تتحول إلى قاعدة في `rules.md` الخاص بالمستخدم، مع سجل نتائج `scorecard.md`.
- مكتبة مؤثرات صوتية برخصة CC0، وخطوط عربية برخصة OFL، وقوالب موشن عربية.
- تثبيت بفك الضغط في مجلد المهارات، أو بطلب من Claude Code. المهارة تفحص ffmpeg و Python و Node.js والنماذج في أول استخدام، وتثبّت ما ينقص بعد موافقة المستخدم. والإزالة بأمر `setup.py uninstall`.

### Added

- Arabic video-editing skill for Claude Code on Windows and macOS.
- First-run onboarding (editor, format, footage, voice, dialect, brand, mode, folders) and a `غيّر إعداداتي` ("change my settings") command.
- Automatic prerequisite check before any question, with the exact install command for anything missing.
- Two modes: **fast** (Claude alone) and **pro** (a team of 9 `mc-*` agents in parallel).
- Three footage types: on camera, screen recording, and no footage (script → voice → motion graphics).
- Three formats: 9:16, 16:9, or both.
- Always delivers `final.mp4` with `.srt`, `.txt` and a cover image, mastered to −14 LUFS.
- `timeline.xml` (FCP7 XML) for DaVinci Resolve and Premiere Pro, one track per layer.
- Optional LIVE Resolve mode through the user-installed davinci-resolve-mcp bridge.
- Dialects: Iraqi, Gulf, Levantine, Egyptian, Maghrebi, Sudanese, Yemeni, MSA, and any other dialect the user describes, with the user's own retake words.
- Learning loop: each correction becomes a rule in the user's `rules.md`, tracked in `scorecard.md`.
- Bundled CC0 sound effects, OFL Arabic fonts and Arabic motion templates.
- Install by unzipping into the skills folder, or by asking Claude Code. On first use the skill checks ffmpeg, Python, Node.js and the models and installs what is missing after the user agrees. Uninstall with `setup.py uninstall`.
