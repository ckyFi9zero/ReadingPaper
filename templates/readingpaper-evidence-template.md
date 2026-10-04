# ReadingPaper 三阶段阅读与证据链模板

这份模板用于新论文和已有论文的统一改造。它把三类页面、PDF 定位、代码证据和双栏联动放进同一套约定中。复制本文件后，按论文目录逐项填写；未核对的内容必须保留为 `unverified`，不要用推测代替原文证据。

## 0. 使用方式

每篇论文使用一个稳定的 slug，例如 `3d-unoutdet-2025`。先准备论文目录，再按 Stage 1 → Stage 2 → Stage 3 的顺序补充页面和 `evidence-map.json`。页面中的标题、段落和代码块都要有稳定的 HTML `id`，证据图通过这些 `id` 建立双向链接。

推荐目录：

```text
papers/<paper-slug>/
├── index.html              # 论文入口和阶段导航
├── first-pass.html         # Stage 1：第一遍初读
├── deep-read.html          # Stage 2：第二遍深读 / 写作精读
├── code.html               # Stage 3：代码阅读
├── evidence-map.json       # 论文—PDF—源码证据图
├── linked-reader.html      # 构建后生成的双栏联动页
└── source.pdf              # 可选，本地私有文件，默认不提交
```

如果某一阶段暂时没有内容，可以先保留导航入口和空状态，但不要伪造证据节点。

## 1. 公共元数据和 PDF 来源

在论文目录或站点配置中记录：

```yaml
paper: <paper-slug>
title: <论文标题>
year: <年份>
pdf:
  # 有本地文件时使用；source.pdf 应加入忽略规则
  local: source.pdf
  # 没有本地文件时填写 DOI、arXiv 或出版商 PDF 外链
  external: <https://...>
```

PDF 定位同时保存“页码”和“语义标签”。页码从 PDF 阅读器的实际页码开始，不能只依赖浏览器滚动位置；图、表、公式和章节名用于人工复核。链接策略如下：

- 本地 PDF：`source.pdf#page=<页码>`。
- 外部 PDF：保存稳定的 DOI、arXiv 或出版商链接，并单独保存 `page` 字段。
- 代码：必须指向固定的完整 commit SHA、文件路径和行号范围，禁止使用 `main`、`master` 或仓库首页。
- 无法确认精确句子时，使用页面中的近似区域 `regions`。区域坐标是 PDF 页面左上角为原点的归一化值，范围均为 `0..1`；它表达“跳到大致位置”，不宣称逐句对齐。

区域示例：

```json
"regions": [
  {
    "x": 0.08,
    "y": 0.42,
    "width": 0.46,
    "height": 0.18,
    "label": "方法总体流程"
  }
]
```

## 2. Stage 1 页面：第一遍初读

Stage 1 的目标是快速建立论文地图，不追求逐句翻译。页面应回答“研究在解决什么问题、为什么重要、作者提出了什么、证据在哪里”。所有判断先落到 PDF 页码、图表或章节。

建议页面骨架：

```html
<section id="section-01" data-stage="first-pass">
  <h2>01 · 论文定位</h2>
  <p>标题、作者、 venue、任务和数据集。</p>
</section>

<section id="section-02" data-stage="first-pass">
  <h2>02 · Research Problem</h2>
  <p>具体问题、发生场景、重要性和最终后果。</p>
  <a data-evidence="note:problem">跳到 PDF 证据</a>
</section>

<section id="section-03" data-stage="first-pass">
  <h2>03 · Core Idea</h2>
  <p>用自己的话概括方法主线，标出对应图或方法章节。</p>
</section>

<section id="section-04" data-stage="first-pass">
  <h2>04 · Method Overview</h2>
  <p>只记录模块和输入输出，不提前补充代码中没有的细节。</p>
</section>

<section id="section-05" data-stage="first-pass">
  <h2>05 · Evidence and Results</h2>
  <p>主要实验、数据集、指标和结论边界。</p>
</section>

<section id="section-06" data-stage="first-pass">
  <h2>06 · Limitations</h2>
  <p>作者明确承认的限制，以及仍需核对的问题。</p>
</section>
```

每个 Stage 1 观点至少对应一个 `note` 节点和一个 `pdf` 节点。页面中可以显示“PDF 第 N 页 / Fig. X / Sec. Y”，点击观点后让左侧 PDF 跳到该页和近似区域；从左侧证据卡片应能返回右侧观点。

