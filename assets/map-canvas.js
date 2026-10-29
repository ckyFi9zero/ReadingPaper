"use strict";
// No dependencies: the generated HTML remains a complete readable list without JS.
(() => {
  class ReadingMapCanvas {
    constructor(graph) {
      this.graph = graph;
      this.stage = graph.querySelector('.map-stage');
      this.svg = graph.querySelector('.map-connectors');
      this.rows = [...graph.querySelectorAll('.map-node-row')];
      this.rows.forEach((row, i) => { row.closest('.map-tree-item').dataset.layoutKey = String(i); });
      this.scale = 1; this.x = 0; this.y = 0;
      this.mode = window.innerWidth > 650 ? 'mindmap' : 'list';
      document.querySelectorAll('[data-canvas-action]').forEach(button => button.addEventListener('click', () => {
        const action = button.dataset.canvasAction;
        if (action === 'view') this.setMode(this.mode === 'mindmap' ? 'list' : 'mindmap');
        else {
          if (this.mode !== 'mindmap') this.setMode('mindmap');
          if (action === 'fit') this.fit();
          if (action === 'actual') { this.zoomTo(1); this.reveal(this.graph.querySelector('.is-selected') || this.rows[0].querySelector('[data-node-id]'), true); }
          if (action === 'in') this.zoomTo(this.scale * 1.2);
          if (action === 'out') this.zoomTo(this.scale / 1.2);
        }
      }));
      graph.addEventListener('wheel', event => {
        if (this.mode !== 'mindmap' || !(event.ctrlKey || event.metaKey)) return;
        event.preventDefault();
        const rect = graph.getBoundingClientRect();
        this.zoomTo(this.scale * Math.exp(-event.deltaY * .003), event.clientX - rect.left, event.clientY - rect.top);
      }, {passive:false});
      graph.addEventListener('keydown', event => {
        if (this.mode !== 'mindmap' || event.target !== graph) return;
        const directions = {ArrowLeft:[70,0],ArrowRight:[-70,0],ArrowUp:[0,70],ArrowDown:[0,-70]};
        if (directions[event.key]) { event.preventDefault(); this.x += directions[event.key][0]; this.y += directions[event.key][1]; this.paint(); }
        if (['+', '=', '-'].includes(event.key)) { event.preventDefault(); this.zoomTo(this.scale * (event.key === '-' ? 1/1.2 : 1.2)); }
        if (event.key === 'Home') { event.preventDefault(); this.fit(); }
      });
      graph.addEventListener('focusin', event => {
        const node = event.target.closest('[data-node-id]');
        if (node) this.reveal(node);
      });
      graph.addEventListener('pointerdown', event => {
        if (this.mode !== 'mindmap' || event.button !== 0) return;
        this.drag = {id:event.pointerId,x:event.clientX,y:event.clientY,startX:this.x,startY:this.y,moved:false};
      });
      graph.addEventListener('pointermove', event => {
        const drag = this.drag;
        if (!drag || drag.id !== event.pointerId) return;
        if (Math.hypot(event.clientX - drag.x,event.clientY - drag.y) > 5) {
          drag.moved = true; graph.setPointerCapture(event.pointerId); graph.classList.add('is-panning');
        }
        if (drag.moved) { this.x = drag.startX + event.clientX - drag.x; this.y = drag.startY + event.clientY - drag.y; this.paint(); }
      });
      const end = event => {
        if (this.drag?.id !== event.pointerId) return;
        this.suppressClick = this.drag.moved;
        if (graph.hasPointerCapture(event.pointerId)) graph.releasePointerCapture(event.pointerId);
        this.drag = null; graph.classList.remove('is-panning');
      };
      graph.addEventListener('pointerup', end); graph.addEventListener('pointercancel', end);
      graph.addEventListener('click', event => {
        if (this.suppressClick) { event.stopImmediatePropagation(); event.preventDefault(); this.suppressClick = false; }
      }, true);
      this.resizeObserver = new ResizeObserver(() => { if (this.mode === 'mindmap') this.fit(); });
      this.resizeObserver.observe(graph);
      this.setMode(this.mode);
    }
    setMode(mode) {
      this.mode = mode;
      this.graph.classList.toggle('is-mindmap', mode === 'mindmap');
      const button = document.querySelector('[data-canvas-action="view"]');
      if (button) { button.textContent = mode === 'mindmap' ? '列表阅读' : '脑图视图'; button.setAttribute('aria-pressed', String(mode === 'list')); }
      if (mode === 'mindmap') this.refresh();
      else { this.stage.style.transform = ''; this.stage.style.width = ''; this.stage.style.height = ''; document.querySelector('#map-zoom').textContent = '列表'; }
    }
    refresh(refit = true) {
      if (this.mode !== 'mindmap') return;
      const rows = this.rows.filter(row => !row.closest('[hidden]'));
      const entries = rows.map(row => {
        const item = row.closest('.map-tree-item');
        const children = item.querySelector(':scope > .map-node-children');
        return {id:item.dataset.layoutKey,width:220,height:row.offsetHeight,
          children:children && !children.hidden ? [...children.children].filter(child=>!child.hidden).map(child=>child.dataset.layoutKey) : []};
      });
      const ids = new Set(entries.map(entry=>entry.id));
      const roots = rows.filter(row => {
        const parent = row.closest('.map-tree-item').parentElement.closest('.map-tree-item');
        return !parent || !ids.has(parent.dataset.layoutKey);
      }).map(row=>row.closest('.map-tree-item').dataset.layoutKey);
      this.layout = window.ReadingMapLayout.layoutForest(entries, roots);
      this.stage.style.width = `${this.layout.width}px`; this.stage.style.height = `${this.layout.height}px`;
      this.svg.setAttribute('width', this.layout.width); this.svg.setAttribute('height', this.layout.height); this.svg.replaceChildren();
      for (const row of rows) {
        const item = row.closest('.map-tree-item'), pos = this.layout.positions[item.dataset.layoutKey];
        row.style.left = `${pos.x}px`; row.style.top = `${pos.y}px`;
        const parent = item.parentElement.closest('.map-tree-item');
        const parentPos = parent && this.layout.positions[parent.dataset.layoutKey];
        if (!parentPos) continue;
        const x1 = parentPos.x + parentPos.width, y1 = parentPos.y + parentPos.height / 2;
        const x2 = pos.x, y2 = pos.y + pos.height / 2, mid = (x1+x2)/2;
        const path = document.createElementNS('http://www.w3.org/2000/svg','path');
        path.setAttribute('d',`M${x1},${y1} C${mid},${y1} ${mid},${y2} ${x2},${y2}`);
        path.setAttribute('class','map-connector');
        path.dataset.edgeFrom = parent.querySelector(':scope > .map-node-row > [data-node-id]').dataset.nodeId;
        path.dataset.edgeTo = row.querySelector('[data-node-id]').dataset.nodeId;
        this.svg.append(path);
      }
      if (refit) this.fit(); else this.paint();
    }
    fit() {
      if (!this.layout || this.mode !== 'mindmap') return;
      // Keep text readable. Large expanded maps remain reachable by pan/keyboard/list.
      this.scale = Math.max(.85, Math.min(1, (this.graph.clientWidth - 32)/this.layout.width, (this.graph.clientHeight - 32)/this.layout.height));
      this.x = this.layout.width * this.scale < this.graph.clientWidth ? (this.graph.clientWidth-this.layout.width*this.scale)/2 : 16;
      this.y = this.layout.height * this.scale < this.graph.clientHeight ? (this.graph.clientHeight-this.layout.height*this.scale)/2 : 16;
      this.paint();
    }
    zoomTo(scale, x=this.graph.clientWidth/2, y=this.graph.clientHeight/2) {
      const next = Math.max(.85, Math.min(2, scale)), ratio = next/this.scale;
      this.x = x-(x-this.x)*ratio; this.y = y-(y-this.y)*ratio; this.scale = next; this.paint();
    }
    paint() {
      if (!this.layout) return;
      const clamp = (value,size,world) => world <= size ? (size-world)/2 : Math.max(size-world-24,Math.min(24,value));
      this.x = clamp(this.x,this.graph.clientWidth,this.layout.width*this.scale);
      this.y = clamp(this.y,this.graph.clientHeight,this.layout.height*this.scale);
      this.stage.style.transform = `translate(${this.x}px,${this.y}px) scale(${this.scale})`;
      this.graph.dataset.zoom = String(this.scale);
      const zoom = document.querySelector('#map-zoom');
      if (zoom) { zoom.textContent = `${Math.round(this.scale*100)}%`; zoom.title = '最低85%，保持文字可读；拖动画布或切换列表查看其余节点'; }
    }
    reveal(node, force=false) {
      if (!node) return;
      if (this.mode !== 'mindmap') { node.scrollIntoView({block:'nearest',behavior:'instant'}); return; }
      if (!this.layout) return;
      const pos = this.layout.positions[node.closest('.map-tree-item').dataset.layoutKey];
      if (!pos) return;
      const left=this.x+pos.x*this.scale, top=this.y+pos.y*this.scale;
      if (force || left<8 || left+pos.width*this.scale>this.graph.clientWidth-8 || top<8 || top+pos.height*this.scale>this.graph.clientHeight-8) {
        this.x = this.graph.clientWidth/2-(pos.x+pos.width/2)*this.scale;
        this.y = this.graph.clientHeight/2-(pos.y+pos.height/2)*this.scale; this.paint();
      }
    }
    highlight(id) {
      this.svg.querySelectorAll('.map-connector').forEach(edge => edge.classList.toggle('is-related', edge.dataset.edgeFrom===id || edge.dataset.edgeTo===id));
    }
  }
  window.ReadingMapCanvas = ReadingMapCanvas;
})();
