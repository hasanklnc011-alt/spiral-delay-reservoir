"""Render docs/figures/system-animation.gif by capturing docs/animation.html
frame by frame with a headless Chromium/Edge browser.

The interactive page has a capture mode: `?capture&f=<i>&n=<total>` freezes the
animation at a deterministic state and hides the controls. This script screenshots
each frame, crops to the scene + panels, and assembles a looping GIF.

Requirements: Pillow, and a Chromium-family browser (Edge or Chrome). Set
BROWSER below if auto-detection fails.

    python scripts/capture_animation_gif.py
"""
from __future__ import annotations

import http.server
import os
import shutil
import socketserver
import subprocess
import threading
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGE_DIR = ROOT / "docs"
OUT = PAGE_DIR / "figures" / "system-animation.gif"
TMP = ROOT / "scripts" / "_capture_frames"

PORT = 8744
N = 40                       # frames in the loop
W, HPX = 980, 1340           # browser window (CSS px)
SCALE = 2                    # device scale factor -> 2x crisp screenshots
CROP_CSS = (12, 202, 968, 1196)   # left, top, right, bottom in CSS px
DURATION_MS = 90

CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    shutil.which("chromium") or "", shutil.which("google-chrome") or "",
]
BROWSER = next((c for c in CANDIDATES if c and Path(c).exists()), "")
if not BROWSER:
    raise SystemExit("No Chromium-family browser found; set BROWSER in this script.")


def main() -> None:
    os.chdir(PAGE_DIR)
    TMP.mkdir(exist_ok=True)
    srv = socketserver.TCPServer(("127.0.0.1", PORT), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.4)

    def shot(f: int, path: Path) -> None:
        url = f"http://127.0.0.1:{PORT}/animation.html?capture&f={f}&n={N}"
        subprocess.run(
            [BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={SCALE}", f"--window-size={W},{HPX}",
             "--virtual-time-budget=2200", f"--screenshot={path}", url],
            capture_output=True, timeout=90)

    box = tuple(int(v * SCALE) for v in CROP_CSS)
    frames = []
    for f in range(N):
        p = TMP / f"f{f:03d}.png"
        shot(f, p)
        img = Image.open(p).convert("RGB").crop(box)
        frames.append(img.resize((img.width // 2, img.height // 2), Image.LANCZOS))
        print(f"frame {f + 1}/{N}", frames[-1].size)

    srv.shutdown()
    pal = frames[len(frames) // 2].convert("P", palette=Image.ADAPTIVE, colors=200)
    gif = [fr.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for fr in frames]
    gif[0].save(OUT, save_all=True, append_images=gif[1:], duration=DURATION_MS, loop=0, optimize=True)
    shutil.rmtree(TMP, ignore_errors=True)
    print("wrote", OUT.relative_to(ROOT), f"{OUT.stat().st_size / 1e6:.1f} MB, {len(gif)} frames, {gif[0].size}")


if __name__ == "__main__":
    main()
