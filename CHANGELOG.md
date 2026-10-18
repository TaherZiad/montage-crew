# سجل الإصدارات — Changelog

كل التغييرات المهمة في montage-crew مسجلة هنا. أرقام الإصدارات تتبع نظام [SemVer](https://semver.org/).
All notable changes are listed here. Versions follow [Semantic Versioning](https://semver.org/).

## [2.0.0] — 2026-10-18

montage-crew أصبحت إضافة (plugin) لـ Claude Code. montage-crew is now a Claude Code plugin.

### الجديد

- التثبيت كإضافة: `/plugin marketplace add` ثم `/plugin install montage-crew@montage-crew`، والتحديث بـ `/plugin update`. نسخة ZIP من الموقع ما زالت متاحة.
- أربعة أوامر: `/montage-crew:montage` و `/montage-crew:learn` و `/montage-crew:brand` و `/montage-crew:settings`. والعبارات العادية تعمل كما هي.
- برامج مونتاج جديدة: After Effects (سكربت `ae_import.jsx` يبني التركيبة بكل الطبقات)، و CapCut و Final Cut Pro (الفيديو النهائي ومجلد `project/layers/` بطبقات شفافة مرقّمة وملف `order.txt`).
- سؤال جديد في الإعداد عن الأساليب التي تحبها: أساليب جاهزة، وشكل الترجمة، وطابع الحركة، وروابط صناع محتوى يعجبك أسلوبهم.
- نوع مادة جديد: «الاثنان» (كاميرا وتسجيل شاشة في نفس الفيديو).
- هوية بصرية محفوظة: «احفظ هويتي» تنسخ الشعار والخطوط إلى `~/.montage-crew/brand/` وتستخرج الألوان من الشعار أو الصور أو الموقع.
- التعلّم مما تعلّمه لها: فيديو، أو رابط صانع محتوى، أو صفحة من موقع موشن غرافيك. تحفظ الأسلوب باسم في `~/.montage-crew/styles/` والحركات الجديدة في `~/.montage-crew/learned/`. تتعلم الطريقة فقط ولا تنسخ ملفات الآخرين.
- فيديو من فكرة فقط في أي طلب («ما عندي فيديو، عندي فكرة: …»)، مهما كان نوع المادة في الإعداد.
- 12 أسلوباً جاهزاً مدمجاً في `skills/montage-crew/styles/`، وتُضاف أساليب جديدة في الإصدارات القادمة.

### التغييرات

- كل بيانات المستخدم في `~/.montage-crew/` (أو `MONTAGE_CREW_HOME`)، خارج مجلد الإضافة، فلا يمسحها أي تحديث.
- ملف الإعداد بصيغة الإصدار 2، وإعداد الإصدار 1 يُنقل تلقائياً مع الإبقاء على كل الإجابات.
- الشعار لم يعد مساراً خارجياً يتعطل إذا نُقل الملف: يُنسخ إلى مجلد الهوية.
- في نسخة الإضافة يظهر الوكلاء باسم `montage-crew:mc-*`، ولا تُنسخ ملفات إلى `~/.claude/agents/`.
- بنية الحزمة: المهارة في `skills/montage-crew/`، والوكلاء في `agents/`، والأوامر في `commands/`.

### Added

- Plugin install: `/plugin marketplace add`, then `/plugin install montage-crew@montage-crew`; update with `/plugin update`. The website ZIP is still available.
- Four commands: `/montage-crew:montage`, `/montage-crew:learn`, `/montage-crew:brand`, `/montage-crew:settings`. Plain phrases keep working.
- New editors: After Effects (`ae_import.jsx` builds the composition with every layer), CapCut and Final Cut Pro (final video plus `project/layers/` with numbered transparent layers and `order.txt`).
- New setup question about the styles you like: built-in looks, caption style, motion feel and links to creators you like.
- New footage type: mixed (camera and screen recording in one video).
- Saved brand kit: «احفظ هويتي» ("save my brand") copies your logo and fonts into `~/.montage-crew/brand/` and extracts the palette from your logo, images or website.
- Learning from what you teach it: a video, a creator's link or a motion-design site page. Styles are saved by name in `~/.montage-crew/styles/`, new techniques in `~/.montage-crew/learned/`. It learns the technique only and never copies other people's files.
- Idea-only videos in any request («ما عندي فيديو، عندي فكرة» "I have no video, I have an idea"), whatever the profile's footage type.
- 12 built-in style cards in `skills/montage-crew/styles/`; new styles can ship as cards in later versions.

### Changed

- All user data lives in `~/.montage-crew/` (or `MONTAGE_CREW_HOME`), outside the plugin folder, so updates never erase it.
- Profile schema v2; a v1 profile is migrated automatically, keeping every answer.
- The logo is no longer an external path that breaks when the file moves: it is copied into the brand folder.
- In the plugin the pro-mode agents are named `montage-crew:mc-*`, and nothing is copied to `~/.claude/agents/`.
- Package layout: the skill is in `skills/montage-crew/`, agents in `agents/`, commands in `commands/`.

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
