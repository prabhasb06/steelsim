import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import puppeteer from '../frontend/node_modules/puppeteer/lib/puppeteer/puppeteer.js';

const baseUrl = 'http://127.0.0.1:5174/';
const browserCandidates = [
  process.env.PUPPETEER_EXECUTABLE_PATH,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
].filter(Boolean);

const executablePath = browserCandidates.find(candidate => existsSync(candidate));
const browser = await puppeteer.launch({
  headless: true,
  ...(executablePath ? { executablePath } : {}),
});

const page = await browser.newPage();
page.on('response', resp => { if (resp.status() >= 400) console.log('404 URL: ' + resp.url() + ' (' + resp.status() + ')'); });
const consoleErrors = [];
page.on('console', msg => {
  if (msg.type() === 'error') consoleErrors.push(msg.text());
});

try {
  console.log('1. Navigating to homepage: ' + baseUrl);
  await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.VPHero, h1, .name', { timeout: 8000 });
  const homeText = await page.evaluate(() => document.body.textContent);
  console.log('   Home loaded. Length: ' + homeText.length);
  assert.ok(homeText.includes('SteelSim'), 'Expected home page to include SteelSim');
  assert.ok(homeText.includes('SteelSim creates the factory; ACAMIS understands the factory'), 'Expected core product statement');

  // 2. Open Getting Started -> Introduction
  console.log('2. Opening Introduction page...');
  await page.goto(`${baseUrl}getting-started/introduction`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  const introHeading = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + introHeading);
  assert.ok(introHeading.includes('Introduction'));

  // 3. Test Task 1 pages
  console.log('3. Testing Task 1 pages...');
  await page.goto(`${baseUrl}task-1-builder/overview`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  let h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Task 1 overview'));

  await page.goto(`${baseUrl}task-1-builder/topology-validation`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Topology validation'));

  // 4. Test Task 2 pages
  console.log('4. Testing Task 2 pages...');
  await page.goto(`${baseUrl}task-2-simulation/overview`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Task 2 overview'));

  await page.goto(`${baseUrl}task-2-simulation/simulation-lifecycle`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Simulation lifecycle'));

  await page.goto(`${baseUrl}task-2-simulation/control-center`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Simulation Control Center'));

  // 5. Test Reference pages
  console.log('5. Testing Reference pages...');
  await page.goto(`${baseUrl}reference/standard-tmt-topology`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Standard TMT topology'));

  await page.goto(`${baseUrl}reference/rest-api`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('REST API'));

  // 6. Test Project pages
  console.log('6. Testing Project pages...');
  await page.goto(`${baseUrl}project/architecture`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Architecture'));

  await page.goto(`${baseUrl}project/integration`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 8000 });
  h1 = await page.$eval('h1', el => el.textContent?.trim());
  console.log('   H1: ' + h1);
  assert.ok(h1.includes('Task 1 and Task 2 integration'));

  // 7. Test Right-Side Outline (On this page)
  console.log('7. Verifying On this page outline...');
  const outlineExists = await page.evaluate(() => {
    const outline = document.querySelector('.VPDocAsideOutline, .outline-title, .aside-container');
    return Boolean(outline);
  });
  console.log('   Outline present: ' + outlineExists);

  // 8. Test Search button existence
  console.log('8. Testing local search trigger...');
  const searchBtn = await page.$('.VPNavBarSearchButton, .DocSearch-Button');
  console.log('   Search button found: ' + Boolean(searchBtn));

  // 9. Test Theme Switcher (Dark / Light toggle)
  console.log('9. Testing theme switcher...');
  const initialThemeIsDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
  const toggled = await page.evaluate(() => {
    const btn = document.querySelector('.VPSwitchAppearance button, .VPSwitchAppearance');
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  });
  if (toggled) {
    await new Promise(r => setTimeout(r, 400));
    const toggledThemeIsDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    console.log('   Appearance toggled: ' + toggledThemeIsDark);
    assert.notEqual(initialThemeIsDark, toggledThemeIsDark);
    await page.evaluate(() => {
      document.querySelector('.VPSwitchAppearance button, .VPSwitchAppearance')?.click();
    });
  }

  // 10. Test Mobile Viewport
  console.log('10. Testing mobile responsive layout (375x667)...');
  await page.setViewport({ width: 375, height: 667 });
  await page.goto(`${baseUrl}getting-started/introduction`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('h1', { timeout: 5000 });
  const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  console.log('   Mobile horizontal overflow: ' + hasOverflow);
  assert.equal(hasOverflow, false, 'Mobile viewport should have no horizontal overflow');

  // 11. Verify Console Errors
  console.log('11. Verifying console errors...');
  console.log('   Console errors count: ' + consoleErrors.length);
  if (consoleErrors.length > 0) {
    console.log('   Errors: ' + JSON.stringify(consoleErrors));
  }
  assert.deepEqual(consoleErrors, []);

  console.log('\n======================================================');
  console.log('>>> ALL DOCUMENTATION SITE CHECKS PASSED WITH 0 ERRORS! <<<');
  console.log('======================================================\n');
} finally {
  await browser.close();
}
