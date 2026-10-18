"""Generates thumbnail.html and demo.html, which run the real ui.html + code.js against a mock figma API.

Step 1 of rebuilding the README media (see render.py for step 2). Output goes to scripts/media/build/.
"""
import base64
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent / 'build'
OUT.mkdir(exist_ok=True)

ui = (ROOT / 'ui.html').read_text()
code = (ROOT / 'code.js').read_text()

YELLOW = '#FBF151'  # the logo's yellow
ROUNDED = "ui-rounded, 'SF Pro Rounded', system-ui"

# the logo: four squares on a 100x100 grid, in a light and a dark version
# (sources: etc./logo-white.svg, etc./logo-black.svg, redrawn from the user's PNGs)
LOGO = {
    'light': {'bg': '#ffffff', 'squares': [(5, 4, 30, '#666666'), (55, 10, 40, '#FBF151'),
                                           (8, 50, 40, '#000000'), (63, 68, 30, '#b2b2b2')]},
    # dark is the plugin icon; it has extra padding so Figma's rounded icon corners don't clip it
    'dark': {'bg': '#111111', 'squares': [(8, 10.5, 30, '#a0a0a0'), (52, 10.5, 40, '#FBF151'),
                                          (8, 49.5, 40, '#ffffff'), (62, 59.5, 30, '#585858')]}
}


def logo_svg(size, variant='light'):
    v = LOGO[variant]
    rects = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{w}" fill="{c}"/>' for x, y, w, c in v['squares'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}">'
            f'<rect width="100" height="100" fill="{v["bg"]}"/>{rects}</svg>')


# window header icon = the plugin icon, drawn from the vector so it never depends on a stale PNG
icon = 'data:image/svg+xml;base64,' + base64.b64encode(logo_svg(100, 'dark').encode()).decode()


RUNTIME = r"""
const S = 0.2                      // canvas zoom
const FRAME = { x: 0, y: 0 }      // set per page (stage coords of the phone frame)
const NODES = {
  title:  { type: 'TEXT', name: 'Title', x: 48, y: 144, width: 984, height: 96, fontSize: 72, paragraphSpacing: 24 },
  card:   { type: 'RECTANGLE', name: 'Hero card', x: 48, y: 288, width: 984, height: 432 },
  button: { type: 'FRAME', name: 'Button', x: 48, y: 1680, width: 984, height: 144 }
}
for (const k in NODES) {
  const n = NODES[k]
  n.absoluteBoundingBox = { x: n.x, y: n.y, width: n.width, height: n.height }
}

let iframe, uiWin, uiDoc
let selection = []
let selHandler = null
let pluginOnMessage = null
const pending = []

let uiShown
const shown = new Promise(r => { uiShown = r })

const figma = {
  mixed: Symbol('mixed'),
  // the tour is treated as already seen, so the media shows the main UI
  clientStorage: { getAsync: () => Promise.resolve('2.0'), setAsync: () => Promise.resolve() },
  showUI () { uiShown() },
  ui: {
    postMessage (m) { uiWin.onmessage({ data: { pluginMessage: m } }) },
    resize (w, h) { iframe.style.height = h + 'px' },
    set onmessage (f) { pluginOnMessage = f; pending.splice(0).forEach(m => f(m)) },
    get onmessage () { return pluginOnMessage }
  },
  on (ev, f) { if (ev === 'selectionchange') selHandler = f },
  currentPage: {
    get selection () { return selection },
    set selection (v) { selection = v; drawSelection(); if (selHandler) selHandler() }
  },
  notify (t) { showToast(t) },
  openExternal () {}
}

// the UI calls parent.postMessage({ pluginMessage }); deliver it synchronously
window.postMessage = data => {
  const m = data && data.pluginMessage
  if (!m) return
  if (pluginOnMessage) pluginOnMessage(m)
  else pending.push(m)
}

function nodeRect (k) {
  const n = NODES[k]
  return { x: FRAME.x + n.x * S, y: FRAME.y + n.y * S, w: n.width * S, h: n.height * S }
}

function drawSelection () {
  const layer = document.getElementById('selection')
  if (!layer) return
  layer.innerHTML = ''
  const keys = Object.keys(NODES).filter(k => selection.includes(NODES[k]))
  if (keys.length === 0) return
  const rects = keys.map(nodeRect)
  if (keys.length > 1) {
    for (const r of rects) layer.appendChild(box(r, 'outline'))
  }
  const x1 = Math.min(...rects.map(r => r.x)), y1 = Math.min(...rects.map(r => r.y))
  const x2 = Math.max(...rects.map(r => r.x + r.w)), y2 = Math.max(...rects.map(r => r.y + r.h))
  const u = { x: x1, y: y1, w: x2 - x1, h: y2 - y1 }
  layer.appendChild(box(u, 'sel'))
  for (const [hx, hy] of [[u.x, u.y], [u.x + u.w, u.y], [u.x, u.y + u.h], [u.x + u.w, u.y + u.h]]) {
    const h = document.createElement('div')
    h.className = 'handle'
    h.style.left = hx + 'px'
    h.style.top = hy + 'px'
    layer.appendChild(h)
  }
  const badge = document.createElement('div')
  badge.className = 'badge'
  badge.textContent = Math.round(u.w / S) + ' × ' + Math.round(u.h / S)
  badge.style.left = (u.x + u.w / 2) + 'px'
  badge.style.top = (u.y + u.h + 6) + 'px'
  layer.appendChild(badge)
}

function box (r, cls) {
  const d = document.createElement('div')
  d.className = cls
  Object.assign(d.style, { left: r.x + 'px', top: r.y + 'px', width: r.w + 'px', height: r.h + 'px' })
  return d
}

function showToast (t) {
  const el = document.getElementById('toast')
  if (!el) return
  el.textContent = t
  el.hidden = false
}
function clearToast () {
  const el = document.getElementById('toast')
  if (el) el.hidden = true
}

function select (...keys) { figma.currentPage.selection = keys.map(k => NODES[k]) }

function startPlugin () {
  iframe = document.getElementById('ui')
  uiWin = iframe.contentWindow
  uiDoc = iframe.contentDocument
  uiWin.setTimeout = () => 0      // keep frames deterministic (no copy-flash timeout)
  const run = new Function('figma', '__html__', document.getElementById('plugin-code').textContent)
  run(figma, '')
  // code.js reads clientStorage before showing the UI; resolves once the first update has been posted
  return shown
}
"""

