"use strict";

// Offline research-map interaction. The graph and its detail payload are
// generated into the HTML; no fetch, backend, CDN, or browser storage is used.
(() => {
  const search = document.querySelector("#map-search");
  const graph = document.querySelector("#map-graph");
  const detailsScript = document.querySelector("#map-details");
  const inspector = document.querySelector("#map-inspector");
  const controls = ["weather", "route", "challenge"]
    .map(k => document.querySelector(`#map-${k}`)).filter(Boolean);
  const items = Array.from(document.querySelectorAll("[data-map-item]"));
  const graphNodes = graph ? Array.from(graph.querySelectorAll("[data-node-id]")) : [];
  const edges = graph ? Array.from(graph.querySelectorAll(".map-edge")) : [];
  const status = document.querySelector("#map-results");
  const empty = document.querySelector("#map-empty");
  let payload = {details: {}};
  try { if (detailsScript) payload = JSON.parse(detailsScript.textContent); } catch { payload = {details: {}}; }

  const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
  const nodeMatches = item => {
    const terms = (search?.value || "").trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.every(term => (item.dataset.search || "").includes(term))) return false;
    return controls.every(control => {
      const key = control.id.slice(4);
      return !control.value || (item.dataset[key] || "").split("|").includes(control.value);
    });
  };

  function graphAncestors(visible) {
    const keep = new Set(visible);
    let changed = true;
    while (changed) {
      changed = false;
      for (const edge of edges) {
        if (keep.has(edge.dataset.edgeTo) && !keep.has(edge.dataset.edgeFrom)) {
          keep.add(edge.dataset.edgeFrom); changed = true;
        }
      }
    }
    return keep;
  }

  function syncFiltersToGraph() {
    const matches = new Set(graphNodes.filter(nodeMatches).map(node => node.dataset.nodeId));
    const visible = graphAncestors(matches);
    for (const node of graphNodes) node.hidden = !visible.has(node.dataset.nodeId);
    for (const edge of edges) edge.hidden = !(visible.has(edge.dataset.edgeFrom) && visible.has(edge.dataset.edgeTo));
  }

  function updateFilters() {
    for (const item of items) {
      if (item.closest("#map-graph")) continue;
      item.hidden = !nodeMatches(item);
    }
    for (const item of items.slice().reverse()) {
      if (!item.hidden) {
        for (let parent = item.parentElement; parent; parent = parent.parentElement) {
          if (parent.hasAttribute("data-map-item")) {
            parent.hidden = false;
            if (search?.value.trim() || controls.some(c => c.value)) parent.open = true;
          }
        }
      }
    }
    syncFiltersToGraph();
    const visible = items.filter(item => !item.hidden).length;
    if (status) status.textContent = `${visible} 个节点或论文记录匹配`;
    if (empty) empty.hidden = visible !== 0;
  }

  function sourceMarkup(source) {
    const evidence = (source.evidence || []).map(item => `<li><a href="${esc(item.href)}">${esc(item.label)}</a> <small>${esc(item.status)}</small></li>`).join("");
    return `<li class="inspector-source"><a href="${esc(source.href)}">${esc(source.name)} (${esc(source.year)})</a>${evidence ? `<ul>${evidence}</ul>` : ""}</li>`;
  }

  function updateInspector(nodeId) {
    if (!inspector) return;
    const detail = payload.details?.[nodeId];
    if (!detail) { inspector.innerHTML = '<p class="map-inspector-empty">点击图中的节点查看定义、关联论文和证据。</p>'; return; }
    const layer = detail.kind === "challenge" ? "技术挑战" : detail.kind === "insight" ? "技术 insight" : ({task:"Task",pipeline:"Pipeline / representation",module:"Module", "follow-up":"Follow-up"}[detail.kind] || detail.kind);
    const typeLine = detail.novelty_class ? `${layer} · ${detail.novelty_class} 类层级 · ${detail.confidence}` : `${layer} · ${detail.status}`;
    const techniques = detail.techniques?.length ? `<p><strong>技术：</strong>${detail.techniques.map(esc).join(" · ")}</p>` : "";
    const failures = detail.observable_failures?.length ? `<p><strong>可观察现象：</strong>${detail.observable_failures.map(esc).join("；")}</p>` : "";
    const sources = detail.sources?.length ? `<h4>来源论文</h4><ul class="inspector-sources">${detail.sources.map(sourceMarkup).join("")}</ul>` : "";
    inspector.innerHTML = `<div class="map-inspector-content"><p class="map-inspector-type">${esc(typeLine)}</p><h3>${esc(detail.name)}</h3><p>${esc(detail.description || "")}</p>${techniques}${failures}${detail.motivation ? `<p><strong>动机：</strong>${esc(detail.motivation)}</p>` : ""}${detail.transfer_boundary ? `<p class="map-transfer"><strong>迁移边界：</strong>${esc(detail.transfer_boundary)}</p>` : ""}${sources}</div>`;
  }

  function highlightNeighbors(nodeId) {
    const connected = new Set([nodeId]);
    for (const edge of edges) {
      if (edge.dataset.edgeFrom === nodeId) connected.add(edge.dataset.edgeTo);
      if (edge.dataset.edgeTo === nodeId) connected.add(edge.dataset.edgeFrom);
    }
    for (const node of graphNodes) node.classList.toggle("is-related", connected.has(node.dataset.nodeId));
    for (const edge of edges) edge.classList.toggle("is-related", edge.dataset.edgeFrom === nodeId || edge.dataset.edgeTo === nodeId);
  }

  function selectNode(nodeId, updateUrl = true) {
    if (!nodeId || !payload.details?.[nodeId]) return;
    for (const node of graphNodes) node.classList.toggle("is-selected", node.dataset.nodeId === nodeId);
    highlightNeighbors(nodeId); updateInspector(nodeId);
    if (updateUrl) {
      try { history.replaceState(null, "", `${location.pathname}${location.search}#${encodeURIComponent(nodeId)}`); } catch { /* file:// */ }
    }
  }

  function restoreNodeFromHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (id && payload.details?.[id]) {
      selectNode(id, false);
      const node = graphNodes.find(item => item.dataset.nodeId === id);
      node?.scrollIntoView({block:"center", inline:"center"});
    }
  }

  function resetMapView() {
    if (search) search.value = "";
    controls.forEach(control => { control.value = ""; });
    graphNodes.forEach(node => node.classList.remove("is-selected", "is-related"));
    edges.forEach(edge => edge.classList.remove("is-related"));
    updateInspector(""); updateFilters();
    try { history.replaceState(null, "", `${location.pathname}${location.search}`); } catch { /* file:// */ }
  }

  graphNodes.forEach(node => {
    node.addEventListener("click", () => selectNode(node.dataset.nodeId));
    node.addEventListener("keydown", event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); selectNode(node.dataset.nodeId); } });
  });
  search?.addEventListener("input", updateFilters);
  controls.forEach(control => control.addEventListener("change", updateFilters));
  document.querySelector("#map-reset")?.addEventListener("click", resetMapView);
  document.querySelectorAll("[data-map-action]").forEach(button => button.addEventListener("click", () => {
    const action = button.dataset.mapAction;
    if (action === "reset") resetMapView();
    if (action === "expand") document.querySelectorAll(".map-branch,.map-challenge,.map-fact").forEach(item => { item.open = true; });
    if (action === "trunk") document.querySelectorAll(".map-branch,.map-challenge,.map-fact").forEach(item => { item.open = item.classList.contains("map-branch") && !item.parentElement.closest(".map-branch"); });
  }));
  window.addEventListener("hashchange", restoreNodeFromHash);
  updateFilters(); restoreNodeFromHash();
})();
