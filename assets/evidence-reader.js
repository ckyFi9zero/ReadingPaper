import { GlobalWorkerOptions, TextLayer, getDocument } from "./pdfjs/pdf.min.mjs";

(() => {
  "use strict";

  // PDF.js 5.x uses the proposed Uint8Array#toHex API when computing a PDF
  // fingerprint. Some Chromium/Firefox builds used by the local reader do
  // not expose that proposal yet, so provide the small compatible fallback.
  if (typeof Uint8Array.prototype.toHex !== "function") {
    Object.defineProperty(Uint8Array.prototype, "toHex", {
      configurable: true,
      value() {
        return Array.from(this, (byte) => byte.toString(16).padStart(2, "0")).join("");
      },
    });
  }

  // PDF.js 5.x also uses the still-proposed Map#getOrInsertComputed API.
  // Chromium/Firefox releases commonly used with the local reader do not
  // expose it yet, so provide the TC39-compatible behavior here.
  if (typeof Map.prototype.getOrInsertComputed !== "function") {
    Object.defineProperty(Map.prototype, "getOrInsertComputed", {
      configurable: true,
      value(key, callback) {
        if (this.has(key)) return this.get(key);
        const value = callback(key);
        this.set(key, value);
        return value;
      },
    });
  }

  const root = document.body;
  const pdfUrl = root.dataset.pdf;
  const defaultStage = root.dataset.defaultStage || "first-pass";
  const stages = JSON.parse(root.dataset.stages || "[]");
  const noteFrame = document.getElementById("note-viewer");
  const status = document.getElementById("reader-status");
  const locationLabel = document.getElementById("pdf-location");
  const pageInput = document.getElementById("pdf-page");
  const totalLabel = document.getElementById("pdf-total");
  const viewer = document.getElementById("pdf-viewer");
  const quoteBox = document.getElementById("pdf-quote");
  const quoteText = document.getElementById("pdf-quote-text");
  let map = null;
  let currentStage = defaultStage;
  let activeTargets = [];
  let pendingFragment = null;
  let pdfReader = null;

  function nodeMap() {
    return Object.fromEntries((map.nodes || []).map((node) => [node.id, node]));
  }

  function pdfEvidenceForEdge(edge, nodes) {
    for (const id of [edge.from, edge.to]) {
      const node = nodes[id];
      if (node && node.kind === "pdf") return node;
    }
    return null;
  }

  function evidenceForNode(nodeId, nodes) {
    const queue = [nodeId];
    const seen = new Set(queue);
    while (queue.length) {
      const current = queue.shift();
      for (const edge of map.edges || []) {
        if (edge.from !== current && edge.to !== current) continue;
        const pdf = pdfEvidenceForEdge(edge, nodes);
        if (pdf) return { edge, pdf };
        const next = edge.from === current ? edge.to : edge.from;
        if (!seen.has(next)) {
          seen.add(next);
          queue.push(next);
        }
      }
    }
    return null;
  }

  function normalisePdfText(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[‐‑‒–—]/g, "-")
      .replace(/-/g, "")
      .replace(/\s+/g, "")
      .replace(/[“”‘’'"`.,;:!?()[\]{}]/g, "");
  }

  class PdfReader {
    constructor(url) {
      this.url = url;
      this.pdf = null;
      this.page = 1;
      this.renderToken = 0;
      this.pageMeta = null;
    }

    async init() {
      try {
        GlobalWorkerOptions.workerSrc = new URL("./pdfjs/pdf.worker.mjs", import.meta.url).toString();
        // The in-app browser can block module workers for local pages, so keep
        // a deterministic main-thread fallback. The native PDF link remains
        // available for users who want the system viewer.
        this.pdf = await getDocument({ url: this.url, disableWorker: true }).promise;
        totalLabel.textContent = String(this.pdf.numPages);
        pageInput.max = String(this.pdf.numPages);
        await this.show(1);
        document.getElementById("pdf-prev").addEventListener("click", () => this.show(this.page - 1));
        document.getElementById("pdf-next").addEventListener("click", () => this.show(this.page + 1));
        pageInput.addEventListener("change", () => this.show(Number(pageInput.value)));
      } catch (error) {
        viewer.innerHTML = '<div class="pdf-error">PDF 加载失败。可以点击上方“系统 PDF”打开原文件。<br><small></small></div>';
        viewer.querySelector("small").textContent = error?.message || String(error);
        locationLabel.textContent = "加载失败";
      }
    }

    async show(page, quote = "", regions = []) {
      if (!this.pdf) return;
      const next = Math.max(1, Math.min(this.pdf.numPages, Number(page) || 1));
      this.page = next;
      pageInput.value = String(next);
      locationLabel.textContent = `第 ${next} 页`;
      const token = ++this.renderToken;
      viewer.innerHTML = '<div class="pdf-loading">正在渲染第 ' + next + ' 页…</div>';
      const pdfPage = await this.pdf.getPage(next);
      if (token !== this.renderToken) return;
      const base = pdfPage.getViewport({ scale: 1 });
      const scale = Math.min(Math.max((viewer.clientWidth - 34) / base.width, 0.8), 1.65);
      const viewport = pdfPage.getViewport({ scale });
      const pageBox = document.createElement("div");
      pageBox.className = "pdf-page";
      pageBox.style.width = `${viewport.width}px`;
      pageBox.style.height = `${viewport.height}px`;
      pageBox.style.setProperty("--total-scale-factor", String(scale));
      const canvas = document.createElement("canvas");
      canvas.width = Math.ceil(viewport.width * devicePixelRatio);
      canvas.height = Math.ceil(viewport.height * devicePixelRatio);
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;
      pageBox.appendChild(canvas);
      const textLayerDiv = document.createElement("div");
      textLayerDiv.className = "pdf-text-layer";
      pageBox.appendChild(textLayerDiv);
      viewer.replaceChildren(pageBox);
      const context = canvas.getContext("2d");
      const renderTask = pdfPage.render({ canvasContext: context, viewport, transform: devicePixelRatio !== 1 ? [devicePixelRatio, 0, 0, devicePixelRatio, 0, 0] : null });
      const textContent = await pdfPage.getTextContent();
      const layer = new TextLayer({ textContentSource: textContent, container: textLayerDiv, viewport });
      await Promise.all([renderTask.promise, layer.render()]);
      if (token !== this.renderToken) return;
      const spans = [...textLayerDiv.querySelectorAll("span")];
      // Source text items and rendered spans are not one-to-one (empty items
      // need not create a visible span). Search the actual rendered text.
      this.pageMeta = { page, spans, textLayerDiv };
      spans.forEach((span, index) => { span.dataset.textIndex = String(index); });
      this.clearHighlights();
      this.showRegions(regions);
    }

    showRegions(regions) {
      const pageBox = this.pageMeta?.textLayerDiv?.parentElement;
      if (!pageBox) return;
      const items = Array.isArray(regions) ? regions : regions ? [regions] : [];
      items.forEach((region) => {
        if (!region || !["x", "y", "width", "height"].every((key) => Number.isFinite(region[key]))) return;
        const mark = document.createElement("div");
        mark.className = "pdf-evidence-region";
        mark.style.left = `${region.x * 100}%`;
        mark.style.top = `${region.y * 100}%`;
        mark.style.width = `${region.width * 100}%`;
        mark.style.height = `${region.height * 100}%`;
        if (region.label) mark.title = region.label;
        pageBox.appendChild(mark);
      });
    }

    clearHighlights() {
      const root = this.pageMeta?.textLayerDiv;
      if (!root) return;
      root.querySelectorAll("span.pdf-quote-highlight").forEach((mark) => {
        const parent = mark.parentNode;
        while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
        mark.remove();
        parent.normalize();
      });
    }

    highlight(quote) {
      if (!this.pageMeta || !quote) return false;
      const { textLayerDiv } = this.pageMeta;
      const walker = document.createTreeWalker(textLayerDiv, NodeFilter.SHOW_TEXT);
      const segments = [];
      let node;
      while ((node = walker.nextNode())) {
        const raw = node.nodeValue || "";
        const offsets = [];
        let normalised = "";
        for (let index = 0; index < raw.length; index += 1) {
          let character = raw[index].toLowerCase();
          if (/[‐‑‒–—]/.test(character)) character = "-";
          if (/\s/.test(character) || /[-“”‘’'"`.,;:!?()[\]{}]/.test(character)) continue;
          normalised += character;
          offsets.push(index);
        }
        if (normalised) segments.push({ node, normalised, offsets });
      }
      // Search against the same whitespace-free representation used for the
      // quote. PDF.js may split a sentence at line breaks or text runs, so a
      // literal space between items would prevent an exact match.
      const combined = segments.map((segment) => segment.normalised).join("");
      const target = normalisePdfText(quote);
      const at = combined.indexOf(target);
      const targetLength = target.length;
      if (!targetLength || at < 0) return false;
      let cursor = 0;
      let first = null;
      segments.forEach((segment) => {
        const start = cursor;
        const end = cursor + segment.normalised.length;
        const selectedStart = Math.max(at, start);
        const selectedEnd = Math.min(at + targetLength, end);
        if (selectedEnd > selectedStart) {
          const rawStart = segment.offsets[selectedStart - start];
          const rawEnd = segment.offsets[selectedEnd - start - 1] + 1;
          const range = document.createRange();
          range.setStart(segment.node, rawStart);
          range.setEnd(segment.node, rawEnd);
          const mark = document.createElement("span");
          mark.className = "pdf-quote-highlight";
          range.surroundContents(mark);
          first ||= mark;
        }
        cursor = end;
      });
      return first;
    }
  }

  function showQuote(pdf, page, regions = pdf?.regions || []) {
    const quotes = Array.isArray(pdf?.quotes) && pdf.quotes.length
      ? pdf.quotes
      : pdf?.quote
        ? [pdf.quote]
        : [];
    if (!quotes.length) {
      quoteBox.hidden = true;
      quoteText.textContent = "";
      pdfReader?.show(page, [], regions);
      return;
    }
    quoteBox.hidden = false;
    quoteBox.querySelector("span").textContent = regions?.length
      ? "对应原文位置（近似区域）"
      : quotes.length > 1
        ? "对应原文句子（多处证据）"
        : "对应原文句子";
    quoteText.textContent = quotes.join("\n\n");
    pdfReader?.show(page, quotes, regions);
  }

  function jumpToEvidence(pdf, label, regions) {
    if (!pdf) {
      status.textContent = "该段暂未登记 PDF 证据";
      return;
    }
    const activeRegions = regions || pdf.regions || [];
    status.textContent = `已定位到 PDF 第 ${pdf.page} 页${label ? `：${label}` : ""}${activeRegions.length ? "（近似区域）" : ""}`;
    showQuote(pdf, pdf.page, activeRegions);
  }

  function clearHighlights() {
    activeTargets.forEach((element) => element.classList.remove("evidence-reader-active"));
    activeTargets = [];
  }

  function markTarget(element, pdf, label, regions) {
    clearHighlights();
    element.classList.add("evidence-reader-active");
    activeTargets.push(element);
    element.scrollIntoView({ block: "center", behavior: "smooth" });
    jumpToEvidence(pdf, label, regions);
  }

  function attachStageListeners() {
    if (!map) return;
    const doc = noteFrame.contentDocument;
    if (!doc) return;
    const cleanupStyle = doc.createElement("style");
    cleanupStyle.textContent = currentStage === "first-pass"
      ? ".page{display:block;max-width:none;padding:24px 28px}.page>.sidebar{display:none}body>div[role=\"navigation\"]{display:none!important}"
      : ".layout{display:block;max-width:none;padding:24px 28px}.layout>aside{display:none}body{overflow:auto}body>div[role=\"navigation\"]{display:none!important}";
    cleanupStyle.textContent += ".evidence-reader-target{cursor:pointer}.evidence-reader-active{outline:3px solid #a36b21;outline-offset:4px;background:#fff7e6!important;scroll-margin-top:24px}";
    doc.head.appendChild(cleanupStyle);
    const nodes = nodeMap();
    const stageNodes = (map.nodes || []).filter((node) => node.stage === currentStage && node.anchor);
    stageNodes.forEach((node) => {
      const target = doc.getElementById(node.anchor);
      if (!target) return;
      target.classList.add("evidence-reader-target");
      target.title = "点击跳到对应 PDF 页和近似证据位置";
      target.addEventListener("click", (event) => {
        if (event.target.closest("a,button,input,select")) return;
        event.preventDefault();
        const evidence = evidenceForNode(node.id, nodes);
        markTarget(target, evidence?.pdf, node.label || node.id, evidence?.edge?.region ? [evidence.edge.region] : undefined);
      });
    });
    (map.edges || []).forEach((edge) => {
      const card = doc.getElementById("evidence-" + edge.id);
      if (!card) return;
      card.classList.add("evidence-reader-target");
      card.addEventListener("click", (event) => {
        if (event.target.closest("a,button,input,select")) return;
        event.preventDefault();
        markTarget(card, pdfEvidenceForEdge(edge, nodes), edge.type, edge.region ? [edge.region] : undefined);
      });
    });
    doc.addEventListener("click", (event) => {
      const link = event.target.closest("a");
      if (!link) return;
      const href = link.getAttribute("href") || "";
      const card = event.target.closest(".evidence-card");
      if (link.classList.contains("evidence-pdf") && card) {
        const edge = (map.edges || []).find((item) => "evidence-" + item.id === card.id);
        if (edge) {
          event.preventDefault();
          jumpToEvidence(pdfEvidenceForEdge(edge, nodes), "证据卡片", edge.region ? [edge.region] : undefined);
        }
        return;
      }
      const internal = href.match(/^(first-pass|deep-read|code)\.html(?:#(.*))?$/);
      if (internal) {
        event.preventDefault();
        setStage(internal[1], internal[2] || null);
      }
    });
    if (pendingFragment) {
      const target = doc.getElementById(pendingFragment);
      if (target) {
        target.scrollIntoView({ block: "center", behavior: "auto" });
        target.classList.add("evidence-reader-active");
        activeTargets.push(target);
      }
      pendingFragment = null;
    }
  }

  function setStage(stage, fragment) {
    if (!stages.includes(stage)) return;
    currentStage = stage;
    pendingFragment = fragment;
    document.querySelectorAll(".reader-stage").forEach((button) => {
      button.toggleAttribute("aria-current", button.dataset.stage === stage);
    });
    clearHighlights();
    noteFrame.src = stage + ".html";
    status.textContent = "已切换到" + (stage === "code" ? "代码阅读" : stage === "first-pass" ? "第一遍初读" : "第二遍深读");
  }

  document.querySelectorAll(".reader-stage").forEach((button) => button.addEventListener("click", () => setStage(button.dataset.stage)));
  noteFrame.addEventListener("load", attachStageListeners);
  const inlineMap = document.getElementById("reader-map");
  const mapPromise = inlineMap
    ? Promise.resolve(JSON.parse(inlineMap.textContent))
    : fetch(root.dataset.map).then((response) => response.json());
  mapPromise.then(async (data) => {
    map = data;
    pdfReader = new PdfReader(pdfUrl);
    await pdfReader.init();
    setStage(defaultStage);
  }).catch((error) => {
    status.textContent = "证据映射或 PDF 读取失败";
    console.error(error);
  });
})();
