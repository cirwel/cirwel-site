// Render public/og.svg to public/og.png (1200×630) with the house faces.
//
// The SVG names the variable fonts first and falls back to Georgia, so a raw
// view of og.svg is legible anywhere; this script wraps it in a page that
// declares @font-face for the vendored fonts in node_modules and screenshots
// it with headless Chromium, so the PNG that share cards actually use is set
// in Bodoni Moda and JetBrains Mono like the site. Run after any change to
// og.svg:  node scripts/render-og.mjs   (needs playwright-core and a Chromium;
// set CHROME to a browser path, or let playwright-core find its own).
import { chromium } from 'playwright-core';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const svg = readFileSync(resolve(root, 'public/og.svg'), 'utf8');
const f = (p) => 'file://' + resolve(root, 'node_modules', p);
const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:'Bodoni Moda Variable';font-style:normal;font-weight:400 900;src:url(${f('@fontsource-variable/bodoni-moda/files/bodoni-moda-latin-opsz-normal.woff2')}) format('woff2-variations')}
@font-face{font-family:'Bodoni Moda Variable';font-style:italic;font-weight:400 900;src:url(${f('@fontsource-variable/bodoni-moda/files/bodoni-moda-latin-opsz-italic.woff2')}) format('woff2-variations')}
@font-face{font-family:'JetBrains Mono';font-weight:500;src:url(${f('@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2')}) format('woff2')}
@font-face{font-family:'JetBrains Mono';font-weight:400;src:url(${f('@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2')}) format('woff2')}
html,body{margin:0;background:#F5F1E8}svg{display:block}
</style><body>${svg}</body>`;

const launch = process.env.CHROME ? { executablePath: process.env.CHROME } : {};
const browser = await chromium.launch({ ...launch, args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await page.setContent(html, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(200);
await page.screenshot({ path: resolve(root, 'public/og.png'), clip: { x: 0, y: 0, width: 1200, height: 630 } });
await browser.close();
console.log('wrote public/og.png');
