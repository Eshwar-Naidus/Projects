const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  const errors = [];
  page.on('pageerror', err => errors.push({ type: 'pageerror', message: err.message }));
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push({ type: 'console.error', message: msg.text() });
  });

  console.log("--- AUDITING INDEX.HTML ---");
  await page.goto('http://127.0.0.1:8799/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  const indexMeta = await page.evaluate(() => {
    return {
      title: document.title,
      fps: document.getElementById('fps-readout')?.textContent,
      glbStatus: document.getElementById('glb-status')?.textContent,
      selectedMesh: document.getElementById('selected-mesh-name')?.textContent,
      oscCanvasPresent: !!document.getElementById('motion-oscilloscope'),
      subCanvasPresent: !!document.getElementById('subassembly-canvas'),
      subActiveTitle: document.getElementById('sub-active-title')?.textContent,
      subWatchdog: document.getElementById('sub-meta-watchdog')?.textContent,
      interactiveRowCount: document.querySelectorAll('.manifest-table tbody tr').length
    };
  });
  console.log("INDEX EVALUATION:", JSON.stringify(indexMeta, null, 2));

  // Test interactive click on sub-assembly table row
  await page.click('tr[data-mesh="SM_Kronos_Stator_Mid"]');
  await page.waitForTimeout(300);
  const afterRowClick = await page.evaluate(() => ({
    selectedMesh: document.getElementById('selected-mesh-name')?.textContent,
    subActiveTitle: document.getElementById('sub-active-title')?.textContent,
    activeAttr: document.querySelector('tr[data-mesh="SM_Kronos_Stator_Mid"]')?.dataset.active
  }));
  console.log("AFTER ROW CLICK:", JSON.stringify(afterRowClick, null, 2));

  // Test self-devastation auto-healing immunity trigger
  await page.click('#btn-sub-devastate');
  await page.waitForTimeout(300);
  const afterDevastate = await page.evaluate(() => ({
    subWatchdog: document.getElementById('sub-meta-watchdog')?.textContent,
    glbStatus: document.getElementById('glb-status')?.textContent
  }));
  console.log("AFTER DEVASTATION TRIGGER:", JSON.stringify(afterDevastate, null, 2));

  console.log("--- AUDITING IMPLEMENTATION-3D-FLOWCHART.HTML ---");
  await page.goto('http://127.0.0.1:8799/implementation-3d-flowchart.html', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  const flowMeta = await page.evaluate(() => {
    return {
      title: document.title,
      activeNode: document.getElementById('hud-active-node')?.textContent,
      telemetry: document.getElementById('hud-telemetry')?.textContent,
      svgRotorCount: document.querySelectorAll('.svg-rotor').length,
      svgMovingPackets: [0,1,2,3,4].map(i => !!document.getElementById(`svg-pkt-${i}`)),
      cameraAspectResponsive: !!window.ResizeObserver
    };
  });
  console.log("FLOWCHART EVALUATION:", JSON.stringify(flowMeta, null, 2));

  // Test interactive SVG node click
  await page.click('.svg-node[data-idx="2"]');
  await page.waitForTimeout(300);
  const afterFlowClick = await page.evaluate(() => ({
    activeNode: document.getElementById('hud-active-node')?.textContent,
    inspectorTitle: document.getElementById('insp-title')?.textContent
  }));
  console.log("AFTER FLOWCHART NODE CLICK:", JSON.stringify(afterFlowClick, null, 2));

  console.log("DISCERN STAGE ERRORS CAPTURED:", JSON.stringify(errors, null, 2));
  await browser.close();
})();
