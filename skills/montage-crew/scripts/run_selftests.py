"""Run every montage-crew selftest (offline: nothing is downloaded) and print one line per script.

  python run_selftests.py            all tests (~1-2 min: a few short renders)
  python run_selftests.py --quick    skip the render-heavy ones (compose, matte, jumpcut)
Exit 0 = all passed. Tests write only to temporary folders; the data dir is pointed at a temp folder too.
"""
import os, pathlib, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent
PY = [sys.executable]
TESTS = [  # (name, command, heavy)
    ("setup", PY + ["setup.py", "--selftest"], False),
    ("mc_profile", PY + ["mc_profile.py", "--selftest"], False),
    ("net", PY + ["net.py", "--selftest"], False),
    ("brand", PY + ["brand.py", "--selftest"], False),
    ("learn", PY + ["learn.py", "--selftest"], False),
    ("fetch_assets", PY + ["fetch_assets.py", "--selftest"], False),
    ("story", PY + ["story.py", "--selftest"], False),
    ("transcribe", PY + ["transcribe.py", "--selftest"], False),
    ("zones", PY + ["zones.py", "--selftest"], False),
    ("overlay_check", PY + ["overlay_check.py", "--selftest"], False),
    ("assets", PY + ["assets.py", "--selftest"], False),
    ("live", PY + ["live.py", "--selftest"], False),
    ("wall", PY + ["wall.py", "--selftest"], False),
    ("room", PY + ["room.py", "--selftest"], False),
    ("sheet", PY + ["sheet.py", "--selftest"], False),
    ("beat", PY + ["beat.py", "--selftest"], False),
    ("audio", PY + ["audio.py", "--selftest"], False),
    ("master", PY + ["master.py", "--selftest"], False),
    ("park", PY + ["park.py", "--selftest"], False),
    ("push", PY + ["push.py", "--selftest"], False),
    ("jumpcut", PY + ["jumpcut.py", "--selftest"], True),
    ("matte", PY + ["matte.py", "--selftest"], True),
    ("compose", PY + ["compose.py", "--selftest"], True),
]


def main():
    quick = "--quick" in sys.argv
    sys.dont_write_bytecode = True  # never write __pycache__ into the (plugin) skill folder
    sys.path.insert(0, str(HERE))
    import mc_profile
    tests = list(TESTS)
    node = mc_profile.tool("node")
    if (HERE.parent / "assets" / "rtl-kit.js").is_file() and os.path.isfile(node):
        tests.append(("kashida (node)", [node, "test_kashida.js"], False))
    fails = 0
    with tempfile.TemporaryDirectory() as data:
        env = {**os.environ, "MONTAGE_CREW_HOME": data, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1", "HF_HUB_DISABLE_TELEMETRY": "1"}
        for name, cmd, heavy in tests:
            if quick and heavy:
                print(f"  skip  {name}")
                continue
            t0 = time.time()
            r = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
            ok = r.returncode == 0
            fails += not ok
            print(f"{'  ok ' if ok else 'FAIL '}  {name:<15} {time.time() - t0:5.1f}s")
            if not ok:
                print("        " + (r.stdout + r.stderr).strip()[-1200:].replace("\n", "\n        "))
    print(f"\n{len(tests) - fails}/{len(tests)} passed" + ("" if not fails else f" — {fails} FAILED"))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
