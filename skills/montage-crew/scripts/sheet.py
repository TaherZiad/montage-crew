"""One contact sheet instead of many single frames (token saver, from video-ad-editor 07_contact_sheet).

  python sheet.py video.mp4 out.jpg 1.2 4.6 12.3 27.6 31.0 48.4     (any count; 3 columns, 360 px tiles, time stamped)
  python sheet.py --selftest

Read ONLY the sheet — never the frames one by one. Stamps are drawn with PIL (ffmpeg drawtext is missing in some builds).
"""
import io, pathlib, subprocess, sys, tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mc_profile import FFMPEG  # noqa: E402


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] == "--selftest":
        return selftest()
    src, out, times = argv[0], argv[1], [float(t) for t in argv[2:]]
    if not times:
        sys.exit(__doc__)
    tiles = []
    for t in times:
        png = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{t}", "-i", src, "-frames:v", "1", "-vf", "scale=360:-2",
                              "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
        im = Image.open(io.BytesIO(png)).convert("RGB") if png else Image.new("RGB", (360, 640), (40, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 92, 30], fill=(0, 0, 0))
        d.text((8, 7), f"{t:.2f}s", fill=(255, 255, 255))
        tiles.append(im)
    cols, tw, th = min(3, len(tiles)), tiles[0].width, tiles[0].height
    sheet = Image.new("RGB", (cols * tw, -(-len(tiles) // cols) * th), (20, 20, 20))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(out, quality=85)
    print(f"{len(tiles)} frames -> {out}")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        v, o = pathlib.Path(d) / "v.mp4", pathlib.Path(d) / "s.jpg"
        subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=540x960:r=30:d=2", "-pix_fmt", "yuv420p",
                        str(v)], check=True)
        main([str(v), str(o), "0.2", "1.0", "1.8", "0.5"])
        with Image.open(o) as im:
            assert im.size == (3 * 360, 2 * 640), im.size
    print("selftest ok")


if __name__ == "__main__":
    main()
