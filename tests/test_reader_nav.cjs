// Static DOM execution regression; actual desktop/mobile acceptance is separate.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/reader-nav.js'), 'utf8');
function render(page, dataset) {
  let bar;
  const document = {
    currentScript: dataset === null ? null : { dataset },
    createElement(tag) { return { tag, style: {}, attrs: {}, children: [], setAttribute(k,v) { this.attrs[k]=v; }, append(a) { this.children.push(a); } }; },
    body: { prepend(node) { bar=node; } },
  };
  vm.runInNewContext(source, { document, location: { pathname: '/ReadingPaper/' + page } });
  return bar;
}
const legacy = ['../../index.html', 'index.html', 'first-pass.html', 'deep-read.html', 'code.html'];
test('legacy two-level reading pages retain all five routes and current-page marking', () => {
  const bar = render('papers/rpsnownet-2026/first-pass.html', {});
  assert.deepEqual(bar.children.map(a=>a.href), legacy);
  assert.equal(bar.children[2].attrs['aria-current'], 'page');
  assert.equal(bar.attrs.role, 'navigation');
});
test('absent or partial script configuration retains legacy behavior', () => {
  for (const data of [null, {readerRoot:'../'}, {readerPaper:'../papers/rpsnownet-2026/'}]) {
    assert.deepEqual(render('papers/rpsnownet-2026/code.html', data).children.map(a=>a.href), legacy);
  }
});
test('actual RPSnowNet revisit script produces six correct project-prefixed existing targets', () => {
  const page = 'revisits/rpsnownet-20261111.html';
  const html = fs.readFileSync(path.join(root,page),'utf8');
  const script = html.match(/<script\b[^>]*src=["']\.\.\/assets\/reader-nav\.js(?:\?[^"']*)?["'][^>]*>/);
  assert.ok(script, 'shared reader navigation script present');
  const attr = key => { const m=script[0].match(new RegExp(key+'=["\']([^"\']+)["\']')); assert.ok(m,key); return m[1]; };
  const links = render(page,{readerRoot:attr('data-reader-root'),readerPaper:attr('data-reader-paper')}).children;
  const targets=['index.html','revisits.html',...['index.html','first-pass.html','deep-read.html','code.html'].map(f=>'papers/rpsnownet-2026/'+f)];
  assert.equal(links.length,6);
  links.forEach((link,i)=>{
    const url=new URL(link.href,'https://ckyfi9zero.github.io/ReadingPaper/'+page);
    assert.equal(url.pathname,'/ReadingPaper/'+targets[i]);
    assert.ok(fs.existsSync(path.join(root,targets[i])),targets[i]);
  });
});
