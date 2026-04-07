# 论文深度解析笔记：Multi-Structure Mapping for Filtering Electric Arc Noise in Power Line Environments

**期刊**: IEEE Robotics and Automation Letters (RA-L), Vol. 11, No. 2, February 2026

**作者**: Najlae Boulajoul, Alexis Lussier Desbiens, François Ferland

---

## 1. Abstract 解析

> Electric arc noise around energized power lines corrupts drone LiDAR measurements, accumulating in occupancy grids and producing spurious obstacles that degrade navigation reliability.

`S1` **功能：问题定义与危害陈述。** 开篇第一句即锁定研究对象（electric arc noise）、受影响的传感器（drone LiDAR）、以及具体后果链条：噪声→占据栅格累积→虚假障碍物→导航可靠性下降。注意这句话的信息密度极高，一句话内完成了"现象→机理→后果"的三级因果链。这是RA-L这类短篇幅期刊（Letters）摘要的典型写法——没有铺垫空间，必须立即切入核心问题。

> Existing filters designed for environmental clutter such as snow, dust, and rain fail to consistently reject these short-lived arc transients and remain difficult to deploy on resource-limited platforms.

`S2` **功能：现有方法的不足（Gap Statement）。** 两个并列的不足：(1) 滤波效果不一致，(2) 计算资源要求高。"such as snow, dust, and rain"明确了现有方法所针对的噪声类型，隐含了本文噪声类型（电弧）的独特性。"short-lived arc transients"是关键描述词，为后续方法的时间一致性设计埋下伏笔。

> We propose a dual-structure filtering framework that dynamically separates transient arc noise from persistent environmental features.

`S3` **功能：方法概述（Contribution Claim）。** "dual-structure"是本文的核心概念标签。"dynamically separates transient … from persistent"点明方法论的核心思想——利用瞬态vs持久的时间特性差异进行分离。

> Instead of filtering scan-by-scan, the proposed filter leverages spatio-temporal neighborhood consistency across consecutive LiDAR frames to suppress short-duration particles.

`S4` **功能：与传统方法的区分（Differentiation）。** "Instead of"句式明确划清了与逐帧滤波方法的界限。核心创新点落在"spatio-temporal neighborhood consistency across consecutive frames"——跨帧的时空邻域一致性。

> A transient k-d tree accelerates neighborhood queries and removes arc noise around valid structures, while a persistent octree integrates only enduring features into the global map.

`S5` **功能：双结构的具体说明。** 用一个并列句分别交代两个数据结构及其各自职责：k-d tree（局部瞬态缓冲，快速查询）和octree（全局持久地图，仅融合持久特征）。这句话是对"dual-structure"的展开。

> Experiments show up to 10 times faster filtering and mapping precision of 92.27% with F1-scores up to 95%.

`S6` **功能：定量结果摘要。** 两个维度的指标：速度（10倍提升）和精度（precision 92.27%, F1 95%）。"up to"的措辞是保守策略，取最佳结果而非平均值，这在摘要中是常见且可接受的。

> Real-world inspection flights over energized power lines confirm that the approach maintains accurate, up-to-date maps and robust performance in the presence of electric arc noise.

`S7` **功能：实际验证声明。** 强调了"real-world"和"energized power lines"，表明不仅仅是仿真验证。这对于一篇应用导向的RA-L论文至关重要——审稿人会关注方法是否经过真实场景考验。

**摘要总结与迁移指导：** 本摘要遵循经典的"问题→Gap→方法→核心思想→结果→验证"六拍结构，7句话覆盖完整。对于Letters类短文，摘要是微缩版的全文，每句都不可或缺。值得学习的是S1的三级因果链写法和S4用"Instead of"进行方法定位的技巧。

---

## 2. Introduction 解析

Introduction较长，我将按逻辑段落进行分组解析。

### 2.1 第一逻辑段：领域背景与研究情境

> `S1` ACCURATE environmental perception is critical for robotic applications, and LiDAR sensors are widely employed to capture high-precision spatial data [1], [2], [3].

**功能：大背景建立。** 从最宏观的"机器人感知"入手，引出LiDAR作为核心传感器。引用[1][2][3]为SLAM/导航/点云处理的经典文献，目的是**奠基**——表明这是一个成熟且重要的领域。RA-L论文的引言开头通常不超过1-2句宏观背景。

