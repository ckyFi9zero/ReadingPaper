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
  let graphMode = "all";
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
    const filtering = Boolean(search?.value.trim() || controls.some(control => control.value));
    if (graphMode === "trunk" && !filtering && payload.type === "literature") {
      for (const node of graphNodes) {
        if (["module", "follow-up"].includes(node.dataset.nodeKind)) visible.delete(node.dataset.nodeId);
      }
    }
    for (const node of graphNodes) {
      node.toggleAttribute("hidden", !visible.has(node.dataset.nodeId));
      node.setAttribute("tabindex", visible.has(node.dataset.nodeId) ? "0" : "-1");
    }
    for (const edge of edges) edge.toggleAttribute("hidden", !(visible.has(edge.dataset.edgeFrom) && visible.has(edge.dataset.edgeTo)));
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
    const visible = items.filter(item => !item.hasAttribute("hidden")).length;
    if (status) status.textContent = `${visible} 个节点或论文记录匹配`;
    if (empty) empty.hidden = visible !== 0;
  }

  function evidenceMarkup(values) {
    return values?.length ? `<ul class="map-evidence">${values.map(item => `<li><a href="${esc(item.href)}">${esc(item.label)}</a> <small>${esc(item.status)}</small></li>`).join("")}</ul>` : "";
  }

  function claimMarkup(claim, label) {
    if (!claim) return "";
    return `<div class="analysis-claim"><strong>${esc(label)}</strong><p>${esc(claim.text)}</p><small class="analysis-basis">${esc(claim.basis_label)}</small>${evidenceMarkup(claim.evidence)}</div>`;
  }

  function sourceMarkup(source, index) {
    const chain = (source.chain || []).map(item => claimMarkup(item, item.label)).join("");
    return `<li class="inspector-source"><details ${index === 0 ? "open" : ""}><summary>${esc(source.name)} (${esc(source.year)})</summary><p class="analysis-caption">${esc(source.scope)}</p><p><a href="${esc(source.href)}">打开论文</a> · <a href="${esc(source.analysis_href)}">完整五分支解析树 →</a></p>${chain}${evidenceMarkup(source.evidence)}</details></li>`;
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
    const related = new Set([detail.parent, ...(detail.children || [])].filter(Boolean));
    for (const edge of edges) {
      if (edge.dataset.edgeFrom === nodeId) related.add(edge.dataset.edgeTo);
      if (edge.dataset.edgeTo === nodeId) related.add(edge.dataset.edgeFrom);
    }
    const relatedMarkup = related.size ? `<h4>关联节点</h4><div class="map-related">${[...related].filter(id => payload.details[id]).map(id => `<button type="button" data-select-node="${esc(id)}">${esc(payload.details[id].name)}</button>`).join("")}</div>` : "";
    inspector.innerHTML = `<div class="map-inspector-content"><p class="map-inspector-type">${esc(typeLine)}</p><h3>${esc(detail.name)}</h3><p>${esc(detail.description || "")}</p>${claimMarkup(detail.principle, "可复用的技术认识")}${techniques}${failures}${detail.motivation ? `<p><strong>动机：</strong>${esc(detail.motivation)}</p>` : ""}${detail.transfer_boundary ? `<p class="map-transfer"><strong>迁移边界：</strong>${esc(detail.transfer_boundary)}</p>` : ""}${relatedMarkup}${evidenceMarkup(detail.evidence)}${sources}</div>`;
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
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    if (id && payload.details?.[id]) {
      selectNode(id, false);
      const node = graphNodes.find(item => item.dataset.nodeId === id);
      if (node) {
        const rect = node.getBoundingClientRect();
        const bounds = graph.getBoundingClientRect();
        let left = graph.scrollLeft;
        if (rect.right > bounds.right - 12) left += rect.right - bounds.right + 12;
        else if (rect.left < bounds.left + 12) left += rect.left - bounds.left - 12;
        graph.scrollTo({left,
          top:graph.scrollTop + rect.top - bounds.top - (graph.clientHeight - rect.height) / 2, behavior:"instant"});
        graph.closest(".map-overview")?.scrollIntoView({block:"start", behavior:"instant"});
      }
    } else if (id) {
      const target = document.getElementById(id);
      if (!target) return;
      for (let parent = target; parent; parent = parent.parentElement) {
        if (parent.tagName === "DETAILS") parent.open = true;
        if (parent.hasAttribute("data-map-item")) parent.hidden = false;
      }
      target.scrollIntoView({block:"start", behavior:"instant"});
    }
  }

  function resetMapView() {
    graphMode = "all";
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
    if (action === "expand") { graphMode = "all"; document.querySelectorAll(".map-branch,.map-challenge,.map-fact").forEach(item => { item.open = true; }); }
    if (action === "trunk") { graphMode = "trunk"; document.querySelectorAll(".map-branch,.map-challenge,.map-fact").forEach(item => { item.open = item.classList.contains("map-branch") && !item.parentElement.closest(".map-branch"); }); }
    syncFiltersToGraph();
  }));
  inspector?.addEventListener("click", event => {
    const button = event.target.closest("[data-select-node]");
    if (button) selectNode(button.dataset.selectNode);
  });
  document.addEventListener("click", event => {
    const button = event.target.closest("[data-analysis-action]");
    if (button) {
      button.closest(".map-fact")?.querySelectorAll(".analysis-branch").forEach(branch => {
        branch.open = button.dataset.analysisAction === "expand";
      });
    }
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor && anchor.hash === location.hash) restoreNodeFromHash();
  });
  window.addEventListener("hashchange", restoreNodeFromHash);
  // Native fragment navigation can run after a deferred script and scroll to
  // the lower evidence card sharing the graph node ID. Restore after load too.
  window.addEventListener("load", () => requestAnimationFrame(restoreNodeFromHash), {once:true});
  updateFilters(); restoreNodeFromHash();
})();
