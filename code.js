figma.showUI(__html__);
figma.ui.resize(600, 400);
figma.ui.onmessage = msg => {
    if (figma.currentPage.selection.length > 0) {
        if (figma.currentPage.selection[0].type === 'TEXT') {
            const sel = figma.currentPage.selection[0];
            const dpi = msg.val;
            sendTextpx(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextdp(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextmm(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextpt(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextinch(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
        }
        else {
            const sel = figma.currentPage.selection[0];
            const dpi = msg.val;
            sendpx(sel.x, sel.y, sel.height, sel.width, dpi);
            senddp(sel.x, sel.y, sel.height, sel.width, dpi);
            sendmm(sel.x, sel.y, sel.height, sel.width, dpi);
            sendpt(sel.x, sel.y, sel.height, sel.width, dpi);
            sendinch(sel.x, sel.y, sel.height, sel.width, dpi);
        }
    }
    else {
        const message = 'Select atleast 1 layer';
        sendmsg(message);
    }
};
// if no layer selected
function sendmsg(str) {
    figma.ui.postMessage({
        type: 'sendmsg',
        str
    });
}
// functions to get units
function getdp(px, dpi) {
    const dp = px * (160 / dpi);
    return dp;
}
function getpt(px, dpi) {
    const pt = px * (72 / dpi);
    return pt;
}
function getinch(px, dpi) {
    const inch = 0.01 * px;
    return inch;
}
function getmm(px, dpi) {
    const mm = 0.26 * px;
    return mm;
}
// if the active component is not tex tthen return these values
function sendpx(x, y, height, width, dpi) {
    figma.ui.postMessage({
        type: 'sendpx',
        x,
        y,
        height,
        width
    });
}
function senddp(x, y, height, width, dpi) {
    figma.ui.postMessage({
        type: 'senddp',
        x: getdp(x, dpi),
        y: getdp(y, dpi),
        height: getdp(height, dpi),
        width: getdp(width, dpi)
    });
}
function sendmm(x, y, height, width, dpi) {
    figma.ui.postMessage({
        type: 'sendmm',
        x: getmm(x, dpi),
        y: getmm(y, dpi),
        height: getmm(height, dpi),
        width: getmm(width, dpi)
    });
}
function sendpt(x, y, height, width, dpi) {
    figma.ui.postMessage({
        type: 'sendpt',
        x: getpt(x, dpi),
        y: getpt(y, dpi),
        height: getpt(height, dpi),
        width: getpt(width, dpi)
    });
}
function sendinch(x, y, height, width, dpi) {
    figma.ui.postMessage({
        type: 'sendinch',
        x: getinch(x, dpi),
        y: getinch(y, dpi),
        height: getinch(height, dpi),
        width: getinch(width, dpi)
    });
}
//  if current selection is text then return these
function sendTextpx(x, y, height, width, fontSize, paragraphSpacing, dpi) {
    figma.ui.postMessage({
        type: 'sendTextpx',
        x,
        y,
        height,
        width,
        fontSize,
        paragraphSpacing
    });
}
function sendTextdp(x, y, height, width, fontSize, paragraphSpacing, dpi) {
    figma.ui.postMessage({
        type: 'sendTextdp',
        x: getdp(x, dpi),
        y: getdp(y, dpi),
        height: getdp(height, dpi),
        width: getdp(width, dpi),
        fontSize: getdp(fontSize, dpi),
        paragraphSpacing: getdp(paragraphSpacing, dpi)
    });
}
function sendTextmm(x, y, height, width, fontSize, paragraphSpacing, dpi) {
    figma.ui.postMessage({
        type: 'sendTextmm',
        x: getmm(x, dpi),
        y: getmm(y, dpi),
        height: getmm(height, dpi),
        width: getmm(width, dpi),
        fontSize: getmm(fontSize, dpi),
        paragraphSpacing: getmm(paragraphSpacing, dpi)
    });
}
function sendTextpt(x, y, height, width, fontSize, paragraphSpacing, dpi) {
    figma.ui.postMessage({
        type: 'sendTextpt',
        x: getpt(x, dpi),
        y: getpt(y, dpi),
        height: getpt(height, dpi),
        width: getpt(width, dpi),
        fontSize: getpt(fontSize, dpi),
        paragraphSpacing: getpt(paragraphSpacing, dpi)
    });
}
function sendTextinch(x, y, height, width, fontSize, paragraphSpacing, dpi) {
    figma.ui.postMessage({
        type: 'sendTextinch',
        x: getinch(x, dpi),
        y: getinch(y, dpi),
        height: getinch(height, dpi),
        width: getinch(width, dpi),
        fontSize: getinch(fontSize, dpi),
        paragraphSpacing: getinch(paragraphSpacing, dpi)
    });
}
function sendresp() {
    figma.ui.postMessage({
        type: 'resp'
    });
}
figma.on('selectionchange', () => {
    if (figma.currentPage.selection.length > 0) {
        sendresp();
        if (figma.currentPage.selection[0].type === 'TEXT') {
            const sel = figma.currentPage.selection[0];
            const dpi = 160;
            sendTextpx(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextdp(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextmm(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextpt(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
            sendTextinch(sel.x, sel.y, sel.height, sel.width, sel.fontSize, sel.paragraphSpacing, dpi);
        }
        else {
            const sel = figma.currentPage.selection[0];
            const dpi = 160;
            sendpx(sel.x, sel.y, sel.height, sel.width, dpi);
            senddp(sel.x, sel.y, sel.height, sel.width, dpi);
            sendmm(sel.x, sel.y, sel.height, sel.width, dpi);
            sendpt(sel.x, sel.y, sel.height, sel.width, dpi);
            sendinch(sel.x, sel.y, sel.height, sel.width, dpi);
        }
    }
    else {
        const message = 'Select atleast 1 layer';
        sendmsg(message);
    }
});
