# ReadingPaper Research Map

研究地图层把论文阅读笔记连接成两种互补结构：

- `literature-tree.yaml`：按 task → pipeline/representation → module 组织领域发展，并标注四类 novelty。
- `challenge-insight-tree.yaml`：按技术 challenge → insight/technique 组织跨任务的技术武器库。
- `novelty-gate.yaml`：记录候选 failure case 的四种情况判定；它与 `novelty_class` 是两套不同的标签。
- `sources/paper-facts/`：每篇论文的可追溯事实层。事实必须关联现有论文页的 stage 和 HTML anchor。

运行 `python3 scripts/build_research_map.py` 会校验 YAML 并生成 `research-map.html`、`literature-tree.html` 和 `challenge-insight-tree.html`。后两页包含离线 inline SVG 总览图：点击节点可在右侧查看来源论文和证据，搜索/筛选会同步淡化不匹配的节点。生成页面可以从论文库首页的“研究地图”入口打开。

新增或补充论文时，先填写对应的 `sources/paper-facts/<slug>.yaml`，再更新两棵树和必要的 novelty gate。没有证据的判断保留为 `unverified` 或 `provisional`。
