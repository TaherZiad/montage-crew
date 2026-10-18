"""Script-level tools on words.json (transcribe.py output): retakes, set words, hook, subtitles, sync.
Ported from video-ad-editor v3.8 (MIT, github.com/majedphotos/video-ad-editor, see NOTICES.md), generalised to
any Arabic dialect: the dialect, the set words and the digits come from the user's profile (mc_profile.py).

  python story.py show  words.json              numbered sentences (source times) + RETAKES (repeated sentence -> the 1st is the mistake)
                                                + set words + a ready --drop string for jumpcut.py
  python story.py drop  words.json 3 7 12       --drop ranges for those sentences (feed to jumpcut.py --drop)
  python story.py hooks words_cut.json          strongest lines for a written hook (number/contrast/question/story/curiosity/command)
                                                + every number the speaker actually said
  python story.py check words_cut.json "hook 1" ["hook 2" ...]   hook rules: 3-8 words, >=1 pull device, the profile's dialect,
                                                numbers only from the speech, not the first line  (exit 1 on any ❌)
  python story.py srt   words_cut.json out/name  -> name.srt (YouTube/LinkedIn) + name.txt (full speech for the post caption)
  python story.py sync  words_cut.json final_words.json   sentence starts in the render vs plan (transcribe the final with
                                                --model small first); ✅ when max drift < 0.1 s  (exit 1 otherwise)
  python story.py --selftest
Options: --dialect <name>  --set-words "w1,w2,phrase three"  --digits western|arabic_indic   (override the profile)
"""
import difflib, json, pathlib, re, statistics, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mc_profile  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HIND = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
PUNCT = "…؟?!.,،:؛«»\"'*|-"
END = tuple(".؟?!…")
GAP = 0.6  # s of silence that also ends a sentence


def norm(w):
    w = w.translate(HIND).strip(PUNCT)
    w = re.sub("[ً-ْـ]", "", w)  # tashkeel + tatweel
    w = w.replace("چ", "ج").replace("گ", "ك").replace("ڤ", "ف").replace("پ", "ب")
    return w.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")


def toks(s):
    return [t for t in (norm(x) for x in re.split(r"[\s|…]+", s.translate(HIND))) if t]


def load(p):
    return json.load(open(p, encoding="utf-8"))


def sentences(words):
    """[{s, e, text, i0, i1}] — split on end punctuation or a pause >= GAP."""
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and w["s"] - words[i - 1]["e"] >= GAP:
            out.append(cur); cur = []
        cur.append(i)
        if w["w"].strip().endswith(END):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return [{"s": words[c[0]]["s"], "e": words[c[-1]]["e"], "i0": c[0], "i1": c[-1],
             "text": " ".join(words[j]["w"].strip() for j in c)} for c in out]


# ── settings from the profile ──────────────────────────────────────────────
CFG = {"dialect": "msa", "slates": [], "digits": "western"}


def configure(dialect=None, set_words=None, digits=None):
    p = mc_profile.load_profile()
    CFG["dialect"] = dialect or p["language"].get("dialect") or "msa"
    words = set_words if set_words is not None else mc_profile.set_words(p)
    CFG["slates"] = [tuple(toks(w)) for w in words if toks(w)]
    CFG["digits"] = digits or p["language"].get("digits") or "western"


# ── retakes + set words ────────────────────────────────────────────────────
STOP = {"في", "من", "على", "الى", "عن", "ويا", "مع", "هذا", "هاي", "هذي", "هذه", "اللي", "الي", "و", "او", "ثم", "بس", "يا",
        "ان", "ما", "لا", "كل", "كان", "صار", "هو", "هي", "يعني", "اني", "انا", "انت", "ده", "دي", "دا", "اللي", "هاد", "هيدا",
        "عشان", "علشان", "مش", "مو", "شي", "حاجه", "بعدين", "كمان", "برضو", "تره", "ترا", "واجد"}
# words that say "that take failed, again" in many dialects (a set word list from the profile adds to them)
REDO = {"نعيد", "انعيد", "نعيدها", "خلنعيد", "اعيد", "نعاود", "عاود", "نعيدو", "منعيد", "بنعيد"}


