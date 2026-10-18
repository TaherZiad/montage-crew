"""Shared helpers for montage-crew scripts: data dir, the user's profile, and safe tool lookup.

  python mc_profile.py path            JSON {install_kind, skill_dir, data_dir, profile, py} (absolute; use these to
                                       resolve the SKILL_DIR / DATA_DIR / PY placeholders at runtime)
  python mc_profile.py show            print the profile merged with defaults (JSON)
  python mc_profile.py tools           print where ffmpeg / ffprobe / node were found
  python mc_profile.py validate [file] check a profile against templates/profile.schema.json (exit 1 + reason if invalid)
  python mc_profile.py migrate [file]  v1 -> v2 in place (keeps every value, old file saved as profile.v1.json);
                                       prints {"migrated": bool, "ask": [...]}. Already v2 -> migrated false.
  python mc_profile.py ask [file]      JSON list of the onboarding fields still unset (absent or null) -> ask only these
  python mc_profile.py --selftest

Data dir (user data that upgrades never erase): $MONTAGE_CREW_HOME, else (ZIP install only) the path in
<skill>/data_dir.txt written by the installer, else ~/.montage-crew.
install_kind: "plugin" when this skill sits in <root>/skills/montage-crew and <root>/.claude-plugin/plugin.json exists
(Claude Code plugin: the folder is never written at runtime), else "zip".
Tools are looked up ONLY in the PATH directories (never the current folder: on Windows a bare program name
is searched in the working directory first, so a planted ffmpeg.exe next to a video would run).
Override a tool with MC_FFMPEG / MC_FFPROBE / MC_NODE (absolute path).
"""
import json, os, pathlib, sys

for _s in (sys.stdout, sys.stderr):  # Arabic/emoji output on Windows consoles (cp1256/cp1252) must never crash a script
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = pathlib.Path(__file__).resolve().parent
SKILL_DIR = HERE.parent

DEFAULTS = {
    "schema_version": 2,
    "editor": "none",
    "resolve_live": {"enabled": False, "python": None, "mcp_dir": None},
    "format": "9x16",
    "footage": "camera",
    "style_prefs": {"looks": None, "caption_style": None, "caption_scheme": None, "motion_personality": None,
                    "liked_refs": [], "default_style": None},
    "voice": {"kind": "own", "ai_provider": None, "ai_key_env": None, "ai_voice_id": None},
    "language": {"dialect": "msa", "dialect_note": "", "set_words": ["اكشن", "كت", "نعيد", "من جديد"], "digits": "western"},
    "brand": {"has_brand": None, "name": "", "colors": {"bg": None, "text": None, "accent": None, "extra": []},
              "fonts": {"head": None, "body": None}, "logo": None, "handle": "", "cta": "", "tone": "", "source": None},
    "mode": "fast",
    "paths": {"work_dir": None, "output_dir": None},
}
# onboarding questions whose answer lives at these paths; unset (absent/null) in the file -> ask it
ASK = ["editor", "format", "footage", "voice.kind", "language.dialect", "mode", "paths.work_dir", "paths.output_dir",
       "style_prefs.looks", "style_prefs.caption_style", "style_prefs.motion_personality", "brand.has_brand"]
SIZES = {"9x16": (1080, 1920), "16x9": (1920, 1080)}


def install_kind():
    root = SKILL_DIR.parent.parent
    return "plugin" if SKILL_DIR.parent.name == "skills" and (root / ".claude-plugin" / "plugin.json").is_file() else "zip"


def data_dir():
    env = os.environ.get("MONTAGE_CREW_HOME")
    if env:
        return pathlib.Path(env).expanduser()
    marker = SKILL_DIR / "data_dir.txt"
    if install_kind() == "zip" and marker.is_file():
        txt = marker.read_text(encoding="utf-8-sig").strip()
        if txt:
            return pathlib.Path(txt).expanduser()
    return pathlib.Path.home() / ".montage-crew"


def profile_path():
    return data_dir() / "profile.json"


