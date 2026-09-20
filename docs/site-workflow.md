# 网站维护与发布

## 阅读内容与来源核对

`papers.json` 管目录，正文存放在论文目录或原有 `paper-cards/`。现在三个阶段都可使用 Markdown：

```json
{
  "stages": {"first-pass": "first-pass.html", "deep-read": "deep-read.md", "code": "code.md"},
  "codeUrl": "https://github.com/OWNER/REPOSITORY",
  "openQuestions": ["这里填写真实的待核对问题"],
  "reviews": {
    "code": {"noteStatus": "draft", "status": "unrecorded"}
  }
}
```

这是字段示例，只有实际文件存在时才登记。Markdown 源相对论文目录定位，其中的图片和链接相对源文件定位。手写 HTML 原样保留；不要将生成的 HTML 登记成手写源。旧 `card` 相当于一个深读 Markdown 来源，不能与 `stages.deep-read` 重复。

`noteStatus` 为 `unknown`（默认）、`draft` 或 `organized`；核对 `status` 为 `unrecorded`（默认）或 `source-checked`。已整理不代表已核对。登记 `source-checked` 时必须有 `checkedAt` 日期和非空 `evidence` 列表，例如具体页码、表格或完整 commit 的代码链接。它表示人工登记，不是生成器替人验证了事实。旧卡片保持“来源核对未登记”。

代码笔记可从 `templates/code.md` 开始，分别写论文表述、代码事实、运行观察和个人理解。代码定位尽量记录完整 commit SHA、路径、函数与行号。静态读过代码并不等于复现成功。

## 领域分类

每篇论文可在 `papers.json` 中设置 `category`：`in-field`（领域内）、`out-of-field`（领域外）、`uncategorized`（未分类，省略字段时默认）。例如 `"category": "out-of-field"`。分类表示与个人研究方向的关系，独立于雨、雪、深度学习等 `tags`，也独立于阅读进度；不会根据关键词自动改变分类。

领域内以用户确认的“恶劣天气下的 3D 激光去噪”为边界，目前 9 篇，含扬尘工况的 LIOR De-Dust 和矿区雾尘雪去噪的 SCFNR；DHE-Net、Electric Arc Noise、Density-Sensitive Transformer 和 SA-LPCC 共 4 篇属于领域外，不因同属点云处理就默认算作领域内。

期刊／会议筛选直接从 `venue` 字段自动生成，新增发表来源不需要改代码。同一期刊或会议应统一名称（例如始终使用 `IEEE RA-L`），不要混用缩写与全称；arXiv 作为预印本来源保留。该维度与 `category` 独立，同一期刊可同时有领域内和领域外论文，不需要重复登记论文。

首页下拉菜单的数量表示整个当前目录的分类或发表来源总数；下方“n 篇论文”表示领域、发表来源、关键词和阅读阶段共同筛选后的数量。筛选保存在 URL 中（`category` / `venue` / `q` / `stage`），刷新仍保留；“清除筛选”同时重置这四项，保留排序。

分类与标签修改后重新生成并导出即可，不需要移动论文目录，也不需要改正文。公开范围仍由 `publish.json` 单独管理，领域分类不决定是否公开。

## 生成与检查

```bash
python3 -m pip install -r requirements-site.txt
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m unittest discover -s tests -v
node --test tests/test_app.cjs
```

生成器先完成所有内容渲染和目标文件冲突检查，再写入页面。源文件缺失或目标是手写内容时，避免出现前几页已更新、后几页尚未更新的情况。这不是针对磁盘故障的完整事务保证。

## 本地完整导出

```bash
python3 scripts/export_site.py --profile local
python3 scripts/check_site.py --root _site
```

打开 `_site/index.html` 可阅读独立副本，也可在仓库的 HTTP 预览下访问 `/_site/`。它包括所有已登记论文、现有综述和页面引用的 PDF/Markdown，因此属于本地完整版本。