> `S2` In particular, drone-based LiDAR mapping has proven effective for various inspection tasks [4], [5], [6].

**功能：聚焦到具体应用场景。** 从泛化的LiDAR应用收窄到"drone-based LiDAR mapping"和"inspection tasks"。[4][5][6]提供了无人机巡检的应用证据，作用是**支撑场景合理性**。

> `S3` However, environmental noise can compromise LiDAR data quality.

**功能：转折引出问题。** "However"是信号词，标志从正面（LiDAR有效）转向负面（噪声问题）。这是引言中最经典的"由正转负"过渡句。

> `S4` Prior work has primarily addressed challenges posed by snow, dust, and rain by employing sensor fusion and advanced filtering techniques [7], [8], [9], [10].

**功能：已有工作的覆盖范围界定。** "primarily"是关键词——暗示现有工作有偏向性，为下一句的gap做铺垫。[7]-[10]覆盖了雪/灰尘/雨的滤波文献，作用是**划定已有研究边界**。

> `S5` In power line inspection tasks, electromagnetic interference near energized power lines introduces transient electric arc discharges [11], [12], which leads to false obstacle detections and navigation errors when such artifacts accumulate in maps.

**功能：引出本文特有的噪声类型。** 这是问题聚焦的关键句。[11][12]为电弧放电的物理机理文献（非机器人领域），目的是**为噪声来源提供物理依据**，增强可信度。因果链再次出现：电弧放电→虚假障碍物→导航错误。

> `S6` In our observations, arc noise exhibits several distinct characteristics in contrast to environmental noise such as dust, snow, and rain. `S7` Arc noise typically manifests as brief and sparse bursts, whereas environmental artifacts tend to be longer-lived, more frequent, and more persistent.

**功能：电弧噪声的独特性论证。** 这两句是本文立论的关键。作者通过"in our observations"表明这是一手发现（而非文献引用），用对比句式（brief/sparse vs. longer-lived/frequent/persistent）精确刻画了电弧噪声与传统环境噪声的差异。这个差异是后续方法设计（利用时间瞬态特性）的**直接动机**。审稿人读到这里会形成一个期待：如果噪声是短暂稀疏的，那方法应该利用时间一致性来过滤。

> `S8` Existing filtering methods that primarily rely on intensity thresholds [9] are not well-suited for the unpredictable intensity patterns exhibited by electric arc noise.

**功能：排除第一类方法（基于强度）。** [9]被引用为代表性的强度滤波方法，此处的作用是**作为被否定的对象**。理由是电弧噪声的强度不可预测。

> `S9` Filtering based on spatial distribution characteristics such as Radius Outlier Removal (ROR) [8], [9] may be more effective. `S10` However, when applied directly to point clouds, these approaches can be computationally demanding for resource-constrained applications, especially given the large point clouds typical of power line inspection environments.

**功能：部分肯定但仍指出不足的第二类方法（基于空间分布）。** 写法上先给了一个"may be more effective"的让步，随即用"However"转折指出计算代价问题。[8][9]在此的引用角色转变为**部分可用但有缺陷的方法**。"resource-constrained"呼应了摘要中对平台限制的提及。

**这两步（S8-S10）的逻辑值得学习：** 先排除不可行的方法A，再指出可行但有缺陷的方法B，从而为自己的方法C创造出精确的"需求插口"。

### 2.2 第二逻辑段：本文方法概述

> `S11` We introduce a dual-structure filtering framework that detects transient arc noise by leveraging neighborhood consistency across successive point clouds instead of per-scan filtering.

**功能：方法声明。** 与摘要S3/S4呼应，但在引言中再次出现以确保读者（尤其是跳读的审稿人）不会错过核心贡献。

> `S12` Locally, a k-d tree-based transient buffer captures short-lived, sparse arc particles in a small number of points, where k-d trees are most efficient, resulting in faster nearest-neighbor queries and quicker denoising.

**功能：局部结构的设计合理性论证。** 不仅说明了"用什么"，还解释了"为什么用"——k-d tree在小规模点集上最高效，而瞬态缓冲恰好是小规模的。这种**设计决策与数据特性的匹配论证**是方法论写作的高级技巧。

> `S13` At the global level, we use OctoMap [13], an octree-based probabilistic occupancy map, to integrate only validated, repeatedly observed features, and its hierarchy scales well to large datasets for global mapping.

