"""montage-crew first-use setup. Standard library only; runs on any Python >= 3.8 (the venv it makes needs >= 3.10).

The user only unzips the skill into <claude-home>/skills/montage-crew/. The skill runs this on first use:

  python setup.py check [--json]        JSON status. Exit 0 ready · 2 a system tool is missing · 5 run `install`
  python setup.py tools                 the winget / brew / apt command for each missing system tool (one per line)
  python setup.py install [--offline] [--no-venv] [--gpu] [--no-selftest]
        ZIP install: venv in <data>/venv + pinned pip packages, GSAP (pinned SHA-256), agents/mc-*.md ->
        <claude-home>/agents/, the SKILL_DIR / DATA_DIR / PY placeholders filled in the .md files, <data>/installed.json,
        quick selftest.
        PLUGIN install (this skill is <root>/skills/montage-crew and <root>/.claude-plugin/plugin.json exists): the
        plugin folder is never written: no agents copied (the plugin provides montage-crew:mc-*), no placeholders filled
        (they resolve at runtime: `mc_profile.py path`), no data_dir.txt; venv, packages, GSAP (<data>/vendor/) and
        installed.json all go to the data dir.
  python setup.py install-ytdlp         OPTIONAL, only for learning from links, after the user said yes: yt-dlp
        (pinned version) into the data dir's venv.
        --offline: no network (no pip, no GSAP).  --no-venv: no venv and no pip; this Python becomes PY.
        --gpu: onnxruntime-gpu instead of onnxruntime (NVIDIA).
  python setup.py uninstall [--purge]   ZIP: remove every file in installed.json whose SHA-256 still matches (agents,
        skill folder), keep edited files. PLUGIN: nothing outside the data dir is touched (remove the plugin with
        /plugin). --purge (ask the user first) also deletes the data folder (profile, brand, styles, rules, venv, models).
Common: --claude-home DIR (default: the folder above skills/, else ~/.claude) · --data-home DIR (default:
$MONTAGE_CREW_HOME, else ~/.montage-crew).
Exit codes: 0 ok · 1 error · 2 missing prerequisite (nothing written) · 3 refused: a target exists that montage-crew
did not install (nothing written) · 4 installed but the selftest failed · 5 (check only) not set up yet.
Never touches other skills or agents (only <claude-home>/agents/mc-*.md and this skill's own folder).
"""
import argparse, datetime, hashlib, json, os, pathlib, platform, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # no __pycache__ in the skill folder from setup itself (a refused install writes 0 files)
import mc_profile  # noqa: E402  (stdlib only: tool lookup that never searches the cwd, UTF-8 stdout)

NAME = "montage-crew"
WIN = os.name == "nt"
MAC = sys.platform == "darwin"
TOKENS = tuple("{{%s}}" % k for k in ("SKILL_DIR", "DATA_DIR", "PY"))  # built, so this file holds no literal token
SKIP_DIRS = {"__pycache__", ".git", ".team", "node_modules"}
PY_MODULES = "faster_whisper, onnxruntime, numpy, scipy, cv2, PIL, requests"
GSAP_SHA = "c174bfce53a729418d57a8ad8625e7247c793a22fef8e2851e3cfa3de9cd8280"  # = fetch_assets.PINS["gsap"]
YTDLP_PIN = "2026.8.19"  # exact version; never -U (ARGUS C2)
PLUGIN = mc_profile.install_kind() == "plugin"


def gsap_path(data):
    return (data / "vendor" if PLUGIN else SKILL / "assets") / "gsap.min.js"


def say(msg):
    print(msg, flush=True)


def sha_file(p):
    h = hashlib.sha256()
    try:
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
    except OSError:
        return None
    return h.hexdigest()


