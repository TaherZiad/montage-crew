"""Arabic word-level transcription with faster-whisper.

usage: python transcribe.py <video|audio> [--model large-v3|medium|small] [--out words.json] [--cpu] [--prompt "<topic hint>"]
       python transcribe.py --selftest
writes: words.json  [{"w": word, "s": start, "e": end}]  and  transcript.txt (one segment per line with times)
Device: NVIDIA GPU when CTranslate2 sees one (int8_float16), else CPU int8 — no setup needed for either.
The model is a pinned download (fetch_assets.py, hash-checked) the first time; large-v3 ~3 GB, small ~0.5 GB.
The default topic hint comes from the dialect in the user's profile; --prompt overrides it.
"""
import argparse, json, os, pathlib, sys

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mc_profile  # noqa: E402

DIALECT_NAME = {"iraqi": "العراقية", "gulf": "الخليجية", "levantine": "الشامية", "egyptian": "المصرية",
                "maghrebi": "المغاربية", "sudanese": "السودانية", "yemeni": "اليمنية"}


def default_prompt(profile):
    lang = profile["language"]
    d = lang.get("dialect") or "msa"
    if d in DIALECT_NAME:
        return f"كلام باللهجة {DIALECT_NAME[d]} في فيديو قصير."
    if d == "other" and lang.get("dialect_note"):
        return f"كلام باللهجة {lang['dialect_note']} في فيديو قصير."
    return "كلام باللغة العربية في فيديو قصير."


def to_words(segs):
    words, lines = [], []
    for s in segs:
        lines.append(f"[{s.start:6.2f} → {s.end:6.2f}] {s.text.strip()}")
        for w in s.words or []:
            if w.word.strip():
                words.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    return words, lines


def _cuda_dlls():
    """Windows + a torch CUDA wheel in the same venv: its lib/ holds cuBLAS/cuDNN that CTranslate2 can use."""
    if os.name != "nt":
        return
    try:
        import torch
        os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
    except Exception:
        pass


def load_model(size, cpu):
    from faster_whisper import WhisperModel
    import fetch_assets
    path = fetch_assets.ensure_whisper(size)
    if not cpu:
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                _cuda_dlls()
                return WhisperModel(path, device="cuda", compute_type="int8_float16"), "cuda"
        except Exception as e:
            print(f"GPU unavailable ({type(e).__name__}) -> CPU")
    return WhisperModel(path, device="cpu", compute_type="int8"), "cpu"


def selftest():
    from types import SimpleNamespace as N
    p = mc_profile.load_profile()
    p["language"] = {"dialect": "egyptian", "dialect_note": "", "set_words": [], "digits": "western"}
    assert "المصرية" in default_prompt(p)
    p["language"]["dialect"] = "other"; p["language"]["dialect_note"] = "الحسانية"
    assert "الحسانية" in default_prompt(p)
    p["language"]["dialect"] = "msa"
    assert "العربية" in default_prompt(p)
    segs = [N(start=0.0, end=1.2, text=" مرحبا بكم ", words=[N(word=" مرحبا", start=0.0, end=0.5),
                                                             N(word=" ", start=0.5, end=0.5), N(word="بكم", start=0.6, end=1.2)])]
    w, l = to_words(segs)
    assert [x["w"] for x in w] == ["مرحبا", "بكم"] and w[1]["e"] == 1.2 and "مرحبا بكم" in l[0]
    import faster_whisper  # noqa: F401  (the dependency is installed)
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--out", default=None)
    ap.add_argument("--cpu", action="store_true", help="force CPU int8")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.video:
        return selftest()
    src = pathlib.Path(a.video)
    out = pathlib.Path(a.out) if a.out else src.with_name("words.json")
    prompt = a.prompt or default_prompt(mc_profile.load_profile())
    model, dev = load_model(a.model, a.cpu)
    print(f"whisper {a.model} on {dev}")
    # condition_on_previous_text=False: with it on, a long take can loop one line several times and lose real speech
    segs, info = model.transcribe(str(src), language="ar", word_timestamps=True, vad_filter=True,
                                  initial_prompt=prompt, condition_on_previous_text=False)
    words, lines = to_words(segs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    out.with_name("transcript.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(words)} words, {info.duration:.1f}s -> {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
