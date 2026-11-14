# ReadingPaper Research Map

研究地图层把论文阅读笔记连接成两种互补结构：

- `literature-tree.yaml`：按 task → pipeline/representation → module 组织领域发展，并标注四类 novelty。
- `challenge-insight-tree.yaml`：按技术 challenge → insight/technique 组织跨任务的技术武器库。
- `novelty-gate.yaml`：记录候选 failure case 的四种情况判定；它与 `novelty_class` 是两套不同的标签。
- `sources/paper-facts/`：每篇论文的可追溯事实层。事实必须关联现有论文页的 stage 和 HTML anchor。

运行 `python3 scripts/build_research_map.py` 会校验 YAML 并生成 `research-map.html`、`literature-tree.html` 和 `challenge-insight-tree.html`。后两页包含离线左→右脑图：画布可平移/缩放，点击节点打开详情抽屉；手机默认列表，可切换脑图。搜索/筛选保留匹配节点与其祖先。生成页面可以从论文库首页的“研究地图”入口打开。

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

现有 26 篇来源（19 篇领域内、7 篇领域外）的事实文件增加可选 `analysis`；目前每篇整理一个主要贡献及两组实验记录，不宣称穷尽全部模块。旧事实文件没有 `analysis` 时仍可构建，页面显示待补充。两棵树详情中的来源论文展示失败现象、技术原因、通用 insight，并链接至完整单篇解析。当时 Challenge 树的 12 个 insight 增加 `principle`，区分技术认识与实现名称。

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


## Challenge–Insight 武器库（2026-10-29）

当前沿用 7 类挑战、26 篇事实来源（19 篇领域内、7 篇领域外），将 12 个 insight 整理为 20 张使用卡。保留原有节点 ID，拆分原先混放的技术杠杆：轻量算子 / 离线伪标签 / 分区并行，共享与特定参数 / 互补表征 / 天气条件化 / 参考标签，以及集合对称性 / 隐式观测 / 残差对应精化。未引入私人实验或未发表想法；两篇待整理论文仍为 pending，未增加虚构事实或方法节点。

每个 challenge 的 `why_hard` 是有来源的阅读者归纳。每个 insight 保留 `principle`（解释性的技术认识）、`techniques`（检索词），并必须填写 `playbook`：

- `use_when`：何时考虑；`mechanism`：可核对的操作，不能只写模块名。
- `engineering_tricks`：实现补丁及目的；没有独立对照不称“已证明必要”。
- `assumptions_cost`、`failure_boundary`：数据、传感器、配准、算力等前提与具体失效条件。
- `reported_effect`：现有笔记记录的结果及设置；`evidence_scope`：阅读者对因果与迁移范围的解释。二者分开，整体/累计对照不升级为独立因果证明。

这些字段沿用上面的 claim 结构与状态规则，证据必须属于该 insight 的来源并指向真实阶段/锚点。`source_locations` 为每篇来源登记原文节/图表/算法/页码及对应阅读锚点；页面附已有 DOI 入口。定位从现有公开笔记核对，本轮不是对 26 篇 PDF 的重新审读。`open_questions` 必须为 `not-assessed / unverified` 且无伪装的已核验证据。

搜索覆盖使用条件、机制、补丁、边界和原文定位，允许空格组合关键词，例如 `SDOR boundary band`、`SSR 教师`、`CRFOR ICM`。筛选位于脑图上方；节点保持短标题，完整内容在详情和下方可展开使用卡中阅读。生成器验证卡片完备性、来源归属、锚点和状态；不能代替学术判断。无新增原文审查记录，也不修改阅读页图文门禁、方法树事实和 novelty gate。

武器库页面的共享 JS/CSS 引用附内容哈希版本，避免 Pages 浏览器缓存将新字段配上旧详情渲染；哈希由源资产生成，仍可离线阅读。

## 2026-10-30 两篇待整理来源完成