导出器从源文件重新渲染，避免发布旧 HTML；只复制页面需要的文件。内嵌 PNG/JPEG/WebP/GIF 提取为按内容哈希命名的资源，图像字节不变，便于懒加载、浏览器缓存和去重。已有点击放大仍引用同一图像。原始 HTML 不修改。

`site-manifest.json` 记录输出文件哈希、体积、阅读阶段和大页面提示。HTML 变小不等于图像不需要下载；导出总大小也会包含 PDF。默认总大小预算为 900 MiB、大 HTML 提醒阈值为 2 MiB，可在 `publish.json` 调整。

导出先在临时目录构建并检查，全部成功后才替换输出。旧输出移到 `tmp/site-backups/`，不自动删除；空间不足时由维护者确认清理。没有导出清单的已有同名目录会被拒绝覆盖。检查错误时上一份完整导出保持可用。

## 公开版本

当前 `publish.json` 没有选中任何论文，直接公开导出会提示先确认范围。选择以“论文元信息 + 具体阶段”为单位。例如，确实决定公开某篇已核对初读时：

```json
{
  "papers": [
    {
      "slug": "dsor-2021",
      "stages": ["first-pass"],
      "include_pdf": false,
      "include_questions": false,
      "allow_embedded_images": true
    }
  ],
  "overview": false,
  "assets": [],
  "maxTotalMB": 900,
  "warnPageMB": 2
}
```

这个例子没有自动写入配置。`allow_embedded_images: true` 表示你已经检查并决定公开该阶段内嵌图片，程序不能替你确定转载许可。没有此选择时，含内嵌图的阶段会阻止导出。该开关是按整篇选中阶段生效，需要逐图筛选时先准备适合公开的源笔记。

`include_questions` 默认关闭；未选阶段显示“未公开”，不复制正文；未选论文不会出现在首页或搜索数据；原始卡片下载入口默认移除。`overview: true` 会公开现有综述全文，其中可能含研究候选，需要单独检查，不能因某篇已公开就默认公开综述。

公开页引用的额外图片/字体，逐一加入 `assets`（仓库相对文件路径，不接受目录或通配符）。未允许的附件会使导出失败，不会静默复制或删掉链接。PDF 由对应论文的 `include_pdf` 单独选择。研究资料包、源码、上下文、临时目录不作为公开附件。已选正文和摘要中的内容仍需人工判断；这些规则不等于自动审查科研隐私或版权。

```bash
python3 scripts/export_site.py --profile public
python3 scripts/check_site.py --root _site-public
```

只把 `_site-public/` 作为公开站点。源仓库若公开，仓库里的其他已提交文件仍可被访问，导出规则不会改变源仓库可见性。

## GitHub Pages 工作流

`.github/workflows/pages.yml` 使用 GitHub 的静态网站 Actions。先在仓库 Settings → Pages 中选择 GitHub Actions，然后由维护者手动运行工作流。默认 `deploy=false` 仅构建、检查并上传选中内容的网站 artifact；勾选 `deploy=true` 才部署。空公开清单会在上传前失败。没有 push 自动发布触发器，也不在 Actions 中运行 AI 阅读。阅读 HTML 由用户手动上传，并在 `papers.json` 登记。

流程：安装依赖 → 回归测试 → 本地生成/检查 → 公开导出/检查 → 上传 `_site-public` → 可选部署。部署权限只赋予部署 job，不把整个仓库上传作站点。

项目站点可能位于 `用户名.github.io/仓库名/`，所有链接保留相对路径；检查器拒绝 `/assets/...` 这类会绕过仓库名前缀的站内绝对路径。发布后仍需从实际网址验证图片、刷新及设备访问，当前未执行远端部署。

实现参照 [GitHub Pages 自定义工作流文档](https://docs.github.com/zh/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) 与 [GitHub 官方静态网站工作流](https://github.com/actions/starter-workflows/blob/main/pages/static.yml)，动作版本按 2026-09-17 检查的官方模板选择。
