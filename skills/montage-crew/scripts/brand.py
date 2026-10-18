"""The user's brand kit, kept in the data dir (plugin updates never touch it) and mirrored into profile.brand.

  python brand.py import [--name N] [--handle H] [--cta C] [--tone T] [--logo FILE] [--colors "#bg,#text,#accent[,#x..]"]
                         [--font-head FILE|NAME] [--font-body FILE|NAME] [--fonts FILE..] [--samples FILE..] [--guide FILE]
                         [--site URL]
  python brand.py show          brand.json (JSON)          python brand.py palette IMG..   candidate colours (JSON)
  python brand.py sync          brand.json -> profile.brand python brand.py clear          delete the kit, reset profile.brand
  python brand.py --selftest

Writes <data>/brand/: brand.json, logo.<ext>, fonts/<name>.<ext> (+ OFL.txt for Google fonts), samples/<name>.<ext>,
guide.<ext>. Files are accepted by their content (magic bytes), never by their name: logo/samples png jpg webp svg,
fonts ttf otf woff2, guide pdf png jpg webp. SVGs with scripts, event handlers, external links or entities are refused.
Colours: given with --colors, else proposed from the logo + samples + site (bg = the most used, text = the best
contrast, accent = the most vivid) with the WCAG contrast of text on bg (>= 4.5 wanted; a warning when lower).
--site: fetches the page and its stylesheets (net.py guard, https, size caps) and keeps colours, font NAMES and the logo
only (never the site's font files). A font NAME that is not bundled is fetched from Google Fonts (OFL) when it exists there.
Re-running import updates only what you pass. Text fields: <= 80 characters, no < > or control characters.
"""
import argparse, colorsys, html.parser, json, os, re, shutil, sys, tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

from PIL import Image, ImageFont

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(HERE))
import mc_profile  # noqa: E402
import net  # noqa: E402
from learn import palette, safe_dir, _is_link  # noqa: E402

MB = 1 << 20
CAP = {"image": 15 * MB, "font": 5 * MB, "guide": 15 * MB, "html": 5 * MB, "total": 40 * MB}
KINDS = {"logo": {"png", "jpg", "webp", "svg"}, "sample": {"png", "jpg", "webp", "svg"},
         "font": {"ttf", "otf", "woff2"}, "guide": {"pdf", "png", "jpg", "webp"}}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
TEXT_BAD = re.compile(r"[<>\x00-\x1f\x7f]")
FONT_NAME = re.compile(r"^[\w \-]{1,60}$")
SVG_BAD = re.compile(r"<script|\son\w+\s*=|javascript:|<foreignObject|<!DOCTYPE|<!ENTITY|<\?xml-stylesheet|@import", re.I)
SVG_HREF = re.compile(r"(?:xlink:)?href\s*=\s*[\"']\s*([^\"']*)", re.I)
GENERIC = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace",
           "inherit", "initial", "unset", "emoji", "math", "-apple-system", "blinkmacsystemfont", "segoe ui", "arial",
           "helvetica", "helvetica neue", "roboto", "apple color emoji", "segoe ui emoji", "noto color emoji"}
GFONT_HOSTS = {"fonts.googleapis.com", "fonts.gstatic.com", "raw.githubusercontent.com"}


def die(msg):
    raise SystemExit(msg)


def brand_dir(*sub):
    return safe_dir("brand", *sub)


# ---------- intake ----------
def sniff(b):
    if b.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if b.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        return "webp"
    if b[:4] in (b"\x00\x01\x00\x00", b"true"):
        return "ttf"
    if b[:4] == b"OTTO":
        return "otf"
    if b[:4] == b"wOF2":
        return "woff2"
    if b.startswith(b"%PDF-"):
        return "pdf"
    head = b[:2048].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    if (head.startswith(b"<svg") or head.startswith(b"<?xml")) and b"<svg" in head:
        return "svg"
    return None