PHONE = """
<div class="frame-label" style="left:{fx}px;top:{ly}px">Android · Home</div>
<div class="phone" style="left:{fx}px;top:{fy}px">
  <div class="p-title" style="left:{tx}px;top:{ty}px;width:{tw}px;height:{th}px;font-size:{tf}px;line-height:{th}px">Good morning</div>
  <div class="p-card" style="left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px">
    {logo}
  </div>
  {rows}
  <div class="p-button" style="left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px;line-height:{bh}px">Get started</div>
</div>
"""


def phone(fx, fy, s=0.2):
    rows = ''
    for i, y in enumerate([784, 976, 1168, 1360]):
        rows += (f'<div class="p-row" style="top:{y*s}px">'
                 f'<i style="width:{96*s}px;height:{96*s}px"></i>'
                 f'<b style="width:{(520 - i*60)*s}px"></b><b class="short" style="width:{(300 + i*40)*s}px"></b></div>')
    return PHONE.format(
        fx=fx, fy=fy, ly=fy - 18,
        tx=48*s, ty=144*s, tw=984*s, th=96*s, tf=72*s,
        cx=48*s, cy=288*s, cw=984*s, ch=432*s,
        bx=48*s, by=1680*s, bw=984*s, bh=144*s,
        rows=rows, logo=logo_svg(64, 'dark'))