def _root(w):
    return w[2:] if len(w) > 4 and w.startswith("ال") else w


def _slate_tokens():
    return {t for ph in CFG["slates"] for t in ph}


def _content(s):
    sl = _slate_tokens()
    return [w for w in (_root(t) for t in toks(s)) if w not in STOP and w not in sl]


def sim(a, b):
    """shared content words over the shorter sentence, or char similarity — whichever is higher."""
    wa, wb = _content(a), _content(b)
    if len(wa) < 3 or len(wb) < 3:  # a set word alone is a slate, not a retake
        return 0.0
    shared = len(set(wa) & set(wb)) / min(len(wa), len(wb))
    return max(shared, difflib.SequenceMatcher(None, " ".join(wa), " ".join(wb)).ratio())


def retakes(S, win=2, th=0.6):
    """(i, j, score): sentence i looks re-said as j (within the next `win`) -> i is the mistake."""
    out = []
    for i in range(len(S) - 1):
        for j in range(i + 1, min(i + 1 + win, len(S))):
            if (r := sim(S[i]["text"], S[j]["text"])) >= th:
                out.append((i, j, r)); break
    return out


def slates(words):
    """[(i0, i1, text)] for every set word / set phrase from the profile — they never belong in the edit."""
    W = [norm(w["w"]) for w in words]
    out, i = [], 0
    while i < len(W):
        hit = next((ph for ph in sorted(CFG["slates"], key=len, reverse=True) if tuple(W[i:i + len(ph)]) == ph), None)
        if hit:
            out.append((i, i + len(hit) - 1, " ".join(hit))); i += len(hit)
        else:
            i += 1
    return out


def drop_ranges(S, idx):
    """jumpcut.py drops words whose START falls in [a, b) — cover first..last word of each sentence."""
    return ",".join(f"{S[i]['s'] - 0.01:.2f}-{S[i]['e']:.2f}" for i in sorted(idx))


def show(words):
    S = sentences(words)
    for n, x in enumerate(S, 1):
        print(f"{n:>3} [{int(x['s'] // 60):02d}:{x['s'] % 60:05.2f}] {x['text']}")
    print(f"\n{len(S)} sentences · {words[-1]['e']:.1f}s")
    R = retakes(S)
    if R:
        print("\n🔁 RETAKES (the first of each pair is the mistake):")
        for i, j, r in R:
            print(f"  {i + 1} -> {j + 1} ({r * 100:.0f}%)\n     {i + 1}: {S[i]['text']}\n     {j + 1}: {S[j]['text']}")
    redo_words = REDO | {t for ph in CFG["slates"] for t in ph if "عيد" in t or "جديد" in t}
    redo = [n for n, x in enumerate(S, 1) if set(toks(x["text"])) & redo_words]
    if redo:
        print(f"\n⚠️ a restart word in sentence(s) {redo}: that take failed — drop it up to the restart word (and the half-take"
              " before it if the speaker restarts); read those lines and add their ranges with `story.py drop`")
    sl = slates(words)
    rng = [f"{words[a]['s'] - 0.01:.2f}-{words[b]['e']:.2f}" for a, b, _ in sl]
    if R or sl:
        names = " / ".join(" ".join(p) for p in CFG["slates"]) or "-"
        print(f"\n🎬 {len(sl)} set words ({names}) always go.")
        print(f'  jumpcut.py ... --drop "{",".join(filter(None, [drop_ranges(S, [i for i, _, _ in R])] + rng))}"')