Beyond the Snowflakes 与 SnowRemovalNet 已根据原文及图表核对补充事实层、单篇解析、Literature tree 和 Challenge–Insight 关联，`pending-papers.yaml` 现为空。加上当日 AWCR 后，当前地图共 29 篇来源（22 篇领域内、7 篇领域外），7 类挑战、21 张使用卡。历史日期下的数量是当时快照，不代表当前覆盖。

- SnowRemovalNet 并入 `insight-multidomain`、`insight-offline-labels`、`insight-task`，保留 ASDR+C-GLP 的既有工作身份、概率训练与组合消融边界，不把整体增益归因于单一模块。
- Beyond the Snowflakes 并入 `insight-task` 并新增 `insight-confound-control`：新增分支来自错误分解—对象元信息—天气共变这一独立诊断思路，不按论文数复制卡片。RF/SHAP 为代理预测模型的统计解释，不是检测器内部因果权重；各数据集的训练/传感器条件单独记录。
- 新事实文件记录本轮原 PDF 核验范围、版本、SHA-256；可点击证据仍指向既有阅读页锚点。旧来源维持原核验等级，本轮不声称重新审查全部历史 PDF。未取得的配置、原文未报告的独立消融和物理机制仍明确保留待核验。
- pending 回归测试改用独立测试样例，避免因真实论文完成而失去对遗漏、非法登记、重复与伪造节点的检查；新增两篇事实/两树/非 pending 覆盖回归。

## 2026-10-30 领域外来源按原任务纳入

领域分类表示论文与当前天气 LiDAR 研究方向的相关性，不是任务树的分类轴，也不是使用卡的收录门槛。当前共 43 篇事实来源（22 篇领域内、21 篇领域外）、21 个任务根、100 个 Literature 节点、28 类挑战与 43 张使用卡；数量是本次范围快照，不表示领域完整。

本轮覆盖现有 21 篇领域外来源：保留 7 篇旧事实的稳定 ID 与历史证据，补入其余 14 篇事实和单篇解析；22 篇领域内事实与 novelty gate 不变；阅读页仅对 Metric-Semantic Mapping 的一处 Table III mIoU 转录错误做授权勘误（70.4%→76.0%，原图不变）。领域外武器卡描述原论文真正解决的问题，不要求先证明天气迁移，也不要求先抽象成通用机制。

- Literature tree 按点集理解、几何恢复/补全、BEV/三维检测、定位/建图、具身导航、移动操作、图像去噪等实际任务组织。相同输出任务复用根节点，不设置统一“领域外”桶；训练监督、传感器与评测条件留在各路线和单篇说明。
- Challenge–Insight 将集合排列不变性、几何观测、配准对应、目标形状等已有卡移到原生挑战下，稳定 insight ID 不变。新增卡按独立技术杠杆组织；现有跨论文时序/下游关联不因移动而丢失，不按论文数量机械复制卡。
- “本轮材料核验范围”明确全文可访问性、版本差异与局部核对范围。笔记转述仍不是本轮 PDF 全文核验或复现；原任务结果、组件证据和跨域迁移各自保留边界。未取得原文、未报告消融等缺口不伪装成新研究空白。
- 结构校验不再禁止领域外来源进入任务树，但所有事实必须解析到实际 pipeline，且该路线或其子节点必须包含该来源；来源、阶段、锚点、claim 状态的检查不放宽。
- 后续新增的 **领域内或领域外** 论文均须纳入事实/任务树，或显式加入 `pending-papers.yaml`，注明有效登记日期与材料缺口。待整理项不计入已整理数量，也不能拥有占位事实/节点/卡片；已整理来源不能通过待整理登记被撤回。当前 21 篇覆盖有独立回归测试，未来资料不足时不必为过检查杜撰武器卡。

`task.conditions` 可选，用于公开显示监督与评测条件；对应证据仍由 `task.evidence` 负责。`source_review.scope` 可选，为公开可读的本轮材料范围说明，不替代逐条 claim 的证据与状态。现有左→右布局与搜索/路线/挑战筛选保持不变；仅追加“来源范围：全部/领域内/领域外”筛选。混合来源卡可在任一相关范围保留，匹配节点祖先仍可见。

## 2026-11-04 RAHF-Net 原任务证据增量

