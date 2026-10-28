# ReadingPaper Research Map

研究地图层把论文阅读笔记连接成两种互补结构：

- `literature-tree.yaml`：按 task → pipeline/representation → module 组织领域发展，并标注四类 novelty。
- `challenge-insight-tree.yaml`：按技术 challenge → insight/technique 组织跨任务的技术武器库。
- `novelty-gate.yaml`：记录候选 failure case 的四种情况判定；它与 `novelty_class` 是两套不同的标签。
- `sources/paper-facts/`：每篇论文的可追溯事实层。事实必须关联现有论文页的 stage 和 HTML anchor。

运行 `python3 scripts/build_research_map.py` 会校验 YAML 并生成 `research-map.html`、`literature-tree.html` 和 `challenge-insight-tree.html`。后两页包含离线 inline SVG 总览图：点击节点可在右侧查看来源论文和证据，搜索/筛选会同步淡化不匹配的节点。生成页面可以从论文库首页的“研究地图”入口打开。

新增或补充论文时，先填写对应的 `sources/paper-facts/<slug>.yaml`，再更新两棵树和必要的 novelty gate。没有证据的判断保留为 `unverified` 或 `provisional`。

## 领域分类与地图待整理（2026-10-28）

论文库的领域归类与跨论文地图的完成状态相互独立。新论文可以属于领域内，但不能因为已有初读就自动声称其事实层、Literature tree、Challenge–insight tree 已整理。此类论文须逐篇登记在 `pending-papers.yaml`，并在三张地图页面上显式显示“地图待整理”；不会生成占位学术结论或虚构节点，也不计入地图已整理来源数。

```yaml
version: 1
papers:
  - paper: beyondsnowflakes-2026
    status: pending
    registered_at: '2026-10-28'
    reason: 初读已整理；跨论文事实层及两棵树尚未整理，不能由领域分类或初读完成状态推定已纳入地图。
```

检查器要求登记的论文真实存在、归类为领域内、尚无事实文件或方法树节点，且具有明确原因和有效登记日期。不接受未知、重复、已整理的待办项。未登记的领域内遗漏仍然报错；2026-10-28 之前已纳入地图的 19 篇来源仍必须保留事实与节点覆盖，不能借待整理名单撤回。后续真正完成事实与两树关联时，必须移除对应待整理项，避免既“待整理”又“已纳入”的矛盾状态。仅有登记和结构检查不等于验证了新的学术判断。

## 单篇论文解析树（2026-10-15）

地图入口的“单篇论文解析树”按用户提供的模板展示五个分支：Abstract 速览、Introduction 问题与思路、Method 技术实现、Experiments 贡献与证据、Limitation 边界。它是两棵跨论文树的事实提取层；不能仅凭单篇作者的贡献声明判定首创性。速览由笔记重组，不代表作者摘要的写作结构。默认展开 DROR，其他论文可搜索或通过 hash 直接定位。

现有 26 篇来源（19 篇领域内、7 篇领域外）的事实文件增加可选 `analysis`；目前每篇整理一个主要贡献及两组实验记录，不宣称穷尽全部模块。旧事实文件没有 `analysis` 时仍可构建，页面显示待补充。两棵树右侧的来源论文现在展示失败现象、技术原因、通用 insight，并链接至完整单篇解析。Challenge 树的 12 个 insight 增加 `principle`，区分技术认识与实现名称。

```yaml
analysis:
  updated_at: '2026-10-15'
  previous_methods: {text: 前人如何处理, basis: note-summary, status: source-checked, evidence: [...]}
  technical_reason: {text: 为什么失败, basis: analyst-inference, status: inferred, evidence: [...]}
  insight: {text: 可以复用的技术认识, basis: analyst-inference, status: inferred, evidence: [...]}
  contributions:
    - id: contribution-main
      name: 主要技术贡献
      module_ids: [module-dror-2018]
      motivation: {text: 为什么需要它, basis: note-summary, status: source-checked, evidence: [...]}
      implementation: {text: 具体做法, basis: note-summary, status: source-checked, evidence: [...]}
      mechanism: {text: 为什么可能有效, basis: analyst-inference, status: inferred, evidence: [...]}
      advantage: {text: 预期优势, basis: analyst-inference, status: inferred, evidence: [...]}
  experiments:
    - id: experiment-overall
      name: 整体效果与评测条件
      kind: comparison
      assessment: reported
      contribution_ids: [contribution-main]
      result: {text: 笔记中的实验记录, basis: note-summary, status: source-checked, evidence: [...]}
      interpretation: {text: 证据支持的范围, basis: analyst-inference, status: inferred, evidence: [...]}
  boundary: {text: 适用边界, basis: note-summary, status: source-checked, evidence: [...]}
```

上面是字段示意，`[...]` 需替换为真实证据对象。`contribution`、`experiment` 的 ID 在单篇内唯一；网页锚点同时包含论文 slug。

证据规则：

- `note-summary / source-checked` 显示“笔记转述”：本轮核对的是已登记阅读页，不是重新核对 PDF，也不等于复现结果。
- `analyst-inference / inferred` 显示“阅读者归纳”：需有来源锚点，但该锚点不表示归纳已获独立验证。
- `not-assessed / unverified` 显示“尚未核验”：必须保留空证据列表，不以其他章节的链接冒充验证。
- 每篇解析的证据必须来自该篇已登记的阶段及存在的 HTML anchor。Challenge `principle` 可引用其已有 source papers，仍保留跨论文归纳身份。
- 实验 `kind` 为 `comparison / ablation / design-choice`；`assessment` 为 `reported / not-reported-in-note / not-assessed`。笔记未记录独立消融不能解释为已经完成模块验证，也不表示检查了未取得的补充材料。
- `contribution_ids` 是阅读者记录的证据关联，不能直接解释为因果证明。未报告或未核验的实验不得关联为贡献支持。
- 总体性能、模块作用、累计配置增益、跨域迁移分别解释；领域外来源不升级为已验证天气方案。原有 novelty 标签及 gate 不变。

维护时先在笔记中核对对应章节，再手动维护 YAML。新增 insight 时先写出技术认识，再列出具体技术；不要用模块名称直接替代 insight。构建器只验证结构与链接，不生成学术结论。

```bash
.venv/bin/python scripts/build_research_map.py --check
.venv/bin/python scripts/build_site.py
.venv/bin/python scripts/check_site.py
.venv/bin/python -m unittest discover -s tests -v
node --check assets/research-map.js
```

可选真实浏览器交互回归无需 npm 依赖，要求 Node 22+ 和支持 WebDriver BiDi 的 Firefox。以独立临时 profile 启动 Firefox 的 `--headless --remote-debugging-port 9333`，再运行：

```bash
FIREFOX_BIDI_URL=ws://127.0.0.1:9333/session node --test tests/test_research_map_browser.cjs
```

测试覆盖解析分支展开、嵌套 hash、insight 文本搜索、图节点选中与关联跳转、筛选保留父节点、SVG 隐藏状态，以及桌面和手机视口。未提供 `FIREFOX_BIDI_URL` 时跳过浏览器测试，不声称通过。设置 `MAP_SCREENSHOTS` 可将截图保存到指定目录。

本地导出包含解析树和图内数据；公开导出仍按 `publish.json` 选择阶段，不导出研究地图层。
