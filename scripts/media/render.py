"""Renders build/demo.html frame by frame with headless Chrome and stitches etc./demo.gif with Pillow.
Also renders build/cover.html to etc./cover.png.

Usage (needs Google Chrome and Pillow, e.g. in a venv: python3 -m venv venv && venv/bin/pip install pillow):
    python3 scripts/media/build_pages.py
    venv/bin/python scripts/media/render.py
"""
import json
import pathlib
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
M = pathlib.Path(__file__).resolve().parent / 'build'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
URL = 'file://' + str(M / 'demo.html')
FRAMES = M / 'frames'
PROFILES = M / 'profiles'
FRAMES.mkdir(exist_ok=True)
PROFILES.mkdir(exist_ok=True)

dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--dump-dom', URL],
                     capture_output=True, text=True).stdout
plan = json.loads(re.findall(r'<pre id="plan">(\[[^<]*\])', dom)[-1])
print(len(plan), 'frames,', sum(plan) / 1000, 's')


def shoot(i):
    out = FRAMES / f'{i:03d}.png'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    f'--user-data-dir={PROFILES / str(i % 6)}',
                    '--force-device-scale-factor=1.5', '--window-size=1040,620',
                    f'--screenshot={out}', f'{URL}#f={i}'],
                   capture_output=True)
    return out


# cover: 960x480 CSS at 2x = 1920x960 (Figma Community cover size)
subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                f'--user-data-dir={PROFILES / "cover"}', '--force-device-scale-factor=2',
                '--window-size=960,480', f'--screenshot={ROOT / "etc." / "cover.png"}',
                'file://' + str(M / 'cover.html')], capture_output=True)

# one profile per worker slot so parallel Chrome instances don't collide
with ThreadPoolExecutor(6) as pool:
    paths = []
    for start in range(0, len(plan), 6):
        paths += list(pool.map(shoot, range(start, min(start + 6, len(plan)))))

# shared palette from a few representative frames keeps colors stable across the GIF
images = [Image.open(p).convert('RGB') for p in paths]
w, h = images[0].size
sample = Image.new('RGB', (w, h * 4))
for k, idx in enumerate([0, len(images) // 3, 2 * len(images) // 3, len(images) - 1]):
    sample.paste(images[idx], (0, h * k))
palette = sample.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]

out = ROOT / 'etc.' / 'demo.gif'
frames[0].save(out, save_all=True, append_images=frames[1:], duration=plan, loop=0, optimize=False, disposal=1)
print(out, out.stat().st_size // 1024, 'KB', (w, h))
