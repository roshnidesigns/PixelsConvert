# PixelsConvert — project context

Living summary of the PixelsConvert Figma plugin so work can be picked up in a fresh chat.
**Keep this file updated** whenever features, decisions, or open issues change (update the
Changelog and "Current status" sections at minimum). Code lives in this folder / GitHub
(https://github.com/roshnidesigns/PixelsConvert, branch `master`); this doc explains the *why*
and the state of things, not the code line by line.

_Last updated: 2026-10-18_

## What it is

A Figma Design plugin, **already published on the Figma Community**
(https://www.figma.com/community/plugin/870191885836440905/PixelsConvert). Select a layer and it
shows that layer's X, Y, width and height (plus font size and paragraph spacing for a single text
layer) converted into **px, dp, sp, pt, mm and inch** for a chosen screen density.

- **Density tabs:** ldpi 120 · mdpi 160 (default, baseline) · hdpi 240 · xhdpi 320 · xxhdpi 480 ·
  xxxhdpi 640 · Custom (number field, 1–2000 dpi, red error outside that range).
- **Copy:** click any cell to copy it with its unit (e.g. `24dp`); "Copy all" copies the table as
  tab-separated text (pastes into spreadsheets as columns).
- **Multiple layers:** shows the combined bounding box ("N layers selected (combined bounds)").
- **Mixed text:** a text layer with several font sizes shows "mixed".
- **What's new tour:** on first launch of a new version, a 6-step tour (fresh look, density tabs,
  sp, click to copy, multiple layers, accuracy) with Back/Next, dots, Skip, arrow keys/Esc, then
  "Start converting" fades into the main UI. Shown once per `WHATS_NEW_VERSION` (currently `'2.0'`),
  to new and existing users alike.
- **Footer links:** "♥ Show some love" and "Get Pro / Plus →". **Currently hidden**: `PRO_URL` /
  `LOVE_URL` at the top of the `<script>` in `ui.html` are empty strings. Each link appears once its
  URL is filled in, and the whole footer is hidden while both are empty.

## Current status

- All features above work and were tested by the user inside Figma (light and dark mode).
- **Not yet published** as a new Community version: the live plugin is still the old 2020 version.
  Publish via Figma desktop → Plugins → Development → pixels.Convert → Publish new version.
- **Publishing** (being done by the user, 2026-10-18): the footer links were hidden first because
  the user has no real URLs yet. Upload `etc./plugin-icon.png` (icon), `etc./thumbnail.png`
  (1920×1080 thumbnail) and `etc./carousel/2.png`–`7.png` (carousel, after the thumbnail).
  Tagline chosen from options: "Pixels to dp, sp, pt, mm and inch. For every screen density." (100-char limit).
- **When real URLs arrive:** set `PRO_URL` / `LOVE_URL`, then rebuild the README media (the footer
  will show again) and publish another version.
- README image (thumbnail), carousel and demo GIF are up to date with the new UI. **Rebuild them after any visible UI
  change** (see "README media" below).

## Files

