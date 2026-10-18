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
- **Footer links:** "♥ Show some love" and "Get Pro / Plus →".

## Current status

- All features above work and were tested by the user inside Figma (light and dark mode).
- **Not yet published** as a new Community version: the live plugin is still the old 2020 version.
  Publish via Figma desktop → Plugins → Development → pixels.Convert → Publish new version.
- **Before publishing:**
  - Replace placeholder links `PRO_URL` / `LOVE_URL` (top of the `<script>` in `ui.html`,
    currently `example.com`). The user hasn't given real URLs yet.
  - README cover image and demo GIF (`etc./cover.png`, `etc./demo.gif`) show the old UI.

## Files

| File | Role |
|------|------|
| `manifest.json` | id `870191885836440905` (the published plugin), `editorType: ["figma"]`, `documentAccess: dynamic-page`, no network access |
| `code.ts` | Plugin logic (runs in Figma's sandbox). Source of truth. |
| `code.js` | Compiled `code.ts` — this is what Figma runs. Must be kept in sync (see Build). |
| `ui.html` | The whole UI: HTML + CSS + JS in one file, shown in the plugin window. |
| `etc./` | Cover image, demo GIF, icons used by the README / Community page. |

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

**Formulas** (px are treated as physical pixels at the chosen dpi):
- dp = px × 160 / dpi · sp = dp ÷ font scale (fixed at 1.0, so sp = dp)
- inch = px / dpi · mm = inch × 25.4 · pt = px × 72 / dpi
- Verified: at every density, px = dpi gives 1 inch = 25.4 mm = 72 pt = 160 dp.

**ui.html**
- Table is built from `ROWS` × `UNITS` arrays; density tabs from `DENSITIES`.
- Colors are CSS variables mapped to Figma's theme vars with light fallbacks (for browser previews).
- Values rounded to 2 decimals for display and copying.
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

## Decisions made

- **Everything is free.** Copy values and Custom DPI were planned as premium; the user chose to
  make them free for now. "Pro / Plus" link stays as a pointer to a future website.
- **sp at default font scale only** (sp = dp); no font-scale picker.
- **2-decimal rounding** everywhere (small inch values lose precision, e.g. 0.04 — accepted).
- **Figma-native look:** Figma theme colors, 11px type, tabs instead of a dropdown, no "Get!"
  button (values update live).
- Long property labels wrap to two lines rather than truncating.
- Commits go straight to `master` (user's own repo) after the user confirms it works in Figma.

## Known limitations / ideas

- Multi-select X/Y are canvas coordinates, while single-select X/Y are relative to the parent.
- Text rows only appear for a single text layer.
- Possible later: real premium gating (Figma native payments or license key), font-scale picker,
  more decimals for inch, iOS-specific units (@1x/@2x/@3x).

## Changelog

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
