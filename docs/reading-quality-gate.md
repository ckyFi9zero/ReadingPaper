# 初读图文与分类发布门禁

生效：2026-10-28。缘由：Beyond the Snowflakes 的首版虽有原创流程示意，却没有让读者直接查看关键实验原图；同时把“未提出去噪网络”错误地用作领域外判据。该错误必须在流程中显式拦截，不能只口头承诺。

## 必做的人工核验

1. 阅读当前版本全文，实际查看图表；按安装的 reader skill 输出对应阶段。Stage 1 保持十二项及作者表述 / 概括 / 直接观察的来源边界。
2. 选择理解关键论证所必要的证据图，裁成独立 Figure/Table 局部，核对坐标轴、图例、子图、数值与原始图注。紧邻相应分析，标作者、原图/裁剪身份、图号、PDF 页序和原始来源。原创流程示意可以辅助，但**不计作论文证据图**；“链接到原图”也不等于正文已展示证据。
3. 审查公开范围和版权情况。仅使用必要、可解释的局部材料，不搬运整篇 PDF / 整页图集，不把缺少 CC 许可一概等同于禁止任何必要摘录，也不把教育目的自动等同于已获授权。许可不明时记录实际依据与边界；无法合理取得/核验必要图表时停在待补材料，不能造图冒充。
4. 分类依据项目相关性，不依赖单个关键词或是否提出新去噪网络。直接相关的恶劣天气 LiDAR 数据、去噪效果与检测鲁棒性评测可以是领域内。记录具体理由、用户范围和原文定位；有歧义时保留未分类及明确理由，不代替用户改研究方向。
5. 真实查看桌面和窄屏，逐图加载、图文邻近、长表格局部滚动、点击放大及原尺寸查看。**检查尚未进行时不能把视觉字段填 true。** 本次在 390px 窄屏检查无页面横向溢出，热图可切换原尺寸并在弹窗内滚动；打印样式只做静态检查，不冒充实际打印验证。

## 机器会拦截什么

`python3 scripts/check_reading_publish.py` 对新登记的初读执行 fail-closed 检查，并已接入 `build_site.py`（任何生成文件写入/删除前）、`check_site.py` 和导出流程。

- 原有 39 个 slug 固定为迁移边界，历史条目原样兼容，不表示已补做新标准审查。其他新初读必须登记 `readingQuality`，省略字段或倒填阅读日期不能豁免；不要向旧名单添加新论文规避检查。
- 必须有分类结论、具体理由、范围/原文依据及日期，且结论与 `category` 一致。本次用户确认的领域内结论和 Figure 4/7/8 修复另有明确约束；不是程序自动推断相关性。
- 登记的证据图必须对应实际 `<figure>`、离线 raster 图片、准确身份属性、图注/页码/源链接、同节展开分析和可用结构的放大入口。仅有 SVG 流程图、远程源链接、空白小图、隐去的分析或虚构图元素不能满足规则。
- 人工版权范围审查和桌面/手机/放大验收须有完成记录。
- 全文确实没有适合该阶段的证据图时才可用 `no-suitable-figures`：必须记录已阅读全文、没有相关图表的判断、具体原因与页/节证据、来源、复核者和日期；“拿不到图”不是无图论文例外。本篇修复不能使用该例外。无图例外的 zoom 可为 `"not-applicable"`，不能为凑验收造图。

这些是结构和复核记录检查，**不能代替人判断图像是否真源于论文、分析是否正确、分类是否恰当或法律许可是否成立**；最低字数不是分析质量保证。必须同时完成上面的人工审查。

## 可兼容元信息示例

在 `papers.json` 对应条目增加可选对象；新初读实际必填，历史条目可逐篇明确升级。以下只是格式示例，不应原样复制虚假“通过”记录：

```json
"readingQuality": {
  "version": 1,
  "classification": {
    "confirmedCategory": "in-field",
    "rationale": "具体说明论文与用户研究方向的关系，不把是否提出去噪网络当作唯一标准。",
    "source": "用户确认的范围日期；论文具体 Section / PDF 页码及对应事实。",
    "reviewedAt": "YYYY-MM-DD"
  },
  "graphics": {
    "status": "included",
    "items": [{
      "figureId": "fig-4", "kind": "paper-crop", "label": "Figure 4", "pdfPage": 4,
      "sourceUrl": "https://arxiv.org/html/2610.13891v1#S4.F4", "analysisId": "analysis-fig-4"
    }]
  },
  "rightsReview": {"basis": "逐图公开范围、出处、许可状态及必要摘录的具体审查说明。", "reviewedAt": "YYYY-MM-DD"},
  "visualReview": {"desktop": false, "mobile": false, "zoom": false, "reviewedAt": "YYYY-MM-DD"}
}
```

HTML 证据图使用 `data-visual-role="evidence" data-origin="paper-crop"`；原创示意使用 `data-visual-role="schematic"`。分析元素的 `id` 对应 `analysisId`，且 `data-for="fig-4"`。图注中的链接与 `sourceUrl` 相同。可以用本地相对图片或 data URL；本地 PNG 与 HTML 必须一起保存/发布。具体实现见本篇修复页及回归测试。

## 发布前顺序与停止条件

```bash
python3 scripts/check_reading_publish.py
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m unittest discover -s tests -v
node --check assets/app.js
node --check assets/reader-nav.js
node --test tests/test_app.cjs
```

另运行安装 skill 的 `check_html_media.py`，人工核对图文证据。新增错误阻止发布；与本次无关的既有错误必须以未修改基线重跑证明并明确记录，不得静默豁免或扩大修改范围。2026-10-28 已确认的基线仅为 `papers/3d-unoutdet-2025/linked-reader.html` 的两处本地 `source.pdf` 缺失链接；不要为了本次修复删掉旧页面或上传其 PDF。

检查通过后，重读远端主分支以避免覆盖并发更新，非强制更新提交；等待**对应提交**的 Pages 任务完成，再检查公网首页分类、实际文章、所有新增图片及放大行为。提交成功不等于发布成功。每日自动任务同样必须遵守上述停止条件。

此门禁约束仓库的标准构建/检查/导出及自动任务发布前置步骤。当前 GitHub Pages 的动态 Jekyll 本身不执行这些 Python 检查；未增加分支保护或改部署设置，因此**不是无法绕过的 GitHub 服务端权限锁**。不得把“未运行检查直接提交”称为合规发布。

回归测试包含：真实旧页面/只补登记仍失败、流程图冒充失败、错误分类或缺理由失败、缺图片/出处/放大/视觉复核失败、新论文缺字段/倒填日期失败、已修复图文通过、合理无图例外，以及导出后图资源完整性。地图另保留原 19 篇覆盖，新篇尚未建树时必须显式登记待整理，不能伪造已完成分析。
