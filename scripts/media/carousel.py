"""Generates the Figma Community carousel slides (build/carousel-N.html, 960x540 CSS -> 1920x1080).

Each slide pairs a short headline with the real plugin UI (ui.html + code.js on the mock figma API from
build_pages.py) set up to show one feature. render.py screenshots them to etc./carousel/N.png.
Slide 1 of the carousel is etc./thumbnail.png, so these start at 2.
"""
import html

import build_pages as bp

OUT = bp.OUT
ROUNDED = bp.ROUNDED
YELLOW = bp.YELLOW

# UI copies for slides that need a second window or the What's new tour, with animations frozen
FREEZE = '<style>*,*::before,*::after{animation:none!important;transition:none!important}</style>'
ui_frozen = bp.ui.replace('</head>', FREEZE + '</head>')
ui_tour = ui_frozen.replace('<html lang="en">', '<html lang="en" data-whats-new="2.0">')

CSS = f"""
{bp.COMMON_CSS}
.stage {{ width: 960px; height: 540px; background: #141414; }}
.grid {{ position: absolute; inset: 0; background-image: linear-gradient(#1f1f1f 1px, transparent 1px),
  linear-gradient(90deg, #1f1f1f 1px, transparent 1px); background-size: 32px 32px; }}
.copy {{ position: absolute; left: 56px; top: 64px; width: 330px; }}
.brand {{ display: flex; align-items: center; gap: 8px; color: #b2b2b2; font: 700 13px {ROUNDED}; }}
.brand svg {{ border-radius: 6px; box-shadow: 0 0 0 1px #333; }}
.kicker {{ display: inline-block; margin-top: 32px; padding: 3px 10px; border-radius: 6px; background: {YELLOW};
  color: #000; font: 700 13px {ROUNDED}; }}
.copy h1 {{ margin: 14px 0 12px; font: 800 38px/1.05 {ROUNDED}; letter-spacing: -0.8px; color: #fff; }}
.copy p {{ margin: 0; font: 500 16px/1.45 {ROUNDED}; color: #b2b2b2; }}
.window {{ transform-origin: top left; background: #2c2c2c; box-shadow: 0 0 0 1px #444, 0 20px 60px rgba(0,0,0,.6); }}
.window header {{ color: #fff; border-color: #444; }}
.window.light {{ background: #fff; box-shadow: 0 0 0 1px #ddd, 0 20px 60px rgba(0,0,0,.6); }}
.window.light header {{ color: #1e1e1e; border-color: #e6e6e6; }}
.toast {{ position: absolute; padding: 10px 16px; border-radius: 6px; background: #fff; color: #1e1e1e; font-size: 13px;
  font-weight: 500; box-shadow: 0 8px 24px rgba(0,0,0,.5); transform: translateX(-50%); }}
.cursor {{ position: absolute; width: 26px; height: 26px; }}
.sel {{ position: absolute; border: 1.5px solid #0d99ff; }}
.outline {{ position: absolute; border: 1px solid #0d99ff; opacity: .7; }}
.handle {{ position: absolute; width: 7px; height: 7px; margin: -3.5px 0 0 -3.5px; background: #fff; border: 1px solid #0d99ff; }}
.badge {{ position: absolute; transform: translateX(-50%); padding: 1px 5px; border-radius: 3px; background: #0d99ff;
  color: #fff; font-size: 10px; font-weight: 500; white-space: nowrap; }}
.frame-label {{ color: #8c8c8c; }}
"""

CURSOR = ('<svg class="cursor" id="cursor" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.5 13.8 L10.6 20.4 L13.4 19.2 '
          'L10.4 12.7 L16.6 12.4 Z" fill="#000" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>')

HELPERS = """
const SCALE = Number(iframe.closest('.window').dataset.scale)
// stage position of an element inside the (scaled) plugin window
function at (el, fx, fy) {
  const f = iframe.getBoundingClientRect(), r = el.getBoundingClientRect()
  return { x: f.left + (r.left + r.width * fx) * SCALE, y: f.top + (r.top + r.height * fy) * SCALE }
}
function place (id, p, dx, dy) {
  const e = document.getElementById(id)
  e.style.left = (p.x + (dx || 0)) + 'px'
  e.style.top = (p.y + (dy || 0)) + 'px'
}
"""


def window(style, scale, frame_id='ui', srcdoc=None, light=False):
    doc = html.escape(srcdoc if srcdoc is not None else bp.ui, quote=True)
    ic = bp.icon
    return (f'<div class="window{" light" if light else ""}" data-scale="{scale}" '
            f'style="{style};transform:scale({scale})"><header><img src="{ic}">pixels.Convert'
            f'<span class="x">✕</span></header><iframe id="{frame_id}" srcdoc="{doc}"></iframe></div>')