**功能：全局结构的设计合理性论证。** 同样的"用什么+为什么"模式。OctoMap [13]在此的引用作用是**借力经典工具**——利用其成熟性和广泛认可度来增强本文方法的可信度。

> `S14` We validate the approach on LineDrone-NADILE [14] data collected during inspections of 315 kV power lines, demonstrating reduced computational load and improved noise removal for accurate mapping in large-scale, noisy environments.

**功能：验证概述。** [14]引出实验平台。"315 kV"这个具体数字增强了真实场景感。

### 2.3 第三逻辑段：贡献列表

作者列出三条贡献：

1. **电弧噪声的定量表征**（稀疏性、寿命、空间足迹），论证了为何需要超越单帧启发式方法。
2. **双结构映射**：有界增长的瞬态k-d tree + 持久全局octree。
3. **真实数据集的现场验证**。

**深度分析：** 贡献的排列顺序有讲究。第一条是"问题理解"层面的贡献（quantification），第二条是"方法"层面，第三条是"验证"层面。这种从"理解问题→解决问题→验证方案"的递进结构非常清晰。值得注意的是，第一条贡献（噪声表征）在很多论文中被忽略，但在本文中它是方法设计的基础——正是因为量化了噪声的"短寿命"和"稀疏性"，才合理化了双结构的设计。这体现了**数据驱动的方法设计**思路。

### 2.4 引言末尾：全文路线图

> The remainder of the letter is organized as follows: Section II reviews related work; Sections III and IV detail the methodology; followed by conclusions in Section VI.

**功能：标准路线图句。** 在RA-L论文中常见但非必需。提供阅读导航。

**Introduction总结与迁移指导：**

本文引言采用了经典的"漏斗型"结构，但有两个值得学习的特色：

* **噪声特性对比**（S6-S7）：在指出gap之前，先用一手观察建立了"本文噪声与传统噪声本质不同"的认知，这为gap的论证提供了物理层面的支撑，而非仅仅说"没人做过"。
* **方法与数据特性的匹配论证**（S12-S13）：在介绍方法时同步解释了数据结构选择的合理性，避免了方法节再重复论证。

---

## 3. Related Work（Section II）解析

### 3.1 Mapping Approaches（II.A）

这一小节简要综述了3D映射方法的发展脉络：

* 早期点云/网格方法 [10][15][16]：可视化好但缺乏体积占据信息。
* 概率栅格方法 [17]：有占据信息但分辨率固定。
* 层次结构（OctoMap）[13][18]：自适应分辨率，效率高。
* 语义映射扩展 [19]：增加计算复杂度。

**深度分析：** 这个综述的逻辑线索是"从简单到复杂"的方法演进，最终落脚到OctoMap——本文方法的全局地图组件。文献的引用策略非常有目的性：每种方法都被简短提及其优势和局限，最终将OctoMap定位为"优雅但不能处理动态瞬态现象"的工具。最后一句"do not inherently address very dynamic and transient phenomena"是**精确指向本文所填补的gap**。

### 3.2 Noise Filtering Approaches（II.B）

这一小节更长，按方法类别组织：

1. **传感器融合**（LiDAR-Camera [20], LiDAR-Radar [21]）：作者用了大段篇幅解释为何融合方法在高压环境下可能失效——细导线难以跨传感器一致检测[22][23]，电弧瞬态噪声在不同模态中捕获不一致。这段分析很细致，目的是**预防审稿人的"为何不用融合"质疑**。

2. **基于强度的方法**（LIOR [24]）：强度不可预测，不适用。

3. **空间滤波**（SOR, ROR [8]）：计算密集。

4. **深度学习方法** [16][25]：计算量大、需要标注数据，不适合资源受限的无人机。

**深度分析：** 这个相关工作节的结构是**分类否定法**——将现有方法按类别逐一审视，对每一类给出在电弧噪声场景下失效的理由。这种写法的优势在于系统性强，但风险在于可能显得过于否定。作者通过适度的让步语气（"may struggle with", "effectiveness remains to be thoroughly evaluated"）来平衡。

最后的总结句非常关键：

> These trade-offs between mapping accuracy, particularly arc-noise recognition, and computational efficiency, measured as per-frame point-cloud processing, motivate ongoing research into methods for dynamic, noisy environments.

这句话将gap具体化为两个维度的权衡：**精度vs效率**，直接为本文方法（兼顾两者）铺平道路。

---

## 4. Preliminaries（Section III）解析

