"""AI voice-over: script text -> <work>/audio/voice.wav (48 kHz) with ElevenLabs (default) or OpenAI.

  python tts.py <script.txt|-> --out <work>/audio/voice.wav [--provider elevenlabs|openai] [--voice ID] [--model M]
  python tts.py <script.txt|-> --out ... --dry-run     character count + which key variable, NO call, nothing sent
  python tts.py --selftest                            offline (the provider is faked)

Defaults come from the profile: voice.ai_provider, voice.ai_voice_id, voice.ai_key_env (the NAME of an environment
variable; the key itself is never stored, printed, logged, written or put on a command line or in a URL — it is sent
only in the provider's auth header). Endpoints are fixed in this file (https://api.elevenlabs.io, https://api.openai.com).
Paid call: show the --dry-run character count to the user and get a yes first. Limits per call: ElevenLabs 5000,
OpenAI 4096 characters (split longer scripts and run once per part).
"""
import argparse, json, os, pathlib, re, subprocess, sys, tempfile, urllib.error, urllib.request

sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mc_profile  # noqa: E402
import net  # noqa: E402
from mc_profile import FFMPEG  # noqa: E402

PROVIDERS = {
    "elevenlabs": {"env": ["ELEVENLABS_API_KEY", "XI_API_KEY"], "limit": 5000, "model": "eleven_multilingual_v2",
                   "voice": None, "voice_re": r"[A-Za-z0-9]{8,40}"},
    "openai": {"env": ["OPENAI_API_KEY"], "limit": 4096, "model": "gpt-4o-mini-tts", "voice": "alloy",
               "voice_re": r"[a-z]{2,20}"},
}
MAX_AUDIO = 60 << 20


def request(provider, text, voice, model):
    """(url, header names that carry the key, json body) — URL built only from fixed parts + a validated voice id."""
    if provider == "elevenlabs":
        return (f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128", "xi-api-key",
                {"text": text, "model_id": model})
    return ("https://api.openai.com/v1/audio/speech", "Authorization",
            {"model": model, "voice": voice, "input": text, "response_format": "mp3"})


def _post(url, headers, body):
    """HTTP POST -> bytes. Replaced in the selftest."""
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with net._build().open(req, timeout=120) as r:
        data = r.read(MAX_AUDIO + 1)
    if len(data) > MAX_AUDIO:
        raise SystemExit("the provider sent more audio than expected; nothing saved")
    return data


def settings(a):
    v = mc_profile.load_profile().get("voice") or {}
    provider = (a.provider or v.get("ai_provider") or "elevenlabs").lower()
    if provider not in PROVIDERS:
        raise SystemExit(f"provider {provider!r}: use one of {', '.join(PROVIDERS)}")
    P = PROVIDERS[provider]
    env = v.get("ai_key_env") if (v.get("ai_provider") or "elevenlabs").lower() == provider else None
    env = env or next((n for n in P["env"] if os.environ.get(n)), P["env"][0])
    why = mc_profile.key_env_problem(env, provider)
    if why:
        raise SystemExit(f"voice.ai_key_env: {why}")
    voice = a.voice or (v.get("ai_voice_id") if (v.get("ai_provider") or "").lower() == provider else None) or P["voice"]
    if not voice or not re.fullmatch(P["voice_re"], voice):
        raise SystemExit(f"--voice: a {provider} voice id is needed (pattern {P['voice_re']}); it is set in onboarding")
    model = a.model or P["model"]
    if not re.fullmatch(r"[a-z0-9_.-]{2,60}", model):
        raise SystemExit("--model: letters, digits, _ . - only")
    return provider, env, voice, model


def read_text(src):
    t = sys.stdin.read() if src == "-" else pathlib.Path(src).read_text(encoding="utf-8-sig")
    t = re.sub(r"[ \t]+", " ", t).strip()
    if not t:
        raise SystemExit("the script is empty")
    return t


