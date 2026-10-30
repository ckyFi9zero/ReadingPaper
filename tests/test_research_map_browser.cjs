// Optional real-browser checks, without npm dependencies (Node 22+).
// Start Firefox with --headless --remote-debugging-port 9333 and a fresh profile,
// then FIREFOX_BIDI_URL=ws://127.0.0.1:9333/session node --test tests/test_research_map_browser.cjs
const {test, before, after} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const endpoint = process.env.FIREFOX_BIDI_URL;
const expectedFactCount = fs.readdirSync(path.resolve(__dirname, '../research-map/sources/paper-facts')).filter(name => name.endsWith('.yaml')).length;
let ws, context, sequence = 0;
const pending = new Map();
function command(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => {pending.delete(id); reject(new Error(`BiDi timeout: ${method}`));}, 15000);
    pending.set(id, {resolve(value) {clearTimeout(timer); resolve(value);}, reject(error) {clearTimeout(timer); reject(error);}});
    ws.send(JSON.stringify({id, method, params}));
  });
}
async function evaluate(expression) {
  const result = await command('script.evaluate', {expression:`JSON.stringify(${expression})`, target:{context}, awaitPromise:true});
  assert.equal(result.type, 'success', JSON.stringify(result));
  return JSON.parse(result.result.value);
}
async function open(name, hash = '') {
  await command('browsingContext.navigate', {context, url:pathToFileURL(path.resolve(__dirname, '..', name)).href + hash, wait:'complete'});
}
async function screenshot(name) {
  if (!process.env.MAP_SCREENSHOTS) return;
  fs.mkdirSync(process.env.MAP_SCREENSHOTS, {recursive:true});
  const result = await command('browsingContext.captureScreenshot', {context, origin:'viewport'});
  fs.writeFileSync(path.join(process.env.MAP_SCREENSHOTS, `${name}.png`), Buffer.from(result.data, 'base64'));
}
before(async () => {
  if (!endpoint) return;
  ws = new WebSocket(endpoint);
  await new Promise((resolve, reject) => {ws.onopen=resolve; ws.onerror=reject;});
  ws.onmessage = event => {
    const message = JSON.parse(event.data);
    const task = pending.get(message.id);
    if (!task) return;
    pending.delete(message.id);
    if (message.type === 'error') task.reject(new Error(JSON.stringify(message)));
    else task.resolve(message.result);
  };
  await command('session.new', {capabilities:{alwaysMatch:{}}});
  ({context} = await command('browsingContext.create', {type:'tab'}));
});
after(async () => {
  if (!ws) return;
  try {await command('browsingContext.close', {context}); await command('session.end');}
  finally {ws.close();}
});
const browserTest = (name, fn) => test(name, {skip:!endpoint, timeout:30000}, fn);

browserTest('paper hash opens the five-branch tree and expand/collapse controls work', async () => {
  await command('browsingContext.setViewport', {context, viewport:{width:1440,height:1000}, devicePixelRatio:1});
  await open('research-map.html', '#paper-dror-2018');
  assert.deepEqual(await evaluate(`({count:document.querySelectorAll('.paper-analysis-tree').length, open:document.getElementById('paper-dror-2018').open, branches:document.querySelectorAll('#paper-dror-2018 .analysis-branch').length})`), {count:26,open:true,branches:5});
  await screenshot('paper-tree-desktop');
  assert.equal(await evaluate(`(()=>{document.querySelector('#paper-dror-2018 [data-analysis-action="expand"]').click();return document.querySelectorAll('#paper-dror-2018 .analysis-branch[open]').length})()`), 5);
  assert.equal(await evaluate(`(()=>{document.querySelector('#paper-dror-2018 [data-analysis-action="collapse"]').click();return document.querySelectorAll('#paper-dror-2018 .analysis-branch[open]').length})()`), 0);
});

browserTest('nested contribution hash opens all enclosing details', async () => {
  await open('research-map.html', '#analysis-lisnownet-2022-contribution-main');
  assert.deepEqual(await evaluate(`({paper:document.getElementById('paper-lisnownet-2022').open,method:document.getElementById('analysis-lisnownet-2022-method').open})`), {paper:true,method:true});
});

browserTest('search indexes insight text and empty search restores all papers', async () => {
  await open('research-map.html');
  assert.equal(await evaluate(`(()=>{const q=document.getElementById('map-search');q.value='排列不变性';q.dispatchEvent(new Event('input'));return !document.getElementById('paper-pointnet-2017').hidden})()`), true);
  assert.equal(await evaluate(`(()=>{const q=document.getElementById('map-search');q.value='';q.dispatchEvent(new Event('input'));return document.querySelectorAll('.map-fact:not([hidden])').length})()`), expectedFactCount);
});