Stage 1 的记录规则：

1. `derived-from` 只用于“这条笔记直接来自哪段原文”。
2. 对作者没有明确说出的因果关系，使用 `inferred`，并在笔记中写出推断依据。
3. 结果只写论文实际报告的指标和数据集，不能把摘要中的宣传句扩展成更强的结论。
4. 先给章节、图表和页码，再写自己的概括，避免出现没有来源的孤立总结。

## 3. Stage 2 页面：第二遍深读 / 写作精读

Stage 2 重建作者的论证路线，关注每个段落承担的功能，以及“主张—证据—结论边界”。它可以是 HTML，也可以由 Markdown 构建成 HTML；关键是保留稳定锚点。

建议页面骨架：

```html
<section id="section-07" data-stage="deep-read">
  <h2>07 · Introduction Argument</h2>
  <article id="claim-gap">
    <h3>问题与研究缺口</h3>
    <p>原文如何从现象推进到 gap；链接 Sec. I 的 PDF 区域。</p>
  </article>
</section>

<section id="section-08" data-stage="deep-read">
  <h2>08 · Method Logic</h2>
  <article id="claim-module-logic">
    <h3>模块逻辑</h3>
    <p>输入、模块、监督信号、输出和必要假设。</p>
  </article>
</section>

<section id="section-09" data-stage="deep-read">
  <h2>09 · Figures, Equations and Tables</h2>
  <p>每个关键图表或公式说明它支持哪个主张，并保存 PDF 页码。</p>
</section>

<section id="section-10" data-stage="deep-read">
  <h2>10 · Evidence Audit</h2>
  <p>区分 source-checked、inferred 和 unverified；写出证据不足的位置。</p>
</section>

<section id="section-11" data-stage="deep-read">
  <h2>11 · Conclusion Boundary</h2>
  <p>作者证明了什么、没有证明什么、哪些结论依赖特定数据或设置。</p>
</section>
```

Stage 2 的 PDF 链接比 Stage 1 更细，但仍优先使用“页码 + 图/表/章节 + 近似区域”的组合。一个段落可以关联多个 PDF 节点；一个 PDF 节点也可以支持多个观点。不要为了制造一一对应而重复复制证据。

## 4. Stage 3 页面：代码阅读

Stage 3 连接论文方法和实现，默认是静态阅读。页面必须明确哪些内容已经运行验证，哪些只是源码阅读或推断。

建议页面骨架：

```html
<section id="code-version" data-stage="code">
  <h2>版本与阅读范围</h2>
  <p>仓库 URL、完整 commit SHA、分支快照、阅读日期和未阅读目录。</p>
</section>

<section id="code-entrypoints" data-stage="code">
  <h2>入口与数据流</h2>
  <p>从训练/推理入口到数据、模型、损失和评估的调用路径。</p>
</section>

<section id="code-modules" data-stage="code">
  <h2>模块与论文对应</h2>
  <article id="code-module-<name>">
    <h3><模块名称></h3>
    <p>代码文件、函数、输入输出、论文中的对应模块和 PDF 证据。</p>
    <a href="https://github.com/OWNER/REPO/blob/<FULL_COMMIT>/<PATH>#L<START>-L<END>">固定版本源码</a>
  </article>
</section>

<section id="code-differences" data-stage="code">
  <h2>论文与实现的差异</h2>
  <p>记录默认参数、数据预处理、未公开细节和论文描述与代码的差异。</p>
</section>

<section id="code-validation" data-stage="code">
  <h2>运行观察</h2>
  <p>命令、环境、结果和失败原因；未运行时明确写 static-read。</p>
</section>
```

代码节点至少填写：

```json
{
  "kind": "code",
  "repo": "https://github.com/OWNER/REPO",
  "commit": "<完整 40 位 commit SHA>",
  "path": "path/to/file.py",
  "start": 14,
  "end": 101,
  "label": "模块或函数名称"
}
```

代码模块如果在 PDF 的一张总览图中只占一部分，应在连接该 `implements` 边时填写边级 `region`。这样点击不同代码块会落到同一页上的不同近似区域，而不会误称为精确逐句匹配。