COMMON_CSS = f"""
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; overflow: hidden; }}
body {{ font-family: Inter, system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }}
.stage {{ position: relative; overflow: hidden; }}
.window {{ position: absolute; background: #fff; border-radius: 10px; overflow: hidden;
  box-shadow: 0 0 0 0.5px rgba(0,0,0,.18), 0 6px 24px rgba(0,0,0,.14), 0 2px 6px rgba(0,0,0,.08); }}
.window header {{ display: flex; align-items: center; gap: 8px; height: 40px; padding: 0 12px 0 14px;
  border-bottom: 1px solid #e6e6e6; font-size: 12px; font-weight: 600; color: #1e1e1e; }}
.window header img {{ width: 18px; height: 18px; }}
.window header .x {{ margin-left: auto; color: #757575; font-size: 16px; font-weight: 400; }}
.window iframe {{ display: block; width: 560px; height: 320px; border: 0; }}
.frame-label {{ position: absolute; font-size: 10px; color: #8c8c8c; }}
.phone {{ position: absolute; width: 216px; height: 384px; background: #fff; overflow: hidden;
  box-shadow: 0 0 0 0.5px rgba(0,0,0,.12); }}
.phone > * {{ position: absolute; }}
.p-title {{ font-weight: 700; color: #1e1e1e; letter-spacing: -0.2px; }}
.p-card {{ background: #111111; border-radius: 6.4px; display: flex; align-items: center; justify-content: center; }}
.p-card svg {{ display: block; }}
.p-row {{ left: 9.6px; right: 9.6px; height: 19.2px; }}
.p-row i {{ position: absolute; left: 0; top: 0; border-radius: 50%; background: #ececec; }}
.p-row b {{ position: absolute; left: 26px; top: 3px; height: 5px; border-radius: 3px; background: #e3e3e3; }}
.p-row b.short {{ top: 12px; background: #efefef; }}
.p-button {{ background: #1e1e1e; color: #fff; border-radius: 14.4px; text-align: center; font-size: 9px; font-weight: 600; }}
"""

ui_attr = html.escape(ui, quote=True)
code_block = f'<script type="text/plain" id="plugin-code">{code}</script>'
window_html = (f'<div class="window" id="win" style="{{style}}"><header><img src="{icon}">pixels.Convert'
               f'<span class="x">✕</span></header><iframe id="ui" srcdoc="{ui_attr}"></iframe></div>')


