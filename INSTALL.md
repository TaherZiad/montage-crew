# تثبيت montage-crew

التثبيت خطوتان: تضع المهارة في مجلد مهارات Claude Code، ثم تطلب أول فيديو. المهارة تفحص الباقي بنفسها.
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

باقي البرامج (ffmpeg و Python و Node.js والنماذج) تفحصها المهارة في أول استخدام، كما في الخطوة 2.

---

## الخطوة 1: ضع المهارة في مكانها

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

---

## الخطوة 2: اطلب أول فيديو

افتح Claude Code في أي مجلد واكتب:

```text
منتجلي هذا الفيديو: <مسار الفيديو>
```

في هذا الاستخدام الأول تفعل المهارة ما يلي، بالترتيب:

1. **تفحص جهازك:** ffmpeg، و Python 3.10 أو أحدث، و Node.js 18 أو أحدث، وكرت الشاشة، والمساحة الفارغة.
2. **إذا نقص شيء** تخبرك باسمه وبأمر تثبيته، وتنتظر موافقتك قبل أن تثبّته. لا تثبّت أي شيء بدون «نعم» منك.
3. **تجهّز ما تحتاجه:** بيئة Python الخاصة بها في `~/.montage-crew/`، والنماذج (Whisper حتى 3.1 GB، ونموذج فصل الخلفية حوالي 15 MB، ومكتبة GSAP حوالي 73 KB). قبل كل تنزيل كبير تعرض حجمه وتنتظر موافقتك، وبعده تفحص البصمة SHA-256.
4. **تسألك أسئلة الإعداد** (4 أسئلة كحد أقصى في كل رسالة، ولكل سؤال جواب افتراضي). الأسئلة مشروحة في [README.md](README.md#أول-تشغيل-أسئلة-الإعداد).
5. **تبدأ المونتاج** مباشرة بعد أن تقول «نعم» للملخص.

في نفس هذا التجهيز تنسخ المهارة وكلاء الوضع الاحترافي `mc-*.md` إلى `~/.claude/agents/`. لا تلمس أي وكيل أو مهارة أخرى، وإذا وجدت ملفاً بنفس الاسم ليس منها ترفض وتخبرك.

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

ضع الإصدار الجديد مكان القديم بنفس الخطوة 1، أو اكتب في Claude Code:

```text
حدّث السكل من هذا الملف: <مسار ملف ZIP الجديد>
```

يدوياً يمكنك فك الإصدار الجديد فوق القديم مباشرة، أو حذف المجلد القديم `~/.claude/skills/montage-crew/` أولاً. الطريقتان صحيحتان. في الاستخدام التالي تلاحظ المهارة الإصدار الجديد وتعيد التجهيز وحدها (ومنه تحديث وكلاء `mc-*`).

إعدادك وقواعدك ونماذجك محفوظة في `~/.montage-crew/`، والتحديث لا يمسها.

---

## الإزالة

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

الإزالة تحذف فقط الملفات التي ثبّتتها المهارة والتي لم تتغير منذ ذلك (مجلد المهارة ووكلاء `mc-*`). الملفات التي عدّلتها بنفسك تبقى، ويطبع الأمر قائمتها. وتُبقي مجلد `~/.montage-crew/` (إعدادك وقواعدك) حتى تعود إليها لاحقاً. لا تلمس أي مهارة أو وكيل آخر.
لحذف كل شيء، بما فيه الإعداد والقواعد وبيئة Python والنماذج، أضف `--purge` إلى نهاية الأمر.

فيديوهاتك في مجلد التسليم ومجلد العمل لا تُحذف أبداً. احذفها بنفسك إن أردت.

---

## حل المشاكل

| المشكلة | الحل |
|---|---|
| Claude Code لا يتعرف على المهارة | تأكد أن الملف `~/.claude/skills/montage-crew/SKILL.md` موجود (الأمر في الخطوة 1)، وليس داخل مجلد إضافي مثل `montage-crew/montage-crew/`. ثم أغلق Claude Code وافتحه من جديد. |
| ثبّتّ برنامجاً لكن المهارة ما زالت لا تجده | أغلق Claude Code والنافذة الطرفية، وافتحهما من جديد. إذا استمر، أعد تشغيل الجهاز. |
| أمر `python` يفتح متجر مايكروسوفت | من الإعدادات: Apps › Advanced app settings › App execution aliases، أوقف `python.exe` و `python3.exe`، ثم افتح Claude Code من جديد. |
| التفريغ النصي بطيء جداً | طبيعي بدون كرت شاشة: عدة دقائق لكل دقيقة فيديو. مع كرت NVIDIA على Windows تستخدمه المهارة تلقائياً. |
| مقاطع «offline» في Resolve أو Premiere | انقر بالزر الأيمن › Relink واختر مجلد `project/media/`. |
| الفيديو في Resolve أطول أو أبطأ من الأصل | معدل إطارات المشروع كان 24. أنشئ مشروعاً جديداً، اضبطه على 30 من File › Project Settings قبل الاستيراد، ثم استورد `timeline.xml` مرة أخرى. |

---

<a id="english"></a>

## English

Installing takes two steps: put the skill in Claude Code's skills folder, then ask for your first video. The skill checks everything else itself.

**You need only Claude Code**, installed and signed in. If you don't have it: `irm https://claude.ai/install.ps1 | iex` (Windows PowerShell) or `curl -fsSL https://claude.ai/install.sh | bash` (macOS Terminal).

### Step 1: put the skill in place
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

### Step 2: ask for your first video
Say `منتجلي هذا الفيديو: <path to the video>` ("edit this video for me"). On first use the skill:
1. checks ffmpeg, Python 3.10+, Node.js 18+, the GPU and free disk space;
2. names anything missing with its install command (`winget install Gyan.FFmpeg` / `Python.Python.3.12` / `OpenJS.NodeJS.LTS` on Windows; `brew install ffmpeg` / `python@3.12` / `node` on macOS, which needs Homebrew from brew.sh) and installs it only after your yes;
3. sets up its Python environment in `~/.montage-crew/` and downloads the models (Whisper up to 3.1 GB, the matting model about 15 MB, GSAP about 73 KB), showing each size first and checking SHA-256 after;
4. asks the setup questions (see [README.md](README.md#first-run));
5. starts editing after you say yes to the summary.

The same setup step copies the pro-mode `mc-*.md` agents to `~/.claude/agents/`; it never touches other agents or skills, and refuses if a file with the same name is not its own. After installing a program you may need to restart Claude Code.

### LIVE Resolve mode (optional)
When you choose Resolve during setup, the skill offers this mode and guides you. Full details: `scripts/LIVE_RESOLVE.md` in the skill folder. In short: install DaVinci Resolve (free 21.1 or Studio); install the third-party, MIT-licensed davinci-resolve-mcp bridge (`https://github.com/samuelgursky/davinci-resolve-mcp`) with its console bridge, at the tested tag `v4.8.20` (`git checkout v4.8.20`, not `main`), keeping confirmations on; add the skill's work and output folders to the bridge's allowed folders; give the skill the bridge's Python path and folder. Each session: Workspace › Console › **Lua** tab → paste the bridge's `dofile(...)` line → expect `listening on 127.0.0.1`.
**Warning:** while the bridge runs, programs on your computer can control Resolve. Start it only while editing and stop it afterwards. If the bridge fails, the skill falls back to `final.mp4` + `timeline.xml`.

### Upgrade
Repeat step 1 with the new ZIP, or say `حدّث السكل من هذا الملف: <path to the new zip>` ("update the skill from this file"). `~/.montage-crew/` (profile, rules, models) is kept. By hand, unzip over the old folder or delete it first; both work. On the next use the skill notices the new version and re-runs its setup, which also updates the `mc-*` agents.

### Uninstall
Run it with your system Python (`py -3` or `python` on Windows, `python3` on macOS), not the skill's venv:
```powershell
py -3 "$HOME\.claude\skills\montage-crew\scripts\setup.py" uninstall
```
```bash
python3 ~/.claude/skills/montage-crew/scripts/setup.py uninstall
```
It removes only the files the skill installed that are unchanged (SHA-256 check): the skill folder and the `mc-*` agents. Files you edited are kept and listed. It keeps `~/.montage-crew/`. Add `--purge` to delete `~/.montage-crew/` too (profile, rules, venv, models). Your videos are never deleted.

### Troubleshooting
- Claude Code doesn't see the skill: check `SKILL.md` is at `~/.claude/skills/montage-crew/SKILL.md`, not one folder deeper; restart Claude Code.
- A program you installed is still "missing": close Claude Code and the terminal, open them again; reboot if needed.
- `python` opens the Microsoft Store: Settings › Apps › Advanced app settings › App execution aliases → turn off `python.exe` and `python3.exe`.
- Offline clips in Resolve/Premiere: right-click › Relink › `project/media/`.
- The edit runs long/slow in Resolve: the project was 24 fps. Set 30 fps in File › Project Settings before importing.
