const WIDTH = 560
figma.showUI(__html__, { width: WIDTH, height: 320, themeColors: true })

const BASELINE_DPI = 160
const MM_PER_INCH = 25.4
// Android's default font scale; sp equals dp at this scale
const FONT_SCALE = 1

// density chosen in the UI; kept so selection changes don't reset it
let currentDpi = BASELINE_DPI

figma.ui.onmessage = msg => {
  if (msg.type === 'setdpi') {
    currentDpi = msg.val
    update()
  } else if (msg.type === 'notify') {
    figma.notify(msg.text)
  } else if (msg.type === 'open') {
    figma.openExternal(msg.url)
  } else if (msg.type === 'resize') {
    figma.ui.resize(WIDTH, Math.max(160, Math.min(600, msg.height)))
  }
}

figma.on('selectionchange', update)

// functions to get units
function getdp (px: number, dpi: number) {
  return px * (BASELINE_DPI / dpi)
}
function getsp (px: number, dpi: number) {
  return getdp(px, dpi) / FONT_SCALE
}
function getpt (px: number, dpi: number) {
  return px * (72 / dpi)
}
function getinch (px: number, dpi: number) {
  return px / dpi
}
function getmm (px: number, dpi: number) {
  return (px / dpi) * MM_PER_INCH
}

// converts a px value (or null when not applicable / mixed) into every unit
function convert (px: number | null, dpi: number) {
  if (px === null) return null
  return {
    px,
    dp: getdp(px, dpi),
    sp: getsp(px, dpi),
    mm: getmm(px, dpi),
    pt: getpt(px, dpi),
    inch: getinch(px, dpi)
  }
}

// figma.mixed is returned when a text layer has more than one value for a property
function numberOrMixed (value: number | PluginAPI['mixed']) {
  return value === figma.mixed ? 'mixed' : value
}

// x, y, width, height of the selection; combined bounds when several layers are selected
function getBounds (selection: readonly SceneNode[]) {
  if (selection.length === 1) {
    const node = selection[0]
    return { x: node.x, y: node.y, width: node.width, height: node.height }
  }
  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity
  for (const node of selection) {
    const box = node.absoluteBoundingBox
    if (!box) continue
    minX = Math.min(minX, box.x)
    minY = Math.min(minY, box.y)
    maxX = Math.max(maxX, box.x + box.width)
    maxY = Math.max(maxY, box.y + box.height)
  }
  return { x: minX, y: minY, width: maxX - minX, height: maxY - minY }
}

function update () {
  const selection = figma.currentPage.selection
  if (selection.length === 0) {
    figma.ui.postMessage({ type: 'empty', str: 'Select a layer to see its values' })
    return
  }

  const dpi = currentDpi
  const bounds = getBounds(selection)
  const values = {
    x: convert(bounds.x, dpi),
    y: convert(bounds.y, dpi),
    height: convert(bounds.height, dpi),
    width: convert(bounds.width, dpi),
    fontSize: null,
    paragraphSpacing: null
  }

  // text values are only shown for a single text layer
  const node = selection[0]
  if (selection.length === 1 && node.type === 'TEXT') {
    const fontSize = numberOrMixed(node.fontSize)
    const paragraphSpacing = numberOrMixed(node.paragraphSpacing)
    values.fontSize = fontSize === 'mixed' ? 'mixed' : convert(fontSize, dpi)
    values.paragraphSpacing = paragraphSpacing === 'mixed' ? 'mixed' : convert(paragraphSpacing, dpi)
  }

  const str = selection.length === 1
    ? node.name
    : selection.length + ' layers selected (combined bounds)'

  figma.ui.postMessage({ type: 'values', str, dpi, values })
}

update()
