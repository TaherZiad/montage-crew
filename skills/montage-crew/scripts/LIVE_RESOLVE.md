# LIVE Resolve mode (optional)

**You do not need this.** `compose.py` renders the final video without any editor, and `compose.py --xml` gives you a
timeline you can open in Resolve or Premiere. LIVE mode is for people who want to *watch* the video build up inside
DaVinci Resolve while the agents work, and to change things there themselves.

It relies on a third-party, open-source **DaVinci Resolve MCP server** that includes a *console bridge* (a small Lua file
you start from Resolve's Console). The bridge is what lets scripts talk to the **free** edition of Resolve. montage-crew
does not ship or install it; you install it yourself from its GitHub page and follow its README.

## Setup (once)

1. Install the Resolve MCP server at the **tested release tag `v4.8.20`** (repository link: INSTALL.md › LIVE Resolve
   mode; after `git clone`, run `git checkout v4.8.20`, not `main`), following its README, including its Python
   virtual environment and its console bridge. It is third-party software: review its options and keep its
   confirmations on. In its settings, add montage-crew's work and output folders (default `~/montage-crew-work` and
   `~/Videos/montage-crew`) to its allowed folders. Use an ASCII-only work folder.
   Note its folder (the one that contains `src/utils/resolve_bridge_client.py`) and its venv python
   (`venv\Scripts\python.exe` on Windows, `venv/bin/python` on macOS).
2. Tell montage-crew where it is. Either add this to `~/.montage-crew/profile.json` (or answer the onboarding question):
   ```json
   "resolve_live": { "enabled": true, "python": "<venv python path>", "mcp_dir": "<install folder>" }
   ```
   or set the environment variables `MC_RESOLVE_MCP_DIR` and `MC_RESOLVE_PYTHON`.
3. Open Resolve with a project, open **Workspace › Console**, choose **Lua**, and paste the bridge line from the MCP
   server's README (a `dofile(...)` line that runs the bridge's `resolve_bridge.lua`), press Enter and expect
   `listening on 127.0.0.1`. Leave Resolve open.

   **Warning:** while the bridge runs, programs on your computer can control Resolve. Start it only while editing and
   stop it afterwards (close Resolve, or stop the bridge as its README explains). The bridge also stops during a
   render (`render_live.py`); paste the line again to continue live work.
4. Check it:
   ```
   <venv python> <skill>/scripts/live.py ping
   ```
   It prints the Resolve version, the open project and timeline. Exit code 1 = not reachable (it says why).

## Use

All commands run with the MCP server's python (`$PYR`), not montage-crew's own venv:

| command | what it does |
|---|---|
| `$PYR live.py setup <work> <timeline>` | opens or creates the timeline (1080×1920 @ 30, named tracks) |
| `$PYR live.py put <work> <layer> <file> [--at S] [--in S] [--dur S]` | places or replaces one layer (plate, behind, aroll, speaker, split, captions, motion, extra, voice, music) |
| `$PYR live.py sfx <work> audio/sfx_cues.json` | places all sound effects on A3–A6 |
| `$PYR live.py camera <work> <layer> <file> <framing.json> [--parallax 0.4]` | smooth zooms as one clip per frame (the free edition has no keyframe API) |
| `$PYR live.py state <work>` | what you changed by hand since the last placement (exit 2 = changes) |
| `$PYR render_live.py <work> "<timeline>" <frames> <name> [--hd]` | renders the timeline, then frees the bridge |

Rules: it never deletes a timeline and never touches clips it did not place. If you moved, trimmed or deleted one of
its clips, your change wins and is reported. Re-rendered layers need a **new file name** (Resolve caches media by path).

## Limits

- Resolve 21.1 moved Python scripting inside Resolve to Studio; the Lua console bridge is what keeps the free edition
  working. If a future Resolve version blocks it, use `compose.py` (no Resolve needed) and import `timeline.xml`.
- If anything here fails, nothing else in montage-crew is affected.