这一节是本文的特色结构——在正式方法之前，用一整节介绍实验平台和噪声分析。

### 4.1 LineDrone-NADILE平台（III.A）

详细介绍了无人机平台、计算单元（Jetson Xavier NX）、传感器（Velodyne VLP-16, 10Hz）、任务流程（起飞→插入电缆→巡检→返航）。

**深度分析：** 这段的存在有两个目的：(1) 为实验节提供必要的硬件上下文；(2) 更重要的是，通过描述实际任务中遇到的问题来**从应用端论证研究动机**：

> …sparse bursts of arc noise accumulated in the global OctoMap, were interpreted as static obstacles, and caused the planner to fail to converge.

这句话是全文最有说服力的动机句之一——它不是抽象地说"噪声有害"，而是**具体描述了一次真实系统失败**（规划器无法收敛）。这种来自一手工程经验的动机论证，比纯文献推导的gap更能打动审稿人。

### 4.2 Electric Arc Analysis（III.B）

这一小节是贡献一（噪声定量表征）的具体实现。

**实验设计：** 两次完全相同飞行（带电vs不带电），通过ICP对齐后差分识别电弧体素。这个实验设计非常巧妙——通过**控制变量法**（唯一变量是线路是否带电）来分离电弧噪声。

**关键定量发现：**

* 电弧噪声仅占总体素的0.021%（极稀疏）
* 可传播至39.71米
* 平均最近邻距离3.13m（vs有效点0.71m）——**稀疏4.4倍**
* 平均持续时间仅0.26秒（极短暂）

**深度分析：** Table I和Fig. 3的数据为方法设计提供了直接的参数依据。例如：

* 0.26秒的寿命 → 决定了瞬态缓冲持续时间(\tau_{\text{buffer}})的上界
* 3.13m的邻域距离 → 指导了邻域搜索半径(r)的选择
* 极低的体素占比 → 合理化了"将少数瞬态点从大量持久点中分离"的思路

这种**数据驱动的方法参数化**是本文的显著优势。很多论文的参数选择缺乏实验依据，而本文在提出方法之前就用专门的分析为参数设置提供了科学基础。

---

## 5. Proposed Approach（Section IV）解析

### 5.1 方法节开篇

> Per-scan filtering fails on arc noise because returns are short-lived, neighborhoods are incomplete, and point clouds are large.

`S1` **功能：方法节的动机重申。** 用三个并列原因解释了为何不能逐帧滤波，直接衔接到"因此需要双结构"。这种在方法节开头用一句话重申"为何需要本方法"的写法，可以帮助跳读到方法节的读者快速理解背景。

### 5.2 Transient Buffer Construction（IV.A）

#### 5.2.1 k-d tree结构（IV.A.1）

详细描述了k-d tree的构建和邻域查询过程。公式(1)给出了分裂平面距离：

[
d_{\text{plane}} = |q_{a_l} - p_{n,a_l}|
]

**深度分析：** k-d tree本身是经典数据结构，此处的叙述目的不是教读者k-d tree原理，而是为后续的搜索复杂度分析（(O(\log N))）和"为何k-d tree适合小规模瞬态缓冲"的论点提供技术铺垫。修剪策略（pruning）的描述强调了效率，呼应了"计算资源有限"的约束。

#### 5.2.2 概率邻域搜索（IV.A.2）

这是方法的核心创新之一。传统ROR使用硬阈值，本文改为概率保留：

[
p_{\text{keep}} = \max\left(p_{\text{floor}}, \frac{1}{1 + \exp\left(-\frac{r^2 - d_K^2}{\beta^2}\right)}\right)
]

**深度分析：** 这个公式的设计逻辑值得细究：

* 使用sigmoid函数实现从"保留"到"丢弃"的**软过渡**，而非硬阈值。动机是硬阈值对密集电弧爆发和稀疏有效点区域都敏感（过滤过度或不足）。
* (p_{\text{floor}})保留了一个最低保留概率，防止孤立但有效的点被完全丢弃（如细电缆）。
* (\beta)控制过渡的陡峭程度，实验节(V.B)中会给出其敏感性分析。

判定保留的条件(h(i) \leq p_{\text{keep}})使用了基于点索引的伪随机函数，实现了**确定性采样**——同一点在相同条件下结果一致，这对可复现性很重要。