# ---------- locations ----------
def homes(a):
    if a.claude_home:
        claude = pathlib.Path(a.claude_home).expanduser()
    elif PLUGIN:  # only reported; a plugin install never writes there
        claude = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR") or pathlib.Path.home() / ".claude")
    elif SKILL.parent.name == "skills":
        claude = SKILL.parent.parent
    else:
        claude = pathlib.Path.home() / ".claude"
    data = pathlib.Path(a.data_home).expanduser() if a.data_home else mc_profile.data_dir()
    return pathlib.Path(os.path.abspath(claude)), pathlib.Path(os.path.abspath(data))


def venv_py(data):
    return data / "venv" / ("Scripts/python.exe" if WIN else "bin/python")


def version():
    if PLUGIN:
        try:
            return json.loads((SKILL.parent.parent / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
        except (OSError, ValueError, KeyError):
            return "unknown"
    try:
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", (SKILL / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else "unknown"
    except OSError:
        return "unknown"


def manifest_path(data):
    """each install kind keeps its own record, so a plugin and a ZIP install can share one data dir."""
    return data / ("installed-plugin.json" if PLUGIN else "installed.json")


def load_manifest(data):
    try:
        m = json.loads(manifest_path(data).read_text(encoding="utf-8"))
        ok = isinstance(m, dict) and isinstance(m.get("files"), list)
        return m if ok and m.get("install_kind", "zip") == ("plugin" if PLUGIN else "zip") else None
    except (OSError, ValueError):
        return None


def write_manifest(data, m):
    data.mkdir(parents=True, exist_ok=True)
    tmp = manifest_path(data).with_suffix(".json.tmp")
    tmp.write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(manifest_path(data)))


def is_link(p):
    p = pathlib.Path(p)
    return p.is_symlink() or (WIN and p.exists() and os.path.realpath(str(p)).lower() != os.path.abspath(str(p)).lower())


def safe_target(path, skill, agents):
    """Only <skill>/** (skill folder named montage-crew) or <agents>/mc-*.md, never through a link/junction."""
    p = pathlib.Path(os.path.abspath(str(path)))
    if skill.name != NAME or agents.name != "agents":
        return False
    in_skill = skill in p.parents
    is_agent = p.parent == agents and re.fullmatch(r"mc-[\w-]+\.md", p.name) is not None
    if not (in_skill or is_agent):
        return False
    stop = skill.parent if in_skill else agents.parent
    q = p
    while q != stop and q != q.parent:
        if is_link(q):
            return False
        q = q.parent
    return True


# ---------- check / tools ----------
def run_out(cmd, timeout=30):
    try:
        r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.SubprocessError) as e:
        return 1, str(e)


def tool_info(name, args, pattern, minimum=None):
    exe = mc_profile.tool(name)
    if not os.path.isfile(exe):
        return {"ok": False, "path": None, "version": None}
    _, out = run_out([exe] + args)
    m = re.search(pattern, out)
    ver = m.group(1) if m else None
    ok = True
    if minimum and ver:
        ok = tuple(int(x) for x in re.findall(r"\d+", ver)[:2]) >= minimum
    return {"ok": ok and bool(ver or not minimum), "path": exe, "version": ver}


def gpu():
    if MAC and platform.machine() == "arm64":
        return "apple"
    return "cuda" if os.path.isfile(mc_profile.tool("nvidia-smi")) else "none"


