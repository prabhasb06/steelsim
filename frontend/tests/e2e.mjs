import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import puppeteer from 'puppeteer';
import { createServer } from 'node:http';

// Test the complete browser -> FastAPI -> provider path without a real paid API key.
const modelRequests = [];
const modelServer = createServer(async (request, response) => {
  let body = '';
  for await (const chunk of request) body += chunk;
  modelRequests.push({ path: request.url, authorization: request.headers.authorization, payload: JSON.parse(body) });
  response.writeHead(200, { 'Content-Type': 'application/json' });
  response.end(JSON.stringify({ choices: [{ message: { content: 'E2E provider reviewed live SteelSim telemetry.' } }] }));
});
await new Promise(resolve => modelServer.listen(0, '127.0.0.1', resolve));

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
await page.setViewport({ width: 1440, height: 1000 });
page.setDefaultTimeout(15_000);
const consoleIssues = [];
page.on('console', message => {
  if (message.type() === 'error' || message.type() === 'warn') consoleIssues.push(message.text());
});

async function clickButton(label) {
  await page.waitForFunction(text => [...document.querySelectorAll('button')]
    .some(button => button.textContent?.trim() === text && !button.disabled), {}, label);
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
  await page.select('form select', 'OPENAI_COMPATIBLE');
  await page.type('input[placeholder="Provider model ID"]', 'e2e-text-model');
  await page.type('input[placeholder="https://provider.example/v1"]', `http://127.0.0.1:${modelServer.address().port}/v1`);
  await page.type('input[type="password"]', 'fake-e2e-key');
  await clickButton('Test & connect');
  await page.waitForFunction(() => document.body.textContent?.includes('VERIFIED · e2e-text-model'));
  assert.equal(await page.$eval('input[type="password"]', e => e.value), '');
  await clickButton('Request model review');
  await page.waitForFunction(() => document.body.textContent?.includes('E2E provider reviewed live SteelSim telemetry.'));
  assert.equal(modelRequests.length, 2);
  assert.equal(modelRequests[1].authorization, 'Bearer fake-e2e-key');
  assert.ok(modelRequests[1].payload.messages[1].content.includes('node_telemetry'));
  assert.ok(!JSON.stringify(modelRequests[1].payload).includes('fake-e2e-key'));
  await clickButton('Disconnect');
  await page.waitForFunction(() => document.body.textContent?.includes('API STATUS · NOT CONNECTED'));
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
  await page.waitForFunction(() => document.body.textContent?.includes('Simulated recovery complete'), { timeout: 30_000 });
  await page.select('select', 'OBSERVE');
  await new Promise(resolve => setTimeout(resolve, 500));
  await clickButton('Furnace stability');
  await page.waitForFunction(() => document.body.textContent?.includes('Furnace instability') && !document.querySelector('select')?.disabled);
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

  await clickButton('Operations History');
  const archivedRun = await page.evaluate(async id => {
    const runs = await fetch('/api/history/runs').then(r => r.json());
    return runs.find(r => r.simulation_id === id && r.tick > 0);
  }, createdSimulationId);
  assert.ok(archivedRun, 'Deleted simulation must remain in history');
  await page.waitForSelector(`[data-run-id="${archivedRun.id}"]`);
  await page.click(`[data-run-id="${archivedRun.id}"]`);
  await page.waitForFunction(() => document.body.textContent?.includes('Download incident report'));
  await clickButton('Play replay');
  await page.waitForFunction(() => Number(document.querySelector('input[aria-label="Replay frame"]')?.value) > 0);
  await clickButton('Pause replay');
  if (process.env.STEELSIM_HISTORY_SCREENSHOT) await page.screenshot({ path: process.env.STEELSIM_HISTORY_SCREENSHOT });
  await clickButton('Restore as paused session');
  await page.waitForFunction(() => document.body.textContent?.includes('Simulation Control Center'));
  await page.waitForFunction(() => [...document.querySelectorAll('span')].some(e => e.textContent?.trim() === 'PAUSED'));
  await clickButton('Plant Builder');
  await page.waitForSelector('.react-flow__node');
  assert.equal(await page.$$eval('.react-flow__node', nodes => nodes.length), 10);

  assert.deepEqual(consoleIssues, []);
  console.log('SteelSim browser smoke test passed.');
} finally {
  await browser.close();
  await new Promise(resolve => modelServer.close(resolve));
}
