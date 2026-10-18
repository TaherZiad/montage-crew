صُنعت بواسطة Eng. Taher — https://eng-taher.vercel.app

# montage-crew — مونتير عربي داخل Claude Code

مهارة (skill) مجانية لـ Claude Code، أي مساعد ذكي يعمل مونتاج فيديوهاتك أنت ويكتب كود الأنيميشن نيابة عنك. تعمل على فيديوهاتك القصيرة بالعربية: تقص السكتات واللقطات المعادة، وتكتب ترجمة عربية باتجاه صحيح، وتضيف موشن غرافيك وأصواتاً، ثم تسلّمك فيديو نهائياً جاهزاً للنشر.
تعمل على جهازك (Windows أو macOS)، وتسألك عن طريقة عملك في أول مرة، ثم تتعلم من كل ملاحظة تعطيها.
For English, see [the English section](#english) below.

---

## البداية السريعة

1. ضع المهارة في مجلد مهارات Claude Code: افتح Claude Code واكتب «ثبّت السكل من هذا الملف» مع مسار ملف ZIP، أو فك الضغط يدوياً. الخطوات في [INSTALL.md](INSTALL.md).
2. اطلب أول فيديو:

```text
منتجلي هذا الفيديو: <مسار الفيديو>
```

أي عبارة بنفس المعنى تكفي. في أول مرة تفحص المهارة جهازك (ffmpeg و Python و Node.js والنماذج)، وتخبرك بما ينقص وتثبّته بعد موافقتك، ثم تسألك بضعة أسئلة عن إعدادك، ثم تبدأ المونتاج مباشرة.
الشيء الوحيد الذي تحتاجه مسبقاً هو Claude Code نفسه.

---

## ماذا تفعل المهارة

- **القص:** تحذف السكتات الطويلة واللقطات المعادة والكلمات التي تقولها عند إعادة اللقطة (مثل «اكشن، كت، نعيد»).
- **الترجمة على الشاشة:** كل الكلام مكتوب بعبارات قصيرة، بخطوط عربية مجانية، وباتجاه صحيح من اليمين إلى اليسار.
- **الموشن غرافيك:** أيقونات وبطاقات وأرقام وعناوين متحركة في أقوى لحظات الفيديو، ويمكن أن يظهر النص خلف المتكلم.
- **الصوت:** تنظيف الصوت، ومؤثرات صوتية (SFX) برخصة CC0، وموسيقى هادئة تنخفض تحت الكلام، وضبط مستوى الصوت النهائي على −14 LUFS.
- **الغلاف:** صورة غلاف بمقاس 9:16 وبمقاس 3:4 لشبكة الحساب.
- **الصيغ:** ريلز وتيك توك (9:16)، أو يوتيوب (16:9)، أو الاثنتان معاً.
- **نوع المادة:** تصوير أمام الكاميرا، أو تسجيل شاشة، أو بدون تصوير أصلاً (فكرة ← سكربت ← صوت ← موشن).

---

## أول تشغيل: أسئلة الإعداد

قبل أي سؤال، تفحص المهارة جهازك وحدها: ffmpeg و Python و Node وكرت الشاشة ونظام التشغيل والمساحة الفارغة.
إذا نقص شيء تخبرك باسمه وبأمر تثبيته، وتثبّته فقط بعد أن تقول «نعم».

بعد ذلك تسألك على 3 رسائل (4 أسئلة كحد أقصى في كل رسالة، ولكل سؤال جواب افتراضي، والرد الفارغ أو «تمام» يقبله):

| # | السؤال | الخيارات | الافتراضي |
|---|---|---|---|
| 1 | برنامج المونتاج الذي تستخدمه | DaVinci Resolve المجاني · Resolve Studio · Premiere Pro · لا شيء | لا شيء (تستلم الفيديو النهائي فقط) |
| 2 | مقاس الفيديو | عمودي 9:16 · أفقي 16:9 · الاثنان معاً | 9:16 |
| 3 | نوع اللقطات عادةً | أمام الكاميرا · تسجيل شاشة · بدون لقطات | أمام الكاميرا |
| 4 | طريقة العمل | سريع · احترافي | سريع |
| 5 | الصوت | صوتك · صوت ذكاء اصطناعي (بمفتاحك) · موسيقى فقط | صوتك |
| 6 | اللهجة | قائمة اللهجات في الأسفل | الفصحى |
| 7 | كلمات الإعادة | الكلمات التي تقولها عند إعادة لقطة | اكشن، كت، نعيد، من جديد |
| 8 | شكل الأرقام | 123 · ١٢٣ | 123 |
| 9 | الهوية البصرية (اختياري) | 3 ألوان · خط العناوين وخط النص · الشعار · اسم الحساب وعبارة الدعوة | فارغ = تُحدَّد لكل فيديو |
| 10 | المجلدات | مجلد العمل · مجلد التسليم | `~/montage-crew-work` و `~/Videos/montage-crew` |
| 11 | وضع Resolve المباشر (فقط إذا اخترت Resolve) | لا، أعطني ملف تايملاين · نعم | لا |

مجلد العمل يجب أن يكون بأحرف إنجليزية فقط، لأن بعض الأدوات تفشل مع المسارات العربية.

في النهاية تعرض عليك ملخصاً، وتحفظه بعد أن تقول «نعم».
لتغيير أي إعداد لاحقاً، اكتب:

```text
غيّر إعداداتي
```

فتعود الأسئلة نفسها، وتكون إجاباتك الحالية هي الافتراضية.
يمكنك أيضاً تغيير نوع المادة أو الصيغة لفيديو واحد فقط في نفس الطلب، مثلاً: «هذا تسجيل شاشة».

---

## طريقتان لاستلام المونتاج

### الطريقة 1: فيديو نهائي + ملف تايملاين (للجميع)

في كل الأحوال تستلم في مجلد التسليم:

- `final.mp4` — الفيديو النهائي (H.264، صوت AAC بتردد 48 kHz، مستوى −14 LUFS).
- ملف الترجمة `.srt` ونص الكلام `.txt`.
- صورة الغلاف.

وإذا اخترت DaVinci Resolve أو Premiere Pro، تستلم أيضاً مجلد `project/` وفيه `timeline.xml` ومجلد `media/`.
افتح الملف في برنامجك فتجد كل الطبقات مرتبة على مسارات منفصلة، وأكمل التعديل يدوياً:

- **في DaVinci Resolve:** قبل الاستيراد اضبط معدل الإطارات للمشروع على 30 من File › Project Settings، ثم File › Import › Timeline واختر `timeline.xml`.
- **في Premiere Pro:** File › Import واختر `timeline.xml`.
- إذا ظهرت مقاطع بحالة «offline»: انقر بالزر الأيمن › Relink واختر مجلد `project/media/`.

### الطريقة 2: وضع Resolve المباشر (اختياري)

في هذا الوضع تبني المهارة التايملاين **داخل DaVinci Resolve وهو مفتوح أمامك**: كل طبقة تظهر لحظة جاهزيتها، ويمكنك التعديل في نفس الوقت، والمهارة تحافظ على تعديلاتك.

- يحتاج جسراً مفتوح المصدر اسمه davinci-resolve-mcp (رخصة MIT، وليس من صنعنا)، وأنت من يثبّته. خطوات الإعداد في [INSTALL.md](INSTALL.md#وضع-resolve-المباشر-اختياري).
- يعمل على Resolve المجاني (الإصدار 21.1) عن طريق تبويب **Lua** في نافذة Console، ويعمل كذلك على Resolve Studio.
- تنبيه: الجسر يسمح للبرامج على جهازك بالتحكم في دافنشي — شغّله فقط وقت المونتاج وأطفئه بعده.
- إذا توقف الجسر في أي لحظة، ترجع المهارة إلى الطريقة 1 تلقائياً وتخبرك بسطر واحد. التسليم لا يتوقف بسبب Resolve.

---

## سريع أو احترافي

| | سريع | احترافي |
|---|---|---|
| من يعمل | Claude وحده، خطوة بعد خطوة | فريق من 9 وكلاء `mc-*` يعملون بالتوازي، و Claude هو القائد |
| الوقت | أقصر | أطول، لكن النتيجة أغنى |
| الموشن غرافيك | في أقوى اللحظات (تقريباً واحد كل 6 ثوانٍ) | لكل فكرة، مع بحث عن صور وأيقونات خاصة بكلامك |
| الغلاف | فقط إذا طلبته | دائماً |
| الاستهلاك من اشتراكك في Claude | أقل | أكثر بكثير |
| مراجعة الجودة | Claude يراجع بنفسه | وكيل مراجعة مستقل (`mc-qa`) يفحص الفيديو قبل التسليم |

وكلاء الوضع الاحترافي:

| الوكيل | عمله |
|---|---|
| `mc-cutter` | التفريغ النصي والقص والتوقيت النهائي |
| `mc-scout` | فحص المادة الخام وجمع الصور والأيقونات والشعارات |
| `mc-picture` | فصل المتكلم عن الخلفية، والتأطير والتقريب، والمناطق الآمنة للنص |
| `mc-audio` | الصوت والمؤثرات والموسيقى |
| `mc-captions` | الترجمة والجملة الافتتاحية المكتوبة (الهوك) |
| `mc-motion` | الموشن غرافيك (من نسخة إلى 3 نسخ حسب طول الفيديو) |
| `mc-cover` | صورة الغلاف |
| `mc-qa` | مراجعة الجودة |
| `mc-writer` | كتابة السكربت عندما لا يوجد تصوير |

---

## تتعلم من ملاحظاتك

كل ما تعطيها ملاحظة، تتعلم.
مثلاً: «الترجمة كبيرة» أو «لا تضع موسيقى في الفيديوهات التعليمية». تسجّل المهارة الملاحظة، وفي نهاية كل فيديو تحوّلها إلى قاعدة دائمة في ملف `rules.md` الخاص بك، وتخبرك في سطرين بما تعلمته.
في الفيديو التالي تقرأ قواعدك قبل أن تبدأ، فلا تحتاج إلى تكرار نفس الملاحظة.
القواعد ملكك: يمكنك فتح الملف وتعديله أو حذف أي قاعدة، وتحديث المهارة لا يمسحها.

---

## اللهجات

تكتب المهارة الترجمة والهوك بلهجتك، وتعرف كلمات الإعادة الخاصة بك فتحذفها من القص:

- العراقية
- الخليجية
- الشامية
- المصرية
- المغاربية
- السودانية
- اليمنية
- الفصحى
- لهجة أخرى: تكتب اسمها وملاحظة عنها

وتسألك أيضاً: هل تقول كلمة معينة عند إعادة اللقطة؟ (الافتراضي: اكشن، كت، نعيد، من جديد)، وهل تريد الأرقام بشكل 123 أو ١٢٣.

---

## بياناتك تبقى على جهازك

- **ملفات الفيديو والصوت تُعالج على جهازك:** القص والتفريغ النصي (Whisper) وفصل المتكلم عن الخلفية والتصيير كلها محلية.
- **إعداداتك وقواعدك محفوظة في مجلد واحد على جهازك:** `~/.montage-crew/`
  - `profile.json` — إجاباتك على أسئلة الإعداد.
  - `rules.md` و `scorecard.md` و `corrections/` — ما تعلمته المهارة منك.
  - `venv/` و `models/` — بيئة Python والنماذج التي تُنزَّل أول مرة.
- **المهارة لا ترسل أي بيانات إلى صاحبها:** لا تتبّع ولا فحص تحديثات.
- **ما يخرج إلى الإنترنت:**
  - Claude Code نفسه يرسل إلى Anthropic النصوص والصور التي يقرؤها أثناء العمل (التفريغ النصي، لقطات من الفيديو)، كأي استخدام عادي لـ Claude Code.
  - تنزيل النماذج والملفات في أول استخدام (Whisper من Hugging Face، ونموذج فصل الخلفية من GitHub، ومكتبة GSAP من jsDelivr)، مع عرض الحجم قبل التنزيل وفحص البصمة (SHA-256) بعده.
  - البحث عن صور وأيقونات مجانية لفيديوك.
  - إذا اخترت صوت ذكاء اصطناعي: نص السكربت يذهب إلى مزوّد الصوت بمفتاحك أنت. المهارة تسألك عن **اسم** متغير البيئة الذي يحمل المفتاح فقط، ولا تكتب قيمة المفتاح على القرص أبداً.

---

## محتويات الحزمة

| المسار | المحتوى |
|---|---|
| `README.md` | هذا الملف |
| `INSTALL.md` | خطوات التثبيت والإزالة |
| `LICENSE` | رخصة المهارة |
| `NOTICES.md` | رخص المكونات الخارجية (الخطوط، المؤثرات الصوتية، القوالب، المراجع) |
| `CHANGELOG.md` | سجل الإصدارات |
| `SKILL.md` و `onboarding.md` و `references/` و `scripts/` و `assets/` و `templates/` | المهارة نفسها |
| `requirements.txt` | مكتبات Python التي تثبّتها المهارة في أول استخدام |
| `agents/` | وكلاء الوضع الاحترافي `mc-*` |

---

## الرخصة

- مجانية للاستخدام والتعديل.
- الفيديوهات التي تصنعها بها ملكك، ويمكنك استخدامها تجارياً (إعلانات، عملاء، قنوات ربحية).
- لا يجوز بيع المهارة نفسها أو إعادة نشرها كمنتج مدفوع.
- المكونات الخارجية (الخطوط، المؤثرات الصوتية، القوالب، المراجع) تبقى برخصها الأصلية. التفاصيل في [LICENSE](LICENSE) و [NOTICES.md](NOTICES.md).
- الشعارات والعلامات التجارية التي تنزّلها المهارة لفيديوك (مثل شعارات التطبيقات) تبقى ملكاً لأصحابها: يمكنك عرضها في الفيديو، لكن لا تستخدمها كشعار لك.

---

<a id="english"></a>

## English

**montage-crew** is a free Claude Code skill: an AI assistant that edits your own short Arabic videos on your own computer (Windows or macOS) and writes the animation code for you.
It cuts silences and retakes, writes right-to-left Arabic captions, adds motion graphics, sound effects and music, and delivers a finished video.
It asks about your setup on the first run and learns from every correction you give it.

### Quick start
You only need Claude Code beforehand.
1. Put the skill in Claude Code's skills folder: open Claude Code and say `ثبّت السكل من هذا الملف: <path to the zip>` ("install the skill from this file"), or unzip it by hand. Steps are in [INSTALL.md](INSTALL.md).
2. Say `منتجلي هذا الفيديو: <path to the video>` ("edit this video for me"). Any wording with the same meaning works.

### First run
The skill first checks ffmpeg, Python 3.10+, Node.js 18+, the models, the GPU, the OS and free disk space by itself. If something is missing, it names it with its install command and installs it only after your yes.
It then asks its setup questions over 3 messages (at most 4 per message, each with a default; an empty answer or «تمام» accepts it): editor (default: none), format (9:16, 16:9 or both; default 9:16), usual footage (on camera, screen recording, or none), mode (fast or pro; default fast), voice (own, AI with your own key, or music only), dialect (default MSA), retake words, digits, brand (optional; empty = chosen per video), folders (default `~/montage-crew-work` and `~/Videos/montage-crew`; the work folder must be an ASCII path), and, only for Resolve users, LIVE mode. It shows a summary and saves after one "yes".
To change settings later, say `غيّر إعداداتي` ("change my settings"). You can also override the footage type or format for one video in the same request.

### Two ways to get the edit
1. **Final video + timeline XML (everyone).** You always get `final.mp4` (H.264, AAC 48 kHz, −14 LUFS), an `.srt`, a `.txt` transcript and a cover image. If your editor is DaVinci Resolve or Premiere Pro, you also get `project/timeline.xml` + `project/media/` with every layer on its own track. In Resolve, set the project frame rate to 30 in File › Project Settings, then File › Import › Timeline. In Premiere, use File › Import. Offline clips: right-click › Relink › choose `project/media/`.
2. **LIVE Resolve mode (optional).** The skill builds the timeline inside an open DaVinci Resolve, layer by layer, and keeps your own edits. It needs the open-source davinci-resolve-mcp bridge (MIT, third-party), which you install yourself; see [INSTALL.md](INSTALL.md#live-resolve-mode-optional). It works on Resolve free 21.1 through the Lua tab of the Console, and on Studio. Warning: while the bridge runs, programs on your computer can control Resolve, so start it only while editing and close it afterwards. If the bridge fails, the skill falls back to path 1 and tells you in one line.

### Fast vs pro
- **Fast:** Claude works alone, step by step. Shorter runs and less of your Claude plan's usage. Motion graphics on the strongest moments (about one every 6 s). A cover only if you ask.
- **Pro:** Claude leads a team of 9 `mc-*` agents working in parallel (cutter, scout, picture, audio, captions, motion ×1–3, cover, QA, writer). Richer graphics and an independent QA pass, but it uses much more of your plan.

### It learns from you
Every correction you give is logged. At the end of each video it becomes a rule in your own `rules.md`, and the skill tells you in two lines what it learned. The next video reads your rules first, so you never repeat a correction. You can edit or delete any rule; upgrades never erase them.

### Dialects
Iraqi, Gulf, Levantine, Egyptian, Maghrebi, Sudanese, Yemeni, MSA, or any other dialect you describe. You also set your retake words (default: اكشن، كت، نعيد، من جديد) and Western (123) or Arabic-Indic (١٢٣) digits.

### Your data stays local
- Video and audio are processed on your computer (cutting, Whisper transcription, background removal, rendering).
- Your profile, rules, scorecard, corrections, Python venv and models live in `~/.montage-crew/`.
- The skill sends nothing to its author: no telemetry, no update check.
- Network use: Claude Code itself sends what it reads (transcripts, video frames) to Anthropic, as in any Claude Code session; first-use downloads of models and GSAP (size shown first, SHA-256 checked after); searches for free images and icons; and, only if you chose an AI voice, the script text goes to your voice provider with your own key. The skill stores only the *name* of the environment variable that holds the key, never its value.

### Licence
Free to use and modify. Videos you make with it are yours, including for commercial use. You may not sell or redistribute the skill itself as a paid product. Third-party parts keep their own licences: see [LICENSE](LICENSE) and [NOTICES.md](NOTICES.md). Brand logos the skill downloads for your video remain their owners' trademarks.