def status(a):
    claude, data = homes(a)
    agents = claude / "agents"
    py_ok = sys.version_info >= (3, 10)
    st = {
        "version": version(), "install_kind": "plugin" if PLUGIN else "zip", "skill_dir": SKILL.as_posix(), "claude_home": claude.as_posix(), "data_dir": data.as_posix(),
        "os": "windows" if WIN else ("macos" if MAC else sys.platform),
        "gpu": gpu(),
        "ffmpeg": tool_info("ffmpeg", ["-version"], r"ffmpeg version n?([\w.\-]+)"),
        "ffprobe": tool_info("ffprobe", ["-version"], r"ffprobe version n?([\w.\-]+)"),
        "node": tool_info("node", ["--version"], r"v?(\d+\.\d+\.\d+)", (18, 0)),
        "python": {"ok": py_ok, "path": sys.executable, "version": platform.python_version()},
    }
    probe = data
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    try:
        st["disk_free_gb"] = round(shutil.disk_usage(str(probe)).free / 1e9, 1)
    except OSError:
        st["disk_free_gb"] = None
    man = load_manifest(data)
    vpy = pathlib.Path(man["python"]) if man and man.get("python") else venv_py(data)
    pk = vpy.is_file() and run_out([vpy, "-c", "import " + PY_MODULES], 120)[0] == 0
    st["venv"] = {"python": vpy.as_posix(), "exists": vpy.is_file(), "packages_ok": pk}
    st["py"] = vpy.as_posix() if vpy.is_file() else pathlib.Path(sys.executable).as_posix()
    st["assets"] = {"gsap": sha_file(gsap_path(data)) == GSAP_SHA, "gsap_path": gsap_path(data).as_posix()}
    st["optional"] = {"yt-dlp": tool_info("yt-dlp", ["--version"], r"(\d{4}\.\d+\.\d+)"),
                      "why": "only to learn from links (learn.py); install: setup.py install-ytdlp"}
    want = sorted(p.name for p in (SKILL / "agents").glob("mc-*.md"))
    st["agents"] = ({"provided_by": "plugin", "missing": []} if PLUGIN else
                    {"dir": agents.as_posix(), "missing": [n for n in want if not (agents / n).is_file()]})
    left = [p.name for p in SKILL.rglob("*.md") if not (SKIP_DIRS & set(p.relative_to(SKILL).parts))
            and p.parent != SKILL / "agents" and any(t.encode() in p.read_bytes() for t in TOKENS)]
    st["placeholders_left"] = [] if PLUGIN else left  # ZIP: a new ZIP unzipped over the old one -> install again
    st["installed"] = bool(man) and man.get("version") == st["version"] and not st["placeholders_left"]
    st["missing_tools"] = [n for n in ("ffmpeg", "ffprobe", "node", "python") if not st[n]["ok"]]
    st["ready"] = not st["missing_tools"] and st["installed"] and pk and not st["agents"]["missing"]
    st["detected"] = {"os": st["os"], "gpu": st["gpu"], "ffmpeg": st["ffmpeg"]["version"], "python": st["python"]["version"],
                      "node": st["node"]["version"], "at": datetime.datetime.now().isoformat(timespec="seconds")}
    return st


def cmd_check(a):
    st = status(a)
    print(json.dumps(st, indent=1, ensure_ascii=False))
    return 0 if st["ready"] else (2 if st["missing_tools"] else 5)