**写作技巧：** 作者先在文字中解释了设计动机（"hard-thresholding approach can be sensitive to..."），然后给出公式，再解释公式各项含义和极端行为（(d_K < r)时、(d_K = r)时、(d_K > r)时）。这种"动机→公式→解释"的三步法是数学公式呈现的标准范式。

#### 5.2.3 瞬态缓冲持续时间（IV.A.3）

缓冲窗口(\tau_{\text{buffer}})需满足两个约束：

[
\alpha_{\min} \cdot \Delta t \leq \tau_{\text{buffer}} \leq \tau_n
]

上界由噪声寿命(\tau_n = 0.26)s决定（不应保留超过噪声寿命的数据），下界由帧间重叠要求决定。最终选择(\tau_{\text{buffer}} = 0.2)s（两帧）。

**深度分析：** 这个参数推导是本文的亮点之一。它展示了一个**有理论依据的参数选择过程**，而非简单的经验调参。公式(4)-(6)虽然简单，但逻辑链条清晰：物理约束（噪声寿命）→几何约束（帧间重叠）→参数区间→选择整数倍。Table II进一步用不同速度和噪声寿命的组合验证了选择的鲁棒性。

### 5.3 Global Map Construction（IV.B）

全局地图使用octree（OctoMap），关键技术是**批量插入**：

[
\bar{p}*{ijk} = \frac{1}{|B*{ijk}|} \sum_{p \in B_{ijk}} p
]

将缓冲窗口内的有效点按体素索引排序后批量更新，减少octree遍历和动态节点分配的开销。

**深度分析：** 这一小节相对简短，因为octree/OctoMap是成熟工具。作者的贡献在于**批量插入策略**和**仅融合经过瞬态缓冲验证的点**这一流程设计，而非octree本身的改进。写作上，简洁是正确的——不需要重新解释OctoMap的原理，只需说明如何使用它。

---

## 6. Experimental Evaluation and Results（Section V）解析

### 6.1 实验设置

**关键信息：**

* 3个不同电力线环境，每个环境10次测试（共90次）
* 硬件：Intel i7-11800H + 16GB RAM（非机载计算，但代表了嵌入式性能的上界）
* 对比方法：LIOR（基于强度）、ROR（基于半径），均来自[8]
* 超参数基于噪声分析结果：(r = 1.5)m, (K = 2), 强度阈值10, (r_{\text{octree}} = 1)m, (\tau_{\text{buffer}} = 0.2)s
* 100ms实时性约束（导航模块10Hz）

**深度分析：** 实验设计的两个亮点：

1. **跨环境泛化测试**（3个不同的塔架/电缆布局）——表明方法不是过拟合到单一场景。
2. **统一超参数**——在所有环境中使用相同参数，验证了泛化性。

作者坦诚地说明没有先前工作专门处理电弧噪声（"To the best of our knowledge, no prior research has specifically addressed filtering electric arc noise"），因此选择了最相关的替代方法（LIOR和ROR）进行对比。这种处理方式是合理的——如果确实没有直接竞争方法，选择相关方法并解释选择理由即可。

### 6.2 Resource Consumption（V.A）

Table IV是本节的核心。关键对比（r = 1.5m）：

| 指标       | LIOR    | ROR     | **Ours** |
| -------- | ------- | ------- | -------- |
| 邻域搜索(ms) | N/A     | 460-523 | 20-22    |
| 总迭代(ms)  | 1.1-1.5 | 462-525 | 22-26    |
| 最大迭代(ms) | 5-9     | 622-807 | 65-81    |

**深度分析：**

LIOR最快但后续会证明其滤波无效。关键对比在ROR与本文方法之间：

* **邻域搜索速度提升约20倍**：这直接源于k-d tree在小规模点集上的(O(\log N))优势vs ROR的暴力搜索。
* **最大迭代时间在100ms内**：满足实时性约束。
* **随半径增大的稳定性**：ROR的时间随(r)剧增（从560到707ms），而本文方法相对稳定（从25到75ms）。

Fig. 4（性能时间曲线）的分析也很有价值：作者坦诚地讨论了本文方法偶尔出现的时间尖峰（spike），并将其归因于ROS调度和系统级开销，而非算法本身的不稳定。这种**对自身不足的坦诚解释**增强了可信度。

### 6.3 Mapping Accuracy（V.B）

Table V给出了混淆矩阵，Table VI给出了性能指标。