def python_exe():
    """The venv Python setup made (<data>/venv), else the one running now."""
    v = data_dir() / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return v if v.is_file() else pathlib.Path(sys.executable)


def paths():
    ab = lambda p: pathlib.Path(os.path.abspath(p)).as_posix()
    return {"install_kind": install_kind(), "skill_dir": ab(SKILL_DIR), "data_dir": ab(data_dir()),
            "profile": ab(profile_path()), "py": ab(python_exe())}


def _merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = _merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def _read(p):
    try:
        raw = json.loads(pathlib.Path(p).read_text(encoding="utf-8-sig"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, ValueError):
        return {}


def upgrade(raw):
    """v1 dict -> v2 dict (a copy; values kept). The flat v1 brand moves into the v2 shape; new fields are left out
    (unset), so ask() lists them. v2 input comes back unchanged."""
    raw = json.loads(json.dumps(raw))
    if not raw or raw.get("schema_version", 1) != 1:
        return raw
    b = raw.get("brand") if isinstance(raw.get("brand"), dict) else {}
    if b and "colors" not in b:
        fname = lambda f: pathlib.Path(f.replace(chr(92), "/")).stem if isinstance(f, str) and any(c in f for c in "/.:" + chr(92)) else f
        new = {"colors": {k: b.get(k) for k in ("bg", "text", "accent")}, "fonts": {"head": fname(b.get("font_head")),
               "body": fname(b.get("font_body"))}, "logo": b.get("logo"), "handle": b.get("handle") or "", "cta": b.get("cta") or ""}
        new["colors"]["extra"] = []
        if any(v for v in (*new["colors"].values(), *new["fonts"].values(), new["logo"], new["handle"], new["cta"])):
            new["has_brand"] = True
        raw["brand"] = new
    raw["schema_version"] = 2
    return raw


def load_profile(path=None):
    """Profile (v1 upgraded in memory) merged over DEFAULTS. Missing/corrupt file -> defaults."""
    return _merge(DEFAULTS, upgrade(_read(path or profile_path())))


def ask(path=None):
    """Onboarding fields still unset in the user's file (absent or null) -> the questions to ask."""
    raw, out = upgrade(_read(path or profile_path())), []
    for k in ASK:
        v = raw
        for part in k.split("."):
            v = v.get(part) if isinstance(v, dict) else None
        if v is None:
            out.append(k)
    return out


def save(prof, path=None):
    """Atomic write (tmp + replace), UTF-8 without BOM; 'updated' stamped."""
    from datetime import datetime, timezone
    p = pathlib.Path(path or profile_path())
    p.parent.mkdir(parents=True, exist_ok=True)
    prof["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(prof, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def migrate(path=None):
    """v1 file -> v2 file. The v1 file is kept as profile.v1.json. Unknown/corrupt file -> untouched."""
    p = pathlib.Path(path or profile_path())
    raw = _read(p)
    if not raw or raw.get("schema_version") != 1:
        return {"migrated": False, "ask": ask(p)}
    bak = p.with_name(p.stem + ".v1.json")
    if not bak.exists():
        bak.write_bytes(p.read_bytes())
    new = upgrade(raw)
    new["style_prefs"] = dict(DEFAULTS["style_prefs"])  # null = not asked yet
    new["brand"] = _merge(DEFAULTS["brand"], new.get("brand"))
    dropped = []
    for _ in range(5):  # a bad v1 value is reset to its default with a warning, never a crash
        errs = [e for e in check(new) if not e.endswith(": missing")]
        if not errs:
            break
        for e in errs:
            keys = e.split(":")[0].lstrip("$.").split("[")[0].split(".")
            parent, dflt = new, DEFAULTS
            for k in keys[:-1]:
                parent, dflt = parent.get(k, {}), (dflt or {}).get(k, {})
            if not isinstance(parent, dict) or keys[-1] not in parent:
                continue
            old = parent[keys[-1]]
            if isinstance(dflt, dict) and keys[-1] in dflt:
                parent[keys[-1]] = json.loads(json.dumps(dflt[keys[-1]]))
            else:
                del parent[keys[-1]]
            item = {"field": ".".join(keys), "why": e.split(": ", 1)[-1]}
            if keys[:2] == ["brand", "logo"] or keys[:2] == ["brand", "fonts"]:
                item["old_value"] = old  # a path: the skill offers `brand.py import --logo <old_value>`
            dropped.append(item)
            print(f"warning: profile {item['field']} reset ({item['why']})", file=sys.stderr)
    save(new, p)
    return {"migrated": True, "backup": str(bak), "dropped": dropped, "ask": ask(p)}


def canvas(fmt=None, profile=None):
    """'9x16'|'16x9'|'1080x1920' -> (w, h). 'both' -> the 9:16 one (render twice for both)."""
    fmt = fmt or (profile or load_profile())["format"]
    if fmt in SIZES:
        return SIZES[fmt]
    if fmt == "both":
        return SIZES["9x16"]
    w, h = (int(v) for v in str(fmt).lower().split("x"))
    return w, h


def set_words(profile=None):
    return list((profile or load_profile())["language"].get("set_words") or [])


def _path_dirs():
    return [d for d in os.environ.get("PATH", "").split(os.pathsep) if d and os.path.isabs(d)]


def tool(name):
    """Absolute path of a program found in PATH (never the cwd). Not found -> an absolute path that cannot exist
    (<drive root>/ffmpeg-NOT-FOUND-install-it), so the call fails with that name instead of searching the cwd."""
    env = os.environ.get(f"MC_{name.upper()}")
    if env and os.path.isfile(env):
        return env
    exts = [""] + (os.environ.get("PATHEXT", ".EXE;.CMD;.BAT").lower().split(";") if os.name == "nt" else [])
    venv_bin = str(data_dir() / "venv" / ("Scripts" if os.name == "nt" else "bin"))  # ours: e.g. the optional yt-dlp
    for d in _path_dirs() + [venv_bin]:
        for e in exts:
            p = os.path.join(d, name + e)
            if os.path.isfile(p) and (os.name == "nt" or os.access(p, os.X_OK)):
                return p
    return os.path.join(os.path.abspath(os.sep), f"{name}-NOT-FOUND-install-it")


FFMPEG = tool("ffmpeg")
FFPROBE = tool("ffprobe")


def ffmpeg_major():
    import re, subprocess
    try:
        out = subprocess.run([FFMPEG, "-version"], capture_output=True, text=True).stdout
        m = re.search(r"ffmpeg version n?(\d+)", out)
        return int(m.group(1)) if m else 99  # git builds: assume new
    except OSError:
        return 0


def filter_script_args(path):
    """['-/filter_complex', path] on ffmpeg >= 7, ['-filter_complex_script', path] before."""
    return ["-/filter_complex", str(path)] if ffmpeg_major() >= 7 else ["-filter_complex_script", str(path)]


SCHEMA = SKILL_DIR / "templates" / "profile.schema.json"


def _check(v, sc, path, errs):
    """Small JSON-Schema subset (type, const, enum, required, properties, additionalProperties, items, pattern,
    min/maxLength, maxItems, format date-time) — enough for profile.schema.json, no extra dependency."""
    import re
    from datetime import datetime
    types = sc.get("type")
    if types:
        tmap = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
                "integer": int, "number": (int, float)}
        ok = any(isinstance(v, tmap[t]) and not (t in ("integer", "number") and isinstance(v, bool))
                 for t in ([types] if isinstance(types, str) else types))
        if not ok:
            errs.append(f"{path}: expected {types}, got {type(v).__name__}"); return
    if "const" in sc and (v != sc["const"] or isinstance(v, bool) != isinstance(sc["const"], bool)):  # True == 1 in Python
        errs.append(f"{path}: must be {sc['const']!r}")
    if "enum" in sc and v not in sc["enum"]:
        errs.append(f"{path}: {v!r} not one of {sc['enum']}")
    if isinstance(v, str):
        if "minLength" in sc and len(v) < sc["minLength"]:
            errs.append(f"{path}: too short")
        if "maxLength" in sc and len(v) > sc["maxLength"]:
            errs.append(f"{path}: too long")
        m = re.search(sc["pattern"], v) if "pattern" in sc else True
        if not m or (m is not True and sc["pattern"].endswith("$") and m.end() != len(v)):  # "$" also matches before "\n"
            errs.append(f"{path}: does not match {sc['pattern']}")
        if sc.get("format") == "date-time":
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                errs.append(f"{path}: not an ISO date-time")
    if isinstance(v, list):
        if "maxItems" in sc and len(v) > sc["maxItems"]:
            errs.append(f"{path}: more than {sc['maxItems']} items")
        for i, x in enumerate(v):
            _check(x, sc.get("items", {}), f"{path}[{i}]", errs)
    if isinstance(v, dict):
        for k in sc.get("required", []):
            if k not in v:
                errs.append(f"{path}.{k}: missing")
        props = sc.get("properties", {})
        for k, x in v.items():
            if k in props:
                _check(x, props[k], f"{path}.{k}", errs)
            elif sc.get("additionalProperties") is False:
                errs.append(f"{path}.{k}: unknown key")


def validate(path=None, schema=None):
    """[] when the profile file is valid, else the list of problems."""
    p = pathlib.Path(path) if path else profile_path()
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except OSError:
        return [f"{p}: missing"]
    except ValueError as e:
        return [f"{p}: not JSON ({e})"]
    return check(data, schema)


# AI voice key: the profile stores only the NAME of an environment variable, never the key
KEY_ENVS = {"elevenlabs": {"ELEVENLABS_API_KEY", "XI_API_KEY"}, "openai": {"OPENAI_API_KEY"}}
KEY_ENV_DENY = ("ANTHROPIC_", "CLAUDE", "AWS_", "AZURE_", "GITHUB_", "GH_", "GOOGLE_", "NPM_", "PYPI_", "HF_")
KEY_ENV_DENY_EXACT = {"PATH", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "COMSPEC", "PATHEXT"}


def key_env_problem(name, provider=None):
    """None when the env-var name is acceptable for this provider, else the reason."""
    import re
    if name is None:
        return None
    if not isinstance(name, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", name):
        return "must be the NAME of an environment variable (A-Z, 0-9, _), never the key itself"
    if re.fullmatch(r"[A-F0-9_]{24,}", name):
        return "looks like a key, not a variable name"
    if name.startswith(KEY_ENV_DENY) or name in KEY_ENV_DENY_EXACT:
        return f"{name} is reserved for other tools; use the voice provider's own variable"
    allowed = KEY_ENVS.get((provider or "").lower())
    if allowed and name not in allowed:
        return f"for {provider} use one of {sorted(allowed)}"
    return None


def _inside(p, root):
    try:
        return pathlib.Path(os.path.realpath(p)).is_relative_to(pathlib.Path(os.path.realpath(root)))
    except (OSError, ValueError):
        return False


def check(data, schema=None):
    """[] when a profile dict is valid (schema + the rules a schema can't say), else the problems."""
    errs = []
    _check(data, json.loads(pathlib.Path(schema or SCHEMA).read_text(encoding="utf-8-sig")), "$", errs)
    if not isinstance(data, dict):
        return errs
    v = data.get("voice") if isinstance(data.get("voice"), dict) else {}
    why = key_env_problem(v.get("ai_key_env"), v.get("ai_provider")) if isinstance(v.get("ai_key_env"), str) else None
    if why:
        errs.append(f"$.voice.ai_key_env: {why}")
    b = data.get("brand") if isinstance(data.get("brand"), dict) else {}
    if isinstance(b.get("logo"), str) and not _inside(b["logo"], data_dir() / "brand"):
        errs.append("$.brand.logo: must be a file inside the data folder's brand/ (run brand.py import --logo)")
    refs = (data.get("style_prefs") or {}).get("liked_refs") if isinstance(data.get("style_prefs"), dict) else None
    for i, r in enumerate(refs if isinstance(refs, list) else []):
        if isinstance(r, str) and "://" in r and not r.lower().startswith(("http://", "https://")):
            errs.append(f"$.style_prefs.liked_refs[{i}]: only http(s) links or local paths")
    return errs


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        os.environ["MONTAGE_CREW_HOME"] = d
        assert data_dir() == pathlib.Path(d)
        assert load_profile()["format"] == "9x16"                      # no file -> defaults
        profile_path().write_text("{broken", encoding="utf-8")
        assert load_profile()["mode"] == "fast"                         # corrupt -> defaults, never a crash
        profile_path().write_text(json.dumps({"format": "16x9", "language": {"dialect": "egyptian"}}), encoding="utf-8")
        p = load_profile()
        assert p["language"]["dialect"] == "egyptian" and p["language"]["digits"] == "western"  # deep merge
        assert canvas(profile=p) == (1920, 1080) and canvas("9x16") == (1080, 1920) and canvas("720x1280") == (720, 1280)
        # a profile saved with a UTF-8 BOM (Notepad, PowerShell 5.1 Out-File) is still the user's profile
        profile_path().write_text(json.dumps({"format": "both", "language": {"dialect": "egyptian"}}), encoding="utf-8-sig")
        assert load_profile()["format"] == "both" and load_profile()["language"]["dialect"] == "egyptian"
        # v1 -> v2: values kept, flat brand reshaped, only new questions asked
        v1 = {"schema_version": 1, "editor": "premiere", "format": "9x16", "footage": "screen", "mode": "pro",
              "voice": {"kind": "own"}, "language": {"dialect": "iraqi"}, "paths": {"work_dir": "w", "output_dir": "o"},
              "brand": {"bg": "#111111", "text": "#FAFAFA", "accent": None, "font_head": "Cairo", "font_body": None,
                        "logo": None, "handle": "@me", "cta": ""}}
        profile_path().write_text(json.dumps(v1), encoding="utf-8-sig")
        p = load_profile()
        assert p["schema_version"] == 2 and p["brand"]["colors"]["bg"] == "#111111" and p["brand"]["fonts"]["head"] == "Cairo"
        assert p["brand"]["handle"] == "@me" and p["brand"]["has_brand"] is True and "font_head" not in p["brand"]
        assert ask() == ["style_prefs.looks", "style_prefs.caption_style", "style_prefs.motion_personality"], ask()
        r = migrate()
        assert r["migrated"] and (pathlib.Path(d) / "profile.v1.json").is_file() and r["ask"] == ask()
        m = json.loads(profile_path().read_text(encoding="utf-8"))
        assert m["schema_version"] == 2 and m["editor"] == "premiere" and m["brand"]["colors"]["extra"] == []
        assert m["style_prefs"]["looks"] is None and m["brand"]["tone"] == "" and not migrate()["migrated"]
        assert "brand.has_brand" in ask(pathlib.Path(d) / "none.json") and len(ask(pathlib.Path(d) / "none.json")) == len(ASK)
        del os.environ["MONTAGE_CREW_HOME"]
    # tool(): a planted program in the cwd is never picked
    with tempfile.TemporaryDirectory() as d:
        fake = pathlib.Path(d) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        fake.write_text("x")
        old = os.getcwd()
        os.chdir(d)
        try:
            assert pathlib.Path(tool("ffmpeg")).resolve() != fake.resolve()
            missing = tool("no-such-tool-xyz")
            assert os.path.isabs(missing) and "NOT-FOUND" in missing
        finally:
            os.chdir(old)
    if SCHEMA.is_file():  # the schema ships in templates/ (FLUX); check our validator against its example
        ex = SKILL_DIR / "templates" / "profile.example.json"
        assert validate(ex) == [], validate(ex)
        with tempfile.TemporaryDirectory() as d:
            bad = json.loads(ex.read_text(encoding="utf-8"))
            bad["format"] = "4x3"; bad["voice"]["ai_key_env"] = "sk-live-123"; bad["extra"] = 1
            del bad["mode"]
            f = pathlib.Path(d) / "p.json"; f.write_text(json.dumps(bad), encoding="utf-8")
            e = " | ".join(validate(f))
            assert all(k in e for k in ("$.format", "$.voice.ai_key_env", "$.extra", "$.mode")), e
            good = json.loads(ex.read_text(encoding="utf-8"))
            f.write_text(json.dumps(good, ensure_ascii=False), encoding="utf-8-sig")       # BOM: valid
            assert validate(f) == [], validate(f)
            good["schema_version"] = True                                                   # True == 1, still wrong
            f.write_text(json.dumps(good), encoding="utf-8")
            assert any("$.schema_version" in x for x in validate(f)), validate(f)
            v1 = json.loads(ex.read_text(encoding="utf-8"))                                # a real v1 file migrates valid
            v1.update(schema_version=1, brand={"bg": "#000000", "text": None, "accent": None, "font_head": None,
                                               "font_body": None, "logo": None, "handle": "", "cta": "Follow"})
            del v1["style_prefs"]
            f.write_text(json.dumps(v1), encoding="utf-8")
            assert validate(f) and migrate(f)["migrated"] and validate(f) == [], validate(f)
            v1.update(brand={"bg": "red;}</style><script>", "text": None, "accent": None, "font_head": "C:/f/My Font.ttf",
                             "font_body": None, "logo": "C:/elsewhere/logo.png", "handle": "<img src=x onerror=alert(1)>",
                             "cta": "ok"}, voice=dict(v1["voice"], ai_provider="elevenlabs", ai_key_env="ANTHROPIC_API_KEY"))
            f.write_text(json.dumps(v1), encoding="utf-8")
            r = migrate(f)
            m = json.loads(f.read_text(encoding="utf-8"))
            got = {x["field"] for x in r["dropped"]}
            assert got == {"brand.colors.bg", "brand.logo", "brand.handle", "voice.ai_key_env"}, r
            assert m["brand"]["fonts"]["head"] == "My Font" and m["brand"]["cta"] == "ok" and validate(f) == [], validate(f)
            assert next(x for x in r["dropped"] if x["field"] == "brand.logo")["old_value"] == "C:/elsewhere/logo.png"
            assert m["voice"]["ai_key_env"] is None and not any("old_value" in x for x in r["dropped"] if x["field"].startswith("voice"))
            for n, prov, ok in (("ELEVENLABS_API_KEY", "elevenlabs", True), ("OPENAI_API_KEY", "elevenlabs", False),
                                ("MY_TTS_KEY", "other", True), ("GH_TOKEN", None, False), ("PATH", None, False),
                                ("sk-live-123", None, False), ("ABCDEF0123456789ABCDEF0123", None, False)):
                assert (key_env_problem(n, prov) is None) == ok, n
            m["brand"]["name"] = "Taher" + chr(10); f.write_text(json.dumps(m), encoding="utf-8")
            assert any("$.brand.name" in x for x in validate(f)), "trailing newline must not pass ^...$"
            f.write_text("{oops", encoding="utf-8")
            assert "not JSON" in validate(f)[0]
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest()
    elif a[0] == "path":
        print(json.dumps(paths(), ensure_ascii=False, indent=1))
    elif a[0] == "show":
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps(load_profile(), ensure_ascii=False, indent=1))
    elif a[0] == "validate":
        errs = validate(a[1] if len(a) > 1 else None)
        sys.stdout.reconfigure(encoding="utf-8")
        print("\n".join(errs) if errs else "profile ok")
        sys.exit(1 if errs else 0)
    elif a[0] in ("migrate", "ask"):
        r = migrate(a[1] if len(a) > 1 else None) if a[0] == "migrate" else ask(a[1] if len(a) > 1 else None)
        print(json.dumps(r, ensure_ascii=False))
    elif a[0] == "tools":
        for n in ("ffmpeg", "ffprobe", "node"):
            print(f"{n}: {tool(n)}")
    else:
        sys.exit(__doc__)
