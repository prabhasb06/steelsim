import puppeteer from 'puppeteer';

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Capture console logs
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log('BROWSER ERROR:', msg.text());
        }
    });
    
    page.on('pageerror', error => {
        console.log('PAGE ERROR:', error.message);
    });

    console.log('Navigating to http://localhost:5173/');
    await page.goto('http://localhost:5173/');
    
    // Wait for the app to load
    await page.waitForSelector('button');
    
    // Click "Load TMT Template" (Demo)
    const loadDemoText = await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const demoBtn = btns.find(b => b.textContent && b.textContent.includes('Load TMT Template'));
        if (demoBtn) {
            demoBtn.click();
            return true;
        }
        return false;
    });
    console.log('Clicked Load Demo:', loadDemoText);
    
    // Wait for nodes to populate
    await page.waitForTimeout(2000);
    
    // Find an edge and select it, then press Delete
    console.log('Attempting to delete an edge...');
    await page.evaluate(() => {
        const edges = document.querySelectorAll('.react-flow__edge');
        if (edges.length > 0) {
            // Click the first edge
            const event = new MouseEvent('click', { bubbles: true, cancelable: true });
            edges[0].dispatchEvent(event);
        }
    });
    
    await page.waitForTimeout(500);
    
    await page.keyboard.press('Delete');
    await page.waitForTimeout(1000);
    
    console.log('Finished testing edge delete.');
    await browser.close();
})();