# ── written hook (rules from video-ad-editor podcast-hook.md) ──────────────
NUMW = {"واحد": 1, "وحده": 1, "اثنين": 2, "ثنين": 2, "اتنين": 2, "ثنتين": 2, "ثلاث": 3, "ثلاثه": 3, "تلات": 3, "تلاته": 3,
        "اربع": 4, "اربعه": 4, "خمس": 5, "خمسه": 5, "ست": 6, "سته": 6, "سبع": 7, "سبعه": 7, "ثمان": 8, "ثمانيه": 8, "ثمن": 8,
        "تمن": 8, "تمانيه": 8, "تسع": 9, "تسعه": 9, "عشر": 10, "عشره": 10, "عشرين": 20, "ثلاثين": 30, "تلاتين": 30,
        "اربعين": 40, "خمسين": 50, "ستين": 60, "سبعين": 70, "ثمانين": 80, "تمانين": 80, "تسعين": 90, "ميه": 100, "مئه": 100,
        "ميتين": 200, "الف": 1000, "الفين": 2000, "مليون": 1000000, "ساعتين": 2, "دقيقتين": 2, "سنتين": 2, "يومين": 2,
        "مرتين": 2, "شهرين": 2, "اسبوعين": 2}


def nums_in(text):
    out = {int(n) for n in re.findall(r"\d+", text.translate(HIND))}
    for t in toks(text):
        for pre in ("", "و", "ب", "ل", "ال", "وال", "بال"):
            if t.startswith(pre) and t[len(pre):] in NUMW:
                out.add(NUMW[t[len(pre):]])
    return out


# concept -> forms per dialect (normalised spelling). A hook word that belongs to ANOTHER dialect (and not to the
# target one) gets a hint with the target's form. Only unambiguous words are listed (no مره/قوي/كثير...).
CONCEPTS = {
    "how": {"iraqi": ["شلون"], "gulf": ["شلون", "كيف"], "levantine": ["كيف"], "egyptian": ["ازاي"],
            "maghrebi": ["كيفاش"], "sudanese": ["كيف"], "yemeni": ["كيف"], "msa": ["كيف"]},
    "why": {"iraqi": ["ليش"], "gulf": ["ليش", "ليه"], "levantine": ["ليش", "ليه"], "egyptian": ["ليه"], "maghrebi": ["علاش"],
            "sudanese": ["ليه", "ليش"], "yemeni": ["ليش", "ليه"], "msa": ["لماذا"]},
    "now": {"iraqi": ["هسه", "هسا"], "gulf": ["الحين"], "levantine": ["هلق", "هلا"], "egyptian": ["دلوقتي", "دلوقت"],
            "maghrebi": ["دابا", "دروك"], "sudanese": ["هسه", "هسع"], "yemeni": ["الحين", "ذلحين"], "msa": ["الان"]},
    "want": {"iraqi": ["اريد", "تريد", "يريد", "نريد"], "gulf": ["ابي", "تبي", "يبي", "نبي", "ابغي", "تبغي"],
             "levantine": ["بدي", "بدك", "بده", "بدنا"], "egyptian": ["عايز", "عاوز", "عايزه"], "maghrebi": ["بغيت", "باغي"],
             "sudanese": ["داير", "دايره", "عايز"], "yemeni": ["اشتي", "تشتي"], "msa": ["اريد", "تريد", "يريد", "نريد"]},
    "very": {"iraqi": ["كلش", "هوايه"], "gulf": ["وايد"], "levantine": ["كتير"], "egyptian": ["اوي", "خالص"],
             "maghrebi": ["بزاف"], "sudanese": ["خلاص"], "yemeni": ["جدا"], "msa": ["جدا"]},
    "like_this": {"iraqi": ["هيج"], "gulf": ["جذي", "كذا"], "levantine": ["هيك"], "egyptian": ["كده"], "maghrebi": ["هكا"],
                  "sudanese": ["كده", "كدي"], "yemeni": ["كذا", "كذه"], "msa": ["هكذا", "كذا"]},
    "what": {"iraqi": ["شنو", "شني"], "gulf": ["وش", "ايش", "شنو"], "levantine": ["شو", "ايش"], "egyptian": ["ايه"],
             "maghrebi": ["اشنو", "واش"], "sudanese": ["شنو"], "yemeni": ["ايش", "وش"], "msa": ["ماذا"]},
    "not": {"iraqi": ["مو"], "gulf": ["مب", "مو"], "levantine": ["مش", "مو"], "egyptian": ["مش"], "yemeni": ["مش"], "msa": ["ليس"]},
    "will": {"iraqi": ["راح"], "levantine": ["رح"], "msa": ["سوف"]},
}
FORMAL = {"لماذا", "الان", "سوف", "هكذا", "ليس", "ماذا", "لقد", "الذي", "التي"}


