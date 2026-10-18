"""Download the files montage-crew does not ship, from pinned URLs, and verify each one by SHA-256.

  python fetch_assets.py status                 what is present / verified
  python fetch_assets.py gsap [--dest DIR]      GSAP 3.14.2 (jsDelivr) -> <skill>/assets/gsap.min.js (licence: gsap.com/standard-license)
  python fetch_assets.py rvm                    RobustVideoMatting mobilenetv3 ONNX (GitHub release, GPL-3.0) -> <data>/models/rvm/
  python fetch_assets.py whisper <large-v3|medium|small>   faster-whisper model (Hugging Face, pinned revision, model.bin hash)
  python fetch_assets.py --selftest             offline checks of the verify/download logic

Nothing is installed without these checks: a file whose hash does not match is deleted and the command exits 1.
Sizes are printed before each download.
"""
import hashlib, json, os, pathlib, shutil, sys, tempfile, urllib.request

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mc_profile  # noqa: E402

PINS = {
    "gsap": {"url": "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js", "size": 72779,
             "sha256": "c174bfce53a729418d57a8ad8625e7247c793a22fef8e2851e3cfa3de9cd8280", "name": "gsap.min.js"},
    "rvm": {"url": "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx",
            "size": 14975696, "sha256": "88d4531297118f595bf2fd60f6f566aec2e559393802d1f436c380f0cbbd2828",
            "name": "rvm_mobilenetv3_fp32.onnx"},
}
# faster-whisper (CTranslate2 conversions by Systran on Hugging Face): pinned commit + model.bin SHA-256
WHISPER = {
    "large-v3": {"repo": "Systran/faster-whisper-large-v3", "rev": "edaa852ec7e145841d8ffdb056a99866b5f0a478",
                 "bin": "69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1", "approx": "3.1 GB"},
    "medium": {"repo": "Systran/faster-whisper-medium", "rev": "08e178d48790749d25932bbc082711ddcfdfbc4f",
               "bin": "9b45e1009dcc4ab601eff815b61d80e60ce3fd8c74c1a14f4a282258286b51ae", "approx": "1.5 GB"},
    "small": {"repo": "Systran/faster-whisper-small", "rev": "536b0662742c02347bc0e980a01041f333bce120",
              "bin": "3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671", "approx": "0.5 GB"},
}


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while b := f.read(chunk):
            h.update(b)
    return h.hexdigest()


def models_dir():
    return mc_profile.data_dir() / "models"


def _verified_marker(path):
    """Big files: hash once, then trust (size, mtime) recorded next to the data dir."""
    st = os.stat(path)
    return f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}"


def _marker_file():
    return models_dir() / "verified.json"


