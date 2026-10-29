"use strict";
// Pure left-to-right forest layout. Each parent is centered on its children;
// each sibling subtree reserves its full height, including multiline labels.
(function (root) {
  function layoutForest(entries, roots, {columnWidth = 220, columnGap = 64, rowGap = 10, padding = 30} = {}) {
    const byId = new Map(entries.map(entry => [entry.id, entry]));
    const spans = new Map(), positions = {};
    function measure(id) {
      const node = byId.get(id);
      const childrenHeight = node.children.reduce((sum, child) => sum + measure(child), 0) + Math.max(0, node.children.length - 1) * rowGap;
      const height = Math.max(node.height, childrenHeight);
      spans.set(id, height);
      return height;
    }
    roots.forEach(measure);
    let maxRight = padding;
    function place(id, depth, top) {
      const node = byId.get(id), span = spans.get(id);
      const x = padding + depth * (columnWidth + columnGap);
      positions[id] = {x, y: top + (span - node.height) / 2, width: node.width, height: node.height, depth};
      maxRight = Math.max(maxRight, x + node.width);
      const childrenHeight = node.children.reduce((sum, child) => sum + spans.get(child), 0) + Math.max(0, node.children.length - 1) * rowGap;
      let childTop = top + (span - childrenHeight) / 2;
      for (const child of node.children) { place(child, depth + 1, childTop); childTop += spans.get(child) + rowGap; }
    }
    let top = padding;
    for (const id of roots) { place(id, 0, top); top += spans.get(id) + rowGap * 3; }
    return {positions, width: maxRight + padding, height: Math.max(padding * 2, top - rowGap * 3 + padding)};
  }
  if (typeof module !== "undefined" && module.exports) module.exports = {layoutForest};
  else root.ReadingMapLayout = {layoutForest};
})(typeof globalThis !== "undefined" ? globalThis : this);