def dialect_hints(hook, dialect):
    """[(word, suggestion, severity)] — 1 = error (formal MSA word in a dialect video), 2 = warning (another dialect)."""
    if dialect in (None, "", "other"):
        return []
    out = []
    for t in toks(hook):
        if dialect != "msa" and t in FORMAL:
            sug = next((" / ".join(v[dialect]) for v in CONCEPTS.values() if t in v.get("msa", []) and v.get(dialect)), "حذفها")
            out.append((t, sug, 1)); continue
        for v in CONCEPTS.values():
            mine = v.get(dialect)
            if mine and t not in mine and any(t in forms for d, forms in v.items() if d != dialect):
                out.append((t, " / ".join(mine), 2)); break
    return out


DEV = {
    "رقم": lambda s, T: bool(re.search(r"\d", s.translate(HIND))) or any(NUMW.get(t, 0) > 1 for t in T),
    "تناقض": lambda s, T: "…" in s or any(t in ("بس", "وما", "ولا", "مو", "مش", "مب", "بدل", "عكس", "رغم", "حتى", "لكن")
                                           for t in T),
    "سؤال": lambda s, T: "؟" in s or "?" in s or any(t in ("شلون", "ليش", "شنو", "منو", "وين", "شوكت", "شكد", "اشكد", "كم",
                                                        "ازاي", "ليه", "ايه", "امتى", "فين", "مين", "كيف", "ايش", "وش", "متى",
                                                        "لماذا", "ماذا", "شو", "كيفاش", "علاش", "قديش") for t in T),
    "فضول": lambda s, T: any(t in ("السر", "سر", "السبب", "الغلطه", "غلطه", "محد", "ماكو", "مافي", "محدش", "الحقيقه", "الوحيد",
                                   "الفرق", "المشكله", "الخطا") for t in T),
    "أمر": lambda s, T: bool(T) and T[0] in ("لا", "جرب", "خذ", "افتح", "اسمع", "وقف", "انتبه", "اترك", "شوف", "بص", "خليك",
                                             "اتفرج", "تخيل"),
    "قصة": lambda s, T: any(t in ("كنت", "قال", "قلي", "قالي", "يوم", "سويت", "عملت", "خسرت", "فزت", "تعلمت", "ندمت",
                                  "صار", "حصل", "رفضت") for t in T),
}
HOT = ("اول", "اكثر", "اكبر", "اصعب", "احسن", "ابدا", "كل", "محد", "اغلب", "دايما", "غلط", "مستحيل", "سر", "مليون", "ببلاش",
       "مجانا", "كلش", "اوي", "وايد", "كتير", "بزاف")
FILLER = ("يعني", "اه", "طيب", "اوكي", "والله", "هم", "ها", "بقى", "خلاص")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")


def devices(s):
    T = toks(s)
    return [k for k, f in DEV.items() if f(s, T)]


def check(S, hook):
    errs, warns = [], []
    n = len([w for w in re.split(r"[\s|]+", hook.replace("…", " ")) if w.strip(PUNCT)])
    if not 3 <= n <= 8:
        errs.append(f"{n} words — a hook is 3-8 (cut filler words)")
    if CFG["digits"] == "western" and re.search("[٠-٩۰-۹]", hook):
        errs.append("Arabic-Indic digits — the profile uses 1 2 3")
    if CFG["digits"] == "arabic_indic" and re.search("[0-9]", hook):
        errs.append("Western digits — the profile uses ١ ٢ ٣")
    if EMOJI.search(hook):
        errs.append("emoji — remove")
    for t, sug, sev in dialect_hints(hook, CFG["dialect"]):
        (errs if sev == 1 else warns).append(f"«{t}» doesn't fit the {CFG['dialect']} dialect — try «{sug}»")
    dv = devices(hook)
    if not dv:
        errs.append("no pull device: add a number, a contrast (… / but), a question or curiosity (the reason / the mistake)")
    elif len(dv) == 1:
        warns.append(f"one device ({dv[0]}) — strongest is two: number + contrast, or question + number")
    body = " ".join(x["text"] for x in S)
    if miss := sorted(nums_in(hook) - nums_in(body)):
        errs.append(f"number {miss} is not in the speech — never invent a number")
    H, first = set(toks(hook)), set(toks(" ".join(x["text"] for x in S[:2])))
    if H and len(H & first) / len(H) >= 0.75:
        errs.append("that is basically the first line — take the hook from the strongest line, not the first")
    return errs, warns, dv