作者首先解释了为何不使用整体准确率（accuracy）——因为数据极度不平衡（电弧体素仅146 vs 非电弧100万+），accuracy接近100%但无信息量。因此强调**precision、recall和F1**。这个解释体现了作者的统计素养。

r = 1.5m时的关键结果：

| 指标              | LIOR | ROR | **Ours**   |
| --------------- | ---- | --- | ---------- |
| Env.1 Precision | —    | —   | **97.27%** |
| Env.1 F1        | —    | —   | **95.00%** |
| Env.2 F1        | ~0   | ~下降 | **79.01%** |
| Env.3 F1        | ~0   | ~中等 | **83.15%** |

**关键发现的分析：**

* **LIOR完全失效**（recall≈0-1%）：证实了引言中对强度方法不适用电弧噪声的判断。
* **ROR有高recall但低precision**：能找到噪声但误伤太多有效点（false positives多）。
* **本文方法在precision和F1上全面领先**：得益于时间一致性的额外约束减少了false positives。

Fig. 5的可视化结果直观有力：LIOR几乎没有去除任何电弧体素（彩色点仍在），ROR过度去除（连有效结构也受损），本文方法干净地去除了电弧噪声同时保留了环境结构。

**超参数敏感性分析：** 作者对(r, K, \beta, p_{\text{floor}}, \tau_{\text{buffer}}, r_{\text{octree}})六个参数进行了系统性扫描，报告了各参数的推荐范围和物理解释。这种全面的敏感性分析在RA-L论文中不常见（受篇幅限制），但显著增强了方法的实用性和可复现性。

特别值得注意的是对(\beta)的分析——作者给出了具体的数值解释（"points just below (r) are kept with high probability ((p_{\text{keep}} \geq 0.8))"），使得sigmoid函数的行为从抽象公式变为可直觉理解的工程参数。

---

## 7. Conclusion（Section VI）解析

> In this letter, we introduced a dual-structure filtering framework that mitigates electric arc noise in drone-based LiDAR mapping near energized power lines using consecutive-scan neighborhood searches.

`S1` **功能：贡献重述。** 用一句话概括全文核心。

> The method combines k-d tree neighbor queries with octree insertions to process 3D point clouds efficiently.

`S2` **功能：方法摘要。**

> Experiments on custom datasets show that the proposed filter outperforms existing methods.

`S3` **功能：结果摘要。** 注意用词简洁，不再重复具体数字。

> Future work will pursue tighter integrations to further improve mapping performance in large-scale, density-varying environments, addressing challenges for accurate range, depth estimation and reliable feature extraction.

`S4` **功能：未来方向。** 指向密度变化环境和深度估计挑战。这些方向直接源于本文的局限性（固定参数、未处理变密度场景）。

**结论总结：** RA-L的结论通常极简——4句话足够。不重复数字，不引入新信息，仅做高层概括和前瞻。

---

## 8. 全文总结与迁移指导

### 8.1 论文的核心论证逻辑链

```
电弧噪声有独特特性（短暂、稀疏）
    ↓ 现有方法（强度/空间/深度学习）不适用
    ↓ 需要利用时间一致性的新方法
    ↓ 双结构设计：瞬态k-d tree + 持久octree
    ↓ 噪声分析提供参数依据
    ↓ 实验验证：速度20x↑, F1达95%
```

### 8.2 值得学习的写作策略

1. **数据驱动的方法设计**：先量化问题（Section III.B），再基于量化结果设计方法和选择参数。这使得方法设计有物理/统计基础，而非凭空设计。

2. **分类否定法构建Gap**：将相关工作按类别逐一分析其在目标场景下的不足，系统性地排除替代方案。

3. **设计决策的即时论证**：在介绍每个技术选择时（k-d tree、概率保留、缓冲时长），立即解释"为何这样选"，不留疑问给审稿人。

4. **诚实面对局限**：对性能尖峰、数据不平衡、缺乏直接对比方法等问题坦诚讨论并给出合理解释。

5. **多层次验证**：3个环境×10次测试×多参数扫描，从效率和精度两个维度同时验证。

### 8.3 潜在不足

* 实验在离线桌面PC上运行，未在Jetson Xavier NX上实测，对"资源受限平台"的声称缺乏直接证据。
* 仅与LIOR和ROR对比，未与深度学习方法对比（即使后者计算量大，作为upper bound参考仍有价值）。
* 三个环境均来自同一测试站点的315kV线路，地理和电压多样性有限。