| File | Role |
|------|------|
| `manifest.json` | id `870191885836440905` (the published plugin), `editorType: ["figma"]`, `documentAccess: dynamic-page`, no network access |
| `code.ts` | Plugin logic (runs in Figma's sandbox). Source of truth. |
| `code.js` | Compiled `code.ts` — this is what Figma runs. Must be kept in sync (see Build). |
| `ui.html` | The whole UI: HTML + CSS + JS in one file, shown in the plugin window. |
| `etc./` | Cover image, demo GIF, icons used by the README / Community page. `logo-white.png` / `logo-black.png` are the user's 100×100 logos (light / dark); `logo-white.svg` / `logo-black.svg` are the vector redraws; `plugin-icon.png` is the 128×128 Community icon (dark version). |
| `scripts/media/` | Scripts that regenerate `etc./thumbnail.png`, `etc./carousel/*.png`, `etc./demo.gif` and `etc./plugin-icon.png` from the real UI (output scratch in ignored `build/`). |

## Architecture

**code.ts**
- `currentDpi` holds the chosen density (starts at 160) so selection changes don't reset it.
- `update()` runs on selection change and when the UI sends a new dpi. It posts one message to the
  UI: `{type: 'values', str, dpi, values}` where each value row is `{px, dp, sp, mm, pt, inch}`,
  `null` (row not applicable → hidden in UI) or `'mixed'`. With nothing selected it posts
  `{type: 'empty', str}`.
- Single layer → its own `x/y/width/height` (relative to parent). Several layers → union of
  `absoluteBoundingBox` (canvas coordinates).
- Messages handled from UI: `setdpi`, `notify` (→ `figma.notify`), `open` (→ `figma.openExternal`),
  `resize` (UI reports its content height; window is 560px wide, height clamped 160–600).
- `showUI` uses `themeColors: true` so the UI gets Figma's `--figma-color-*` CSS variables.
- Startup is async: `start()` reads `figma.clientStorage` key `whatsNewSeen`. If it isn't
  `WHATS_NEW_VERSION`, it adds `data-whats-new="<version>"` to the `<html>` tag of `__html__`
  **before** `showUI`, so the tour appears with no flash of the main UI. The UI sends
  `whats-new-done` when the tour ends and the plugin saves the version. If storage fails, the
  tour is skipped. `update()` does nothing until the UI is open.
- **To show a tour for a future update:** bump `WHATS_NEW_VERSION` and rewrite `SLIDES` in `ui.html`.

**Formulas** (px are treated as physical pixels at the chosen dpi):
- dp = px × 160 / dpi · sp = dp ÷ font scale (fixed at 1.0, so sp = dp)
- inch = px / dpi · mm = inch × 25.4 · pt = px × 72 / dpi
- Verified: at every density, px = dpi gives 1 inch = 25.4 mm = 72 pt = 160 dp.

**ui.html**
- Table is built from `ROWS` × `UNITS` arrays; density tabs from `DENSITIES`.
- Colors are CSS variables mapped to Figma's theme vars with light fallbacks (for browser previews).
- Values rounded to 2 decimals for display and copying.
- The main UI is wrapped in `<main id="app">`; the tour is `<section id="whats-new">`. `SLIDES`
  holds each step's title, text and an HTML/CSS mini illustration (no image files).
- Clipboard uses a hidden textarea + `document.execCommand('copy')` because `navigator.clipboard`
  is blocked in plugin iframes.
- Needs `<!DOCTYPE html>` — without it the page runs in quirks mode and tables ignore the
  font size / colors.

## Build / dev environment

- **Node is not installed** on the user's Mac, so `npm run build` can't run. `code.js` is produced
  by hand-stripping the TypeScript annotations from `code.ts` (a `sed` over the few typed function
  signatures). Keep `code.ts` lightly typed so this stays trivial. If Node gets installed:
  `npm install` then `npm run build` (tsc, typings from `@figma/plugin-typings`).
- Logic testing without Figma: run `code.js` against a mocked `figma` object with macOS's built-in
  JS engine (`osascript -l JavaScript file.js`).
- UI testing: open `ui.html` in a browser and call `window.onmessage({data:{pluginMessage:…}})`
  with sample data.
- Run in Figma: desktop app → Plugins → Development → Import plugin from manifest → `manifest.json`.

### README media

`scripts/media/build_pages.py` writes `build/thumbnail.html` and `build/demo.html`, which embed the
real `ui.html` (as a same-origin `srcdoc` iframe) and run the real `code.js` against a mock
`figma` object (with `clientStorage` reporting the tour as seen, so the media shows the main
UI). So the images always show true values. The demo is a scripted storyboard
(`STEPS`: select card → xxhdpi → text layer → copy a cell → custom dpi 401 → shift-select →
Copy all) with a fake cursor, captions and Figma-style toasts, on a mock canvas with an
"Android · Home" phone frame (1080×1920 at 0.2 zoom).
`scripts/media/render.py` screenshots each frame with headless Chrome (6 in parallel) and stitches
the GIF with Pillow (shared 128-color palette, ~400 KB, 1560×930), plus renders the thumbnail and carousel at 2×.

```
python3 scripts/media/build_pages.py
<venv>/bin/python scripts/media/render.py   # needs Google Chrome + Pillow (pip install pillow in a venv)
```

`render.py` also regenerates `etc./plugin-icon.png` from `LOGO['dark']` in `build_pages.py`.
`scripts/media/carousel.py` (imported by `render.py`) builds the Community carousel slides 2–7,
1920×1080 each, dark style: (2) density tabs + custom dpi 401, (3) sp column highlighted,
(4) click to copy with cursor + "Copied 24sp" toast, (5) multi-select with a phone frame,
(6) light + dark windows overlapping, (7) the What's new tour. Slide 1 is `etc./thumbnail.png`.
There is no separate README cover anymore: the README uses `thumbnail.png` (user's choice).

**Brand style (since 2026-10-18):**
- **Logo:** four squares on a 100×100 grid, one of them yellow `#FBF151`. Two versions with
  slightly different layouts (exact squares in `LOGO` in `scripts/media/build_pages.py`):
  light (on white: grey, yellow, black, light grey) and dark (on `#111111`: light grey, yellow,
  white, dark grey). **The dark logo is the plugin icon** (chosen because it reads well in both of
  Figma's themes; the light one became a glaring white tile in dark theme). The user redrew the
  dark logo with more padding (8 px sides, 10.5 px top/bottom) so Figma's rounded icon corners
  don't clip the squares. Dark is also used on the cover and in the plugin window header in the
  media; light is for light backgrounds.
- **Yellow:** `#FBF151` (the logo's yellow) everywhere. The old `#FCF300` is retired.
- **Thumbnail / README cover (1920×1080):** near-black `#141414` with a faint 32px pixel grid, the dark logo on a rounded tile,
  white rounded heavy title (`ui-rounded`), unit pills with **sp in yellow**, a density
  chart (squares growing ldpi → xxxhdpi in a grey ramp, xxhdpi in yellow, matching the tab shown),
  and the plugin window in Figma's dark theme.
- **Demo GIF:** light Figma canvas; yellow captions with black outlines; the phone's hero card is
  dark (`#111`) with the dark logo.
- The old style (yellow background, black outline circles, the "dpi" sun icon) is retired. The
  user picked the dark cover (concept C) combined with D's density chart, out of 4 concepts.
- The user's Figma file with the logo (`QPO5NiVWArI5VFovoah68G`, node `2241:10`) isn't shared with
  the connected Figma account, so the logos were redrawn from the PNGs (they match to within a few
  levels of edge smoothing).

## Decisions made

- **Everything is free.** Copy values and Custom DPI were planned as premium; the user chose to
  make them free for now. "Pro / Plus" link stays as a pointer to a future website.
- **sp at default font scale only** (sp = dp); no font-scale picker.
- **2-decimal rounding** everywhere (small inch values lose precision, e.g. 0.04 — accepted).
- **Figma-native look:** Figma theme colors, 11px type, tabs instead of a dropdown, no "Get!"
  button (values update live).
- Long property labels wrap to two lines rather than truncating.
- Commits go straight to `master` (user's own repo) after the user confirms it works in Figma.
- **Figma data security answers** (publish dialog): no backend; no network requests; no user
  authentication; does not store data read/derived from the plugin API (clientStorage only holds the
  constant tour version); solo developer. Re-check these if networking, storage or auth is ever added.
- **The repo is public**, and that's fine. The user knows this `CLAUDE.md` (paths, plans,
  decisions) is visible and chose to keep it in the repo.

## Known limitations / ideas

- Multi-select X/Y are canvas coordinates, while single-select X/Y are relative to the parent.
- Text rows only appear for a single text layer.
- Possible later: real premium gating (Figma native payments or license key), font-scale picker,
  more decimals for inch, iOS-specific units (@1x/@2x/@3x).

## Changelog

- **2026-10-18** — 1920×1080 Community thumbnail (also the README image; `cover.png` removed) and
  six carousel slides.
- **2026-10-18** — New square logo with yellow (light + dark versions, vectors, 128px icon);
  dark cover with density chart and yellow accent; GIF updated with the new logo.
- **2026-10-18** — What's new tour for v2.0 (once per version, via `figma.clientStorage`).
- **2026-10-18** — Hid footer links (empty URLs) for the Community release; rebuilt cover + GIF.
- **2026-10-18** — New README cover + demo GIF of the redesigned UI, generated by
  `scripts/media/`; README feature list and relative image links.
- **2026-10-18** — Added this context doc.
- **2026-10-05** — `4bfc5d0` UI redesign: Figma theme colors + dark mode, density tabs with custom
  dpi field, selection summary + Copy all, empty state, auto-sizing window, wrapping labels.
- **2026-10-05** — `d8db996` sp column, custom DPI, click-to-copy + Copy all, footer links.
- **2026-10-05** — `bb541e4` Fixed mm/inch formulas (ignored dpi), dpi resetting on selection
  change, `figma.mixed` font sizes, multi-select; consolidated code; manifest `editorType` fix;
  README links → roshnidesigns.

## Other folders in the workspace

`/Users/roshni/Desktop/Figma Plugins/` also contains **Swapper** (has its own `CLAUDE.md`) and
**PluginX** — separate plugins, not related to this one.