browserTest('graph hash restores selection, evidence and analysis navigation', async () => {
  await open('literature-tree.html', '#module-dror-2018');
  assert.equal(await evaluate(`document.querySelector('.is-selected').dataset.nodeId`), 'module-dror-2018');
  assert.equal(await evaluate(`Boolean(document.querySelector('#map-inspector a[href="research-map.html#paper-dror-2018"]'))`), true);
  assert.equal(await evaluate(`document.getElementById('map-inspector').textContent.includes('判断点是否孤立')`), true);
  await evaluate(`new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve(true))))`);
  assert.equal(await evaluate(`(()=>{const rect=document.querySelector('.is-selected').getBoundingClientRect();return rect.bottom>0&&rect.top<innerHeight})()`), true);
  await screenshot('literature-inspector-desktop');
  await evaluate(`(()=>{document.querySelector('#map-inspector [data-select-node="pipeline-statistical"]').click();return true})()`);
  assert.equal(await evaluate(`document.querySelector('.is-selected').dataset.nodeId`), 'pipeline-statistical');
});

browserTest('graph filtering retains ancestors and hides unmatched branches; trunk and expand work', async () => {
  await open('literature-tree.html');
  await evaluate(`(()=>{const q=document.getElementById('map-search');q.value='DROR';q.dispatchEvent(new Event('input'));return true})()`);
  assert.equal(await evaluate(`document.querySelector('[data-node-id="module-dror-2018"]').hasAttribute('hidden')`), false);
  assert.equal(await evaluate(`document.querySelector('[data-node-id="pipeline-statistical"]').hasAttribute('hidden')`), false);
  assert.equal(await evaluate(`Boolean([...document.querySelectorAll('.map-edge')].some(edge=>getComputedStyle(edge).display==='none'))`), true);
  await evaluate(`(()=>{document.getElementById('map-reset').click();document.querySelector('[data-map-action="trunk"]').click();return true})()`);
  assert.equal(await evaluate(`document.querySelector('[data-node-id="module-dror-2018"]').getClientRects().length`), 0);
  await evaluate(`(()=>{document.querySelector('[data-map-action="expand"]').click();return true})()`);
  assert.notEqual(await evaluate(`document.querySelector('[data-node-id="module-dror-2018"]').getClientRects().length`), 0);
});

browserTest('challenge inspector separates principle, technique and transfer boundary', async () => {
  await open('challenge-insight-tree.html', '#insight-hierarchy');
  const text = await evaluate(`document.getElementById('map-inspector').textContent`);
  assert.match(text, /可复用的技术认识/);
  assert.match(text, /阅读者归纳/);
  assert.match(text, /MSG\/MRG/);
  assert.match(text, /迁移边界/);
  await screenshot('challenge-inspector-desktop');
});

browserTest('mind maps retain all nodes, pan without scrollbars and offer a mobile list', async () => {
  for (const width of [1440, 390]) {
    await command('browsingContext.setViewport', {context, viewport:{width,height:844}, devicePixelRatio:1});
    for (const name of ['literature-tree.html', 'challenge-insight-tree.html']) {
      await open(name);
      await evaluate(`(()=>{document.querySelector('[data-map-action="expand"]').click();return true})()`);
      assert.equal(await evaluate(`document.documentElement.scrollWidth<=innerWidth`), true);
      if (width === 390) {
        assert.equal(await evaluate(`document.getElementById('map-graph').classList.contains('is-mindmap')`), false);
        await evaluate(`(()=>{document.querySelector('[data-canvas-action="view"]').click();return true})()`);
      }
      assert.equal(await evaluate(`(()=>{const g=document.getElementById('map-graph');return getComputedStyle(g).overflowX==='clip' && Number(g.dataset.zoom)>=.85})()`), true);
      assert.equal(await evaluate(`(()=>{const rows=[...document.querySelectorAll('.map-node-row')].filter(e=>!e.closest('[hidden]'));return rows.every((a,i)=>rows.slice(i+1).every(b=>a.offsetLeft+a.offsetWidth<=b.offsetLeft||b.offsetLeft+b.offsetWidth<=a.offsetLeft||a.offsetTop+a.offsetHeight<=b.offsetTop||b.offsetTop+b.offsetHeight<=a.offsetTop))})()`), true);
      assert.equal(await evaluate(`(()=>{const expected=Object.keys(JSON.parse(document.getElementById('map-details').textContent).details); const visible=[...document.querySelectorAll('[data-node-id]')].filter(n=>n.getClientRects().length).map(n=>n.dataset.nodeId);return expected.every(id=>visible.includes(id))})()`), true);
      await evaluate(`(()=>{document.querySelector('[data-node-id]').click();return true})()`);
      assert.equal(await evaluate(`(()=>{const e=document.getElementById('map-inspector');return e.open && e.scrollWidth<=e.clientWidth})()`), true);
      await screenshot(`${name}-${width}`);
      await evaluate(`(()=>{document.querySelector('[data-close-inspector]').click();document.querySelector('[data-canvas-action="actual"]').click();return true})()`);
      assert.equal(await evaluate(`document.getElementById('map-zoom').textContent`), '100%');
    }
    await open('research-map.html', '#paper-dror-2018');
    await evaluate(`(()=>{document.querySelector('#paper-dror-2018 [data-analysis-action="expand"]').click();return true})()`);
    assert.equal(await evaluate(`document.documentElement.scrollWidth<=innerWidth`), true);
    assert.equal(await evaluate(`document.querySelectorAll('#paper-dror-2018 .analysis-branch[open]').length`), 5);
    await screenshot(`paper-tree-${width}`);
  }
});