def svg_problem(b):
    t = b.decode("utf-8", "replace")
    m = SVG_BAD.search(t)
    if m:
        return f"SVG contains {m.group(0).strip()!r}"
    for h in SVG_HREF.findall(t):
        if h and not h.startswith(("#", "data:image/png", "data:image/jpeg", "data:image/webp")):
            return f"SVG links outside itself ({h[:60]!r})"
    if re.search(r"url\(\s*['\"]?(?!#|data:image/)", t, re.I):
        return "SVG loads an external url()"
    return None


def accept(data, kind, label):
    """bytes -> extension, or SystemExit. Type from the content, never from the name."""
    ext = sniff(data)
    if ext not in KINDS[kind]:
        die(f"{label}: not an accepted {kind} file (found {ext or 'unknown'}; accepted {', '.join(sorted(KINDS[kind]))})")
    if ext == "svg":
        why = svg_problem(data)
        if why:
            die(f"{label}: refused, {why}. Export the logo as PNG instead.")
    if ext in ("png", "jpg", "webp"):
        try:
            with Image.open(__import__("io").BytesIO(data)) as im:
                im.verify()
        except (OSError, ValueError, Image.DecompressionBombError) as e:
            die(f"{label}: unreadable or too large image ({type(e).__name__})")
    return ext


def read_user_file(path, kind):
    """A file the user gave: real target checked (links followed then judged), size capped, content sniffed."""
    p = Path(path).expanduser()
    real = Path(os.path.realpath(p))
    if not real.is_file():
        die(f"not a file: {path}")
    if mc_profile._inside(real, Path(mc_profile.data_dir()) / "brand"):
        return real.read_bytes(), real.suffix.lstrip(".").lower(), real  # already in the kit (re-import)
    cap = CAP["font" if kind == "font" else "image" if kind in ("logo", "sample") else "guide"]
    if real.stat().st_size > cap:
        die(f"{path}: larger than {cap // MB} MB")
    data = real.read_bytes()
    return data, accept(data, kind, str(path)), real


def kit_size():
    root = Path(mc_profile.data_dir()) / "brand"
    return sum(f.stat().st_size for f in root.rglob("*") if f.is_file()) if root.is_dir() else 0


def store(data, ext, sub, stem):
    if kit_size() + len(data) > CAP["total"]:
        die(f"the brand kit would pass {CAP['total'] // MB} MB; remove samples first (brand.py clear)")
    d = brand_dir(*sub) if sub else brand_dir()
    dst = d / f"{stem}.{ext}"
    if _is_link(dst):
        die(f"refused: {dst} is a link")
    tmp = dst.with_name(dst.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, dst)
    return dst


def safe_stem(s):
    return re.sub(r"[^\w-]+", "_", s).strip("_")[:50] or "file"


def font_family(path):
    try:
        name = ImageFont.truetype(str(path), 12).getname()[0] or ""
    except (OSError, ValueError):
        name = ""
    name = re.sub(r"[^\w \-]", "", name).strip()[:60]
    return name or re.sub(r"[^\w \-]", " ", Path(path).stem).strip()[:60] or "Brand Font"


# ---------- colour ----------
def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def luminance(h):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def vivid(h):
    _, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb(h)))
    return s * v


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(rgb(a), rgb(b))) ** 0.5


def propose(cands):
    """[(hex, weight)] -> {bg, text, accent} with contrast; text falls back to near-black/near-white for >= 4.5."""
    cands = [(h.upper(), w) for h, w in cands if HEX.match(h)]
    if not cands:
        return {"bg": None, "text": None, "accent": None}
    merged = []
    for h, w in sorted(cands, key=lambda x: -x[1]):
        near = next((m for m in merged if dist(m[0], h) < 24), None)
        if near:
            near[1] += w
        else:
            merged.append([h, w])
    bg = merged[0][0]
    text = max((h for h, _ in merged[1:]), key=lambda h: contrast(h, bg), default=None)
    if not text or contrast(text, bg) < 4.5:
        text = max(("#111111", "#FAFAFA"), key=lambda h: contrast(h, bg))
    rest = [h for h, _ in merged if dist(h, bg) > 60 and dist(h, text) > 60]
    accent = max(rest, key=vivid, default=None)
    return {"bg": bg, "text": text, "accent": accent}


