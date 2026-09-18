// Run with node --test tests/test_app.cjs. No browser packages required.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/app.js'), 'utf8');

function setup(query = '') {
  const element = (value = '', options = []) => ({
    value, options: options.map(value => ({ value })), events: {}, hidden: false,
    addEventListener(type, fn) { this.events[type] = fn; }, focus() { this.focused = true; },
  });
  const nodes = {
    '#search': element(), '#stage-filter': element('all', ['all', 'first-pass', 'deep-read', 'code']),
    '#category-filter': element('all', ['all', 'in-field', 'out-of-field', 'uncategorized']),
    '#venue-filter': element('', ['', 'IEEE RA-L', 'Nature', 'arXiv']),
    '#sort': element('recent', ['recent', 'year']), '#result-count': element(), '#empty': element(), '#reset': element(),
  };
  const cards = [
    { slug: 'lidar', category: 'in-field', venue: 'IEEE RA-L', search: 'lidar robotics', stages: 'first-pass deep-read', year: '2026', date: '2026-09-17' },
    { slug: 'biology', category: 'out-of-field', venue: 'IEEE RA-L', search: 'biology denoising', stages: 'first-pass', year: '2025', date: '2026-09-18' },
    { slug: 'unknown', category: 'uncategorized', venue: 'arXiv', search: 'unknown denoising', stages: '', year: '2024', date: '2026-09-16' },
  ].map(dataset => ({ dataset, hidden: false }));
  nodes['#paper-list'] = { querySelectorAll: () => cards, append() {} };
  const state = { url: '' };
  vm.runInNewContext(source, {
    document: { querySelector: id => nodes[id] }, URLSearchParams,
    location: { search: query, pathname: '/ReadingPaper/index.html', hash: '#list' },
    history: { replaceState(a, b, url) { state.url = url; } },
  });
  return { nodes, state, visible: () => cards.filter(c => !c.hidden).map(c => c.dataset.slug) };
}

test('category works together with search and reading stage', () => {
  const { nodes, visible, state } = setup('?category=out-of-field&q=denoising&stage=first-pass&venue=IEEE+RA-L');
  assert.deepEqual(visible(), ['biology']);
  assert.match(state.url, /category=out-of-field/);
  nodes['#stage-filter'].value = 'deep-read';
  nodes['#stage-filter'].events.change();
  assert.deepEqual(visible(), []);
  assert.equal(nodes['#empty'].hidden, false);
  assert.equal(nodes['#result-count'].textContent, '0 篇论文');
  nodes['#reset'].events.click();
  assert.equal(visible().length, 3);
  assert.equal(nodes['#category-filter'].value, 'all');
  assert.equal(nodes['#venue-filter'].value, '');
  assert.equal(nodes['#empty'].hidden, true);
  assert.equal(state.url, '/ReadingPaper/index.html#list');
});

test('all categories selectable; URLs reload the same view', () => {
  const { nodes, state, visible } = setup();
  for (const [category, slug] of [['in-field', 'lidar'], ['out-of-field', 'biology'], ['uncategorized', 'unknown']]) {
    nodes['#category-filter'].value = category;
    nodes['#category-filter'].events.change();
    assert.deepEqual(visible(), [slug]);
    const url = new URL(state.url, 'https://example.test');
    assert.deepEqual(setup(url.search).visible(), [slug]);
  }
});

test('invalid URL filters fall back safely; sorting stays independent', () => {
  const { nodes, visible, state } = setup('?category=bad&stage=bad&venue=bad&sort=year');
  assert.equal(nodes['#category-filter'].value, 'all');
  assert.equal(visible().length, 3);
  assert.match(state.url, /sort=year/);
  assert.doesNotMatch(state.url, /bad/);
  nodes['#category-filter'].value = 'in-field';
  nodes['#category-filter'].events.change();
  assert.equal(nodes['#sort'].value, 'year');
  assert.deepEqual(visible(), ['lidar']);
});

test('one venue spans multiple domains and intersects independently', () => {
  const { nodes, visible, state } = setup('?venue=IEEE+RA-L');
  assert.deepEqual(visible().sort(), ['biology', 'lidar']);
  nodes['#category-filter'].value = 'out-of-field';
  nodes['#category-filter'].events.change();
  assert.deepEqual(visible(), ['biology']);
  assert.equal(nodes['#venue-filter'].value, 'IEEE RA-L');
  assert.deepEqual(setup(new URL(state.url, 'https://example.test').search).visible(), ['biology']);
  nodes['#venue-filter'].value = 'arXiv';
  nodes['#venue-filter'].events.change();
  assert.deepEqual(visible(), []);
  nodes['#category-filter'].value = 'all';
  nodes['#category-filter'].events.change();
  assert.deepEqual(visible(), ['unknown']);
});