browserTest('individual branches collapse and hash navigation reopens ancestors', async () => {
  await open('literature-tree.html');
  await evaluate(`(()=>{document.querySelector('[data-map-action="expand"]').click();return true})()`);
  await evaluate(`(()=>{document.querySelector('[data-node-id="pipeline-statistical"]').parentElement.querySelector('[data-toggle-branch]').click();return true})()`);
  assert.equal(await evaluate(`document.querySelector('[data-node-id="module-dror-2018"]').getClientRects().length`), 0);
  await command('browsingContext.navigate', {context, url:pathToFileURL(path.resolve(__dirname, '..', 'literature-tree.html')).href+'#module-dror-2018', wait:'complete'});
  assert.notEqual(await evaluate(`document.querySelector('[data-node-id="module-dror-2018"]').getClientRects().length`), 0);
});

browserTest('weapon search finds the actual operation and opens complete evidence cards', async () => {
  await open('challenge-insight-tree.html');
  await evaluate(`(()=>{const q=document.getElementById('map-search');q.value='CRFOR ICM';q.dispatchEvent(new Event('input'));return true})()`);
  assert.equal(await evaluate(`document.getElementById('map-results').textContent`), '1 张使用卡匹配');
  assert.deepEqual(await evaluate(`[...document.querySelectorAll('.map-insight')].filter(n=>!n.hidden).map(n=>n.id)`), ['insight-confidence']);
  await evaluate(`(()=>{document.querySelector('[data-node-id="insight-confidence"]').click();return true})()`);
  assert.equal(await evaluate(`document.querySelectorAll('#map-inspector .weapon-playbook .analysis-claim').length`), 8);
  assert.equal(await evaluate(`document.querySelector('#map-inspector .weapon-locations').textContent.includes('Table IV')`), true);
  assert.equal(await evaluate(`document.querySelector('#map-inspector .weapon-playbook').textContent.includes('尚未核验')`), true);
});


browserTest('scope filter separates native sources and preserves mixed cards and ancestors', async () => {
  await open('research-map.html');
  assert.equal(await evaluate(`(()=>{const s=document.getElementById('map-scope');s.value='out-of-field';s.dispatchEvent(new Event('change'));return document.querySelectorAll('.map-fact:not([hidden])').length})()`), 21);
  assert.equal(await evaluate(`document.getElementById('paper-dror-2018').hidden`), true);
  await open('challenge-insight-tree.html');
  await evaluate(`(()=>{const s=document.getElementById('map-scope');s.value='out-of-field';s.dispatchEvent(new Event('change'));return true})()`);
  assert.equal(await evaluate(`document.getElementById('insight-temporal').hidden`), false);
  assert.equal(await evaluate(`document.getElementById('insight-adaptive').hidden`), true);
  assert.equal(await evaluate(`document.querySelector('[data-node-id="challenge-set-representation"]').hidden`), false);
  await evaluate(`(()=>{document.getElementById('map-reset').click();return true})()`);
  assert.equal(await evaluate(`document.getElementById('map-scope').value`), '');
  assert.equal(await evaluate(`document.getElementById('insight-adaptive').hidden`), false);
});
