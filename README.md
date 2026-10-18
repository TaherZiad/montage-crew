صُنعت بواسطة Eng. Taher — https://eng-taher.vercel.app

# montage-crew — مونتير عربي داخل Claude Code

إضافة (plugin) مجانية لـ Claude Code، أي مساعد ذكي يعمل مونتاج فيديوهاتك أنت ويكتب كود الأنيميشن نيابة عنك. تعمل على فيديوهاتك القصيرة بالعربية: تقص السكتات واللقطات المعادة، وتكتب ترجمة عربية باتجاه صحيح، وتضيف موشن غرافيك وأصواتاً، ثم تسلّمك فيديو نهائياً جاهزاً للنشر. وإذا لم يكن عندك فيديو، تصنع لك فيديو موشن كاملاً من فكرة.
تعمل على جهازك (Windows أو macOS)، وتسألك عن طريقة عملك مرة واحدة، وتحفظ هويتك البصرية، وتتعلم من ملاحظاتك ومن الأساليب التي تعلّمها لها.
For English, see [the English section](#english) below.

---

## البداية السريعة

1. ثبّتها كإضافة: اكتب هذين الأمرين داخل Claude Code:

```text
/plugin marketplace add TaherZiad/montage-crew
/plugin install montage-crew@montage-crew
```

   أو بأمر واحد في النافذة الطرفية (يحتاج Claude Code بإصدار 2.1.275 أو أحدث):

```text
claude plugin install montage-crew --marketplace TaherZiad/montage-crew
```

   ثم أغلق Claude Code وافتحه من جديد. وتوجد أيضاً نسخة ZIP من الموقع. كل الخطوات في [INSTALL.md](INSTALL.md).
2. اطلب أول فيديو:

```text
منتجلي هذا الفيديو: <مسار الفيديو>
```

أي عبارة بنفس المعنى تكفي، أو استخدم الأمر `/montage-crew:montage`. في أول مرة تفحص المهارة جهازك (ffmpeg و Python و Node.js والنماذج)، وتخبرك بما ينقص وتثبّته بعد موافقتك، ثم تسألك أسئلة الإعداد، ثم تبدأ المونتاج مباشرة.
الشيء الوحيد الذي تحتاجه مسبقاً هو Claude Code نفسه.

---

## ماذا تفعل

- **القص:** تحذف السكتات الطويلة واللقطات المعادة والكلمات التي تقولها عند إعادة اللقطة (مثل «اكشن، كت، نعيد»).
- **الترجمة على الشاشة:** كل الكلام مكتوب بعبارات قصيرة، بخطوط عربية مجانية، وباتجاه صحيح من اليمين إلى اليسار.
- **الموشن غرافيك:** أيقونات وبطاقات وأرقام وعناوين متحركة في أقوى لحظات الفيديو، ويمكن أن يظهر النص خلف المتكلم.
- **الصوت:** تنظيف الصوت، ومؤثرات صوتية (SFX) برخصة CC0، وموسيقى هادئة تنخفض تحت الكلام، وضبط مستوى الصوت النهائي على −14 LUFS.
- **الغلاف:** صورة غلاف بمقاس 9:16 وبمقاس 3:4 لشبكة الحساب.
- **الصيغ:** ريلز وتيك توك (9:16)، أو يوتيوب (16:9)، أو الاثنتان معاً.
- **نوع المادة:** تصوير أمام الكاميرا، أو تسجيل شاشة، أو الاثنان معاً، أو بدون تصوير أصلاً.
- **هويتك في كل فيديو:** شعارك وألوانك وخطوطك محفوظة مرة واحدة، وتُستخدم تلقائياً.

### فيديو من فكرة فقط

ليس عندك تصوير؟ اكتب الفكرة:

```text
ما عندي فيديو، عندي فكرة: <فكرتك>
```

فتكتب المهارة السكربت، ثم تجهّز الصوت، ثم تبني فيديو موشن غرافيك كاملاً. هذا يعمل في أي طلب، مهما كانت إجابتك عن نوع المادة في الإعداد.

---

## الأوامر

إذا ثبّتها كإضافة، عندك أربعة أوامر. وكل أمر له عبارة عادية تكفي بدلاً منه (والعبارات تعمل أيضاً في نسخة ZIP):

| الأمر | ماذا يفعل | أو قل مثلاً |
|---|---|---|
| `/montage-crew:montage` | مونتاج فيديو، أو فيديو موشن من فكرة | «منتجلي هذا الفيديو: …» · «ما عندي فيديو، عندي فكرة: …» |
| `/montage-crew:learn` | تعلّم أسلوباً جديداً من فيديو أو رابط أو موقع موشن | «تعلّم هذا الستايل: <رابط أو مسار>» · «تعلّم من هذا الفيديو» |
| `/montage-crew:brand` | حفظ هويتك البصرية أو تعديلها، أو اقتراح هوية لك | «احفظ هويتي» · «حدّث هويتي» · «اقترح لي هوية» |
| `/montage-crew:settings` | تغيير إجاباتك على أسئلة الإعداد | «غيّر إعداداتي» |

---

## أول تشغيل: أسئلة الإعداد

قبل أي سؤال، تفحص المهارة جهازك وحدها: ffmpeg و Python و Node وكرت الشاشة ونظام التشغيل والمساحة الفارغة.
إذا نقص شيء تخبرك باسمه وبأمر تثبيته، وتثبّته فقط بعد أن تقول «نعم».

بعد ذلك تسألك على 4 رسائل (4 أسئلة كحد أقصى في كل رسالة، ولكل سؤال جواب افتراضي، والرد الفارغ أو «تمام» يقبله):

| # | السؤال | الخيارات | الافتراضي |
|---|---|---|---|
| 1 | برنامج المونتاج الذي تستخدمه | DaVinci Resolve المجاني · Resolve Studio · Premiere Pro · After Effects · CapCut · Final Cut Pro · لا شيء | لا شيء (تستلم الفيديو النهائي فقط) |
| 2 | مقاس الفيديو | عمودي 9:16 · أفقي 16:9 · الاثنان معاً | 9:16 |
| 3 | هل تصوّر فيديوهاتك بنفسك؟ | أمام الكاميرا · تسجيل شاشة · الاثنان · بدون تصوير (فكرة فقط) | أمام الكاميرا |
| 4 | طريقة العمل | سريع · احترافي | سريع |
| 5 | الصوت | صوتك · صوت ذكاء اصطناعي (بمفتاحك) · موسيقى فقط | صوتك |
| 6 | اللهجة | قائمة اللهجات في الأسفل | الفصحى |
| 7 | كلمات الإعادة | الكلمات التي تقولها عند إعادة لقطة | اكشن، كت، نعيد، من جديد |
| 8 | شكل الأرقام | 123 · ١٢٣ | 123 |
| 9 | الأساليب التي تحبها | من 1 إلى 3 من 12 أسلوباً جاهزاً، وشكل الترجمة (من معرض الترجمات)، وطابع الحركة (ناعم · سريع · فخم)، وروابط صناع محتوى يعجبك أسلوبهم (تعرض عليك المهارة أن تتعلم منها بعد الحفظ) | `premium-soft`، وترجمة CAP-04 بألوان SC-02، وحركة ناعمة |
| 10 | هل عندك هوية بصرية؟ | نعم (تعطيها شعارك وألوانك وخطوطك أو رابط موقعك) · لا · «اقترح لي هوية» | لا (تُحدَّد لكل فيديو) |
| 11 | المجلدات | مجلد العمل · مجلد التسليم | `~/montage-crew-work` و `~/Videos/montage-crew` |
| 12 | وضع Resolve المباشر (فقط إذا اخترت Resolve) | لا، أعطني ملف تايملاين · نعم | لا |

مجلد العمل يجب أن يكون بأحرف إنجليزية فقط، لأن بعض الأدوات تفشل مع المسارات العربية.

في النهاية تعرض عليك ملخصاً، وتحفظه بعد أن تقول «نعم».
لتغيير أي إعداد لاحقاً، اكتب «غيّر إعداداتي» (أو `/montage-crew:settings`)، فتعود الأسئلة نفسها، وتكون إجاباتك الحالية هي الافتراضية.
يمكنك أيضاً تغيير نوع المادة أو الصيغة لفيديو واحد فقط في نفس الطلب، مثلاً: «هذا تسجيل شاشة».

---

## هويتك البصرية: تُحفظ مرة واحدة

اكتب «احفظ هويتي» (أو `/montage-crew:brand`) وأعطها ما عندك: الشعار، أو صوراً من حسابك، أو رابط موقعك، أو الألوان والخطوط بنفسك.
تنسخ المهارة الملفات إلى مجلد هويتك في `~/.montage-crew/brand/`، وتستخرج الألوان من الشعار أو الصور أو الموقع، وتعرض عليك النتيجة قبل الحفظ.
من الموقع تأخذ الألوان وأسماء الخطوط والشعار فقط. ملفات الخطوط تأتي من Google Fonts أو من ملف تعطيه أنت. استخدم هويتك أنت فقط، وليس شعار جهة أخرى.
ليس عندك هوية بعد؟ اكتب «اقترح لي هوية» فتقترح عليك ألواناً وخطوطاً تناسب محتواك.
بعدها تستخدم هويتك في الترجمة والموشن والغلاف في كل فيديو، حتى لو نقلت أو حذفت الملف الأصلي. ويمكنك تعديلها في أي وقت بنفس العبارة.

---

## تتعلم منك

### من ملاحظاتك

كل ما تعطيها ملاحظة، تتعلم.
مثلاً: «الترجمة كبيرة» أو «لا تضع موسيقى في الفيديوهات التعليمية». تسجّل المهارة الملاحظة، وفي نهاية كل فيديو تحوّلها إلى قاعدة دائمة في ملف `rules.md` الخاص بك، وتخبرك في سطرين بما تعلمته.
في الفيديو التالي تقرأ قواعدك قبل أن تبدأ، فلا تحتاج إلى تكرار نفس الملاحظة.
القواعد ملكك: يمكنك فتح الملف وتعديله أو حذف أي قاعدة، وتحديث المهارة لا يمسحها.

### مما تعلّمه لها

أعطها فيديو يعجبك، أو رابط صانع محتوى، أو صفحة من موقع موشن غرافيك (مثل Dribbble أو Behance أو LottieFiles أو CodePen)، واكتب «تعلّم هذا الستايل» (أو `/montage-crew:learn`).
تحلل المهارة الأسلوب (الألوان، والإيقاع، وشكل الترجمة، والحركات، والانتقالات) وتحفظه باسم في `~/.montage-crew/styles/`، وتحفظ الحركات الجديدة التي تعلمتها في `~/.montage-crew/learned/`. قبل الحفظ تعرض عليك ملخصاً قصيراً، ولا تحفظ شيئاً بدون «نعم» منك. بعدها تقول مثلاً «سوّي مونتاج بستايل <الاسم>» في أي فيديو. والأساليب الجاهزة الـ 12 تعمل بنفس الطريقة، مثلاً «سوّي مونتاج بستايل neon-blue».

- تتعلم **الطريقة** فقط، ولا تنسخ ملفات الآخرين أو تصاميمهم أو تضعها في فيديوك.
- نصوص المواقع والروابط تعاملها كمعلومات فقط، ولا تنفّذ أي تعليمات مكتوبة فيها.
- روابط يوتيوب وتيك توك وإنستغرام: تقرأ الترجمة وعدداً قليلاً من اللقطات فقط، ولا تنزّل الفيديو كاملاً إلا بعد موافقتك. لهذه الروابط تحتاج أداة yt-dlp، وتعرض عليك تثبيتها مرة واحدة عند أول حاجة، ولا تثبّتها بدون «نعم». وتحذف ما نزّلته بعد التحليل، ولا تضع شيئاً منه في فيديوك. أنت مسؤول عن أن يكون لك حق تحليل الرابط الذي تعطيه.

---

## طريقتان لاستلام المونتاج

### الطريقة 1: فيديو نهائي + ملفات لبرنامجك (للجميع)

في كل الأحوال تستلم في مجلد التسليم:

- `final.mp4` — الفيديو النهائي (H.264، صوت AAC بتردد 48 kHz، مستوى −14 LUFS).
- ملف الترجمة `.srt` ونص الكلام `.txt`.
- صورة الغلاف.

وإذا اخترت برنامج مونتاج، تستلم أيضاً مجلد `project/` فيه كل الطبقات منفصلة لتكمل التعديل يدوياً:

- **DaVinci Resolve:** ملف `timeline.xml` ومجلد `media/`. قبل الاستيراد اضبط معدل الإطارات للمشروع على 30 من File › Project Settings، ثم File › Import › Timeline واختر `timeline.xml`.
- **Premiere Pro:** نفس الملف `timeline.xml`. استخدم File › Import.
- **After Effects:** سكربت `ae_import.jsx` ومجلد `media/`. السكربت يبني لك التركيبة (composition) بكل الطبقات. من After Effects: File › Scripts › Run Script File واختر الملف. لا تحتاج إلى تفعيل خيار «Allow Scripts to Write Files and Access Network».
- **CapCut و Final Cut Pro:** الفيديو النهائي، ومجلد `project/layers/` فيه الطبقات الشفافة (الترجمة والموشن) مرقّمة، وملف `order.txt` يشرح ترتيبها فوق الفيديو.
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

وكلاء الوضع الاحترافي (في الإضافة يظهر اسم كل وكيل هكذا: `montage-crew:mc-cutter`):

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

---

## بياناتك تبقى على جهازك

- **ملفات الفيديو والصوت تُعالج على جهازك:** القص والتفريغ النصي (Whisper) وفصل المتكلم عن الخلفية والتصيير كلها محلية.
- **بياناتك في مجلد واحد على جهازك، خارج مجلد الإضافة:** `~/.montage-crew/` (أو المجلد الذي تحدده بمتغير البيئة `MONTAGE_CREW_HOME`). لهذا لا يمسحها أي تحديث.
  - `profile.json` — إجاباتك على أسئلة الإعداد.
  - `brand/` — هويتك البصرية (الشعار والخطوط و `brand.json`).
  - `styles/` و `learned/` — الأساليب والحركات التي علّمتها لها.
  - `rules.md` و `scorecard.md` و `corrections/` — ما تعلمته المهارة من ملاحظاتك.
  - `venv/` و `models/` و `vendor/` — بيئة Python والنماذج والمكتبات التي تُنزَّل أول مرة.
- **المهارة لا ترسل أي بيانات إلى صاحبها:** لا تتبّع ولا فحص تحديثات.
- **ما يخرج إلى الإنترنت:**
  - Claude Code نفسه يرسل إلى Anthropic النصوص والصور التي يقرؤها أثناء العمل (التفريغ النصي، لقطات من الفيديو)، كأي استخدام عادي لـ Claude Code.
  - تنزيل النماذج والملفات في أول استخدام (Whisper من Hugging Face، ونموذج فصل الخلفية من GitHub، ومكتبة GSAP من jsDelivr)، مع عرض الحجم قبل التنزيل وفحص البصمة (SHA-256) بعده.
  - البحث عن صور وأيقونات مجانية لفيديوك.
  - فتح الروابط التي تعطيها لتتعلم منها، وموقعك إذا أعطيته لاستخراج هويتك، و Google Fonts لتنزيل الخطوط.
  - إذا اخترت صوت ذكاء اصطناعي: نص السكربت يذهب إلى مزوّد الصوت بمفتاحك أنت. المهارة تسألك عن **اسم** متغير البيئة الذي يحمل المفتاح فقط، ولا تكتب قيمة المفتاح على القرص أبداً.

---

## محتويات الحزمة

| المسار | المحتوى |
|---|---|
| `README.md` | هذا الملف |
| `INSTALL.md` | خطوات التثبيت والتحديث والإزالة |
| `LICENSE` | الرخصة |
| `NOTICES.md` | رخص المكونات الخارجية (الخطوط، المؤثرات الصوتية، القوالب، المراجع) |
| `CHANGELOG.md` | سجل الإصدارات |
| `.claude-plugin/` | ملفات تعريف الإضافة (في نسخة الإضافة فقط) |
| `commands/` | الأوامر الأربعة `/montage-crew:…` (في نسخة الإضافة فقط) |
| `skills/montage-crew/` | المهارة نفسها: `SKILL.md` و `onboarding.md` و `references/` و `scripts/` و `assets/` و `templates/` و `styles/`. في نسخة ZIP هذا هو المجلد الرئيسي. |
| `agents/` | وكلاء الوضع الاحترافي `mc-*` |

---

## الرخصة

- مجانية للاستخدام والتعديل.
- الفيديوهات التي تصنعها بها ملكك، ويمكنك استخدامها تجارياً (إعلانات، عملاء، قنوات ربحية).
- لا يجوز بيع الإضافة نفسها أو إعادة نشرها كمنتج مدفوع.
- المكونات الخارجية (الخطوط، المؤثرات الصوتية، القوالب، المراجع) تبقى برخصها الأصلية. التفاصيل في [LICENSE](LICENSE) و [NOTICES.md](NOTICES.md).
- الشعارات والعلامات التجارية التي تنزّلها المهارة لفيديوك (مثل شعارات التطبيقات) تبقى ملكاً لأصحابها: يمكنك عرضها في الفيديو، لكن لا تستخدمها كشعار لك.

---

<a id="english"></a>

## English

**montage-crew** is a free Claude Code plugin: an AI assistant that edits your own short Arabic videos on your own computer (Windows or macOS) and writes the animation code for you.
It cuts silences and retakes, writes right-to-left Arabic captions, adds motion graphics, sound effects and music, and delivers a finished video. No footage? It makes a full motion-graphics video from an idea.
It asks about your setup once, keeps your brand kit, and learns from your corrections and from the styles you teach it.

### Quick start
You only need Claude Code beforehand.
1. Install it as a plugin. Inside Claude Code:
   ```text
   /plugin marketplace add TaherZiad/montage-crew
   /plugin install montage-crew@montage-crew
   ```
   Or in one command from a terminal (needs Claude Code 2.1.275 or newer):
   ```text
   claude plugin install montage-crew --marketplace TaherZiad/montage-crew
   ```
   Then restart Claude Code. A ZIP from the website is also available. All steps are in [INSTALL.md](INSTALL.md).
2. Say `منتجلي هذا الفيديو: <path to the video>` ("edit this video for me") or use `/montage-crew:montage`. Any wording with the same meaning works.

### Commands
With the plugin you get four commands. Each has a plain phrase that works the same (phrases also work in the ZIP version):
- `/montage-crew:montage` — edit a video, or make a motion video from an idea. Or say «منتجلي هذا الفيديو: …» / «ما عندي فيديو، عندي فكرة: …» ("I have no video, I have an idea: …").
- `/montage-crew:learn` — learn a new style from a video, a link or a motion-design site. Or say «تعلّم هذا الستايل: <link or path>» ("learn this style") or «تعلّم من هذا الفيديو» ("learn from this video").
- `/montage-crew:brand` — save or edit your brand kit, or get one suggested. Or say «احفظ هويتي» ("save my brand") or «اقترح لي هوية» ("suggest a brand for me").
- `/montage-crew:settings` — change your setup answers. Or say «غيّر إعداداتي» ("change my settings").

### First run
The skill first checks ffmpeg, Python 3.10+, Node.js 18+, the models, the GPU, the OS and free disk space by itself. If something is missing, it names it with its install command and installs it only after your yes.
It then asks its setup questions once, over 4 messages (at most 4 per message, each with a default; an empty answer or «تمام» accepts it): (1) editor (DaVinci Resolve free or Studio, Premiere Pro, After Effects, CapCut, Final Cut Pro or none; default none), format (9:16, 16:9 or both; default 9:16), whether you film your videos yourself (on camera, screen recording, both, or no footage / idea only; default on camera), mode (fast or pro; default fast); (2) voice (own, AI with your own key, or music only), dialect (default MSA), retake words, digits; (3) the styles you like: 1–3 of the 12 built-in styles (default `premium-soft`), caption style (default CAP-04 with colour scheme SC-02), motion feel (smooth, snappy or premium; default smooth) and links to creators you like, which it offers to learn from after saving; (4) your brand (yes, no, or «اقترح لي هوية» "suggest one for me"; default no), folders (default `~/montage-crew-work` and `~/Videos/montage-crew`; the work folder must be an ASCII path), and, only for Resolve users, LIVE mode. It shows a summary and saves after one "yes". You can override the footage type or format for one video in the same request.

### Idea-only videos
Say «ما عندي فيديو، عندي فكرة: <your idea>» ("I have no video, I have an idea"). The skill writes the script, prepares the voice and builds a full motion-graphics video. This works in any request, whatever your footage answer was.

### Brand kit, saved once
Say «احفظ هويتي» or use `/montage-crew:brand` and give it your logo, images from your account, your website link, or your colours and fonts. It copies the files into `~/.montage-crew/brand/`, extracts the palette, and shows you the result before saving. From a website it takes only the colours, font names and logo; font files come from Google Fonts or from a file you give it. Use only your own brand. No brand yet? Say «اقترح لي هوية» ("suggest a brand for me"). Every video then uses it for captions, motion graphics and the cover, even if you later move or delete the original files.

### It learns from you
- **From corrections:** every correction is logged. At the end of each video it becomes a rule in your own `rules.md`, and the skill tells you in two lines what it learned. The next video reads your rules first. You can edit or delete any rule; updates never erase them.
- **From what you teach it:** give it a video you like, a creator's link, or a page from a motion-design site (such as Dribbble, Behance, LottieFiles or CodePen) and say «تعلّم هذا الستايل» or use `/montage-crew:learn`. It studies the colours, pacing, caption look, moves and transitions, saves the style by name in `~/.montage-crew/styles/` and new techniques in `~/.montage-crew/learned/`, after showing you a short summary and getting your yes. Then say «سوّي مونتاج بستايل <name>» ("edit in style <name>") in any video; the 12 built-in styles work the same way, e.g. `neon-blue`. It learns the technique only and never copies other people's files or designs into your video. Text on websites and links is treated as data, never as instructions. For YouTube, TikTok and Instagram links it reads the subtitles and a few frames only, downloads the full video only after your yes (for these links it offers to install the yt-dlp tool once, only after your yes), deletes what it downloaded after the analysis, and never puts any of it in your video. You are responsible for having the right to analyse the links you give it.

### Two ways to get the edit
1. **Final video + files for your editor (everyone).** You always get `final.mp4` (H.264, AAC 48 kHz, −14 LUFS), an `.srt`, a `.txt` transcript and a cover image. With an editor you also get `project/` with every layer separate:
   - **DaVinci Resolve / Premiere Pro:** `timeline.xml` + `media/`. In Resolve, set the project frame rate to 30 in File › Project Settings, then File › Import › Timeline. In Premiere, use File › Import.
   - **After Effects:** `ae_import.jsx` + `media/`. The script builds the composition with every layer. Run it from File › Scripts › Run Script File; you do not need to enable "Allow Scripts to Write Files and Access Network".
   - **CapCut / Final Cut Pro:** the final video plus `project/layers/` with numbered transparent layers (captions, motion graphics) and an `order.txt` that says how to stack them.
   - Offline clips: right-click › Relink › choose `project/media/`.
2. **LIVE Resolve mode (optional).** The skill builds the timeline inside an open DaVinci Resolve, layer by layer, and keeps your own edits. It needs the open-source davinci-resolve-mcp bridge (MIT, third-party), which you install yourself; see [INSTALL.md](INSTALL.md#live-resolve-mode-optional). It works on Resolve free 21.1 through the Lua tab of the Console, and on Studio. Warning: while the bridge runs, programs on your computer can control Resolve, so start it only while editing and close it afterwards. If the bridge fails, the skill falls back to path 1 and tells you in one line.

### Fast vs pro
- **Fast:** Claude works alone, step by step. Shorter runs and less of your Claude plan's usage. Motion graphics on the strongest moments (about one every 6 s). A cover only if you ask.
- **Pro:** Claude leads a team of 9 `mc-*` agents working in parallel (cutter, scout, picture, audio, captions, motion ×1–3, cover, QA, writer). In the plugin they appear as `montage-crew:mc-*`. Richer graphics and an independent QA pass, but it uses much more of your plan.

### Dialects
Iraqi, Gulf, Levantine, Egyptian, Maghrebi, Sudanese, Yemeni, MSA, or any other dialect you describe. You also set your retake words (default: اكشن، كت، نعيد، من جديد) and Western (123) or Arabic-Indic (١٢٣) digits.

### Your data stays local
- Video and audio are processed on your computer (cutting, Whisper transcription, background removal, rendering).
- Your data lives in one folder outside the plugin, `~/.montage-crew/` (or the folder set by the `MONTAGE_CREW_HOME` environment variable), so updates never erase it: `profile.json`, `brand/`, `styles/`, `learned/`, `rules.md`, `scorecard.md`, `corrections/`, the Python `venv/`, `models/` and `vendor/`.
- The skill sends nothing to its author: no telemetry, no update check.
- Network use: Claude Code itself sends what it reads (transcripts, video frames) to Anthropic, as in any Claude Code session; first-use downloads of models and GSAP (size shown first, SHA-256 checked after); searches for free images and icons; the links you give it to learn from, your own website if you give it for your brand, and Google Fonts for font files; and, only if you chose an AI voice, the script text goes to your voice provider with your own key. The skill stores only the *name* of the environment variable that holds the key, never its value.

### Licence
Free to use and modify. Videos you make with it are yours, including for commercial use. You may not sell or redistribute the plugin itself as a paid product. Third-party parts keep their own licences: see [LICENSE](LICENSE) and [NOTICES.md](NOTICES.md). Brand logos the skill downloads for your video remain their owners' trademarks.