def hooks(words):
    S = sentences(words)
    rows = []
    for i, x in enumerate(S):
        T, dv = toks(x["text"]), devices(x["text"])
        sc = 3 * ("رقم" in dv) + 2 * ("تناقض" in dv) + 2 * ("سؤال" in dv) + 1.5 * ("قصة" in dv) + ("فضول" in dv) + ("أمر" in dv)
        sc += 1.2 * sum(t in HOT for t in T) - 0.6 * sum(t in FILLER for t in T) - 1.5 * (len(T) < 3)
        rows.append((sc, i, x, dv))
    print(f"first line (never the hook): «{S[0]['text']}»\n\nstrongest lines (score · time · devices):")
    for sc, i, x, dv in sorted(rows, key=lambda r: -r[0])[:8]:
        print(f"  {sc:4.1f}  {x['s']:6.2f}s  [{' + '.join(dv) or '—'}]  «{x['text']}»")
    print(f"\nnumbers in the speech (the only ones allowed): {sorted(nums_in(' '.join(x['text'] for x in S))) or 'none'}")
    print("forms: number + paradox · awkward question · failure before success · half-sentence story · reverse command · curiosity gap")


# ── subtitles + sync ───────────────────────────────────────────────────────
def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def srt(words, base):
    S, cues = sentences(words), []
    for x in S:  # split long sentences: <= 8 words / cue
        ws = words[x["i0"]:x["i1"] + 1]
        for k in range(0, len(ws), 8):
            c = ws[k:k + 8]
            cues.append((c[0]["s"], c[-1]["e"], " ".join(w["w"].strip() for w in c)))
    open(base + ".srt", "w", encoding="utf-8").write(
        "\n".join(f"{n}\n{ts(a)} --> {ts(b)}\n{t}\n" for n, (a, b, t) in enumerate(cues, 1)))
    open(base + ".txt", "w", encoding="utf-8").write("\n".join(x["text"] for x in S) + "\n")
    print(f"{len(cues)} cues -> {base}.srt + {base}.txt")


def sync(plan, final):
    """drift of each sentence start: planned (words_cut) vs heard in the render (same first word within ±1.5 s)."""
    F = [(norm(w["w"]), w["s"]) for w in final]
    d = []
    for x in sentences(plan):
        k = norm(plan[x["i0"]]["w"])
        near = [s for w, s in F if w == k and abs(s - x["s"]) <= 1.5]
        if near:
            d.append((min(near, key=lambda s: abs(s - x["s"])) - x["s"], x))
    if not d:
        sys.exit("❌ no sentence matched — is final_words.json from the final render?")
    bad = [(dt, x) for dt, x in d if abs(dt) >= 0.1]
    print(f"{len(d)} sentences matched · median drift {statistics.median(abs(t) for t, _ in d):.3f}s · "
          f"max {max(abs(t) for t, _ in d):.3f}s")
    for dt, x in bad:
        print(f"  ❌ {x['s']:6.2f}s  {dt:+.2f}s  «{x['text'][:40]}»")
    print("✅ in sync" if not bad else "❌ drift >= 0.1 s — check the edit/overlay timing at those sentences")
    return not bad