# ---------- site ----------
class _Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.css, self.sheets, self.icons, self.logos, self._style = [], [], [], [], False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if a.get("style"):
            self.css.append(a["style"])
        rel = a.get("rel", "").lower()
        if tag == "link" and "stylesheet" in rel and a.get("href"):
            self.sheets.append(a["href"])
        elif tag == "link" and "icon" in rel and a.get("href"):
            self.icons.append((0 if "apple-touch" in rel else 1, a["href"]))
        elif tag == "img" and a.get("src") and "logo" in " ".join(a.get(k, "") for k in ("src", "alt", "class", "id")).lower():
            self.logos.append(a["src"])
        self._style = tag == "style"

    def handle_endtag(self, tag):
        self._style = False

    def handle_data(self, d):
        if self._style:
            self.css.append(d)


def css_colors(css):
    c = Counter()
    for m in re.finditer(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", css):
        h = m.group(1)
        h = "".join(x * 2 for x in h) if len(h) == 3 else h[:6]
        c["#" + h.upper()] += 1
    for m in re.finditer(r"rgba?\(\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})(?:[\s,/]+([\d.]+%?))?\s*\)", css):
        if m.group(4) and m.group(4).rstrip("%") in ("0", "0.0"):
            continue
        r, g, b = (min(255, int(x)) for x in m.groups()[:3])
        c["#%02X%02X%02X" % (r, g, b)] += 1
    return c


def css_fonts(css):
    c = Counter()
    for m in re.finditer(r"font-family\s*:\s*([^;}{]+)", css, re.I):
        for fam in m.group(1).split(","):
            fam = fam.strip().strip("'\"").strip()
            if fam and not fam.lower().startswith("var(") and fam.lower() not in GENERIC and FONT_NAME.match(fam):
                c[fam] += 1
                break
    return [f for f, _ in c.most_common(4)]


def read_site(url):
    """colours, font names and a logo from a page + its stylesheets. Data only: nothing is executed or rendered."""
    body, final, _ = net.get(url, CAP["html"], allow_http=url.lower().startswith("http:"))
    page = _Page()
    page.feed(body.decode("utf-8", "replace"))
    css, total = list(page.css), len(body)
    for href in page.sheets[:6]:
        u = urljoin(final, href)
        if urlparse(u).scheme != "https" or total > CAP["total"]:
            continue
        try:
            b, _, _ = net.get(u, CAP["html"])
        except SystemExit as e:
            print(f"warning: skipped a stylesheet ({e})", file=sys.stderr)
            continue
        total += len(b)
        css.append(b.decode("utf-8", "replace"))
    allcss = "\n".join(css)
    logo = None
    for src in page.logos[:2] + [h for _, h in sorted(page.icons)][:2]:
        u = urljoin(final, src)
        if urlparse(u).scheme != "https":
            continue
        try:
            data, _, _ = net.get(u, CAP["image"])
            logo = (data, accept(data, "logo", "site logo"))
            break
        except SystemExit as e:
            print(f"warning: site logo skipped ({e})", file=sys.stderr)
    return {"url": final, "colors": css_colors(allcss).most_common(12), "fonts": css_fonts(allcss), "logo": logo}


# ---------- fonts ----------
def bundled(name):
    key = re.sub(r"[\s_-]+", "", name).lower()
    for f in (mc_profile.SKILL_DIR / "assets" / "fonts").glob("*"):
        if f.suffix.lower() in (".ttf", ".otf", ".woff2") and re.sub(r"[\s_-]+", "", f.stem).lower().startswith(key):
            return f
    return None


def google_font(name):
    """Regular TTF of a Google Font (+ its OFL.txt) into brand/fonts/, or None when Google Fonts doesn't have it."""
    css_url = "https://fonts.googleapis.com/css2?family=" + quote(name).replace("%20", "+")
    try:
        css, _, _ = net.get(css_url, 256 * 1024)
    except SystemExit:
        return None
    urls = re.findall(r"url\((https://fonts\.gstatic\.com/[^)\s]+)\)", css.decode("utf-8", "replace"))
    if not urls or urlparse(urls[0]).hostname not in GFONT_HOSTS:
        return None
    data, _, _ = net.get(urls[0], CAP["font"])
    dst = store(data, accept(data, "font", name), ["fonts"], safe_stem(name))
    slug = re.sub(r"[^a-z0-9]", "", name.lower())
    try:
        lic, _, _ = net.get(f"https://raw.githubusercontent.com/google/fonts/main/ofl/{slug}/OFL.txt", 200 * 1024)
        (dst.parent / f"{safe_stem(name)}.OFL.txt").write_bytes(lic)
    except SystemExit:
        (dst.parent / f"{safe_stem(name)}.OFL.txt").write_text(
            f"{name}: SIL Open Font License 1.1, from Google Fonts ({css_url}).\n", encoding="utf-8")
    return dst


def font_arg(v):
    """--font-head/--font-body: a file -> copied, its family name; a name -> as is (fetched from Google if not bundled)."""
    if v is None:
        return None, None
    if Path(v).expanduser().is_file():
        data, ext, _ = read_user_file(v, "font")
        dst = store(data, ext, ["fonts"], safe_stem(Path(v).stem))
        return font_family(dst), dst
    name = v.strip()
    if not FONT_NAME.match(name):
        die(f"font name {v!r}: letters, digits, spaces and '-' only (max 60), or give the font file")
    return name, None if bundled(name) else google_font(name)


# ---------- brand.json + profile ----------
def load():
    p = Path(mc_profile.data_dir()) / "brand" / "brand.json"
    try:
        b = json.loads(p.read_text(encoding="utf-8-sig"))
        return b if isinstance(b, dict) else {}
    except (OSError, ValueError):
        return {}


def save(b):
    d = brand_dir()
    tmp = d / "brand.json.tmp"
    tmp.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, d / "brand.json")