新增 RAHF-Net v2 全文核验事实与二维语义分割路线，在既有“远近距离采样不均”挑战下增加“按距离切换模态责任”卡。它改变近场几何/远场视觉的融合责任，区别于原有距离补偿邻域阈值卡，保留所有旧节点与旧结论。记录特征 max / 深度 min 池化、软路由、预训练成本，以及 Table 5 配置对照和 DELIVER 单基线压力测试的不同证据范围；不把总体提升归于每个模块，不声称雪尘去噪或跨传感器已验证。仅使用公开论文，无私人研究内容。

## 2026-11-05 实质增量

新增 DTF-Filter 与 ARP 的原文核验事实层及方法路线。DTF-Filter 优先并入既有密度自适应、时序持续性和下游任务 insight，补充 M=5、低速/近距假设、软权重与缺失模块消融的边界；ARP 在效率挑战下新增陈旧度匹配训练与快慢闭环 insight，保留完整基准低于 π0.5 的反例和异步条件。所有新增证据定位到初读页及原文节/图表；不把整体涨分当作单模块因果，不把机器人操作证据当作天气去噪已验证迁移。沿用既有节点ID、布局、详情及筛选。

## 2026-11-06 SiD 原任务证据增量

新增 SiD（CVPR 2026）的正文与补充全文核验事实，保留官方版本及两份 PDF 的 SHA-256。任务树新增“天气条件 LiDAR 扫描生成”，不并入输入受损扫描的过滤或恢复任务；路线下分别记录 RPWS、每步 S→I 扩散和评估端 FMD，所有既有 ID 保持不变。分类节点的新增不表示首次提出任务或领域首创。

- 优先复用 `challenge-weather` 与 `insight-conditioning`，后者扩展为“把退化状态作为恢复或生成条件”，分别注明 LTDNet 恢复与 SiD 新扫描生成的输入、证据和边界，不作跨任务分数排名。
- 新增两张独立机制卡：RPWS 的点存活/强度统计移植，以及每个扩散步的结构引导强度。它们与天气 embedding 调制不同，不按论文重复建立挑战根；FMD 作为评价工具记录，不额外制造已验证的物理真实性或下游收益卡。
- 正文 Table 1 雨天 JSD 为并列，Table 2 晴天不是全指标最佳；Table 3 换 RPWS 也非所有指标单调改善。正文/补充 RPWS 消融数值与 WeatherGen 原报告/复现口径分别保留，不拼接为统一对照；S→I 方向只由本文雪天消融支持，不升级为普适因果证明。
- “无 FT”仍利用真实天气统计；生成分布质量不等于检测/分割提升或有效伪标签。作者明确的环纹、小/远物体平滑和单帧时序限制保留；缺失的实现与下游证据不包装成领域研究空白。`pending-papers.yaml` 保持空，novelty gate 与历史核验等级不变。已完成受影响节点的桌面与手机展开、详情、筛选及来源跳转验收；SiD 事实层显式登记雨、雾、雪，确保天气筛选保留两张新机制卡。沿用既有脑图布局与交互。


## 2026-11-07 GeoReasoner 原任务增量

新增固定 arXiv:2610.41446v1 的全文核验事实与五分支解析。任务树单列城市空中语言目标定位：输入RGB-D、位姿、地理名称/轮廓，输出导航动作与目标停止，区别于RGB-only局部物理执行。新增任务分类不声称领域首创。

- 在“高空相似目标与过早确认”原生挑战下新增两张独立机制卡：把未决关系变成主动观测航点；分开支持、不足与冲突再决定停止。区域假设、候选合并和记忆属于第一卡的实现链，三角色辩论、回退与重规划属于第二卡，不按三个模块机械复制卡片。
- 保留低合理性区域优先、9m合并、6区域/9候选/4次补观测/2次额外重规划的具体设置与缺少独立参数消融的边界。证据不足时的回退停止不等于充分验证；全冲突且预算耗尽时可无已验证目标结束。
- Table 1原报告GeoNav与Table 3同Qwen3.8-Flash重现分别记录；Val-Seen的三项不及RingMo-Agent，Val-Seen-Hard的NE不及HETT。完整系统、组件消融和阅读者机制归纳保持独立，缺少成本、实机与天气迁移证据不包装成已验证收益。
- 保留旧133个Literature节点与29类挑战的原有内容、所有稳定ID和核验等级。增量为5个Literature节点、1类挑战和2张使用卡；pending与novelty gate不变。