# ---------- demo ----------
DEMO_W, DEMO_H = 1040, 620
demo = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.stage {{ width: {DEMO_W}px; height: {DEMO_H}px; background: #f5f5f5; }}
.sel {{ position: absolute; border: 1.5px solid #0d99ff; }}
.outline {{ position: absolute; border: 1px solid #0d99ff; opacity: .7; }}
.handle {{ position: absolute; width: 7px; height: 7px; margin: -3.5px 0 0 -3.5px; background: #fff; border: 1px solid #0d99ff; }}
.badge {{ position: absolute; transform: translateX(-50%); padding: 1px 5px; border-radius: 3px; background: #0d99ff;
  color: #fff; font-size: 10px; font-weight: 500; white-space: nowrap; }}
#cursor {{ position: absolute; width: 22px; height: 22px; pointer-events: none; z-index: 10; }}
#ring {{ position: absolute; width: 30px; height: 30px; margin: -15px 0 0 -15px; border-radius: 50%;
  background: rgba(13,153,255,.25); border: 1.5px solid rgba(13,153,255,.7); z-index: 9; }}
#toast {{ position: absolute; left: 50%; bottom: 24px; transform: translateX(-50%); padding: 10px 16px; border-radius: 6px;
  background: #2c2c2c; color: #fff; font-size: 12px; box-shadow: 0 4px 16px rgba(0,0,0,.2); z-index: 8; }}
#caption {{ position: absolute; left: 24px; bottom: 22px; padding: 7px 14px; border-radius: 999px; background: {YELLOW};
  color: #000; font: 700 13px ui-rounded, 'SF Pro Rounded', system-ui; box-shadow: 0 0 0 1.5px #000; z-index: 8; }}
[hidden] {{ display: none !important; }}
</style></head><body>
<div class="stage" id="stage">
  {phone(102, 72)}
  <div id="selection"></div>
  {window_html.replace('{style}', 'left:440px;top:40px')}
  <div id="caption"></div>
  <div id="toast" hidden></div>
  <div id="ring" hidden></div>
  <svg id="cursor" viewBox="0 0 22 22"><path d="M3 2 L3 18 L7.5 13.8 L10.6 20.4 L13.4 19.2 L10.4 12.7 L16.6 12.4 Z"
    fill="#000" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg>
</div>
{code_block}
<script>{RUNTIME}
FRAME.x = 102; FRAME.y = 72

const tab = i => () => uiDoc.querySelectorAll('.tab')[i]
const el = sel => () => uiDoc.querySelector(sel)
function center (target) {{
  if (typeof target === 'string') {{
    const r = nodeRect(target)
    return {{ x: r.x + r.w * 0.62, y: r.y + r.h * 0.55 }}
  }}
  const r = target().getBoundingClientRect()
  const f = iframe.getBoundingClientRect()
  return {{ x: f.left + r.left + r.width * 0.55, y: f.top + r.top + r.height * 0.6 }}
}}
function typeDpi (v) {{
  return () => {{ const i = uiDoc.getElementById('custom-dpi'); i.value = v; i.oninput() }}
}}

const STEPS = [
  {{ caption: 'Select a layer', hold: 1100 }},
  {{ move: 'card' }}, {{ click: () => select('card') }}, {{ hold: 1500 }},
  {{ caption: 'Pick a screen density', move: tab(4) }}, {{ click: () => tab(4)().click() }}, {{ hold: 1700 }},
  {{ caption: 'Text layers add font size & spacing', move: 'title' }}, {{ click: () => select('title') }}, {{ hold: 1700 }},
  {{ caption: 'Click any value to copy it', move: el('#fontSize-sp') }}, {{ click: () => el('#fontSize-sp')().click(), copy: true }}, {{ hold: 1600 }},
  {{ caption: 'Or enter a custom dpi', move: tab(6) }}, {{ click: () => tab(6)().click() }}, {{ hold: 400 }},
  {{ type: typeDpi('4'), ms: 220 }}, {{ type: typeDpi('40'), ms: 220 }}, {{ type: typeDpi('401'), ms: 220 }}, {{ hold: 1600 }},
  {{ caption: 'Shift-click for combined bounds', move: 'button' }}, {{ click: () => select('title', 'button') }}, {{ hold: 1800 }},
  {{ caption: 'Copy the whole table', move: el('#copy-all') }}, {{ click: () => el('#copy-all')().click() }}, {{ hold: 2200 }}
]
const MOVE_FRAMES = 12, MOVE_MS = 30, CLICK_MS = 160

// replays the script up to frame `target` (or to the end), returning the frame list
function play (target) {{
  const frames = []
  let cur = {{ x: 330, y: 470 }}
  let caption = ''
  let copyFrame = -1
  const emit = (ms, ring) => {{
    frames.push(ms)
    return frames.length - 1 === target ? {{ cur, ring, caption, copyFrame }} : null
  }}
  for (const step of STEPS) {{
    if (step.caption) {{ caption = step.caption; clearToast() }}
    if (step.move) {{
      const from = cur, to = center(step.move)
      for (let i = 1; i <= MOVE_FRAMES; i++) {{
        const t = i / MOVE_FRAMES, e = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2
        cur = {{ x: from.x + (to.x - from.x) * e, y: from.y + (to.y - from.y) * e }}
        const r = emit(MOVE_MS, false); if (r) return r
      }}
    }}
    if (step.click) {{
      clearToast()
      step.click()
      if (step.copy) copyFrame = frames.length
      const r = emit(CLICK_MS, true); if (r) return r
    }}
    if (step.type) {{
      step.type()
      const r = emit(step.ms, false); if (r) return r
    }}
    if (step.hold) {{
      const r = emit(step.hold, false); if (r) return r
    }}
  }}
  return {{ frames }}
}}

window.onload = async () => {{
  await startPlugin()
  const m = location.hash.match(/f=(\\d+)/)
  if (!m) {{
    const {{ frames }} = play(-1)
    document.body.insertAdjacentHTML('beforeend', '<pre id="plan">' + JSON.stringify(frames) + '</pre>')
    return
  }}
  const n = Number(m[1])
  const s = play(n)
  const c = document.getElementById('cursor')
  c.style.left = (s.cur.x - 3) + 'px'
  c.style.top = (s.cur.y - 2) + 'px'
  const ring = document.getElementById('ring')
  ring.hidden = !s.ring
  ring.style.left = s.cur.x + 'px'
  ring.style.top = s.cur.y + 'px'
  document.getElementById('caption').textContent = s.caption
  // the copy flash lasts a few frames after the click
  if (s.copyFrame < 0 || n - s.copyFrame > 2) uiDoc.querySelectorAll('.copied').forEach(e => e.classList.remove('copied'))
}}
</script></body></html>"""
(OUT / 'demo.html').write_text(demo)


# ---------- cover ----------
# dark background with a faint pixel grid, logo tile, unit pills, and a density chart where the
# density shown in the plugin window (xxhdpi) is highlighted in the brand yellow
DENSITIES = [('ldpi', 120), ('mdpi', 160), ('hdpi', 240), ('xhdpi', 320), ('xxhdpi', 480), ('xxxhdpi', 640)]
RAMP = ['#4d4d4d', '#6b6b6b', '#8c8c8c', '#b2b2b2', YELLOW, '#f2f2f2']
chart = ''.join(f'<div class="step{" on" if name == "xxhdpi" else ""}"><i style="width:{8 + dpi / 20}px;height:{8 + dpi / 20}px;'
                f'background:{c}"></i><b>{name}</b><small>{dpi}</small></div>'
                for (name, dpi), c in zip(DENSITIES, RAMP))
units = ''.join(f'<span>{u}</span>' for u in ['px', 'dp', 'sp', 'pt', 'mm', 'inch'])
DARK_VARS = ("--figma-color-bg:#2c2c2c;--figma-color-bg-secondary:#1e1e1e;--figma-color-bg-hover:#383838;"
             "--figma-color-text:#fff;--figma-color-text-secondary:#ffffffb3;--figma-color-text-tertiary:#ffffff66;"
             "--figma-color-border:#444;--figma-color-text-brand:#7cc4f8;--figma-color-bg-brand-tertiary:#394360;"
             "--figma-color-bg-brand:#0c8ce9")


def cover_html(COVER_W, COVER_H, copy_top, chart_bottom, window_top):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{COMMON_CSS}
.stage {{ width: {COVER_W}px; height: {COVER_H}px; background: #141414; }}
.grid {{ position: absolute; inset: 0; background-image: linear-gradient(#1f1f1f 1px, transparent 1px),
  linear-gradient(90deg, #1f1f1f 1px, transparent 1px); background-size: 32px 32px; }}
.copy {{ position: absolute; left: 56px; top: {copy_top}px; width: 360px; }}
.tile {{ display: inline-block; border-radius: 14px; overflow: hidden; line-height: 0; box-shadow: 0 0 0 1px #333; }}
.copy h1 {{ margin: 18px 0 10px; font: 800 44px/1 {ROUNDED}; letter-spacing: -1px; color: #fff; }}
.copy p {{ margin: 0; font: 500 16px/1.4 {ROUNDED}; color: #b2b2b2; }}
.units {{ display: flex; gap: 8px; margin-top: 18px; }}
.units span {{ padding: 4px 11px; border: 1.5px solid #444; border-radius: 6px; color: #fff; font: 700 14px {ROUNDED}; }}
.units span:nth-child(3) {{ background: {YELLOW}; border-color: {YELLOW}; color: #000; }}
.chart {{ position: absolute; left: 56px; bottom: {chart_bottom}px; display: flex; align-items: flex-end; gap: 16px; }}
.step {{ display: flex; flex-direction: column; align-items: center; gap: 3px; color: #fff; font: 700 11px {ROUNDED}; }}
.step i {{ display: block; margin-bottom: 5px; border-radius: 2px; }}
.step small {{ color: #6b6b6b; font-weight: 500; }}
.step.on b {{ color: {YELLOW}; }}
.step.on small {{ color: #b2b2b2; }}
.window {{ transform-origin: top left; background: #2c2c2c; box-shadow: 0 0 0 1px #444, 0 20px 60px rgba(0,0,0,.6); }}
.window header {{ color: #fff; border-color: #444; }}
</style></head><body>
<div class="stage">
  <div class="grid"></div>
  <div class="copy">
    <span class="tile">{logo_svg(64, 'dark')}</span>
    <h1>PixelsConvert</h1>
    <p>Any layer in px, dp, sp, pt, mm and inch, for every screen density.</p>
    <div class="units">{units}</div>
  </div>
  <div class="chart">{chart}</div>
  {window_html.replace('{style}', 'left:432px;top:' + str(window_top) + 'px;transform:scale(0.86)')}
</div>
{code_block}
<script>{RUNTIME}
window.onload = async () => {{
  document.getElementById('ui').contentDocument.documentElement.style.cssText = '{DARK_VARS}'
  await startPlugin()
  select('title')
  uiDoc.querySelectorAll('.tab')[4].click()
}}
</script></body></html>"""


# Community thumbnail (960x540 -> 1920x1080), also used as the README cover
(OUT / 'thumbnail.html').write_text(cover_html(960, 540, copy_top=72, chart_bottom=68, window_top=82))
print('ok')
