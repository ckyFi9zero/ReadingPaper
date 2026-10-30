"use strict";

// Offline research-map interaction. The graph and its detail payload are
// generated into the HTML; no fetch, backend, CDN, or browser storage is used.
(() => {
  const search = document.querySelector("#map-search");
  const graph = document.querySelector("#map-graph");
  const detailsScript = document.querySelector("#map-details");
  const inspector = document.querySelector("#map-inspector");
  const controls = ["scope", "weather", "route", "challenge"]
    .map(k => document.querySelector(`#map-${k}`)).filter(Boolean);
  const items = Array.from(document.querySelectorAll("[data-map-item]"));
  const graphNodes = graph ? Array.from(graph.querySelectorAll("[data-node-id]")) : [];
  const edges = graph ? Array.from(graph.querySelectorAll(".map-edge")) : [];
  const status = document.querySelector("#map-results");
  const empty = document.querySelector("#map-empty");
  let payload = {details: {}};
  const collapsed = new Set();
  let canvas = null;
  const initialBranches = graphNodes.filter(node => (node.closest('.map-tree-item').querySelector(':scope > .map-node-children')?.children.length || 0) > 5).map(node => node.dataset.nodeId);
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

  function syncFiltersToGraph(refit = true) {
    const matches = new Set(graphNodes.filter(nodeMatches).map(node => node.dataset.nodeId));
    const visible = graphAncestors(matches);
    const filtering = Boolean(search?.value.trim() || controls.some(control => control.value));
    for (const node of graphNodes) {
      node.toggleAttribute("hidden", !visible.has(node.dataset.nodeId));
      node.closest(".map-tree-item").hidden = !visible.has(node.dataset.nodeId);
      const childList = node.closest(".map-tree-item").querySelector(":scope > .map-node-children");
      const toggle = node.parentElement.querySelector("[data-toggle-branch]");
      if (childList && toggle) {
        const open = filtering || !collapsed.has(node.dataset.nodeId);
        childList.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        toggle.textContent = open ? "−" : "+";
        toggle.setAttribute("aria-label", `${open ? "收起" : "展开"} ${node.querySelector(".map-node-name").textContent} 的分支`);
      }
    }
    for (const edge of edges) edge.toggleAttribute("hidden", !(visible.has(edge.dataset.edgeFrom) && visible.has(edge.dataset.edgeTo)));
    canvas?.refresh(refit);
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
    if (inspector?.closest(".map-tree-item[hidden]")) closeInspector();
    const weaponLibrary = payload.type === "challenge";
    const visible = items.filter(item => !item.hasAttribute("hidden") && (!weaponLibrary || item.classList.contains("map-insight"))).length;
    if (status) status.textContent = weaponLibrary ? `${visible} 张使用卡匹配` : `${visible} 个节点或论文记录匹配`;
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

  function playbookMarkup(detail) {
    if (!detail.playbook?.length) return "";
    const locations = (detail.source_locations || []).map(item => `<li><strong>${esc(item.name)}</strong>：${esc(item.location)}${item.original_href ? ` · <a href="${esc(item.original_href)}">原论文入口</a>` : ""}${evidenceMarkup(item.evidence)}</li>`).join("");
    return `<section class="weapon-playbook">${detail.playbook.map(item => claimMarkup(item, item.label)).join("")}${claimMarkup(detail.open_questions, "仍待核验")}<h4>论文原文定位（沿用笔记登记）</h4><ul class="weapon-locations">${locations}</ul></section>`;
  }

  function updateInspector(nodeId) {
    if (!inspector) return;
    const detail = payload.details?.[nodeId];
    if (!detail) { inspector.innerHTML = ""; return; }
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
    inspector.innerHTML = `<button type="button" class="map-inspector-close" data-close-inspector>收起证据</button><div class="map-inspector-content"><p class="map-inspector-type">${esc(typeLine)}</p><h3>${esc(detail.name)}</h3>${detail.playbook ? "" : `<p>${esc(detail.description || "")}</p>`}${claimMarkup(detail.kind === "challenge" ? detail.why_hard : null, "为什么难")}${claimMarkup(detail.principle, "可复用的技术认识")}${techniques}${failures}${playbookMarkup(detail)}${detail.motivation ? `<p><strong>动机：</strong>${esc(detail.motivation)}</p>` : ""}${detail.transfer_boundary ? `<p class="map-transfer"><strong>适用与迁移边界：</strong>${esc(detail.transfer_boundary)}</p>` : ""}${relatedMarkup}${evidenceMarkup(detail.evidence)}${sources}</div>`;
  }

  function highlightNeighbors(nodeId) {
    const connected = new Set([nodeId]);
    for (const edge of edges) {
      if (edge.dataset.edgeFrom === nodeId) connected.add(edge.dataset.edgeTo);
      if (edge.dataset.edgeTo === nodeId) connected.add(edge.dataset.edgeFrom);
    }
    for (const node of graphNodes) node.classList.toggle("is-related", connected.has(node.dataset.nodeId));
    for (const edge of edges) edge.classList.toggle("is-related", edge.dataset.edgeFrom === nodeId || edge.dataset.edgeTo === nodeId);
    canvas?.highlight(nodeId);
  }

  function closeInspector() {
    graphNodes.forEach(node => { node.classList.remove("is-selected", "is-related"); node.setAttribute("aria-expanded", "false"); });
    edges.forEach(edge => edge.classList.remove("is-related"));
    if (inspector?.open) inspector.close();
    canvas?.highlight("");
    updateInspector("");
  }

  function selectNode(nodeId, updateUrl = true, target = null) {
    if (!nodeId || !payload.details?.[nodeId]) return;
    const selected = target || graphNodes.find(node => node.dataset.nodeId === nodeId);
    if (selected && !nodeMatches(selected)) {
      if (search) search.value = "";
      controls.forEach(control => { control.value = ""; });
      updateFilters();
    }
    // Navigation must also reach nodes inside a manually collapsed branch.
    for (let parent = selected?.parentElement; parent && parent !== graph; parent = parent.parentElement) {
      if (parent.classList.contains("map-tree-item")) {
        const button = parent.querySelector(":scope > .map-node-row > [data-node-id]");
        if (button) collapsed.delete(button.dataset.nodeId);
      }
    }
    syncFiltersToGraph(false);
    for (const node of graphNodes) {
      node.classList.toggle("is-selected", node === selected);
      node.setAttribute("aria-expanded", String(node === selected));
    }
    canvas?.reveal(selected, true);
    highlightNeighbors(nodeId); updateInspector(nodeId);
    if (inspector && !inspector.open) inspector.showModal();
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
        canvas?.reveal(node, true);
        graph.scrollIntoView({block:"start", behavior:"instant"});
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
    collapsed.clear();
    initialBranches.forEach(id => collapsed.add(id));
    closeInspector();
    if (search) search.value = "";
    controls.forEach(control => { control.value = ""; });
    updateFilters();
    try { history.replaceState(null, "", `${location.pathname}${location.search}`); } catch { /* file:// */ }
  }

  graphNodes.forEach(node => {
    node.addEventListener("click", () => selectNode(node.dataset.nodeId, true, node));
  });
  graph?.addEventListener("click", event => {
    const toggle = event.target.closest("[data-toggle-branch]");
    if (!toggle) return;
    const nodeId = toggle.parentElement.querySelector("[data-node-id]").dataset.nodeId;
    if (collapsed.has(nodeId)) collapsed.delete(nodeId); else collapsed.add(nodeId);
    syncFiltersToGraph();
  });
  search?.addEventListener("input", updateFilters);
  controls.forEach(control => control.addEventListener("change", updateFilters));
  document.querySelector("#map-reset")?.addEventListener("click", resetMapView);
  document.querySelectorAll("[data-map-action]").forEach(button => button.addEventListener("click", () => {
    const action = button.dataset.mapAction;
    if (action === "reset") resetMapView();
    if (action === "expand") { collapsed.clear(); document.querySelectorAll(".map-branch,.map-challenge,.map-fact").forEach(item => { item.open = true; }); }
    if (action === "trunk") { closeInspector(); collapsed.clear(); graphNodes.filter(node => ["pipeline", "module", "challenge"].includes(node.dataset.nodeKind)).forEach(node => collapsed.add(node.dataset.nodeId)); document.querySelectorAll(".map-branch,.map-challenge,.map-fact").forEach(item => { item.open = item.classList.contains("map-branch") && !item.parentElement.closest(".map-branch"); }); }
    syncFiltersToGraph();
  }));
  inspector?.addEventListener("click", event => {
    const button = event.target.closest("[data-select-node]");
    if (button) {
      selectNode(button.dataset.selectNode);
      const selected = graph.querySelector(".is-selected");
      canvas?.reveal(selected, true);
    }
    if (event.target.closest("[data-close-inspector]")) {
      const selected = graph.querySelector(".is-selected");
      closeInspector();
      selected?.focus({preventScroll:true});
    }
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
  initialBranches.forEach(id => collapsed.add(id));
  if (graph && window.ReadingMapCanvas) canvas = new window.ReadingMapCanvas(graph);
  inspector?.addEventListener("close", () => {
    const selected = graph?.querySelector(".is-selected");
    graphNodes.forEach(node => node.setAttribute("aria-expanded", "false"));
    selected?.focus({preventScroll:true});
    canvas?.reveal(selected);
  });
  updateFilters(); restoreNodeFromHash();
})();