def slide(n, kicker, title, text, body, script, dark_ui=True, srcdoc=None):
    win = window('left:420px;top:64px', 0.9, srcdoc=srcdoc) if body is None else body
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="stage" id="stage">
  <div class="grid"></div>
  <div class="copy">
    <div class="brand">{bp.logo_svg(24, 'dark')}PixelsConvert</div>
    <div class="kicker">{kicker}</div>
    <h1>{title}</h1>
    <p>{text}</p>
  </div>
  {win}
</div>
{bp.code_block}
<script>{bp.RUNTIME}
window.onload = async () => {{
  {"document.getElementById('ui').contentDocument.documentElement.style.cssText = '" + bp.DARK_VARS + "'" if dark_ui else ''}
  await startPlugin()
  {HELPERS}
  {script}
}}
</script></body></html>"""
    (OUT / f'carousel-{n}.html').write_text(page)


# 2 — density tabs + custom dpi
slide(2, 'Screen density', 'Every density, one click',
      'Switch from ldpi to xxxhdpi with tabs, or type any custom dpi. Values update as you go.', None, """
  select('card')
  uiDoc.querySelectorAll('.tab')[6].click()
  const input = uiDoc.getElementById('custom-dpi')
  input.value = '401'
  input.oninput()
""")

# 3 — the sp column
slide(3, 'New', 'Now with sp',
      'Get text sizes in scale-independent pixels, right next to dp. Ready for Android specs.', None, """
  select('title')
  uiDoc.querySelectorAll('.tab')[4].click()
  uiDoc.querySelectorAll('td[id$="-sp"]').forEach(td => { if (!td.closest('tr').hidden) td.classList.add('copied') })
  uiDoc.querySelectorAll('th')[3].style.color = getComputedStyle(uiDoc.documentElement).getPropertyValue('--text-brand')
""")

# 4 — click to copy
slide(4, 'Copy', 'Click any value to copy it',
      'Values copy with their unit, like 24sp. Copy all grabs the whole table for a spreadsheet.',
      window('left:420px;top:64px', 0.9) + CURSOR + '<div class="toast" id="toast">Copied 24sp</div>', """
  select('title')
  uiDoc.querySelectorAll('.tab')[4].click()
  const cell = uiDoc.getElementById('fontSize-sp')
  cell.classList.add('copied')
  place('cursor', at(cell, 0.55, 0.6), -3, -2)
  const win = document.querySelector('.window').getBoundingClientRect()
  place('toast', { x: win.left + win.width / 2, y: win.bottom + 18 })
""")

# 5 — several layers: a (scaled-down) phone frame on the canvas with two layers selected
phone_body = ('<div style="position:absolute;left:56px;top:244px;width:300px;height:420px;'
              'transform:scale(0.6);transform-origin:top left">' +
              bp.phone(0, 18) + '<div id="selection"></div></div>' +
              window('left:420px;top:64px', 0.9))
slide(5, 'Multi-select', 'Measure several layers',
      '', phone_body, """
  FRAME.x = 0; FRAME.y = 18
  select('title', 'button')
  uiDoc.querySelectorAll('.tab')[4].click()
  drawSelection()
""")

# 6 — light and dark themes: two windows
themes_body = (window('left:388px;top:40px', 0.72, light=True) +
               window('left:540px;top:176px', 0.72, frame_id='ui2', srcdoc=ui_frozen))
slide(6, 'Themes', 'Light or dark, it fits right in',
      'PixelsConvert follows your Figma theme, so it always feels at home.', themes_body, """
  // remember what the plugin sends so the second (dark) window can show the same values
  let last = null
  const send = figma.ui.postMessage
  figma.ui.postMessage = m => { last = m; send.call(figma.ui, m) }
  select('title')
  uiDoc.querySelectorAll('.tab')[4].click()
  const ui2 = document.getElementById('ui2')
  ui2.contentDocument.documentElement.style.cssText = '""" + bp.DARK_VARS + """'
  ui2.contentDocument.querySelectorAll('.tab').forEach((t, i) => t.setAttribute('aria-checked', String(i === 4)))
  ui2.contentWindow.onmessage({ data: { pluginMessage: last } })
  ui2.style.height = Math.ceil(ui2.contentDocument.body.getBoundingClientRect().height) + 'px'
""", dark_ui=False)

# 7 — the What's new tour
slide(7, 'Welcome', "A quick tour of what's new",
      'The first time someone opens the update, a short tour walks through the new features.', None, """
  uiDoc.getElementById('wn-next').onclick()
  const slides = uiDoc.querySelectorAll('.wn-slide')
  slides.forEach((s, i) => { if (i < slides.length - 1) s.remove() })
""", srcdoc=ui_tour)

print('carousel ok')