def selftest():
    w = lambda t, s, e: {"w": t, "s": s, "e": e}
    configure("iraqi", ["اكشن", "كت", "نعيد", "من جديد"], "western")
    words = [w("اليوم", 0, .4), w("راح", .5, .7), w("أعلمكم", .8, 1.3), w("الذكاء", 1.4, 1.8), w("الاصطناعي.", 1.9, 2.5),
             w("اليوم", 3.5, 3.9), w("راح", 4.0, 4.2), w("أعلمكم", 4.3, 4.8), w("شلون", 4.9, 5.2), w("تستخدمون", 5.3, 5.9),
             w("الذكاء", 6.0, 6.4), w("الاصطناعي.", 6.5, 7.0), w("وفرت", 8.0, 8.4), w("ثلاث", 8.5, 8.8), w("ساعات", 8.9, 9.3),
             w("باليوم", 9.4, 9.9), w("بس", 10.0, 10.2), w("ما", 10.3, 10.4), w("دفعت", 10.5, 10.9), w("شي.", 11.0, 11.3)]
    S = sentences(words)
    assert [x["text"].split()[0] for x in S] == ["اليوم", "اليوم", "وفرت"], S
    assert retakes(S) == [(0, 1, retakes(S)[0][2])] and drop_ranges(S, [0]) == "-0.01-2.50"
    assert sim("اكشن", "اكشن وهنا راح نبدي بسلسلة نبني بها مواقع") == 0.0  # slate alone is not a retake
    sw = [w("كت", 0, .2), w("اكشن", .3, .6), w("زين", .7, 1), w("من", 1.1, 1.2), w("جديد", 1.3, 1.6), w("من", 1.7, 1.8)]
    assert [(a, b) for a, b, _ in slates(sw)] == [(0, 0), (1, 1), (3, 4)]          # phrase matched, lone «من» kept
    assert nums_in("ثلاث ساعات و 10 دقايق") == {3, 10} and nums_in("بالمليون") == {1000000}
    e, _, dv = check(S, "3 ساعات باليوم… وما دفعت شي")
    assert not e and {"رقم", "تناقض"} <= set(dv), e
    e, wr, _ = check(S, "لماذا وفرت 5 ساعات الحين")
    assert any("لماذا" in x for x in e) and any("[5]" in x for x in e) and any("الحين" in x for x in wr), (e, wr)
    configure("egyptian", ["خلاص نعيد"], "western")                                 # same hook, other dialect
    _, wr, _ = check(S, "شلون وفرت 3 ساعات… وما دفعت")
    assert any("ازاي" in x for x in wr), wr
    e, wr, _ = check(S, "ازاي وفرت 3 ساعات… مش بفلوس")
    assert not any("dialect" in x for x in e + wr), (e, wr)
    configure("msa", [], "arabic_indic")
    e, _, _ = check(S, "كيف وفرت 3 ساعات… وما دفعت")
    assert any("Western digits" in x for x in e), e
    configure("other", [], "western")
    assert dialect_hints("شلون ازاي الحين", "other") == []
    assert ts(3725.5) == "01:02:05,500"
    shifted = [{**x, "s": x["s"] + .05} for x in words]
    assert sync(words, shifted)
    print("selftest ok")


def _opt(a, k):
    if k in a:
        i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    return None


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest(); sys.exit()
    d, sw, dg = _opt(a, "--dialect"), _opt(a, "--set-words"), _opt(a, "--digits")
    configure(d, [x.strip() for x in sw.split(",")] if sw is not None else None, dg)
    cmd, W = a[0], load(a[1])
    if cmd == "show":
        show(W)
    elif cmd == "drop":
        print(f'--drop "{drop_ranges(sentences(W), [int(n) - 1 for n in a[2:]])}"')
    elif cmd == "hooks":
        hooks(W)
    elif cmd == "check":
        S, fail = sentences(W), False
        for h in a[2:]:
            e, wr, dv = check(S, h)
            print(f"🪝 «{h}» · devices: {' + '.join(dv) or 'none'}")
            for x in e: print("  ❌", x)
            for x in wr: print("  ⚠️", x)
            print("  ✅ ok" if not e else "")
            fail |= bool(e)
        sys.exit(1 if fail else 0)
    elif cmd == "srt":
        srt(W, a[2])
    elif cmd == "sync":
        sys.exit(0 if sync(W, load(a[2])) else 1)
    else:
        sys.exit(__doc__)