def text_ok(field, v):
    if v is None:
        return None
    v = v.strip()
    if len(v) > 80 or TEXT_BAD.search(v):
        die(f"--{field}: at most 80 characters, without < > or control characters")
    return v


def mirror(b):
    root = Path(mc_profile.data_dir()) / "brand"
    c = b.get("colors") or {}
    return {"has_brand": bool(b), "name": b.get("name", ""),
            "colors": {"bg": c.get("bg"), "text": c.get("text"), "accent": c.get("accent"), "extra": list(c.get("extra") or [])},
            "fonts": {"head": (b.get("fonts") or {}).get("head"), "body": (b.get("fonts") or {}).get("body")},
            "logo": (root / b["logo"]).as_posix() if b.get("logo") else None,
            "handle": b.get("handle", ""), "cta": b.get("cta", ""), "tone": b.get("tone", ""), "source": b.get("source")}


def sync(b=None):
    """profile.brand <- brand.json, only when the profile exists (onboarding creates it, then runs sync)."""
    p = mc_profile.profile_path()
    if not p.is_file():
        return "no profile yet (onboarding runs brand.py sync after creating it)"
    prof = mc_profile.upgrade(mc_profile._read(p))
    prof["brand"] = mirror(load() if b is None else b)
    errs = [e for e in mc_profile.check(prof) if e.startswith("$.brand")]
    if errs:
        die("brand does not fit the profile:\n" + "\n".join(errs))
    mc_profile.save(prof, p)
    return "synced"