## 5. `evidence-map.json` 最小模板

把下面内容复制到 `papers/<paper-slug>/evidence-map.json`，替换所有尖括号字段。`commit` 必须替换成真实的完整 SHA；示例中的占位 SHA 只用于保持 JSON 结构完整。

```json
{
  "version": 1,
  "paper": "<paper-slug>",
  "viewer": {
    "local_pdf": "source.pdf",
    "external_pdf": "<DOI/arXiv/出版商 PDF URL>"
  },
  "nodes": [
    {
      "id": "note:problem",
      "kind": "note",
      "stage": "first-pass",
      "anchor": "section-02",
      "label": "研究问题"
    },
    {
      "id": "note:method-overview",
      "kind": "note",
      "stage": "deep-read",
      "anchor": "section-08",
      "label": "方法总体流程"
    },
    {
      "id": "pdf:method-figure",
      "kind": "pdf",
      "href": "source.pdf#page=3",
      "page": 3,
      "figure": "Fig. 2",
      "regions": [
        {
          "x": 0.08,
          "y": 0.16,
          "width": 0.84,
          "height": 0.28,
          "label": "总体框架图"
        }
      ],
      "label": "方法总体框架"
    },
    {
      "id": "code:module-name",
      "kind": "code",
      "stage": "code",
      "anchor": "code-module-<name>",
      "repo": "https://github.com/OWNER/REPO",
      "commit": "0123456789abcdef0123456789abcdef01234567",
      "path": "path/to/file.py",
      "start": 14,
      "end": 101,
      "label": "源码模块"
    }
  ],
  "edges": [
    {
      "from": "note:problem",
      "to": "pdf:method-figure",
      "type": "derived-from",
      "status": "source-checked"
    },
    {
      "from": "note:method-overview",
      "to": "pdf:method-figure",
      "type": "supports",
      "status": "source-checked"
    },
    {
      "from": "pdf:method-figure",
      "to": "code:module-name",
      "type": "implements",
      "status": "static-read",
      "region": {
        "x": 0.08,
        "y": 0.16,
        "width": 0.28,
        "height": 0.12,
        "label": "该模块在总览图中的位置"
      }
    }
  ]
}
```

关系类型只使用：`derived-from`、`supports`、`implements`、`differs`、`related`。证据状态只使用：`source-checked`、`static-read`、`inferred`、`unverified`。

## 6. 页面联动规则

- 右侧笔记、深读段落或代码模块点击后，左侧跳到关联 PDF 页，并在存在 `regions` 时显示近似橙色区域。
- 左侧 PDF 证据卡片应提供返回右侧锚点的链接；同一证据支持多个观点时，显示多个返回项。
- 页面联动表达“证据在同一页或附近区域”，不承诺 OCR 级逐句对齐。若需要精确文本，必须额外保存经过人工复核的文本引用，并将状态标为 `source-checked`。
- 没有本地 PDF 时，仍保留页码和外部链接；点击时打开外部来源或提示使用系统 PDF。
- 代码链接始终固定 commit、路径和行号。仓库迁移或 commit 失效时，状态改为 `unverified`，不要静默改回默认分支。

## 7. 新论文验收清单

- [ ] `index.html` 能进入 Stage 1、Stage 2、Stage 3 和联动阅读页。
- [ ] 三个阶段的主要段落都有稳定 `id`，且 `note` 节点的 `stage` 与页面一致。
- [ ] 每条 PDF 证据都有正整数页码，以及图/表/章节或近似区域中的至少一种语义定位。
- [ ] 每个代码节点都有真实完整 commit、文件路径、起止行号和可访问链接。
- [ ] 每条边的两端节点存在，关系类型和证据状态属于允许集合。
- [ ] 从笔记可以跳到 PDF，从 PDF 可以返回笔记；代码模块也能返回论文观点。
- [ ] 私有 `source.pdf` 没有被提交到公开仓库。
- [ ] 页面和 JSON 通过仓库检查：

```bash
cd /home/bb/ReadingPaper
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_app.cjs
python3 scripts/export_site.py --profile local
```

已有论文迁移时，先补 `evidence-map.json` 和稳定锚点，再运行构建与检查；不要直接重写原有手写 HTML。只有带 `EvidenceLinks:START/END` 标记的区域才允许由渲染脚本更新。
