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
const consoleErrors = [];
page.on('console', message => {
  if (message.type() === 'error') consoleErrors.push(message.text());
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
  await page.goto(baseUrl, { waitUntil: 'networkidle0' });
  const existingSimulationIds = await page.evaluate(async () => {
    const simulations = await fetch('/api/simulations').then(response => response.json());
    return simulations.map(simulation => simulation.id);
  });
  await clickButton('Demo');
  await page.waitForFunction(() => document.body.textContent?.includes('Medium Frequency Induction Furnace'));

  await clickButton('Simulation');
  await page.waitForFunction(() => document.body.textContent?.includes('Simulation Control Center'));
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

  assert.deepEqual(consoleErrors, []);
  console.log('SteelSim browser smoke test passed.');
} finally {
  await browser.close();
}