## 2026-11-08 独立专题证据

3D-UnOutDet 的专题回看迁至独立 `revisits/3d-unoutdet-20261108.html`，原初读恢复原内容。既有事实与武器库卡中的本次新增证据改用 `revisit: 3d-unoutdet-20261108`，不伪装成初读锚点或新增阅读阶段；验证器以 `revisits.json` 检查论文归属和真实目标。既有 stage 证据、稳定节点与核验等级不变。

## 2026-11-10 NEO-VLA 原任务证据增量

新增固定 arXiv:2611.06918v2 的事实与五分支解析，复用语言条件动作块任务，新增原生视觉计算路线及两个模块节点。现有挑战未覆盖固定视觉读出问题，因此新增一类挑战及一张“按动作需要选择视觉计算层级”卡，不按模块复制武器卡。

保留 skip28/end28 匹配容量证据、first28 同时剪短 backbone 的混杂、Table3 中间视觉接入反例、Table6 共训练范围及 Table8 空间/任务泛化失败。作者 p.2 的预训练/容量混杂明确保留；16页 PDF 未包含 p.7 所指附录，不谎称附录核验。只按机器人操作原任务收录，天气 LiDAR 迁移未验证。历史节点、布局、证据等级、pending 和 novelty gate 不变；本次已在云浏览器1440px桌面/390px手机视口实际核验受影响两卡的详情、筛选、来源链接和专题锚点，沿用既有布局。发布状态仍以main精确SHA对应Pages成功及公网内容核验为准。

## 2026-11-10 LiSnowNet 专题证据增量

重新核对作者 arXiv:2211.10023v1 七页全文及图表，独立专题页记录训练损失、α/β选参和推理残差判定的不同作用。沿用既有 insight-frequency，补充每个β重选α、β未测0/1端点以及不能凭此断言分支可删除的边界；相关证据指向新专题part3/part4，保留历史原文核验登记，不提升旧证据等级。未新增重复卡或未验证的天气迁移。

## 2026-11-12 RPSnowNet专题证据接续

独立专题保留11月11日实际核读日期，11月12日恢复集成。复用 `insight-adaptive`，补充GT描述性观察与先验代理N的区别、视觉选择b再拟合的工程步骤、跨数据集参数条件及Fig.12局部敏感性边界；不新增重复节点，不提升历史来源核验等级。专题证据通过 `revisit: rpsnownet-20261111` 定位独立页，原初读、论文目录、Literature树和其他地图不改。事实层新增独立回看登记和限制说明；完整系统涨分不解释为教师某类错误已获纠正。发布须另完成实际视觉验收及全部回归。


## 2026-11-14 AWCR v2 证据增量

接续11月13日核读与备份，核对 arXiv:2610.35110v2（11月9日修订）。沿用 `insight-task`、原任务路线及全部稳定ID，只更新AWCR事实和既有下游评估卡：将全320视图的71/72诊断恢复与64视图晴天修复集分开；补充验证集选择λ、默认三次拟合的恢复/保留取舍、当前点统计、中央计时与未压缩通信成本；同时保留同一预测在global-ranking与frame-order评价下方向相反的结果。原v1笔记另存，不把旧端点冒充v2默认配置。

其余来源文字、证据列表和核验等级保持不变，不增加挑战或重复使用卡。关键定位回到Tables1–3、S3–S4、S7–S11、S16、S19–S22及相关附录；整体涨分不升级为各组件独立因果证明。未验证的跨传感器与端到端联网实时条件继续保留边界。本轮已实际核对桌面/390px手机的节点详情、雪天筛选与AWCR来源锚点，阅读页四处原图均核对放大及原尺寸滚动；发布后的Pages状态须另行确认，不以提交等同上线。
