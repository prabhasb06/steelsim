import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import puppeteer from 'puppeteer';

const baseUrl = process.env.STEELSIM_BASE_URL ?? 'http://127.0.0.1:5173/';
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
page.setDefaultTimeout(15_000);
const consoleIssues = [];
page.on('console', message => {
  if (message.type() === 'error' || message.type() === 'warn') consoleIssues.push(message.text());
});

async function clickButton(label) {
  const clicked = await page.evaluate(text => {
    const button = [...document.querySelectorAll('button')]
      .find(candidate => candidate.textContent?.trim() === text);
    button?.click();
    return Boolean(button);
  }, label);
  assert.equal(clicked, true, `Expected button "${label}" to be available`);
}

async function clickButtonByTitle(title) {
  const clicked = await page.evaluate(value => {
    const button = document.querySelector(`button[title="${value}"]`);
    button?.click();
    return Boolean(button);
  }, title);
  assert.equal(clicked, true, `Expected button titled "${title}" to be available`);
}

try {
  await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
  const existingSimulationIds = await page.evaluate(async () => {
    const simulations = await fetch('/api/simulations').then(response => response.json());
    return simulations.map(simulation => simulation.id);
  });
  await clickButton('ACAMIS Intelligence');
  await page.waitForFunction(() => document.body.textContent?.includes('Operational Intelligence is standing by'));
  await clickButton('Open Simulation Control');
  await page.waitForFunction(() => document.body.textContent?.includes('Simulation Control Center'));
  await clickButton('Plant Builder');
  await clickButton('Demo');
  await page.waitForFunction(() => document.body.textContent?.includes('Medium Frequency Induction Furnace'));

  await clickButton('Simulation');
  await page.waitForFunction(() => document.body.textContent?.includes('Simulation Control Center'));
  const hiddenBuilderStyle = await page.$eval('[data-testid="builder-layer"]', element => {
    const style = getComputedStyle(element);
    return { inert: element.inert, pointerEvents: style.pointerEvents, left: element.getBoundingClientRect().left, viewport: window.innerWidth };
  });
  assert.equal(hiddenBuilderStyle.inert, true);
  assert.equal(hiddenBuilderStyle.pointerEvents, 'none');
  assert.ok(hiddenBuilderStyle.left >= hiddenBuilderStyle.viewport, 'Inactive Builder must be moved outside the viewport');
  await clickButton('Run Simulation');
  await page.waitForFunction(() => document.body.textContent?.includes('LIVE BACKEND'));
  await page.waitForFunction(() => {
    const badges = [...document.querySelectorAll('span')];
    return badges.some(element => element.textContent?.trim() === 'RUNNING');
  });
  const createdSimulationId = await page.evaluate(async existingIds => {
    const simulations = await fetch('/api/simulations').then(response => response.json());
    return simulations.find(simulation => !existingIds.includes(simulation.id))?.id;
  }, existingSimulationIds);
  assert.ok(createdSimulationId, 'Expected the UI to create a new backend simulation');

  await clickButton('ACAMIS Intelligence');
  await page.waitForFunction(() => document.body.textContent?.includes('Autonomous Operations Center'));
  await clickButton('Cooling water');
  await page.waitForFunction(() => document.body.textContent?.includes('Verified operating incident'));
  for (const domain of ['Safety', 'Maintenance', 'Quality', 'Production', 'Energy', 'Logistics']) {
    assert.equal(await page.evaluate(label => document.body.textContent?.includes(label), domain), true);
  }
  await page.select('select', 'ADVISORY');
  await new Promise(resolve => setTimeout(resolve, 500));
  await clickButton('Apply');
  await page.waitForFunction(() => document.body.textContent?.includes('PROCEDURE_EXECUTED'));
  await clickButton('Clear scenario');
  await page.waitForFunction(() => document.body.textContent?.includes('Plant baseline is being monitored'));
  await page.select('select', 'AUTONOMOUS_SIMULATION');
  await new Promise(resolve => setTimeout(resolve, 500));
  await clickButton('Rolling mill');
  await page.waitForFunction(() => document.body.textContent?.includes('AUTONOMOUS_PROCEDURE_EXECUTED'));
  await page.waitForFunction(() => document.body.textContent?.includes('Autonomous recovery verified'));
  await page.select('select', 'OBSERVE');
  await new Promise(resolve => setTimeout(resolve, 500));
  await clickButton('Furnace stability');
  await page.select('select', 'AUTONOMOUS_SIMULATION');
  await page.waitForFunction(() => document.body.textContent?.includes('HUMAN_VERIFICATION_REQUIRED'));
  await page.waitForFunction(() => document.body.textContent?.includes('STABILIZED'));
  const highRiskActionsBlocked = await page.$$eval('button', buttons =>
    buttons.filter(button => button.textContent?.trim() === 'Apply').every(button => button.disabled),
  );
  assert.equal(highRiskActionsBlocked, true, 'High-risk autonomous procedures must require human verification');
  await clickButton('Clear scenario');

  await clickButton('Simulation');
  await page.waitForFunction(() => document.body.textContent?.includes('Simulation Control Center'));

  await clickButton('Pause');
  await page.waitForFunction(() => {
    const badges = [...document.querySelectorAll('span')];
    return badges.some(element => element.textContent?.trim() === 'PAUSED');
  });
  await clickButton('Reset');
  await page.waitForFunction(() => {
    const badges = [...document.querySelectorAll('span')];
    return badges.some(element => element.textContent?.trim() === 'READY');
  });

  await clickButton('Plant Builder');
  await clickButtonByTitle('Clear');
  await page.waitForFunction(async simulationId => {
    const simulations = await fetch('/api/simulations').then(response => response.json());
    return simulations.every(simulation => simulation.id !== simulationId);
  }, {}, createdSimulationId);
  await clickButton('Simulation');
  await page.waitForFunction(() => document.body.textContent?.includes('No plant is configured'));
  await clickButton('Overview');
  await page.waitForFunction(() => document.body.textContent?.includes('Plant Overview'));

  assert.deepEqual(consoleIssues, []);
  console.log('SteelSim browser smoke test passed.');
} finally {
  await browser.close();
}
