(() => {
  const list = document.querySelector('#revisit-list');
  if (!list) return;
  const search = document.querySelector('#revisit-search');
  const status = document.querySelector('#revisit-status');
  const count = document.querySelector('#revisit-count');
  const empty = document.querySelector('#revisit-empty');
  const cards = [...list.querySelectorAll('[data-revisit-state]')];
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  status.value = ['all', 'reviewed', 'not-yet'].includes(params.get('status')) ? params.get('status') : 'all';
  function update() {
    const words = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const card of cards) {
      card.hidden = !(status.value === 'all' || card.dataset.revisitState === status.value) || !words.every(w => card.dataset.revisitSearch.includes(w));
      if (!card.hidden) shown++;
    }
    count.textContent = `${shown} 篇论文`;
    empty.hidden = shown !== 0;
    const query = new URLSearchParams();
    if (search.value.trim()) query.set('q', search.value.trim());
    if (status.value !== 'all') query.set('status', status.value);
    try { history.replaceState(null, '', `${location.pathname}${query.size ? '?' + query : ''}${location.hash}`); } catch { /* file:// */ }
  }
  search.addEventListener('input', update);
  status.addEventListener('change', update);
  document.querySelector('#revisit-reset').addEventListener('click', () => { search.value = ''; status.value = 'all'; update(); search.focus(); });
  update();
})();
