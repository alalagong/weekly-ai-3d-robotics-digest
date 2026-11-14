const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const [report, resultPath] = process.argv.slice(2);
if (!report || !resultPath) {
  console.error('Usage: node validate_slam_3d_layout.cjs REPORT.html RESULT.json');
  process.exit(2);
}

async function dimensions(page) {
  return page.locator('.deep-table-scroll').evaluate(region => ({
    available: region.clientWidth,
    table: region.querySelector('table').offsetWidth,
    page: document.documentElement.scrollWidth,
    viewport: innerWidth,
    images: [...region.querySelectorAll('img')].map(img => ({
      width: img.getBoundingClientRect().width,
      loaded: img.complete && img.naturalWidth > 0,
    })),
  }));
}

async function validate() {
  const result = { status: 'failed', report: path.basename(report), checks: {} };
  let browser;
  try {
    const { chromium } = require('playwright');
    browser = await chromium.launch({
      executablePath: process.env.SLAM_CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
      headless: true,
    });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(path.resolve(report)).href);

    const desktop = await dimensions(page);
    result.desktop = desktop;
    const table = page.locator('.deep-table-scroll table');
    assert.equal(await table.locator('thead th').count(), 8, 'Deep-read table needs eight columns');
    assert(desktop.table <= desktop.available + 1 && desktop.page <= desktop.viewport + 1,
      `Desktop table ${desktop.table}px exceeds its ${desktop.available}px region, or the page overflows`);
    assert(desktop.images.every(img => img.loaded && img.width > 0 && img.width <= 221),
      'System figures must load as thumbnails of at most 220px');
    result.checks.desktop = true;

    assert.equal(await page.locator('.deep-evidence details[open], .tracking-group[open], .tracking-paper[open]').count(), 0,
      'Evidence and tracking details should start collapsed');
    const disclosures = page.locator('.deep-evidence details');
    for (const detail of await disclosures.all()) {
      await detail.locator('summary').click();
      assert.notEqual(await detail.getAttribute('open'), null, 'Evidence disclosure did not open');
    }
    result.checks.disclosures = true;

    const papers = page.locator('.tracking-paper');
    const total = await papers.count();
    if (total) {
      const search = page.locator('[data-tracking-search]');
      await search.fill('slam-layout-check-no-matching-paper');
      assert.equal(await page.locator('.tracking-paper:not([hidden])').count(), 0, 'Search should hide nonmatching papers');
      await page.locator('[data-tracking-reset]').click();
      assert.equal(await page.locator('.tracking-paper:not([hidden])').count(), total, 'Reset should restore all papers');
    }
    result.checks.tracking = true;

    await page.setViewportSize({ width: 390, height: 844 });
    const narrow = await dimensions(page);
    result.narrow = narrow;
    assert(narrow.table > narrow.available && narrow.page <= narrow.viewport + 1,
      'On narrow screens the table should scroll inside its region');
    assert.deepEqual(errors, [], 'Browser script errors');
    result.checks.narrow = true;
    result.status = 'passed';
  } catch (error) {
    result.error = error.message;
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n');
    console.log(JSON.stringify(result));
  }
}

validate();