def is_verified(path, want):
    try:
        seen = json.loads(_marker_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        seen = {}
    key = _verified_marker(path)
    if seen.get(key) == want:
        return True
    if sha256(path) != want:
        return False
    seen[key] = want
    _marker_file().parent.mkdir(parents=True, exist_ok=True)
    _marker_file().write_text(json.dumps(seen, indent=1), encoding="utf-8")
    return True


def download(url, dest, want_sha, size=None, timeout=60, schemes=("https",)):
    """Stream url -> dest.part, verify, then rename. Never leaves an unverified file at dest."""
    if url.split(":", 1)[0] not in schemes:
        raise SystemExit(f"❌ refusing {url.split(':', 1)[0]}: URL (https only)")
    dest = pathlib.Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if size:
        print(f"downloading {dest.name} ({size / 1e6:.1f} MB) from {url}")
    tmp = dest.with_name(dest.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "montage-crew"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    got = sha256(tmp)
    if got != want_sha:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"❌ {dest.name}: SHA-256 mismatch (got {got[:16]}…, want {want_sha[:16]}…) — file removed")
    os.replace(tmp, dest)
    return dest


def ensure_gsap(dest_dir=None):
    pin = PINS["gsap"]
    dest = pathlib.Path(dest_dir or mc_profile.SKILL_DIR / "assets") / pin["name"]
    if dest.is_file() and sha256(dest) == pin["sha256"]:
        return dest
    return download(pin["url"], dest, pin["sha256"], pin["size"])


def ensure_rvm():
    """RVM model path, downloading it the first time. A copy left by an earlier tool in ~/.cache/rvm is reused
    only when its hash matches."""
    pin = PINS["rvm"]
    for cand in (models_dir() / "rvm" / pin["name"], pathlib.Path.home() / ".cache" / "rvm" / pin["name"]):
        if cand.is_file() and is_verified(cand, pin["sha256"]):
            return cand
    return download(pin["url"], models_dir() / "rvm" / pin["name"], pin["sha256"], pin["size"])


def ensure_whisper(size, local_only=False):
    """Local folder of a pinned faster-whisper model (downloaded the first time). Unknown sizes are refused:
    only pinned models are fetched."""
    if size not in WHISPER:
        raise SystemExit(f"❌ unknown model {size!r}: choose one of {', '.join(WHISPER)}")
    pin = WHISPER[size]
    from faster_whisper.utils import download_model
    try:
        path = download_model(pin["repo"], revision=pin["rev"], local_files_only=True)
    except Exception:
        if local_only:
            return None
        print(f"downloading whisper {size} (~{pin['approx']}, once) from huggingface.co/{pin['repo']}")
        path = download_model(pin["repo"], revision=pin["rev"])
    model_bin = pathlib.Path(path) / "model.bin"
    if not is_verified(model_bin, pin["bin"]):
        raise SystemExit(f"❌ whisper {size}: model.bin hash mismatch — delete {path} and run again")
    return path


def status():
    pin = PINS["gsap"]
    g = mc_profile.SKILL_DIR / "assets" / pin["name"]
    print(f"gsap     : {'ok' if g.is_file() and sha256(g) == pin['sha256'] else 'missing (fetched at install / first use)'}")
    r = [c for c in (models_dir() / "rvm" / PINS['rvm']['name'], pathlib.Path.home() / ".cache/rvm" / PINS['rvm']['name'])
         if c.is_file()]
    print(f"rvm      : {'present ' + str(r[0]) if r else 'missing (downloaded on first matte, 15 MB)'}")
    for s in WHISPER:
        try:
            p = ensure_whisper(s, local_only=True)
        except (SystemExit, ImportError) as e:
            p = f"error: {e}"
        print(f"whisper {s:8}: {p or 'missing (downloaded on first use, ' + WHISPER[s]['approx'] + ')'}")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        os.environ["MONTAGE_CREW_HOME"] = str(d / "data")
        src = d / "src.bin"
        src.write_bytes(b"montage-crew" * 1000)
        good = sha256(src)
        assert good == hashlib.sha256(b"montage-crew" * 1000).hexdigest()
        url = src.as_uri()
        out = download(url, d / "out" / "a.bin", good, schemes=("file",))
        try:
            download(url, d / "out" / "c.bin", good)
            raise AssertionError("file: URL accepted")
        except SystemExit:
            pass
        assert out.read_bytes() == src.read_bytes()
        try:
            download(url, d / "out" / "b.bin", "0" * 64, schemes=("file",))
            raise AssertionError("bad hash accepted")
        except SystemExit:
            pass
        assert not (d / "out" / "b.bin").exists() and not (d / "out" / "b.bin.part").exists()
        assert is_verified(out, good) and is_verified(out, good)          # 2nd call uses the marker
        assert not is_verified(src, "f" * 64)
        try:
            ensure_whisper("tiny-unpinned")
            raise AssertionError("unpinned model accepted")
        except SystemExit:
            pass
        del os.environ["MONTAGE_CREW_HOME"]
    for k, p in PINS.items():
        assert p["url"].startswith("https://") and len(p["sha256"]) == 64, k
    assert all(len(w["rev"]) == 40 and len(w["bin"]) == 64 for w in WHISPER.values())
    print("selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if not a or a[0] == "--selftest":
        selftest()
    elif a[0] == "status":
        status()
    elif a[0] == "gsap":
        print("✅", ensure_gsap(a[a.index("--dest") + 1] if "--dest" in a else None))
    elif a[0] == "rvm":
        print("✅", ensure_rvm())
    elif a[0] == "whisper":
        print("✅", ensure_whisper(a[1] if len(a) > 1 else "large-v3"))
    else:
        sys.exit(__doc__)