def cmd_import(a):
    b = load()
    sources = []
    for f in ("name", "handle", "cta", "tone"):
        v = text_ok(f, getattr(a, f))
        if v is not None:
            b[f] = v
    for f in ("name", "handle", "cta", "tone"):
        b.setdefault(f, "")
    cands = Counter()
    if a.logo:
        data, ext, _ = read_user_file(a.logo, "logo")
        for old in brand_dir().glob("logo.*"):
            if old.suffix != f".{ext}":
                old.unlink()
        b["logo"] = store(data, ext, None, "logo").name
        sources.append("logo")
    site = None
    if a.site:
        site = read_site(a.site)
        b["site"] = {"url": site["url"], "colors": [h for h, _ in site["colors"]], "fonts": site["fonts"]}
        if site["logo"] and not b.get("logo"):
            b["logo"] = store(site["logo"][0], site["logo"][1], None, "logo").name
        for h, n in site["colors"]:
            cands[h] += n
        sources.append(f"site {site['url']}")
    samples = list(b.get("samples") or [])
    for s in (a.samples or []):
        data, ext, real = read_user_file(s, "sample")
        dst = store(data, ext, ["samples"], safe_stem(real.stem))
        if f"samples/{dst.name}" not in samples:
            samples.append(f"samples/{dst.name}")
    b["samples"] = samples
    if a.guide:
        data, ext, _ = read_user_file(a.guide, "guide")
        for old in brand_dir().glob("guide.*"):
            old.unlink()
        b["guide"] = store(data, ext, None, "guide").name
    fonts = dict(b.get("fonts") or {"head": None, "body": None, "files": []})
    files = list(fonts.get("files") or [])
    for f in (a.fonts or []):
        data, ext, real = read_user_file(f, "font")
        dst = store(data, ext, ["fonts"], safe_stem(real.stem))
        fam = font_family(dst)
        files.append(f"fonts/{dst.name}")
        fonts["head"] = fonts.get("head") or fam
        fonts["body"] = fonts.get("body") if fonts.get("body") and fonts["body"] != fonts["head"] else fam
    for key, val in (("head", a.font_head), ("body", a.font_body)):
        name, dst = font_arg(val)
        if name:
            fonts[key] = name
        if dst:
            files.append(f"fonts/{dst.name}")
    if site and site["fonts"]:
        fonts["head"] = fonts.get("head") or site["fonts"][0]
        fonts["body"] = fonts.get("body") or (site["fonts"][1] if len(site["fonts"]) > 1 else site["fonts"][0])
    fonts["files"] = sorted(set(files))
    b["fonts"] = fonts
    # palette from the kit's images (SVG: its fill/stroke colours)
    root = brand_dir()
    imgs = [root / b["logo"]] if b.get("logo") else []
    imgs += [root / s for s in samples]
    pal, ims = [], []
    for f in imgs:
        if f.suffix == ".svg":
            for h, n in css_colors(f.read_text(encoding="utf-8", errors="replace")).items():
                cands[h] += n * 50
            continue
        try:
            im = Image.open(f)
            im.load()
            ims.append(im)
        except (OSError, Image.DecompressionBombError):
            pass
    if ims:
        pal = palette(ims, 8)
        for p in pal:
            cands[p["hex"]] += p["share"] * 1000
    b["palette"] = pal
    if a.colors:
        cs = [c.strip().upper() for c in a.colors.split(",") if c.strip()]
        bad = [c for c in cs if not HEX.match(c)]
        if bad or not 1 <= len(cs) <= 11:
            die(f"--colors: give #RRGGBB values (bg,text,accent[,extra..]); bad: {bad}")
        cs += [None] * (3 - len(cs))
        b["colors"] = {"bg": cs[0], "text": cs[1], "accent": cs[2], "extra": [c for c in cs[3:] if c][:8]}
        b["colors_from"] = "user"
    elif cands and b.get("colors_from") != "user":
        b["colors"] = dict(propose(list(cands.items())), extra=[])
        b["colors_from"] = "proposed"
    c = b.get("colors") or {}
    if c.get("bg") and c.get("text"):
        b["contrast"] = {"text_on_bg": contrast(c["text"], c["bg"]),
                         "accent_on_bg": contrast(c["accent"], c["bg"]) if c.get("accent") else None}
        b["contrast"]["ok"] = b["contrast"]["text_on_bg"] >= 4.5
        if not b["contrast"]["ok"]:
            print(f"warning: text on bg contrast {b['contrast']['text_on_bg']} < 4.5 (hard to read)", file=sys.stderr)
    b["source"] = text_ok("source", ("brand.py import: " + ", ".join(sources))[:200]) if sources else b.get("source")
    b["schema"] = 1
    save(b)
    return {"brand": b, "dir": root.as_posix(), "profile": sync(b)}


def cmd_clear():
    d = Path(mc_profile.data_dir()) / "brand"
    if _is_link(d):
        d.unlink()
    elif d.is_dir():
        shutil.rmtree(d)
    p = mc_profile.profile_path()
    if p.is_file():
        prof = mc_profile.upgrade(mc_profile._read(p))
        prof["brand"] = dict(mc_profile.DEFAULTS["brand"], has_brand=False)
        mc_profile.save(prof, p)
    return {"cleared": d.as_posix()}