def speak(text, out, provider, env, voice, model):
    P = PROVIDERS[provider]
    if len(text) > P["limit"]:
        raise SystemExit(f"{len(text)} characters > {P['limit']} for {provider}: split the script and run once per part")
    key = os.environ.get(env, "")
    if not key:
        raise SystemExit(f"the environment variable {env} is not set. Set it to your {provider} API key in YOUR terminal "
                         f"(Windows: setx {env} <key>, then open a new terminal; macOS: export {env}=<key> in ~/.zshrc). "
                         "Never paste the key in the chat.")
    url, hname, body = request(provider, text, voice, model)
    headers = {"Content-Type": "application/json", "User-Agent": net.UA,
               hname: key if hname == "xi-api-key" else f"Bearer {key}"}
    try:
        audio = _post(url, headers, body)
    except urllib.error.HTTPError as e:
        try:
            msg = e.read(4000).decode("utf-8", "replace")
        except Exception:
            msg = ""
        raise SystemExit(f"{provider} said HTTP {e.code}: {msg.replace(key, '***')[:600]}")
    except (urllib.error.URLError, OSError) as e:
        raise SystemExit(f"cannot reach {provider}: {str(getattr(e, 'reason', e)).replace(key, '***')}")
    if not audio:
        raise SystemExit(f"{provider} returned no audio")
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        mp3 = pathlib.Path(td) / "voice.mp3"
        mp3.write_bytes(audio)
        r = subprocess.run([FFMPEG, "-v", "error", "-y", "-protocol_whitelist", "file,pipe", "-i", str(mp3),
                            "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(out)], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"the audio from {provider} could not be converted: {r.stderr[-300:]}")
    return {"out": str(out), "provider": provider, "voice": voice, "chars": len(text)}


def selftest():
    global _post
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        os.environ["MONTAGE_CREW_HOME"] = str(d / "data")
        txt = d / "s.txt"
        txt.write_text("هلا بيكم، هذا اختبار صوت.", encoding="utf-8")
        ns = lambda **k: argparse.Namespace(**{**dict(provider=None, voice=None, model=None), **k})
        old = {k: os.environ.pop(k, None) for k in ("ELEVENLABS_API_KEY", "XI_API_KEY", "OPENAI_API_KEY")}
        try:
            try:
                settings(ns()); raise AssertionError("no voice id")
            except SystemExit as e:
                assert "voice id" in str(e)
            prov, env, voice, model = settings(ns(voice="AbCdEf1234567890"))
            assert (prov, env, model) == ("elevenlabs", "ELEVENLABS_API_KEY", "eleven_multilingual_v2")
            for bad in ("../../v1/user", "abc def", "x?y=1"):
                try:
                    settings(ns(voice=bad)); raise AssertionError(bad)
                except SystemExit:
                    pass
            assert settings(ns(provider="openai"))[2] == "alloy"
            text = read_text(str(txt))
            try:
                speak(text, d / "v.wav", prov, env, voice, model); raise AssertionError("no key")
            except SystemExit as e:
                assert "is not set" in str(e) and "ELEVENLABS_API_KEY" in str(e)
            secret = "sk-test-" + "Q" * 24
            os.environ["ELEVENLABS_API_KEY"] = secret
            mp3 = d / "t.mp3"
            subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=300:r=44100:d=0.5", str(mp3)], check=True)
            seen = {}

            def fake(url, headers, body):
                seen.update(url=url, headers=headers, body=body)
                return mp3.read_bytes()
            real, _post = _post, fake
            try:
                r = speak(text, d / "audio" / "voice.wav", prov, env, voice, model)
            finally:
                _post = real
            assert seen["url"] == "https://api.elevenlabs.io/v1/text-to-speech/AbCdEf1234567890?output_format=mp3_44100_128"
            assert seen["headers"]["xi-api-key"] == secret and secret not in seen["url"] + json.dumps(seen["body"])
            assert secret not in json.dumps(r) and r["chars"] == len(text)
            info = subprocess.run([mc_profile.FFPROBE, "-v", "error", "-show_entries", "stream=sample_rate,codec_name",
                                   "-of", "json", r["out"]], capture_output=True, text=True).stdout
            assert '"48000"' in info and "pcm_s16le" in info, info

            def leak(url, headers, body):
                raise urllib.error.HTTPError(url, 401, "no", {}, __import__("io").BytesIO(f"bad key {secret}".encode()))
            _post = leak
            try:
                speak(text, d / "v2.wav", prov, env, voice, model); raise AssertionError("401")
            except SystemExit as e:
                assert "401" in str(e) and secret not in str(e) and "***" in str(e), str(e)
            finally:
                _post = real
            try:
                speak("x" * 5001, d / "v3.wav", prov, env, voice, model); raise AssertionError("limit")
            except SystemExit as e:
                assert "split" in str(e)
            mc_profile.profile_path().parent.mkdir(parents=True, exist_ok=True)
            mc_profile.profile_path().write_text(json.dumps({"voice": {"kind": "ai", "ai_provider": "elevenlabs",
                                                                       "ai_key_env": "ANTHROPIC_API_KEY",
                                                                       "ai_voice_id": "AbCdEf1234567890"}}), encoding="utf-8")
            try:
                settings(ns()); raise AssertionError("reserved env name")
            except SystemExit as e:
                assert "reserved" in str(e)
        finally:
            for k, v in old.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v
            del os.environ["MONTAGE_CREW_HOME"]
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--provider", choices=sorted(PROVIDERS))
    ap.add_argument("--voice"); ap.add_argument("--model")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.script:
        return selftest()
    provider, env, voice, model = settings(a)
    text = read_text(a.script)
    if a.dry_run:
        res = {"provider": provider, "voice": voice, "model": model, "chars": len(text),
               "limit": PROVIDERS[provider]["limit"], "key_env": env, "key_set": bool(os.environ.get(env)), "sent": False}
    else:
        if not a.out:
            raise SystemExit("--out <work>/audio/voice.wav is required")
        res = speak(text, a.out, provider, env, voice, model)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
