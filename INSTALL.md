# تثبيت montage-crew

طريقتان للتثبيت: **كإضافة (plugin)** من داخل Claude Code، وهي الأسهل وتتحدث بأمر واحد، أو **كملف ZIP** من الموقع. اختر واحدة فقط.
بعد التثبيت اطلب أول فيديو، والمهارة تفحص الباقي بنفسها.
For English, see [the English section](#english) below.

## ما تحتاجه قبل البدء

**Claude Code فقط**، مثبت ويعمل باشتراك فعّال. إذا لم يكن مثبتاً، استخدم الأمر الرسمي:

على Windows (في PowerShell):

```powershell
irm https://claude.ai/install.ps1 | iex
```

على macOS (في Terminal):

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

باقي البرامج (ffmpeg و Python و Node.js والنماذج) تفحصها المهارة في أول استخدام، كما في [الخطوة 2](#الخطوة-2-اطلب-أول-فيديو).

---

<a id="plugin"></a>

## الخطوة 1، الطريقة 1: إضافة (plugin) — موصى بها

<!-- مستودع الإضافة: TaherZiad/montage-crew — إذا تغيّر اسم المستودع، غيّره في هذا القسم فقط. -->

افتح Claude Code واكتب هذين الأمرين، واحداً بعد الآخر:

```text
/plugin marketplace add TaherZiad/montage-crew
/plugin install montage-crew@montage-crew
```

أو بأمر واحد يضيف المصدر ويثبّت الإضافة معاً (في النافذة الطرفية، خارج Claude Code):

```text
claude plugin install montage-crew --marketplace TaherZiad/montage-crew
```

ثم أغلق Claude Code وافتحه من جديد. اكتب `/montage-crew:` فتظهر لك أوامر الإضافة الأربعة (مشروحة في [README.md](README.md#الأوامر)).

الإضافة تجلب معها وكلاء الوضع الاحترافي باسم `montage-crew:mc-*`، فلا تنسخ المهارة أي ملف إلى `~/.claude/agents/`.

---

## الخطوة 1، الطريقة 2: ملف ZIP من الموقع

نزّل `montage-crew.zip` من https://eng-taher.vercel.app/skills/montage-crew

### الطريقة الأسهل: اطلبها من Claude Code

افتح Claude Code واكتب، مع مسار ملف ZIP الذي نزّلته:

```text
ثبّت السكل من هذا الملف: <مسار ملف montage-crew.zip>
```

لنسخ مسار الملف: على Windows انقر بالزر الأيمن على الملف › **Copy as path**. على macOS اسحب الملف إلى نافذة Claude Code.

### أو يدوياً

فك ضغط الملف بحيث يصبح ملف `SKILL.md` في هذا المكان بالضبط:

| النظام | المكان |
|---|---|
| Windows | `~\.claude\skills\montage-crew\SKILL.md` |
| macOS | `~/.claude/skills/montage-crew/SKILL.md` |

الرمز `~` يعني مجلد المستخدم الخاص بك.
على Windows (في PowerShell، من المجلد الذي فيه ملف ZIP):

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Expand-Archive -Path .\montage-crew.zip -DestinationPath "$HOME\.claude\skills"
Test-Path "$HOME\.claude\skills\montage-crew\SKILL.md"
```

على macOS (في Terminal، من المجلد الذي فيه ملف ZIP):

```bash
mkdir -p ~/.claude/skills
unzip montage-crew.zip -d ~/.claude/skills
test -f ~/.claude/skills/montage-crew/SKILL.md && echo ok
```

آخر أمر يجب أن يطبع `True` على Windows أو `ok` على macOS.
لا تغيّر اسم المجلد: يجب أن يبقى `montage-crew` بالضبط، وإلا ترفض المهارة إكمال التجهيز.

بعد ذلك أغلق Claude Code وافتحه من جديد حتى يرى المهارة.

في نسخة ZIP لا توجد أوامر `/montage-crew:…`، لكن كل شيء يعمل بالعبارات العادية (مثل «منتجلي هذا الفيديو» و «احفظ هويتي»). وفي أول تجهيز تنسخ المهارة وكلاء الوضع الاحترافي `mc-*.md` إلى `~/.claude/agents/`. لا تلمس أي وكيل أو مهارة أخرى، وإذا وجدت ملفاً بنفس الاسم ليس منها ترفض وتخبرك.

---

## الخطوة 2: اطلب أول فيديو

افتح Claude Code في أي مجلد واكتب:

```text
منتجلي هذا الفيديو: <مسار الفيديو>
```

أو، إذا ثبّتها كإضافة، `/montage-crew:montage <مسار الفيديو>`. وإذا لم يكن عندك فيديو، اكتب الفكرة فقط: «ما عندي فيديو، عندي فكرة: …».

في هذا الاستخدام الأول تفعل المهارة ما يلي، بالترتيب:

1. **تفحص جهازك:** ffmpeg، و Python 3.10 أو أحدث، و Node.js 18 أو أحدث، وكرت الشاشة، والمساحة الفارغة.
2. **إذا نقص شيء** تخبرك باسمه وبأمر تثبيته، وتنتظر موافقتك قبل أن تثبّته. لا تثبّت أي شيء بدون «نعم» منك.
3. **تجهّز ما تحتاجه:** بيئة Python الخاصة بها في `~/.montage-crew/`، والنماذج (Whisper حتى 3.1 GB، ونموذج فصل الخلفية حوالي 15 MB، ومكتبة GSAP حوالي 73 KB). قبل كل تنزيل كبير تعرض حجمه وتنتظر موافقتك، وبعده تفحص البصمة SHA-256.
4. **تسألك أسئلة الإعداد** مرة واحدة فقط (4 أسئلة كحد أقصى في كل رسالة، ولكل سؤال جواب افتراضي):
   - برنامج المونتاج: لا شيء، أو DaVinci Resolve، أو Premiere Pro، أو After Effects، أو CapCut، أو Final Cut Pro.
   - مقاس الفيديو، وهل تصوّر فيديوهاتك بنفسك (أمام الكاميرا، أو تسجيل شاشة، أو الاثنان، أو بدون تصوير)، وطريقة العمل (سريع أو احترافي).
   - صوتك، أو صوت ذكاء اصطناعي، أو موسيقى فقط، ثم اللهجة وكلمات الإعادة وشكل الأرقام.
   - الأساليب التي تحبها: أساليب جاهزة، وشكل الترجمة، وطابع الحركة، وروابط صناع محتوى يعجبك أسلوبهم.
   - هويتك البصرية (الشعار، والألوان، والخطوط، أو رابط موقعك)، أو «اقترح لي هوية» — اختياري، وتُحفظ مرة واحدة. ثم المجلدات.

   القائمة الكاملة مع الافتراضيات في [README.md](README.md#أول-تشغيل-أسئلة-الإعداد).
5. **تبدأ المونتاج** مباشرة بعد أن تقول «نعم» للملخص.

الأوامر التي ستقترحها المهارة إذا نقص شيء (للعلم فقط، لا تحتاج إلى تشغيلها مسبقاً):

| البرنامج | Windows | macOS |
|---|---|---|
| ffmpeg | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |
| Python 3.10+ | `winget install Python.Python.3.12` | `brew install python@3.12` |
| Node.js 18+ | `winget install OpenJS.NodeJS.LTS` | `brew install node` |

على macOS تحتاج أوامر `brew` إلى Homebrew (من موقع brew.sh). بعد تثبيت أي برنامج قد تحتاج إلى إغلاق Claude Code وفتحه من جديد.

---

## وضع Resolve المباشر (اختياري)

في هذا الوضع تبني المهارة التايملاين داخل DaVinci Resolve وهو مفتوح أمامك. هو اختياري تماماً: بدونه تستلم `final.mp4` و `timeline.xml` كالمعتاد.
عندما تختار Resolve في أسئلة الإعداد، تسألك المهارة إن كنت تريد هذا الوضع وترشدك خطوة بخطوة. الشرح الكامل في `scripts/LIVE_RESOLVE.md` داخل مجلد المهارة.

باختصار:

1. ثبّت DaVinci Resolve (المجاني 21.1 أو Studio).
2. ثبّت بنفسك الجسر مفتوح المصدر **davinci-resolve-mcp** مع جزء **console bridge**، باتباع ملف README الخاص به:
   `https://github.com/samuelgursky/davinci-resolve-mcp`
   استخدم الإصدار الذي جرّبناه، `v4.8.20`، وليس آخر نسخة من فرع `main`. بعد `git clone` شغّل:

   ```text
   git checkout v4.8.20
   ```

   هذا الجسر برنامج خارجي برخصة MIT وليس من montage-crew. بعض أدواته تشغّل أوامر أو تحذف مجلدات، فأبقِ طلبات التأكيد مفعّلة.
3. في إعدادات الجسر، أضف مجلد العمل ومجلد التسليم إلى المجلدات المسموحة (الافتراضي `~/montage-crew-work` و `~/Videos/montage-crew`).
4. أعطِ المهارة مسار برنامج Python الخاص بالجسر ومسار مجلده، عندما تسألك أو لاحقاً بقول «غيّر إعداداتي».
5. في كل جلسة: افتح Resolve ومشروعاً، ثم Workspace › Console › تبويب **Lua**، والصق سطر `dofile(...)` من README الجسر، ثم Enter. يجب أن يظهر سطر فيه `listening on 127.0.0.1`.

> **تنبيه:** الجسر يسمح للبرامج على جهازك بالتحكم في دافنشي — شغّله فقط وقت المونتاج وأطفئه بعده (أغلق Resolve، أو أوقف الجسر كما يشرح README الجسر).

إذا فشل الجسر في أي لحظة، تكمل المهارة بالطريقة العادية (`final.mp4` + `timeline.xml`) وتخبرك.

---

## التحديث

**الإضافة:** اكتب في Claude Code:

```text
/plugin marketplace update montage-crew
/plugin update montage-crew@montage-crew
```

ثم أغلق Claude Code وافتحه من جديد.

**ملف ZIP:** ضع الإصدار الجديد مكان القديم بنفس الخطوة 1، أو اكتب في Claude Code:

```text
حدّث السكل من هذا الملف: <مسار ملف ZIP الجديد>
```

يدوياً يمكنك فك الإصدار الجديد فوق القديم مباشرة، أو حذف المجلد القديم `~/.claude/skills/montage-crew/` أولاً. الطريقتان صحيحتان. في الاستخدام التالي تلاحظ المهارة الإصدار الجديد وتعيد التجهيز وحدها (ومنه تحديث وكلاء `mc-*`).

في الحالتين، بياناتك محفوظة خارج مجلد المهارة، في `~/.montage-crew/`: إعدادك، وقواعدك، وهويتك البصرية، والأساليب التي علّمتها لها، والنماذج. التحديث لا يمسها أبداً. إعدادات الإصدار 1 تُنقل إلى صيغة الإصدار 2 تلقائياً مع الإبقاء على كل إجاباتك، وتُحفظ نسخة من الملف القديم باسم `profile.v1.json`. بعدها تسألك المهارة الأسئلة الجديدة فقط (الأساليب التي تحبها).

---

## الإزالة

### إذا ثبّتها كإضافة

```text
/plugin uninstall montage-crew@montage-crew
```

ولإزالة مصدر الإضافة أيضاً: `/plugin marketplace remove montage-crew`.

### إذا ثبّتها كملف ZIP

شغّل أمر الإزالة بـ Python الموجود على جهازك (وليس بيئة Python الخاصة بالمهارة).
على Windows (في PowerShell):

```powershell
py -3 "$HOME\.claude\skills\montage-crew\scripts\setup.py" uninstall
```

على macOS (في Terminal):

```bash
python3 ~/.claude/skills/montage-crew/scripts/setup.py uninstall
```

إذا لم يعمل `py -3` على Windows، استخدم `python` بدلاً منه.

الإزالة تحذف فقط الملفات التي ثبّتتها المهارة والتي لم تتغير منذ ذلك (مجلد المهارة ووكلاء `mc-*`). الملفات التي عدّلتها بنفسك تبقى، ويطبع الأمر قائمتها. لا تلمس أي مهارة أو وكيل آخر.
أضف `--purge` إلى نهاية الأمر لحذف `~/.montage-crew/` أيضاً.

### بياناتك بعد الإزالة

في الطريقتين يبقى مجلد `~/.montage-crew/` (إعدادك، وقواعدك، وهويتك، وأساليبك، وبيئة Python، والنماذج)، حتى تعود إليه لاحقاً. لحذفه بنفسك:

على Windows (في PowerShell):

```powershell
Remove-Item -Recurse -Force "$HOME\.montage-crew"
```

على macOS (في Terminal):

```bash
rm -rf ~/.montage-crew
```

إذا غيّرت مكان البيانات بمتغير البيئة `MONTAGE_CREW_HOME`، فاحذف ذلك المجلد بدلاً منه.
فيديوهاتك في مجلد التسليم ومجلد العمل لا تُحذف أبداً. احذفها بنفسك إن أردت.

---

## حل المشاكل

| المشكلة | الحل |
|---|---|
| أوامر `/montage-crew:…` لا تظهر بعد تثبيت الإضافة | أغلق Claude Code وافتحه من جديد. ثم اكتب `/plugin` وتأكد أن montage-crew مثبتة ومفعّلة. |
| `/plugin update` يقول إنه لا يوجد تحديث | شغّل أولاً `/plugin marketplace update montage-crew` ثم أعد أمر التحديث. |
| ثبّتها بالطريقتين معاً | أزل واحدة منهما (الأفضل أن تُبقي الإضافة). بياناتك في `~/.montage-crew/` لا تتأثر. |
| Claude Code لا يتعرف على المهارة (نسخة ZIP) | تأكد أن الملف `~/.claude/skills/montage-crew/SKILL.md` موجود، وليس داخل مجلد إضافي مثل `montage-crew/montage-crew/`. ثم أغلق Claude Code وافتحه من جديد. |
| ثبّتّ برنامجاً لكن المهارة ما زالت لا تجده | أغلق Claude Code والنافذة الطرفية، وافتحهما من جديد. إذا استمر، أعد تشغيل الجهاز. |
| أمر `python` يفتح متجر مايكروسوفت | من الإعدادات: Apps › Advanced app settings › App execution aliases، أوقف `python.exe` و `python3.exe`، ثم افتح Claude Code من جديد. |
| التفريغ النصي بطيء جداً | طبيعي بدون كرت شاشة: عدة دقائق لكل دقيقة فيديو. مع كرت NVIDIA على Windows تستخدمه المهارة تلقائياً. |
| مقاطع «offline» في Resolve أو Premiere | انقر بالزر الأيمن › Relink واختر مجلد `project/media/`. |
| الفيديو في Resolve أطول أو أبطأ من الأصل | معدل إطارات المشروع كان 24. أنشئ مشروعاً جديداً، اضبطه على 30 من File › Project Settings قبل الاستيراد، ثم استورد `timeline.xml` مرة أخرى. |

---

<a id="english"></a>

## English

There are two ways to install: as a **plugin** inside Claude Code (easiest, updates with one command), or as a **ZIP** from the website. Pick one. Then ask for your first video; the skill checks everything else itself.

**You need only Claude Code**, installed and signed in. If you don't have it: `irm https://claude.ai/install.ps1 | iex` (Windows PowerShell) or `curl -fsSL https://claude.ai/install.sh | bash` (macOS Terminal).

### Step 1, way 1: plugin (recommended)
Run the commands from [the Arabic plugin section](#plugin) above: `/plugin marketplace add …` then `/plugin install montage-crew@montage-crew` inside Claude Code, or the one-step `claude plugin install montage-crew --marketplace …` in a terminal. Restart Claude Code; type `/montage-crew:` to see the four commands. The plugin ships the pro-mode agents as `montage-crew:mc-*`, so nothing is copied to `~/.claude/agents/`.

### Step 1, way 2: ZIP from the website
Download `montage-crew.zip` from https://eng-taher.vercel.app/skills/montage-crew.
- **Easiest:** open Claude Code and say `ثبّت السكل من هذا الملف: <path to montage-crew.zip>` ("install the skill from this file").
- **By hand:** unzip so that `SKILL.md` ends up at `~\.claude\skills\montage-crew\SKILL.md` (Windows) or `~/.claude/skills/montage-crew/SKILL.md` (macOS).
  ```powershell
  New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
  Expand-Archive -Path .\montage-crew.zip -DestinationPath "$HOME\.claude\skills"
  Test-Path "$HOME\.claude\skills\montage-crew\SKILL.md"
  ```
  ```bash
  mkdir -p ~/.claude/skills
  unzip montage-crew.zip -d ~/.claude/skills
  test -f ~/.claude/skills/montage-crew/SKILL.md && echo ok
  ```
  The last command must print `True` (Windows) or `ok` (macOS). Keep the folder name exactly `montage-crew`; with any other name the skill refuses to finish setup.
- Restart Claude Code.

The ZIP has no `/montage-crew:…` commands; everything works with plain phrases instead. Its first setup copies the pro-mode `mc-*.md` agents to `~/.claude/agents/`; it never touches other agents or skills, and refuses if a file with the same name is not its own.

### Step 2: ask for your first video
Say `منتجلي هذا الفيديو: <path to the video>` ("edit this video for me"), or `/montage-crew:montage <path>` with the plugin. No video? Just describe the idea. On first use the skill:
1. checks ffmpeg, Python 3.10+, Node.js 18+, the GPU and free disk space;
2. names anything missing with its install command (`winget install Gyan.FFmpeg` / `Python.Python.3.12` / `OpenJS.NodeJS.LTS` on Windows; `brew install ffmpeg` / `python@3.12` / `node` on macOS, which needs Homebrew from brew.sh) and installs it only after your yes;
3. sets up its Python environment in `~/.montage-crew/` and downloads the models (Whisper up to 3.1 GB, the matting model about 15 MB, GSAP about 73 KB), showing each size first and checking SHA-256 after;
4. asks its setup questions once: your editor (none, DaVinci Resolve, Premiere Pro, After Effects, CapCut or Final Cut Pro), format, whether you film yourself, mode, your voice, dialect and retake words, digits, the styles you like, your brand (optional, saved once) and folders (full list in [README.md](README.md#first-run));
5. starts editing after you say yes to the summary.

After installing a program you may need to restart Claude Code.

### LIVE Resolve mode (optional)
When you choose Resolve during setup, the skill offers this mode and guides you. Full details: `scripts/LIVE_RESOLVE.md` in the skill folder. In short: install DaVinci Resolve (free 21.1 or Studio); install the third-party, MIT-licensed davinci-resolve-mcp bridge (`https://github.com/samuelgursky/davinci-resolve-mcp`) with its console bridge, at the tested tag `v4.8.20` (`git checkout v4.8.20`, not `main`), keeping confirmations on; add the skill's work and output folders to the bridge's allowed folders; give the skill the bridge's Python path and folder. Each session: Workspace › Console › **Lua** tab → paste the bridge's `dofile(...)` line → expect `listening on 127.0.0.1`.
**Warning:** while the bridge runs, programs on your computer can control Resolve. Start it only while editing and stop it afterwards. If the bridge fails, the skill falls back to `final.mp4` + `timeline.xml`.

### Update
- **Plugin:** `/plugin marketplace update montage-crew`, then `/plugin update montage-crew@montage-crew`, then restart Claude Code.
- **ZIP:** repeat step 1 with the new ZIP, or say `حدّث السكل من هذا الملف: <path to the new zip>` ("update the skill from this file"). By hand, unzip over the old folder or delete it first; both work. On the next use the skill notices the new version and re-runs its setup, which also updates the `mc-*` agents.

Your data lives outside the skill folder, in `~/.montage-crew/` (profile, rules, brand kit, learned styles, models), so updates never touch it. A v1 profile is migrated to v2 automatically, keeping all your answers (the old file is kept as `profile.v1.json`); the skill then asks only the new questions (the styles you like).

### Uninstall
- **Plugin:** `/plugin uninstall montage-crew@montage-crew` (and `/plugin marketplace remove montage-crew` to drop the source).
- **ZIP:** run with your system Python (`py -3` or `python` on Windows, `python3` on macOS), not the skill's venv:
  ```powershell
  py -3 "$HOME\.claude\skills\montage-crew\scripts\setup.py" uninstall
  ```
  ```bash
  python3 ~/.claude/skills/montage-crew/scripts/setup.py uninstall
  ```
  It removes only the files the skill installed that are unchanged (SHA-256 check): the skill folder and the `mc-*` agents. Files you edited are kept and listed. Add `--purge` to delete `~/.montage-crew/` too.

Both ways keep `~/.montage-crew/` (profile, rules, brand kit, styles, venv, models) so you can come back later. To delete it yourself: `Remove-Item -Recurse -Force "$HOME\.montage-crew"` (Windows) or `rm -rf ~/.montage-crew` (macOS); if you moved it with `MONTAGE_CREW_HOME`, delete that folder instead. Your videos are never deleted.

### Troubleshooting
- `/montage-crew:…` commands don't show after installing the plugin: restart Claude Code, then check under `/plugin` that montage-crew is installed and enabled.
- `/plugin update` says nothing to update: run `/plugin marketplace update montage-crew` first.
- Installed both ways: remove one (keep the plugin). `~/.montage-crew/` is not affected.
- Claude Code doesn't see the ZIP skill: check `SKILL.md` is at `~/.claude/skills/montage-crew/SKILL.md`, not one folder deeper; restart Claude Code.
- A program you installed is still "missing": close Claude Code and the terminal, open them again; reboot if needed.
- `python` opens the Microsoft Store: Settings › Apps › Advanced app settings › App execution aliases → turn off `python.exe` and `python3.exe`.
- Offline clips in Resolve/Premiere: right-click › Relink › `project/media/`.
- The edit runs long/slow in Resolve: the project was 24 fps. Set 30 fps in File › Project Settings before importing.