def cmd_palette(files):
    ims = []
    for f in files:
        data, ext, real = read_user_file(f, "sample")
        if ext != "svg":
            ims.append(Image.open(real))
    pal = palette(ims, 8)
    return {"palette": pal, "proposal": propose([(p["hex"], p["share"]) for p in pal])}


# ---------- selftest ----------
def selftest():
    import io
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        os.environ["MONTAGE_CREW_HOME"] = str(d / "data")
        logo = d / "logo-src.png"
        im = Image.new("RGB", (300, 120), (0x14, 0x14, 0x13))
        for x in range(40, 260):
            for y in range(30, 90):
                im.putpixel((x, y), (0xD9, 0x77, 0x57))
        im.save(logo)
        Image.new("RGB", (100, 100), (0xFA, 0xF9, 0xF5)).save(d / "sample.png")
        ttf = next((mc_profile.SKILL_DIR / "assets" / "fonts").glob("*.ttf"))
        ex = (mc_profile.SKILL_DIR / "templates" / "profile.example.json").read_text(encoding="utf-8")
        mc_profile.profile_path().parent.mkdir(parents=True, exist_ok=True)
        mc_profile.profile_path().write_text(ex, encoding="utf-8")
        ns = lambda **k: argparse.Namespace(**{**dict(name=None, handle=None, cta=None, tone=None, logo=None, colors=None,
                                                         font_head=None, font_body=None, fonts=None, samples=None,
                                                         guide=None, site=None), **k})
        r = cmd_import(ns(name="Eng. Taher", handle="@eng.taher", cta="Follow", logo=str(logo), samples=[str(d / "sample.png")],
                          fonts=[str(ttf)]))
        b = r["brand"]
        assert r["profile"] == "synced" and b["logo"] == "logo.png" and (d / "data" / "brand" / "logo.png").is_file(), r
        c = b["colors"]
        assert (c["bg"], c["text"]) == ("#FAF9F5", "#141413") and dist(c["accent"], "#D97757") < 30 and b["contrast"]["ok"], b
        assert b["fonts"]["head"] and b["fonts"]["files"] == [f"fonts/{safe_stem(ttf.stem)}.ttf"], b["fonts"]
        prof = json.loads(mc_profile.profile_path().read_text(encoding="utf-8"))
        assert prof["brand"]["has_brand"] and prof["brand"]["logo"].endswith("/brand/logo.png") and mc_profile.validate() == []
        r = cmd_import(ns(colors="#0B1020,#F5F5F5,#5EEAD4,#FFD166", tone="calm"))   # update keeps the rest
        assert r["brand"]["colors"]["extra"] == ["#FFD166"] and r["brand"]["name"] == "Eng. Taher" and r["brand"]["logo"]
        assert contrast("#000000", "#FFFFFF") == 21.0 and contrast("#777777", "#FFFFFF") < 4.5
        assert propose([("#FFFFFF", 9), ("#EEEEEE", 5), ("#66AAFF", 1)])["text"] == "#111111"
        # hostile input: refused, nothing written
        bad = {"poly.png": b"MZ\x90\x00" + b"\x00" * 64, "fake.ttf": b"<html>",
               "evil.svg": b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
               "evil2.svg": b'<svg onload="alert(1)"/>', "evil3.svg": b'<svg><image href="https://x.example/a.png"/></svg>',
               "evil4.svg": b'<?xml version="1.0"?><!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]><svg>&x;</svg>',
               "evil5.svg": b'<svg><foreignObject><p/></foreignObject></svg>'}
        for n, data in bad.items():
            (d / n).write_bytes(data)
        for n, kind in (("poly.png", "logo"), ("fake.ttf", "font"), ("evil.svg", "logo"), ("evil2.svg", "logo"),
                        ("evil3.svg", "logo"), ("evil4.svg", "logo"), ("evil5.svg", "logo")):
            try:
                read_user_file(d / n, kind); raise AssertionError(n)
            except SystemExit:
                pass
        ok_svg = d / "ok.svg"
        ok_svg.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#D97757" width="9" height="9"/>'
                           b'<use href="#a"/></svg>')
        assert read_user_file(ok_svg, "logo")[1] == "svg"
        named = d / "logo.svg"; shutil.copyfile(logo, named)     # a PNG named .svg is stored as .png
        assert read_user_file(named, "logo")[1] == "png"
        try:
            os.symlink(d / "poly.png", d / "link.png")           # the link's target is judged, not its name
            try:
                read_user_file(d / "link.png", "logo"); raise AssertionError("link")
            except SystemExit:
                pass
        except OSError:
            pass
        for k, v in (("name", "<img src=x onerror=alert(1)>"), ("cta", "a\nb"), ("tone", "x" * 81)):
            try:
                text_ok(k, v); raise AssertionError(k)
            except SystemExit:
                pass
        for cs in ("red;}</style><script>,#FFFFFF,#000000", "#12345,#FFFFFF"):
            try:
                cmd_import(ns(colors=cs)); raise AssertionError(cs)
            except SystemExit:
                pass
        try:
            font_arg("Evil</style>"); raise AssertionError("font name")
        except SystemExit:
            pass
        # site parsing (offline: net.get is faked); colours, font names and the logo only
        page = (b'<html><head><link rel="stylesheet" href="/a.css"><link rel="icon" href="/fav.png">'
                b'<style>body{background:#0B1020;color:#f5f5f5;font-family:"Inter",sans-serif}</style></head>'
                b'<body style="border:1px solid rgb(94,234,212)"><img class="site-logo" src="https://cdn.example/logo.png">'
                b'<script>fetch("/x")</script></body></html>')
        buf = io.BytesIO(); Image.new("RGB", (64, 64), (0x5E, 0xEA, 0xD4)).save(buf, "PNG")
        web = {"https://brand.example/": page, "https://brand.example/a.css": b"h1{color:#0B1020;font-family:'Cairo'}a{color:#5EEAD4}",
               "https://cdn.example/logo.png": buf.getvalue()}
        real_get = net.get
        net.get = lambda u, cap, allow_http=False: (web[u], u, "") if u in web else (_ for _ in ()).throw(SystemExit("404"))
        try:
            s = read_site("https://brand.example/")
        finally:
            net.get = real_get
        assert s["fonts"][:2] == ["Inter", "Cairo"] and s["logo"][1] == "png", s
        assert dict(s["colors"])["#0B1020"] == 2 and "#5EEAD4" in dict(s["colors"]), s["colors"]
        try:
            read_site("http://127.0.0.1/"); raise AssertionError("ssrf")
        except SystemExit as e:
            assert "refused" in str(e)
        assert bundled(re.sub(r"[-_].*", "", ttf.stem)) is not None and bundled("No Such Font XYZ") is None
        out = cmd_clear()
        assert not Path(out["cleared"]).exists()
        prof = json.loads(mc_profile.profile_path().read_text(encoding="utf-8"))
        assert prof["brand"]["has_brand"] is False and prof["brand"]["logo"] is None and mc_profile.validate() == []
        del os.environ["MONTAGE_CREW_HOME"]
    print("selftest ok")


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--selftest":
        return selftest()
    cmd = sys.argv[1]
    if cmd == "show":
        res = load() or {"brand": None, "hint": "no brand kit yet: brand.py import ..."}
    elif cmd == "sync":
        res = {"profile": sync()}
    elif cmd == "clear":
        res = cmd_clear()
    elif cmd == "palette" and len(sys.argv) > 2:
        res = cmd_palette(sys.argv[2:])
    elif cmd == "import":
        ap = argparse.ArgumentParser(prog="brand.py import")
        for f in ("name", "handle", "cta", "tone", "logo", "colors", "font-head", "font-body", "guide", "site"):
            ap.add_argument(f"--{f}")
        ap.add_argument("--fonts", nargs="+")
        ap.add_argument("--samples", "--images", nargs="+", dest="samples")
        res = cmd_import(ap.parse_args(sys.argv[2:]))
    else:
        sys.exit(__doc__)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