def tool_commands(missing):
    if WIN:
        ids = {"ffmpeg": "Gyan.FFmpeg", "ffprobe": "Gyan.FFmpeg", "node": "OpenJS.NodeJS.LTS", "python": "Python.Python.3.12"}
        return list(dict.fromkeys(f"winget install --id {ids[n]} -e --accept-source-agreements" for n in missing))
    if MAC:
        pk = {"ffmpeg": "ffmpeg", "ffprobe": "ffmpeg", "node": "node", "python": "python@3.12"}
        out = [] if os.path.isfile(mc_profile.tool("brew")) else [
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"']
        return out + list(dict.fromkeys(f"brew install {pk[n]}" for n in missing))
    pk = {"ffmpeg": "ffmpeg", "ffprobe": "ffmpeg", "node": "nodejs", "python": "python3 python3-venv"}
    return ["sudo apt-get install -y " + " ".join(dict.fromkeys(pk[n] for n in missing))] if missing else []


def cmd_tools(a):
    st = status(a)
    for c in tool_commands(st["missing_tools"]):
        print(c)
    if st["missing_tools"]:
        print("# then open a NEW terminal so PATH is refreshed", file=sys.stderr)
    return 0


# ---------- install ----------
def run(cmd, env=None):
    return subprocess.run([str(c) for c in cmd], env=env).returncode


def fill(b, values):
    t = b.decode("utf-8")
    for k, v in values.items():
        t = t.replace(k, v)
    return t.encode("utf-8")


def remove_files(entries, skill, agents):
    """Delete entries whose hash still matches; returns the entries kept (edited by the user)."""
    kept = []
    for f in entries:
        p = pathlib.Path(f.get("path", ""))
        if not safe_target(p, skill, agents):
            say(f"skipped (outside montage-crew): {p}")
            continue
        if not p.is_file():
            continue
        if f.get("sha256") and sha_file(p) != f["sha256"]:
            say(f"kept (changed since install): {p}")
            kept.append(f)
            continue
        p.unlink()
    return kept


def cmd_install(a):
    claude, data = homes(a)
    agents = claude / "agents"
    say(f"montage-crew {version()}\n  skill  {SKILL}\n  agents {agents}\n  data   {data}")
    st = status(a)
    need = [n for n in st["missing_tools"] if n != "python" or not a.no_venv]
    if need:
        say("MISSING: " + ", ".join(need) + ". Install with:\n  " + "\n  ".join(tool_commands(need)))
        say("Then open a new terminal and run setup again. Nothing was written.")
        return 2
    if SKILL.name != NAME:
        say(f"REFUSED: the skill folder must be named '{NAME}' (it is '{SKILL.name}'). Nothing was written.")
        return 3
    if data == SKILL or SKILL in data.parents or (PLUGIN and SKILL.parent.parent in (data, *data.parents)):
        say("REFUSED: the data folder must be outside the skill/plugin folder. Nothing was written.")
        return 3

    old = load_manifest(data)
    ours = {os.path.normcase(f["path"]) for f in (old or {}).get("files", [])}
    use_venv = not a.no_venv
    py = venv_py(data) if use_venv else pathlib.Path(sys.executable)
    values = dict(zip(TOKENS, (SKILL.as_posix(), data.as_posix(), py.as_posix())))

    # plan: agents to copy (filled) + .md files of the skill to fill in place
    plan = []
    for src in ([] if PLUGIN else sorted((SKILL / "agents").glob("mc-*.md"))):
        plan.append((agents / src.name, fill(src.read_bytes(), values)))
    for p in ([] if PLUGIN else sorted(SKILL.rglob("*.md"))):
        if SKIP_DIRS & set(p.relative_to(SKILL).parts):
            continue
        b = p.read_bytes()
        if any(t.encode() in b for t in TOKENS):
            plan.append((p, fill(b, values)))

    bad = [f"{agents} is a link/junction"] if is_link(agents) else []
    for dst, _ in plan:
        if not safe_target(dst, SKILL, agents):
            bad.append(f"unsafe target {dst}")
        elif dst.parent == agents and dst.exists() and os.path.normcase(str(dst)) not in ours:
            bad.append(f"{dst} exists and was not installed by montage-crew")
    if bad:
        for b in bad[:20]:
            say(f"REFUSED: {b}")
        say("Move or rename these, then run setup again. Nothing was written.")
        return 3

    # python env
    pip_line = f'"{py}" -m pip install -r "{SKILL / "requirements.txt"}"'
    if use_venv and not py.is_file():
        say("creating the Python environment ...")
        data.mkdir(parents=True, exist_ok=True)
        if run([sys.executable, "-m", "venv", data / "venv"]) != 0:
            say("ERROR: python -m venv failed (Linux: install python3-venv).")
            return 1
    if use_venv and not a.offline:
        reqs = (SKILL / "requirements.txt").read_text(encoding="utf-8")
        if a.gpu:
            reqs = re.sub(r"^onnxruntime==", "onnxruntime-gpu==", reqs, flags=re.M)
        with tempfile.TemporaryDirectory() as td:
            rp = pathlib.Path(td) / "requirements.txt"
            rp.write_text(reqs, encoding="utf-8")
            say("installing the Python packages (a few minutes, once) ...")
            if run([py, "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r", rp]) != 0:
                say(f"ERROR: pip install failed. Check the internet/proxy and run setup again, or: {pip_line}")
                return 1
    else:
        say(f"skipped the Python packages ({'--offline' if a.offline else '--no-venv'}). Later: {pip_line}")

    # write: agents + filled .md, then GSAP, then the manifest of every file in the skill + agents
    for dst, b in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(b)
    if not PLUGIN:
        (SKILL / "data_dir.txt").write_text(str(data) + "\n", encoding="utf-8")
    env = dict(os.environ, MONTAGE_CREW_HOME=str(data), PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    if not a.offline and run([py, "-B", HERE / "fetch_assets.py", "gsap", "--dest", gsap_path(data).parent], env) != 0:
        say("WARNING: GSAP download failed; it is fetched again on first use.")

    files = [{"path": str(dst), "sha256": sha_file(dst)} for dst, _ in plan if dst.parent == agents]
    for p in ([] if PLUGIN else sorted(SKILL.rglob("*"))):
        if p.is_file() and not (SKIP_DIRS & set(p.relative_to(SKILL).parts)) and p.suffix != ".pyc":
            files.append({"path": str(p), "sha256": sha_file(p)})
    gs = str(SKILL / "assets" / "gsap.min.js")
    if not PLUGIN and not any(f["path"] == gs for f in files):  # fetched later on first use -> still ours to remove
        files.append({"path": gs, "sha256": GSAP_SHA, "optional": True})
    new = {os.path.normcase(f["path"]) for f in files}
    stale = [f for f in (old or {}).get("files", []) if os.path.normcase(f["path"]) not in new]
    kept = remove_files(stale, SKILL, agents)  # e.g. an agent dropped in a newer version
    write_manifest(data, {"name": NAME, "version": version(), "install_kind": "plugin" if PLUGIN else "zip",
                          "installed": datetime.datetime.now().isoformat(timespec="seconds"),
                          "claude_home": str(claude), "skill_dir": str(SKILL), "agents_dir": str(agents),
                          "data_dir": str(data), "python": str(py), "venv": use_venv, "files": files + kept})
    say(f"agents: {sum(1 for d, _ in plan if d.parent == agents)} registered · {len(files)} files recorded")

    if a.no_selftest:
        say("ready (selftest skipped).")
        return 0
    say("running the quick selftest ...")
    if run([py, "-B", HERE / "run_selftests.py", "--quick"], env) != 0:
        say(f"INSTALLED, but the selftest failed (exit 4). If packages are missing: {pip_line}")
        return 4
    say("ready.")
    return 0


def cmd_install_ytdlp(a):
    """yt-dlp==YTDLP_PIN into the data venv (only after the user said yes; learning from links is optional)."""
    claude, data = homes(a)
    py = venv_py(data)
    if not py.is_file():
        say("run `setup.py install` first (the Python environment is missing).")
        return 2
    say(f"installing yt-dlp {YTDLP_PIN} (optional, for learning from links) ...")
    if run([py, "-m", "pip", "install", "--disable-pip-version-check", "-q", f"yt-dlp=={YTDLP_PIN}"]) != 0:
        say("ERROR: pip could not install yt-dlp. Learning from links stays off; local files still work.")
        return 1
    say("yt-dlp ready.")
    return 0


# ---------- uninstall ----------
def prune(skill):
    if not skill.is_dir() or is_link(skill):
        return
    for d in sorted((x for x in skill.rglob("__pycache__") if x.is_dir()), key=lambda x: len(x.parts), reverse=True):
        shutil.rmtree(str(d), ignore_errors=True)
    for d in sorted((x for x in skill.rglob("*") if x.is_dir()), key=lambda x: len(x.parts), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass
    try:
        skill.rmdir()
    except OSError:
        say(f"kept {skill} (it still holds files montage-crew did not install, or a window is open in it)")


def _force_rm(func, path, _exc):
    os.chmod(path, 0o700)
    func(path)


def cmd_uninstall(a):
    claude, data = homes(a)
    if a.purge and data in pathlib.Path(sys.executable).resolve().parents:
        say(f"ERROR: run uninstall with the system Python ({'py -3' if WIN else 'python3'}), not the venv one. Nothing removed.")
        return 1
    m = load_manifest(data)  # the record of THIS setup.py's kind only
    if m and PLUGIN:
        manifest_path(data).unlink()
        say("plugin install: nothing to remove outside the data folder (remove the plugin itself with /plugin).")
    elif m:
        skill = pathlib.Path(m.get("skill_dir") or SKILL)
        agents = pathlib.Path(m.get("agents_dir") or claude / "agents")
        if skill.name != NAME or agents.name != "agents":
            say("ERROR: installed.json does not point at a montage-crew skill / agents folder. Nothing removed.")
            return 1
        kept = remove_files(m["files"], skill, agents)
        prune(skill)
        if kept:
            write_manifest(data, dict(m, files=kept))
            say(f"removed montage-crew; {len(kept)} edited file(s) kept (listed above).")
        else:
            manifest_path(data).unlink()
            say("removed montage-crew (skill folder and mc-* agents).")
    else:
        say(f"nothing to remove: no {manifest_path(data).name} in {data}")
    other = data / ("installed.json" if PLUGIN else "installed-plugin.json")
    if a.purge and other.is_file():
        say(f"note: the other install ({'ZIP' if PLUGIN else 'plugin'}) also uses {data}; --purge removes its data too.")
    if a.purge and data.is_dir():
        if not (m or other.is_file() or data.name == ".montage-crew" or (data / "profile.json").is_file()):
            say(f"not purging {data}: it does not look like a montage-crew data folder.")
            return 1
        shutil.rmtree(str(data), onerror=_force_rm)
        say(f"purged {data}")
    elif data.is_dir():
        say(f"kept your data: {data} (add --purge to delete it)")
    return 0


# ---------- selftest (offline, temp dirs only) ----------
def selftest():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        skill, agents = d / "c" / "skills" / NAME, d / "c" / "agents"
        assert safe_target(skill / "SKILL.md", skill, agents)
        assert safe_target(agents / "mc-qa.md", skill, agents)
        assert not safe_target(agents / "reel-qa.md", skill, agents)
        assert not safe_target(d / "c" / "skills" / "other-skill" / "SKILL.md", skill, agents)
        assert not safe_target(skill / ".." / "other" / "x", skill, agents)
        assert not safe_target(d / "c" / "skills" / "x" / "SKILL.md", d / "c" / "skills" / "x", agents)
        src = ("run %s %s/x {{ keep }}" % (TOKENS[2], TOKENS[0])).encode()
        assert fill(src, {TOKENS[2]: "P", TOKENS[0]: "S"}) == b"run P S/x {{ keep }}"
        (skill).mkdir(parents=True)
        f = skill / "a.txt"
        f.write_text("x", encoding="utf-8")
        g = skill / "b.txt"
        g.write_text("y", encoding="utf-8")
        kept = remove_files([{"path": str(f), "sha256": sha_file(f)}, {"path": str(g), "sha256": "0" * 64}], skill, agents)
        assert not f.exists() and g.exists() and len(kept) == 1
        import fetch_assets
        assert GSAP_SHA == fetch_assets.PINS["gsap"]["sha256"], "GSAP pin out of sync with fetch_assets.py"
    # plugin mode end to end: install/check/uninstall --purge write nothing under the plugin folder and no agents
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        root, home = d / "plugin", d / "claude"
        sk = root / "skills" / NAME
        shutil.copytree(SKILL / "scripts", sk / "scripts", ignore=shutil.ignore_patterns("__pycache__", "tests"))
        shutil.copytree(SKILL / "templates", sk / "templates")
        shutil.copyfile(SKILL / "requirements.txt", sk / "requirements.txt")
        (sk / "SKILL.md").write_text("run %s/scripts/x.py\n" % TOKENS[0], encoding="utf-8")
        (root / "agents").mkdir()
        (root / "agents" / "mc-qa.md").write_text("x %s\n" % TOKENS[2], encoding="utf-8")
        (root / ".claude-plugin").mkdir()
        (root / ".claude-plugin" / "plugin.json").write_text('{"name": "montage-crew", "version": "9.9.9"}', encoding="utf-8")
        snap = lambda: {p.relative_to(root).as_posix(): sha_file(p) for p in root.rglob("*") if p.is_file()}
        before = snap()
        data = d / "data"
        env = dict(os.environ, MONTAGE_CREW_HOME=str(data), PYTHONIOENCODING="utf-8")
        go = lambda *x: subprocess.run([sys.executable, str(sk / "scripts" / "setup.py"), *x, "--claude-home", str(home)],
                                       env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        data.mkdir()
        zip_rec = json.dumps({"name": NAME, "install_kind": "zip", "files": [{"path": str(d / "zip" / "x"), "sha256": "0"}]})
        (data / "installed.json").write_text(zip_rec, encoding="utf-8")   # a ZIP install sharing the data dir (BUG-V2-01)
        r = go("install", "--offline", "--no-venv", "--no-selftest")
        assert r.returncode == 0 and "outside montage-crew" not in r.stdout, r.stdout + r.stderr
        assert (data / "installed.json").read_text(encoding="utf-8") == zip_rec, "the ZIP record must stay untouched"
        m = json.loads((data / "installed-plugin.json").read_text(encoding="utf-8"))
        assert m["install_kind"] == "plugin" and m["version"] == "9.9.9" and m["files"] == [], m
        st = json.loads(go("check").stdout)
        assert st["install_kind"] == "plugin" and st["agents"]["provided_by"] == "plugin" and st["placeholders_left"] == []
        assert st["installed"] and st["assets"]["gsap_path"].endswith("/vendor/gsap.min.js") and "yt-dlp" in st["optional"]
        r = go("uninstall")
        assert r.returncode == 0 and not (data / "installed-plugin.json").exists(), r.stdout
        assert (data / "installed.json").read_text(encoding="utf-8") == zip_rec, "plugin uninstall left the ZIP record"
        r = go("uninstall", "--purge")
        assert r.returncode == 0 and not data.exists() and "other install" in r.stdout, r.stdout
        assert snap() == before, set(snap().items()) ^ set(before.items())
        assert not (home / "agents").exists() and not list(root.rglob("__pycache__")) and not list(root.rglob("data_dir.txt"))
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return 0
    ap = argparse.ArgumentParser(prog="setup.py", description="montage-crew first-use setup")
    ap.add_argument("action", choices=["check", "tools", "install", "install-ytdlp", "uninstall"])
    ap.add_argument("--claude-home")
    ap.add_argument("--data-home")
    ap.add_argument("--json", action="store_true", help="check: JSON output (always on)")
    ap.add_argument("--no-venv", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--purge", action="store_true")
    ap.add_argument("--no-selftest", action="store_true")
    a = ap.parse_args()
    try:
        return {"check": cmd_check, "tools": cmd_tools, "install": cmd_install, "install-ytdlp": cmd_install_ytdlp,
                "uninstall": cmd_uninstall}[a.action](a)
    except KeyboardInterrupt:
        return 1
    except Exception as e:  # one readable line, exit 1 = other error
        say(f"ERROR: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
