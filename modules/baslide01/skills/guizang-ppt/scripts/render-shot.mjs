#!/usr/bin/env node
import { existsSync } from 'node:fs';

let puppeteer;
const fallbackPuppeteerPath = process.env.PUPPETEER_CORE_PATH;

try {
  ({ default: puppeteer } = await import('puppeteer-core'));
} catch (error) {
  if (fallbackPuppeteerPath && existsSync(fallbackPuppeteerPath)) {
    ({ default: puppeteer } = await import(fallbackPuppeteerPath));
  } else {
    console.error('Failed to load puppeteer-core. Install puppeteer-core or set PUPPETEER_CORE_PATH.');
    console.error(error.message);
    process.exit(1);
  }
}

const url = process.argv[2] || 'http://127.0.0.1:8765/assets/template-tableai.html';
const out = process.argv[3] || '/tmp/tableai-slide1.png';

const executableCandidates = [
  process.env.PUPPETEER_EXECUTABLE_PATH,
  process.env.BROWSER_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
].filter((candidate) => candidate && existsSync(candidate));

if (!executableCandidates.length) {
  console.error('No Chrome/Chromium executable found. Set PUPPETEER_EXECUTABLE_PATH or BROWSER_PATH environment variable.');
  process.exit(1);
}

const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
  executablePath: executableCandidates[0],
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 2 });
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise((r) => setTimeout(r, 1500));
  await page.screenshot({ path: out, fullPage: false });
  console.log('saved', out);
} finally {
  await browser.close();
}
