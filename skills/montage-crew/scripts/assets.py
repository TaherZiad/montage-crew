#!/usr/bin/env python3
"""Find + download free-for-commercial assets for reels (no login, keys optional).

  python scripts/assets.py search <kind> "<query>" [--n 8] [--orientation portrait|landscape] [--set lucide]
  python scripts/assets.py download <id|url> [<id> ...] --to <dir> [--manifest path] [--no-manifest]
  python scripts/assets.py kinds

  python scripts/assets.py --selftest

kinds: photo video icon logo svg illustration lottie model3d texture overlay sfx ui
--n is per source. Results are cached in the temp folder (montage_crew_assets_cache.json), so `download`
takes the ids printed by the last searches. `ui` takes a URL/domain as the query (needs `pip install playwright`).
Keys are read ONLY from environment variables, never from a file. Mixkit is not searched: its terms forbid
scripted downloads (open mixkit.co yourself if you want their files).
Optional keys (env): PEXELS_API_KEY PIXABAY_API_KEY UNSPLASH_ACCESS_KEY FREESOUND_API_KEY SKETCHFAB_API_TOKEN
Licence notes live in references/asset-sourcing.md.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
import requests
from html import unescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mc_profile  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
UA = {"User-Agent": "montage-crew/1.0 (asset search for short-video editing)"}
TMP = Path(tempfile.gettempdir())
CACHE = TMP / "montage_crew_assets_cache.json"
KEY = {k: os.environ.get(k) for k in ("PEXELS_API_KEY", "PIXABAY_API_KEY", "UNSPLASH_ACCESS_KEY", "FREESOUND_API_KEY", "SKETCHFAB_API_TOKEN")}
OV_LIC = "cc0,pdm,by"  # Openverse: no NC / ND / SA


def get(url, **kw):
    kw.setdefault("timeout", 30)
    r = requests.get(url, headers={**UA, **kw.pop("headers", {})}, **kw)
    r.raise_for_status()
    return r


def rec(src, nid, title, url, licence, author="", page="", w=None, h=None, preview="", dl="http", **extra):
    return dict(id=f"{src}:{nid}", source=src, title=(title or "").strip()[:80], url=url, licence=licence,
                author=author or "", page=page or url, w=w, h=h, preview=preview or "", dl=dl, **extra)


def cached_json(name, url, days=7):
    p = TMP / f"montage_crew_assets_{name}.json"
    if p.exists() and time.time() - p.stat().st_mtime < days * 86400:
        return json.loads(p.read_text(encoding="utf-8"))
    data = get(url).json()
    p.write_text(json.dumps(data), encoding="utf-8")
    return data


def words(q):
    return [w for w in re.split(r"[\s_\-]+", q.lower()) if w]


# ---------------------------------------------------------------- sources
def pexels(q, n, o, video=False):
    if not KEY["PEXELS_API_KEY"]:
        return []
    url = "https://api.pexels.com/videos/search" if video else "https://api.pexels.com/v1/search"
    p = {"query": q, "per_page": n, **({"orientation": o} if o else {})}
    js = get(url, params=p, headers={"Authorization": KEY["PEXELS_API_KEY"]}).json()
    out = []
    for it in js.get("videos" if video else "photos", []):
        if video:
            f = max((f for f in it["video_files"] if (f.get("width") or 0) <= 3840), key=lambda f: f.get("width") or 0)
            out.append(rec("pexels", f"v{it['id']}", it["url"].rstrip("/").split("/")[-1], f["link"], "Pexels License",
                           it["user"]["name"], it["url"], f["width"], f["height"], it["image"], duration=it["duration"]))
        else:
            out.append(rec("pexels", it["id"], it.get("alt") or "photo", it["src"]["original"], "Pexels License",
                           it["photographer"], it["url"], it["width"], it["height"], it["src"]["medium"]))
    return out


def pixabay(q, n, o, video=False):
    if not KEY["PIXABAY_API_KEY"]:
        return []
    url = "https://pixabay.com/api/videos/" if video else "https://pixabay.com/api/"
    p = {"key": KEY["PIXABAY_API_KEY"], "q": q, "per_page": max(3, n), "safesearch": "true"}
    if o and not video:
        p["orientation"] = {"portrait": "vertical", "landscape": "horizontal"}[o]
    out = []
    for it in get(url, params=p).json().get("hits", [])[:n]:
        if video:
            f = it["videos"].get("large") or it["videos"]["medium"]
            out.append(rec("pixabay", f"v{it['id']}", it["tags"], f["url"], "Pixabay Content License", it["user"],
                           it["pageURL"], f["width"], f["height"], f.get("thumbnail", ""), duration=it["duration"]))
        else:
            out.append(rec("pixabay", it["id"], it["tags"], it["largeImageURL"], "Pixabay Content License", it["user"],
                           it["pageURL"], it["imageWidth"], it["imageHeight"], it["previewURL"]))
    return out


def unsplash(q, n, o):
    if not KEY["UNSPLASH_ACCESS_KEY"]:
        return []
    p = {"query": q, "per_page": n, **({"orientation": "portrait" if o == "portrait" else "landscape"} if o else {})}
    js = get("https://api.unsplash.com/search/photos", params=p,
             headers={"Authorization": f"Client-ID {KEY['UNSPLASH_ACCESS_KEY']}"}).json()
    return [rec("unsplash", it["id"], it.get("alt_description") or "photo", it["urls"]["full"], "Unsplash License",
                it["user"]["name"], it["links"]["html"], it["width"], it["height"], it["urls"]["small"],
                ping=it["links"]["download_location"]) for it in js["results"]]


def openverse(q, n, o, audio=False, ext=None):
    p = {"q": q, "page_size": n, "license": OV_LIC, "mature": "false"}
    if o and not audio:
        p["aspect_ratio"] = "tall" if o == "portrait" else "wide"
    if ext:
        p["extension"] = ext
    js = get(f"https://api.openverse.org/v1/{'audio' if audio else 'images'}/", params=p).json()
    out = []
    for it in js["results"]:
        lic = {"cc0": "CC0", "pdm": "Public Domain Mark"}.get(it["license"], f"CC {it['license'].upper()} {it.get('license_version') or ''}".strip())
        out.append(rec("openverse", it["id"][:13], it.get("title"), it["url"], lic, unquote(it.get("creator") or ""),
                       it.get("foreign_landing_url"), it.get("width"), it.get("height"), it.get("thumbnail"),
                       duration=(it.get("duration") or 0) / 1000 if audio else None, via=it.get("source")))
    return out


def commons(q, n, o, filetype="bitmap"):
    p = dict(action="query", format="json", generator="search", gsrsearch=f"{q} filetype:{filetype}", gsrnamespace=6,
             gsrlimit=n * 2, prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=400)
    pages = get("https://commons.wikimedia.org/w/api.php", params=p).json().get("query", {}).get("pages", {})
    out = []
    for pg in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]
        md = ii.get("extmetadata", {})
        lic = re.sub("<[^>]+>", "", md.get("LicenseShortName", {}).get("value", "?"))
        if not re.search(r"cc0|public domain|^pd|^cc by[\s\d.]*$", lic, re.I):
            continue  # only CC0 / PD / CC BY: no SA, NC, ND, GPL, fair use
        author = " ".join(re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).split())[:60]
        out.append(rec("commons", pg["pageid"], pg["title"][5:], ii["url"], lic, author, ii["descriptionurl"],
                       ii.get("width"), ii.get("height"), ii.get("thumburl", ""), mime=ii.get("mime")))
    return out[:n]


def iconify(q, n, o, prefixes=None):
    p = {"query": q, "limit": max(32, n)}
    if prefixes:
        p["prefixes"] = prefixes
    js = get("https://api.iconify.design/search", params=p).json()
    cols = js.get("collections", {})
    out = []
    for full in js.get("icons", [])[:n]:
        pre, name = full.split(":", 1)
        c = cols.get(pre, {})
        out.append(rec("iconify", full, f"{c.get('name', pre)} / {name}", f"https://api.iconify.design/{pre}/{name}.svg?height=512",
                       c.get("license", {}).get("title", "?"), c.get("author", {}).get("name", ""),
                       f"https://icon-sets.iconify.design/{pre}/?icon-filter={name}", ext=".svg"))
    return out


def lobehub(q, n, o):
    v = cached_json("lobehub_ver", "https://data.jsdelivr.com/v1/packages/npm/@lobehub/icons-static-svg/resolved")["version"]
    files = cached_json(f"lobehub_{v}", f"https://data.jsdelivr.com/v1/packages/npm/@lobehub/icons-static-svg@{v}?structure=flat", 30)
    slug = q.lower().replace(" ", "")
    names = [f["name"] for f in files["files"] if f["name"].startswith("/icons/") and slug in f["name"]]
    names.sort(key=lambda s: (not s.endswith(f"/{slug}-color.svg"), not s.endswith(f"/{slug}.svg"), len(s)))
    return [rec("lobehub", nm[7:-4], f"LobeHub {nm[7:-4]}", f"https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@{v}{nm}",
                "MIT (icon set) / brand trademark", "LobeHub", "https://lobehub.com/icons", ext=".svg") for nm in names[:n]]


def undraw(q, n, o):
    js = get("https://undraw.co/api/search", params={"q": q}).json()
    return [rec("undraw", it["newSlug"], it["title"], it["media"], "unDraw License (free, no attribution)", "Katerina Limpitsouni",
                f"https://undraw.co/search/{quote(q)}", ext=".svg") for it in js.get("results", [])[:n]]


def storyset(q, n, o):
    js = get("https://stories.freepiklabs.com/api/vectors", params={"query": q}).json()
    return [rec("storyset", it["id"], f"{it['slug']}", it["src"], "Storyset/Freepik free licence — ATTRIBUTION REQUIRED",
                "Storyset by Freepik", it["url"], preview=it["preview_no_bg"], ext=".svg") for it in js.get("data", [])[:n]]


def fluent3d(q, n, o):
    tree = cached_json("fluent_tree", "https://api.github.com/repos/microsoft/fluentui-emoji/git/trees/main?recursive=1", 30)
    ws = words(q)
    hits = [t["path"] for t in tree["tree"] if "/3D/" in t["path"] and t["path"].endswith(".png")
            and all(w in t["path"].split("/")[1].lower() for w in ws)]
    hits.sort(key=len)
    return [rec("fluent3d", Path(h).stem, f"Fluent 3D {h.split('/')[1]}",
                "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/" + quote(h), "MIT", "Microsoft",
                "https://github.com/microsoft/fluentui-emoji", 256, 256, ext=".png") for h in hits[:n]]


LOTTIE_Q = 'query($q:String!,$n:Int){searchPublicAnimations(query:$q,first:$n){edges{node{id name jsonUrl gifUrl url createdBy{username}}}}}'


def lottiefiles(q, n, o):
    js = requests.post("https://graphql.lottiefiles.com/2022-08", json={"query": LOTTIE_Q, "variables": {"q": q, "n": n}},
                       headers=UA, timeout=30).json()
    return [rec("lottiefiles", e["node"]["id"], e["node"]["name"], e["node"]["jsonUrl"], "Lottie Simple License (free commercial)",
                (e["node"].get("createdBy") or {}).get("username", ""), e["node"]["url"], preview=e["node"]["gifUrl"], ext=".json")
            for e in js["data"]["searchPublicAnimations"]["edges"]]


def polyhaven(q, n, o, t="models"):
    data = cached_json(f"polyhaven_{t}", f"https://api.polyhaven.com/assets?t={t}", 7)
    ws = words(q)
    score = lambda a: sum(any(w in s.lower() for s in [a["name"], *a.get("tags", []), *a.get("categories", [])]) for w in ws)
    hits = sorted(((score(a), a.get("download_count", 0), k, a) for k, a in data.items()), key=lambda x: (-x[0], -x[1]))
    return [rec("polyhaven", k, a["name"], f"https://api.polyhaven.com/files/{k}", "CC0", ", ".join(a.get("authors", {})),
                f"https://polyhaven.com/a/{k}", preview=f"https://cdn.polyhaven.com/asset_img/thumbs/{k}.png?height=256",
                dl="ph_model" if t == "models" else "ph_tex") for s, _, k, a in hits[:n] if s]


def ambientcg(q, n, o):
    js = get("https://ambientcg.com/api/v2/full_json", params={"q": q, "limit": n, "type": "Material",
                                                                  "include": "downloadData,imageData"}).json()
    out = []
    for a in js.get("foundAssets", []):
        zips = a["downloadFolders"]["default"]["downloadFiletypeCategories"].get("zip", {}).get("downloads", [])
        z = next((d for d in zips if d["attribute"] == "2K-JPG"), zips[0] if zips else None)
        if z:
            out.append(rec("ambientcg", a["assetId"], a["displayName"], z["fullDownloadPath"], "CC0", "ambientCG",
                           a["shortLink"], preview=a.get("previewImage", {}).get("256-PNG", ""), dl="acg"))
    return out


def sketchfab(q, n, o):
    js = get("https://api.sketchfab.com/v3/search", params={"type": "models", "q": q, "downloadable": "true", "count": n * 2}).json()
    out = []
    for it in js["results"]:
        lic = (it.get("license") or {}).get("label", "?")
        if re.search("NonCommercial|NoDerivs|Editorial", lic):
            continue
        thumbs = sorted(it["thumbnails"]["images"], key=lambda i: i["width"])
        out.append(rec("sketchfab", it["uid"], it["name"], f"https://api.sketchfab.com/v3/models/{it['uid']}/download", lic,
                       it["user"]["username"], it["viewerUrl"], preview=thumbs[-1]["url"] if thumbs else "", dl="sketchfab",
                       note="" if KEY["SKETCHFAB_API_TOKEN"] else "download needs SKETCHFAB_API_TOKEN"))
    return out[:n]


def freesound(q, n, o):
    if not KEY["FREESOUND_API_KEY"]:
        return []
    p = {"query": q, "page_size": n, "fields": "id,name,previews,license,username,duration,url",
         "filter": 'license:("Creative Commons 0" OR "Attribution")', "token": KEY["FREESOUND_API_KEY"]}
    js = get("https://freesound.org/apiv2/search/text/", params=p).json()
    return [rec("freesound", it["id"], it["name"], it["previews"]["preview-hq-mp3"], it["license"].rstrip("/").split("/")[-2].upper(),
                it["username"], it["url"], duration=round(it["duration"], 2)) for it in js["results"]]


UI_VARIANTS = {"mobile-dark": ("iPhone 15 Pro Max", "dark", False), "mobile-light": ("iPhone 15 Pro Max", "light", False),
               "desktop-dark": (None, "dark", False), "desktop-light": (None, "light", False), "desktop-full": (None, "dark", True)}


def ui(q, n, o):
    url = q if q.startswith("http") else f"https://{q}"
    host = urlparse(url).netloc
    return [rec("ui", f"{host}|{v}", f"{host} {v}", url, "screenshot of a real product — editorial use (the video is about it)",
                host, url, dl="ui", variant=v) for v in UI_VARIANTS]


OVERLAY_HINT = {"light leak": "light leak", "leak": "light leak", "film burn": "film burn", "grain": "film grain", "dust": "dust"}

KINDS = {
    "photo": [lambda q, n, o: pexels(q, n, o), unsplash, lambda q, n, o: pixabay(q, n, o), openverse, commons],
    "video": [lambda q, n, o: pexels(q, n, o, True), lambda q, n, o: pixabay(q, n, o, True),
              lambda q, n, o: commons(q, n, o, "video")],
    "icon": [iconify],
    "logo": [lobehub, lambda q, n, o: iconify(q, n, o, "logos,simple-icons,devicon,skill-icons"),
             lambda q, n, o: commons(f"{q} logo", n, o, "drawing")],
    "svg": [lambda q, n, o: openverse(q, n, None, ext="svg"), lambda q, n, o: commons(q, n, o, "drawing")],
    "illustration": [undraw, storyset, fluent3d],
    "lottie": [lottiefiles],
    "model3d": [polyhaven, sketchfab],
    "texture": [lambda q, n, o: polyhaven(q, n, o, "textures"), ambientcg],
    "overlay": [lambda q, n, o: pexels(OVERLAY_HINT.get(q.lower(), q), n, o, True),
                lambda q, n, o: pixabay(OVERLAY_HINT.get(q.lower(), q), n, o, True)],
    "sfx": [freesound, lambda q, n, o: openverse(q, n, o, audio=True)],
    "ui": [ui],
}


# ---------------------------------------------------------------- download
GLTF_PIPELINE = "gltf-pipeline@4.3.1"  # pinned: npx runs exactly this release


def safe_join(base, rel):
    """base/rel, refusing anything that leaves base (a JSON from the web decides rel)."""
    base = Path(base).resolve()
    dest = (base / rel).resolve()
    if not dest.is_relative_to(base) or dest == base:
        raise SystemExit(f"refusing a download path outside {base}: {rel!r}")
    return dest


def slug(s):
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()[:48] or "asset"


def fetch(url, dest, headers=None):
    with requests.get(url, headers={**UA, **(headers or {})}, stream=True, timeout=120) as r:
        r.raise_for_status()
        if dest.suffix == "":
            ct = r.headers.get("content-type", "").split(";")[0]
            ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/svg+xml": ".svg", "image/webp": ".webp", "video/mp4": ".mp4",
                   "video/webm": ".webm", "audio/mpeg": ".mp3", "audio/wav": ".wav", "application/json": ".json",
                   "application/zip": ".zip", "model/gltf-binary": ".glb"}.get(ct) or Path(urlparse(r.url).path).suffix or ".bin"
            dest = dest.with_suffix(ext)
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
    return dest


def capture_ui(r, dest):
    from playwright.sync_api import sync_playwright  # optional: pip install playwright && playwright install chromium
    device, scheme, full = UI_VARIANTS[r["variant"]]
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            b = p.chromium.launch(channel="chrome")
        ctx = b.new_context(**(p.devices[device] if device else {"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 2}),
                            color_scheme=scheme)
        pg = ctx.new_page()
        try:
            pg.goto(r["url"], wait_until="load", timeout=45000)
        except Exception:
            pass  # slow site: screenshot what loaded
        pg.wait_for_timeout(3000)  # let entrance animations settle
        dest = dest.with_suffix(".png")
        pg.screenshot(path=str(dest), full_page=full)
        b.close()
    return dest


def download(r, outdir):
    base = outdir / f"{r['source']}_{slug(r['title'])}"
    ext = r.get("ext") or Path(urlparse(r["url"]).path).suffix
    if ext and len(ext) <= 5 and r["dl"] == "http":
        base = base.with_suffix(ext)
    d = r["dl"]
    if d == "ui":
        return capture_ui(r, base)
    if d == "ph_tex":
        files = get(r["url"]).json()
        diff = files.get("Diffuse") or files.get("diffuse")
        res = "4k" if "4k" in diff else max(diff)
        return fetch(diff[res]["jpg"]["url"], base.with_name(f"{base.name}_diff_{res}.jpg"))
    if d == "ph_model":
        g = get(r["url"]).json()["gltf"]["2k"]["gltf"]
        folder = base.with_name(base.name + "_gltf")
        folder.mkdir(exist_ok=True)
        main = fetch(g["url"], folder / Path(urlparse(g["url"]).path).name)
        for rel, inf in g.get("include", {}).items():
            dest = safe_join(folder, rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            fetch(inf["url"], dest)
        glb = base.with_suffix(".glb")
        npx = mc_profile.tool("npx")  # PATH only, never the cwd
        if os.path.isfile(npx) and subprocess.run([npx, "-y", GLTF_PIPELINE, "-i", str(main), "-o", str(glb)], capture_output=True).returncode == 0:
            shutil.rmtree(folder)
            return glb
        return main  # ponytail: left as .gltf folder when gltf-pipeline can't run
    if d == "sketchfab":
        if not KEY["SKETCHFAB_API_TOKEN"]:
            raise SystemExit("sketchfab download needs SKETCHFAB_API_TOKEN (free account) — or open " + r["page"])
        js = get(r["url"], headers={"Authorization": f"Token {KEY['SKETCHFAB_API_TOKEN']}"}).json()
        if "glb" in js:
            return fetch(js["glb"]["url"], base.with_suffix(".glb"))
        z = fetch(js["gltf"]["url"], base.with_suffix(".zip"))
        return z
    if d == "acg":
        z = fetch(r["url"], base.with_suffix(".zip"))
        with zipfile.ZipFile(z) as zf:
            color = next(nm for nm in zf.namelist() if re.search(r"_Color\.(jpg|png)$", nm))
            out = base.with_name(base.name + "_" + Path(color).name)
            out.write_bytes(zf.read(color))
        z.unlink()
        return out
    if r.get("ping"):  # Unsplash API guideline: register the download
        get(r["ping"], headers={"Authorization": f"Client-ID {KEY['UNSPLASH_ACCESS_KEY']}"})
    return fetch(r["url"], base)


def manifest_path(outdir, explicit):
    if explicit:
        return Path(explicit)
    for p in [outdir, *outdir.parents]:
        if p.name == "assets":
            return p / "manifest.json"
    return outdir / "manifest.json"


def load_cache():
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def cmd_search(a):
    cache, found = load_cache(), 0
    for fn in KINDS[a.kind]:
        try:
            if a.kind == "icon" and a.set:
                res = iconify(a.query, a.n, a.orientation, a.set)
            else:
                res = fn(a.query, a.n, a.orientation)
                for w in (words(a.query) if not res and a.kind not in ("ui", "logo") else []):
                    res = fn(w, a.n, a.orientation)  # small catalogues match single words only
                    if res:
                        break
        except Exception as e:
            msg = re.sub(r"for url: (\S+?)\?\S*", r"for \1", str(e))  # never print keys from query strings
            print(f"  [source failed] {type(e).__name__}: {msg[:160]}")
            continue
        if a.orientation:  # sources without a native filter
            want_tall = a.orientation == "portrait"
            res = [r for r in res if not (r["w"] and r["h"]) or (r["h"] > r["w"]) == want_tall]
        for r in res:
            cache[r["id"]] = {**r, "kind": a.kind}
            size = f"{r['w']}x{r['h']}" if r["w"] else (f"{r['duration']}" + ("s" if isinstance(r["duration"], (int, float)) else "") if r.get("duration") else "")
            print(f"{r['id']}\n    {r['title']}  |  {size}  |  {r['licence']}  |  by {r['author'][:40]}")
            print(f"    page: {r['page']}" + (f"\n    preview: {r['preview']}" if r["preview"] else "") + (f"\n    NOTE: {r['note']}" if r.get("note") else ""))
            found += 1
    CACHE.write_text(json.dumps(cache), encoding="utf-8")
    missing = [k for k in ("PEXELS_API_KEY", "PIXABAY_API_KEY", "UNSPLASH_ACCESS_KEY", "FREESOUND_API_KEY") if not KEY[k]]
    if a.kind in ("photo", "video", "overlay", "sfx") and missing:
        print(f"(keyless run — set {', '.join(missing)} for more/better results)")
    print(f"== {found} candidates")


def cmd_download(a):
    cache, outdir = load_cache(), Path(a.to)
    outdir.mkdir(parents=True, exist_ok=True)
    mpath = manifest_path(outdir, a.manifest)
    for i in a.ids:
        r = cache.get(i) or (rec("url", slug(i)[-24:], Path(urlparse(i).path).stem, i, "CHECK LICENCE", page=i) if i.startswith("http") else None)
        if not r:
            print(f"{i}: unknown id — run `search` first")
            continue
        f = download(r, outdir)
        note = ""
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            from PIL import Image
            w, h = Image.open(f).size
            note = f"  {w}x{h}" + ("  << SMALL: <1080 px long side, only for small slots" if max(w, h) < 1080 else "")
        if f.suffix == ".json" and r["source"] == "lottiefiles":
            imgs = sum("p" in x for x in json.loads(f.read_text(encoding="utf-8")).get("assets", []))
            note = f"  << RASTER LOTTIE ({imgs} embedded images): not recolourable/scalable, pick another" if imgs else "  vector lottie"
        print(f"saved {f}  ({f.stat().st_size // 1024} KB){note}")
        if a.no_manifest:
            continue
        m = json.loads(mpath.read_text(encoding="utf-8")) if mpath.exists() else []
        rel = os.path.relpath(f, mpath.parent).replace("\\", "/")
        m.append({"file": rel, "type": r.get("kind", ""), "source": r["source"], "source_url": r["page"], "download_url": r["url"],
                  "licence": r["licence"], "author": r["author"], "title": r["title"], "added": time.strftime("%Y-%m-%d")})
        mpath.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")


def selftest():
    r = rec("x", 1, " A title ", "https://example.org/a.png", "CC0")
    assert r["id"] == "x:1" and r["title"] == "A title" and r["page"] == r["url"]
    assert slug("Hello, World! 3D") == "hello-world-3d"
    base = Path(tempfile.mkdtemp())
    try:
        assert safe_join(base, "textures/a.jpg") == (base / "textures/a.jpg").resolve()
        for bad in ("../evil.txt", "a/../../evil", str(base.parent / "x"), "."):
            try:
                safe_join(base, bad)
                raise AssertionError(f"traversal accepted: {bad}")
            except SystemExit:
                pass
        (base / "proj" / "assets" / "img").mkdir(parents=True)
        assert manifest_path(base / "proj" / "assets" / "img", None) == base / "proj" / "assets" / "manifest.json"
    finally:
        shutil.rmtree(base, ignore_errors=True)
    assert all("mixkit" not in getattr(f, "__name__", "") for v in KINDS.values() for f in v)
    assert "Mozilla" not in UA["User-Agent"] and "@" in GLTF_PIPELINE
    print("selftest ok")


def main():
    if sys.argv[1:2] == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("search")
    s.add_argument("kind", choices=KINDS)
    s.add_argument("query")
    s.add_argument("--n", type=int, default=8, help="results per source")
    s.add_argument("--orientation", choices=["portrait", "landscape"])
    s.add_argument("--set", help="icon: restrict to Iconify prefixes, e.g. lucide or 'solar,tabler' (one family per video)")
    d = sp.add_parser("download")
    d.add_argument("ids", nargs="+")
    d.add_argument("--to", required=True)
    d.add_argument("--manifest")
    d.add_argument("--no-manifest", action="store_true")
    sp.add_parser("kinds")
    a = ap.parse_args()
    if a.cmd == "kinds":
        for k, fns in KINDS.items():
            print(k)
        return
    (cmd_search if a.cmd == "search" else cmd_download)(a)


if __name__ == "__main__":
    main()
