# Snow Removal for LiDAR Point Clouds with Spatio-Temporal Conditional Random Fields

**论文信息：** Wang et al., IEEE Robotics and Automation Letters (RA-L), Vol. 8, No. 10, October 2023

---

## Abstract 解析

### 原文呈现

> LiDAR sensors have been extensively used in numerous applications, including autonomous driving, owing to their ability to generate high-quality 3D point clouds. However, the sensor can be greatly affected in adverse weather conditions, resulting in noisy 3D points that impair LiDAR-based perception performance. This letter proposes a novel de-snowing formulation with Conditional Random Fields (CRF). The proposed approach first constructs the CRF based on k-nearest neighbors with the snow confidence derived from the physical priors of snow, such as intensity and distribution. Then, Iterated Conditional Modes (ICM) is applied for the confidence propagation from points with high certainty to nearby uncertain ones, thereby identifying the latter. Moreover, the method can be extended to fully utilize the temporal information of sequential scans for clearer snow removal. Extensive experiments on the real-scanned WADS dataset validate that our de-snowing approach significantly outperforms baselines and even the learning-based State-of-The-Art (SoTA) one. Furthermore, we demonstrate that our method has the potential to benefit the downstream 3D object detection task in snowy weather.

### 逐句解构与功能标注

| 编号 | 句子                                                         | 功能标注         |
| ---- | ------------------------------------------------------------ | ---------------- |
| S1   | LiDAR sensors have been extensively used in numerous applications, including autonomous driving, owing to their ability to generate high-quality 3D point clouds. | **领域背景建立** |
| S2   | However, the sensor can be greatly affected in adverse weather conditions, resulting in noisy 3D points that impair LiDAR-based perception performance. | **问题动机引出** |
| S3   | This letter proposes a novel de-snowing formulation with Conditional Random Fields (CRF). | **核心贡献声明** |
| S4   | The proposed approach first constructs the CRF based on k-nearest neighbors with the snow confidence derived from the physical priors of snow, such as intensity and distribution. | **方法步骤一**   |
| S5   | Then, Iterated Conditional Modes (ICM) is applied for the confidence propagation from points with high certainty to nearby uncertain ones, thereby identifying the latter. | **方法步骤二**   |
| S6   | Moreover, the method can be extended to fully utilize the temporal information of sequential scans for clearer snow removal. | **方法扩展性**   |
| S7   | Extensive experiments on the real-scanned WADS dataset validate that our de-snowing approach significantly outperforms baselines and even the learning-based State-of-The-Art (SoTA) one. | **实验结果概述** |
| S8   | Furthermore, we demonstrate that our method has the potential to benefit the downstream 3D object detection task in snowy weather. | **应用价值补充** |

### 深度分析

**S1 的角色与策略：** 这是摘要的经典开篇——从宏观技术背景切入。作者选择 "extensively used" 和 "numerous applications" 两个宽泛的修饰词，目的是建立研究的**普适性价值**：LiDAR不是一个冷门传感器，而是被广泛应用的核心技术。随后以 "including autonomous driving" 点出最受关注的应用场景，这是一个**策略性聚焦**——在RA-L这类机器人与自动化领域期刊上，自动驾驶是审稿人最容易产生共鸣的应用方向。"owing to their ability to generate high-quality 3D point clouds" 则简洁交代了LiDAR的核心优势，为后续S2的转折做铺垫。

**S2 的角色与策略：** 关键转折词 "However" 的使用是摘要中最重要的论证节点。S1建立了LiDAR的"优势叙事"，S2立即用对比制造**问题张力**。"greatly affected" 强调影响的严重程度，"resulting in noisy 3D points that impair..." 构成因果链条：恶劣天气 → 噪声点 → 感知性能下降。注意作者选择 "impair" 而非 "degrade" 或 "reduce"，"impair" 在语义上暗示功能性损害，比一般性的性能下降更具紧迫感。S1-S2合在一起构成了经典的 **"优势-威胁"** 叙事框架，为S3的方案提出奠定了必要性基础。

**S3 的角色与策略：** "This letter proposes" 是RA-L期刊（Letters格式）的标准贡献声明句式。"novel" 是必要的但需慎用的形容词——它向审稿人宣告创新性。核心创新点被精准压缩为 "de-snowing formulation with Conditional Random Fields (CRF)"。作者的策略是将CRF这一经典概率图模型与去雪问题进行**跨领域嫁接**，这在摘要中一句话就完成了新颖性的宣示。

**S4-S5 的角色与策略：** 这两句构成方法的**两步流程描述**，使用 "first...Then..." 的时序连接词，使读者能快速把握方法的运作逻辑。S4中 "physical priors of snow, such as intensity and distribution" 是关键——它告诉读者方法不是纯数据驱动的黑箱，而是建立在**物理可解释性**之上的，这在机器人领域是一个重要的加分项。S5中 "confidence propagation from points with high certainty to nearby uncertain ones" 是对ICM在本问题中作用的高度凝练，用直觉性的语言替代了数学细节，使得非CRF专家也能理解核心思想。

**S6 的角色与策略：** "Moreover" 引入附加贡献——时序信息的利用。"can be extended" 的措辞非常讲究：它暗示时序扩展是**自然而然**的，不需要大幅修改框架。这传达了方法的优雅性和可扩展性，同时也暗示空间版本已经是一个完整的贡献，时序版本是锦上添花。

**S7 的角色与策略：** "Extensive experiments" 是标准的实验充分性声明。"real-scanned WADS dataset" 强调了数据集的**真实性**——这一点至关重要，因为很多去雪方法仅在模拟数据上验证。"significantly outperforms" 使用了强程度副词，而 "even the learning-based State-of-The-Art (SoTA) one" 是一个**精心设计的对比点**：一个非学习方法（概率图模型方法）能超越学习方法，这本身就具有很强的话题性和说服力。

**S8 的角色与策略：** "Furthermore" 引入最后的价值升华。"has the potential to benefit the downstream 3D object detection task" 措辞上用了 "potential"，这是学术写作中的**谨慎限定**——作者没有宣称已经全面提升了检测性能，而是展示了一个定性的示例来说明应用前景。这种谦逊而准确的表述是成熟学术写作的标志。

### 结构总结与迁移指导

**整体结构：** 本摘要遵循经典的 **"背景→问题→方法→结果→价值"** 五段式结构，每个环节一到两句话，总共约160词，非常符合RA-L对Letters格式的简洁性要求。

**可迁移原则：**

1. **"优势-威胁"开篇模式**：先肯定技术的广泛价值（S1），再以 "However" 引出在特定场景下的不足（S2），这种叙事张力比直接陈述问题更能吸引读者。
2. **方法描述的两层压缩**：第一层是核心思想的一句话概括（S3），第二层是关键步骤的简洁展开（S4-S5），避免在摘要中陷入技术细节。
3. **比较对象的策略性选择**：S7中特意强调超越"学习方法"，而非仅仅说"优于基线"，因为在当前学术语境下，非学习方法超越学习方法具有更高的话题性。
4. **贡献分层呈现**：主贡献（空间CRF去雪）→ 扩展贡献（时序信息）→ 应用价值（下游检测），层次递进，避免贡献点的平面化罗列。

---

## I. Introduction 解析

Introduction共五段（含贡献列表），我将逐段分析。

### 第一段

#### 原文呈现

> LIGHT Detection And Ranging (LiDAR) sensors can generate accurate 3D point cloud data by reckoning the time of the laser's flight. With the development of manufacturing technology, LiDARs have become much more low-cost and compact and are being extensively utilized for applications such as autonomous driving and robotics [1], [2], [3], [4], [5]. Although they are robust to lighting conditions, undesired noisy points can appear due to the occlusion by small particles like snowflakes in snowy weather [6], [7], [8], [9]. Since most LiDAR-based perception algorithms are trained and tested on clean point cloud data, these noisy points may lead to drastic performance degradation for detection and tracking and consequently cause severe accidents [10], [11], [12], [13]. In this regard, de-snowing algorithms emerge as a crucial preprocessing step to enhance the robustness and reliability of perception.

#### 逐句解构与功能标注

| 编号 | 句子（简述）                                                 | 功能标注                |
| ---- | ------------------------------------------------------------ | ----------------------- |
| S1   | LiDAR sensors can generate accurate 3D point cloud data by reckoning the time of the laser's flight. | **技术原理简介**        |
| S2   | With the development...extensively utilized...autonomous driving and robotics [1]-[5]. | **应用广泛性+文献支撑** |
| S3   | Although they are robust to lighting conditions, undesired noisy points can appear...in snowy weather [6]-[9]. | **核心问题引出**        |
| S4   | Since most LiDAR-based perception algorithms are trained and tested on clean point cloud data...severe accidents [10]-[13]. | **问题严重性论证**      |
| S5   | In this regard, de-snowing algorithms emerge as a crucial preprocessing step... | **研究必要性总结**      |

#### 深度分析

**S1** 以LiDAR的工作原理（飞行时间测距）作为Introduction的起点，这是**面向非专家读者的友好入口**。RA-L的读者涵盖机器人学各子领域，不一定都熟悉LiDAR传感器的细节，因此一句话的原理介绍是必要的。"reckoning the time of the laser's flight" 简洁准确地传达了ToF（Time-of-Flight）原理。

**S2** 的引用策略值得深入分析。[1]-[5] 密集引用了五篇文献，涵盖了：

- **[1] PointPillars** 和 **[2] Part-A²Net**：3D目标检测的代表性方法
- **[3] SalsaNext** 和 **[4] Cylinder3D**：LiDAR语义分割方法
- **[5] LeGO-LOAM**：LiDAR里程计与建图

这不是随意堆砌，而是系统性地展示LiDAR在**检测、分割、建图**三大核心任务中的应用，从而证明LiDAR的广泛重要性。这种**多任务覆盖式引用**是一种高效的背景建立策略。"low-cost and compact" 这一商业化趋势的提及，进一步强调了LiDAR技术的现实紧迫性——它正在大规模部署，因此其在恶劣天气下的脆弱性是一个迫切需要解决的问题。

**S3** 使用 "Although...undesired..." 的让步-转折结构，是本段的关键转折点。"robust to lighting conditions" 先承认LiDAR相对于相机的核心优势（不受光照影响），随即以 "undesired noisy points can appear due to the occlusion by small particles like snowflakes" 指出其在雪天场景下的脆弱性。这种**先肯定再否定**的写法，比直接说"LiDAR在雪天有问题"更有说服力，因为它展示了作者对技术的全面理解。[6]-[9] 四篇文献全部是关于LiDAR在恶劣天气下行为特征的研究：

- **[6] Michaud et al.** 和 **[9] Kutila et al.**：LiDAR在雪天条件下的行为特性分析
- **[7] Jokela et al.**：恶劣天气下点云传感器的测试与验证
- **[8] Bijelic et al.**：雾天条件下的多模态传感器融合

这些引用为"雪花导致噪声点"这一前提提供了**多维度的实证基础**。

**S4** 将问题的严重性从技术层面升级到**安全层面**。"Since most LiDAR-based perception algorithms are trained and tested on clean point cloud data" 揭示了一个系统性假设缺陷——现有算法假设输入是干净的。"drastic performance degradation" 和 "severe accidents" 的措辞将问题的后果推到了最高级别。引用策略上：

- **[10] WeatherNet (Heinzler et al.)**：直接研究恶劣天气下的LiDAR去噪，是核心相关工作
- **[11] Hahner et al.**：LiDAR降雪模拟用于鲁棒3D检测
- **[12] Do & Yoo** 和 **[13] The & Yoo**：恶劣天气下3D检测性能下降的具体案例

这四篇从正反两面支撑了论断——既有研究恶劣天气影响的（[10]-[11]），也有因噪声导致检测失败的具体案例（[12]-[13]）。

**S5** "In this regard" 承接前文所有论证，将去雪算法定位为 "crucial preprocessing step"。注意作者选择 "crucial" 而非 "important"——前者暗示**不可或缺性**，后者仅表示重要性。"enhance the robustness and reliability" 使用了自动驾驶领域两个最核心的评价维度——鲁棒性与可靠性，精准对接审稿人的价值评判标准。

#### 结构总结与迁移指导

本段遵循 **"原理→应用→问题→严重性→必要性"** 的经典漏斗型叙事。

**可迁移原则：**

1. **引用集群的功能分化**：S2的引用证明"广泛应用"，S3的引用证明"天气影响存在"，S4的引用证明"影响后果严重"，每组引用服务于不同的论证目标。不要在同一个论证点上堆砌所有引用。
2. **安全性论证**是自动驾驶领域最有效的"必要性武器"——将技术问题上升到事故风险，可以有效回应"为什么要做这个"的审稿疑问。但需注意适度使用，避免过度渲染。
3. **让步-转折结构**（Although A, B）比直接否定更学术化，因为它展示了作者对技术全貌的把握。

---

### 第二段

#### 原文呈现

> As illustrated in Fig. 1(a) and (c), snow points tend to distribute and cluster around the LiDAR sensor, indicating the possibility of snow removal with spatial prior. Previous work tried to remove snow points by utilizing spatial features such as statistical analysis of neighboring points [14], [15], [16], [17]. However, they encounter limitations in addressing the challenge of removing snow points while preserving non-snow points due to the varying spatial density of snow points. On the other hand, we can observe that the intensity value of snow points tends to be low as shown in Fig. 1(b), while there exist many non-snow points with low intensity. Therefore, it is imperative to formulate a more effective aggregation of spatial density and intensity of snow points, especially for features of neighboring points.

#### 逐句解构与功能标注

| 编号 | 句子                                                         | 功能标注                      |
| ---- | ------------------------------------------------------------ | ----------------------------- |
| S1   | As illustrated in Fig. 1(a) and (c), snow points tend to distribute and cluster around the LiDAR sensor... | **视觉证据引入+空间先验观察** |
| S2   | Previous work tried to remove snow points by utilizing spatial features...[14]-[17]. | **已有方法概述**              |
| S3   | However, they encounter limitations...due to the varying spatial density of snow points. | **已有方法局限性**            |
| S4   | On the other hand, we can observe that the intensity value of snow points tends to be low...while there exist many non-snow points with low intensity. | **第二特征引入+其局限性**     |
| S5   | Therefore, it is imperative to formulate a more effective aggregation of spatial density and intensity... | **研究空白声明**              |

#### 深度分析

**S1** 在Introduction的第二段就引用了Fig. 1，这是一个**非常积极的图文联动策略**。在RA-L这种Letters格式中，空间有限，尽早让读者通过视觉直观理解问题是高效的。"tend to distribute and cluster around the LiDAR sensor" 是从图中提炼的观察性结论，随即推导出 "indicating the possibility of snow removal with spatial prior"——从观察到推断，一句话完成了**空间先验的合理性论证**。这里的Fig. 1是一个四格对比图（原始点云、强度着色、雪点GT、去雪结果），在Introduction中引用(a)和(c)来建立空间分布观察，引用(b)来建立强度观察（在S4中），是对同一张图的**分步利用**策略。

**S2-S3** 构成经典的 **"已有方法→其不足"** 论证对。引用分析：

- **[14] PCL (Rusu & Cousins)**：提供SOR和ROR滤波器的点云库——基础工具性引用
- **[15] DROR (Charron et al.)**：动态半径异常值移除——空间方法的改进代表
- **[16] DSOR (Kurup & Bos)**：可扩展的统计滤波器——空间方法的另一改进
- **[17] Qu et al.**：基于改进马氏距离的方法——最新的空间方法

这四篇按照方法的演进顺序排列（基础→改进→最新），展示了**空间方法的发展轨迹**。S3的 "However" 指出核心困境："removing snow points while preserving non-snow points"，这个**二元对立的trade-off表述**贯穿全文，是本文试图解决的核心矛盾。"varying spatial density" 是具体的失败原因——当雪点密集时，空间特征无法区分雪点和真实物体点。

**S4** 用 "On the other hand" 引入第二个特征维度——强度（intensity）。写法上的精妙之处在于**先给出正面观察再给出反面限制**："the intensity value of snow points tends to be low"（正面：雪点强度低）→ "while there exist many non-snow points with low intensity"（反面：非雪点也有低强度的）。这种**先肯定后否定**的结构，既展示了强度特征的价值，又说明了单独使用它的不足，为融合方案提供了逻辑必要性。

**S5** 用 "Therefore" 收束前文所有论证，得出研究空白的结论。"imperative" 一词传达了**紧迫性**——这不仅仅是一个"可以做"的方向，而是一个"必须做"的方向。"aggregation of spatial density and intensity" 暗示了本文方法的核心思路——特征融合。"especially for features of neighboring points" 则进一步暗示了邻域信息的重要性，为CRF图模型的引入埋下伏笔。

#### 结构总结与迁移指导

本段的论证结构是 **"观察→已有方案A（空间特征）→A的不足→线索B（强度特征）→B的不足→需要A+B的融合"**，这是一种**双线索汇聚**的写法。

**可迁移原则：**

1. **尽早使用图表**：在Introduction中引用图表来建立直觉性理解，比纯文字描述更高效。
2. **构建trade-off矛盾**：明确指出已有方法面临的核心权衡（如精度vs召回），为自己的方法创造解决空间。
3. **双线索不足论证**：分别展示两个方向的价值和局限，然后自然引出融合方案的必要性。

---

### 第三段

#### 原文呈现

> Recently, learning-based approaches are also proposed for snow removal [18], [19], [20]. Point clouds are usually projected into 2D panoramic images to be applicable with CNNs, resulting in the loss of 3D spatial information. Besides, these methods usually rely on large amounts of time-consuming annotated data for supervision. To ease the demands for annotation, some methods introduce the snowfall simulation technology for LiDAR point cloud data [11]. Nevertheless, the domain gap between simulated and real snow-affected data degrades the generalization when applied to real scenes. Among them, LiSnowNet [18] leverages CNNs to achieve the denoise in an unsupervised manner.

#### 逐句解构与功能标注

| 编号 | 句子                                                         | 功能标注                   |
| ---- | ------------------------------------------------------------ | -------------------------- |
| S1   | Recently, learning-based approaches are also proposed for snow removal [18]-[20]. | **学习方法引入**           |
| S2   | Point clouds are usually projected into 2D panoramic images...resulting in the loss of 3D spatial information. | **局限一：信息损失**       |
| S3   | Besides, these methods usually rely on large amounts of time-consuming annotated data for supervision. | **局限二：标注依赖**       |
| S4   | To ease the demands for annotation...snowfall simulation technology...[11]. | **对局限二的已有补救方案** |
| S5   | Nevertheless, the domain gap between simulated and real snow-affected data degrades the generalization... | **补救方案的再否定**       |
| S6   | Among them, LiSnowNet [18] leverages CNNs to achieve the denoise in an unsupervised manner. | **最强基线的特别介绍**     |

#### 深度分析

**S1** 以 "Recently" 开头，标志着从规则方法到学习方法的讨论转换。引用三篇核心学习方法：

- **[18] LiSnowNet (Yu et al.)**：无监督CNN去雪，当时的SoTA
- **[19] SLiDE (Bae et al.)**：自监督LiDAR去雪
- **[20] 4DenoiseNet (Seppanen et al.)**：利用时序信息的去噪网络

这三篇代表了学习方法的不同监督范式（无监督、自监督、监督），展示了作者对该方向的全面掌握。

**S2-S5** 构成了对学习方法系统性的 **"提出→批评→补救→再批评"** 论证链，这是本段最精巧的论证结构：

- **S2**：2D投影导致3D信息丢失——**结构性缺陷**。这直接指向了CNN-based方法的技术瓶颈。
- **S3**：标注数据需求——**实践性缺陷**。"time-consuming" 强调标注的成本。
- **S4**：引入模拟数据[11]作为解决方案——**展示学界的尝试**。这一句很关键，它不是直接否定学习方法，而是承认学界正在努力解决标注问题，展示了**学术公正性**。
- **S5**："Nevertheless" 指出域间差距（domain gap）——这是**对补救方案的再否定**。论证链因此闭合：即使用模拟数据来缓解标注问题，也会引入新的泛化问题。

这种**四层递进式批评**比简单的"学习方法有局限"更具说服力，因为它展示了作者对该领域的深度理解——不仅知道问题，还知道已有的补救尝试以及为什么它们也不够。

**S6** 单独提及LiSnowNet [18]是一个重要的**策略性选择**。在S2-S5的批评框架中，LiSnowNet作为无监督方法，避开了S3（标注依赖）和S4-S5（模拟数据域间差距）的批评。因此它是**最难被上述框架否定的基线**。作者在Introduction中特别提及它，是为后续实验中超越它做铺垫——先让读者认识到这是一个强对手，后面超越它时的说服力才更强。这是一种**"先立后破"的延迟论证策略**。

#### 结构总结与迁移指导

**可迁移原则：**

1. **层层剥洋葱式批评**：不要一句话否定对手方法，而是展示你了解它们的问题、学界的补救尝试、以及补救为何仍然不够。这建立了比"简单否定"更强的学术信誉。
2. **识别并特别介绍最强基线**：在Introduction中提前点名最难超越的对手，为实验部分的对比创造期待感。
3. **批评的公正性**：即使在否定对手方法时，也要承认其合理之处（如S4承认模拟数据方案的出发点），这种学术公正性会赢得审稿人的好感。

---

### 第四段

#### 原文呈现

> In contrast to previous rule-based approaches that directly assign a binary label to each point, we propose to involve probabilities to each point and formulate the problem as a belief propagation task using Conditional Random Fields (CRF) [21]. Our approach, named CRF-based Outlier Removal (CRFOR), is a de-snowing method that effectively leverages the spatial and physical features of neighboring points and can be easily extended to incorporate temporal information across sequential scans. CRFOR estimates the confidence of the initial label for each point based on priors such as that snow points usually possess relatively low intensity, low density, and high irregularity of distribution and the opposite for non-snow ones. Then, the CRF-based graph probability model is constructed to propagate belief from points with high certainty to uncertain points. Iterated Conditional Modes (ICM) [22] is utilized for the optimization and inference of labels for uncertain points.

#### 逐句解构与功能标注

| 编号 | 句子                                                         | 功能标注               |
| ---- | ------------------------------------------------------------ | ---------------------- |
| S1   | In contrast to previous rule-based approaches...we propose to involve probabilities...CRF [21]. | **方法论转变声明**     |
| S2   | Our approach, named CRFOR...effectively leverages...can be easily extended... | **方法命名与核心优势** |
| S3   | CRFOR estimates the confidence of the initial label...based on priors... | **步骤一：初始化**     |
| S4   | Then, the CRF-based graph probability model is constructed to propagate belief... | **步骤二：信念传播**   |
| S5   | Iterated Conditional Modes (ICM) [22] is utilized for the optimization... | **步骤三：优化**       |

#### 深度分析

**S1** 是本文最重要的**范式转换声明**。"In contrast to" 不是简单的 "different from"，它暗示一种**根本性的方法论对立**：以往方法直接赋予二值标签（硬判决），本文引入概率（软判决）。这种从 deterministic 到 probabilistic 的转变，在方法论层面就构成了创新。

**[21] Lafferty, McCallum & Pereira (2001)** 是CRF的奠基论文，此处引用是对方法理论根源的**溯源式引用**。在机器人领域引用机器学习的经典工作，传达了作者的**跨学科视野**，同时也为方法的理论基础提供了权威背书。

**S2** 完成了方法的**品牌化**——命名为CRFOR（CRF-based Outlier Removal）。好的方法命名在学术传播中至关重要：CRFOR简洁、含义明确、易于记忆和引用。"effectively leverages" 和 "can be easily extended" 分别回应了审稿人关注的两个核心维度：**有效性**（方法管用吗？）和**扩展性**（方法的适用范围有多广？）。

**S3-S4-S5** 以 "estimates...constructed...utilized" 的时序动词串联了方法的三步流程：初始化 → 图构建与信念传播 → 优化推断。S3中的 "priors such as that snow points usually possess relatively low intensity, low density, and high irregularity" 将三个物理先验一次性列出，与第二段中分散讨论的空间密度和强度特征进行了**整合呼应**，并增加了第三个特征（分布不规则性），使方法的信息基础更加丰富。

**[22] Besag (1986)** 是ICM的原始论文，同样是**溯源式引用**。ICM是一种简单快速的近似推断方法（逐点迭代更新），作者选择它而非更复杂的变分推断或MCMC采样，暗示了方法对**计算效率**的关注——这在自动驾驶的实时性要求下是一个重要的设计考量。

#### 结构总结与迁移指导

本段是整个Introduction的**核心枢纽**——将前面铺垫的问题和空白，与提出的解决方案进行对接。

**可迁移原则：**

1. **第一句明确方法论对立**：用 "In contrast to" 这样的强对比连接词，建立与已有方法的本质区别，而非细节差异。
2. **方法命名在本段完成**：命名紧跟核心思想的提出，便于后续一致性引用。
3. **溯源式引用建立权威**：对于方法中使用的核心工具（CRF、ICM），引用其原始论文而非应用论文，展示理论功底。
4. **方法描述的"三步法"**：初始化→核心计算→优化推断，是一种清晰的流程化叙事，审稿人容易跟随。

---

### 第五段（贡献列表）

#### 原文呈现

> In summary, our contributions are as follows:
>
> - We propose a novel de-snowing method CRFOR by formulating the point cloud snow removal problem with a Conditional Random Field model to take full advantage of the spatial and physical feature and temporal information across sequential scans.
> - We implement both the spatial and spatial-temporal versions of CRFOR and introduce ICM to perform belief propagation from points with high certainty to nearby uncertain points.
> - We conduct comprehensive experiments and ablation studies on real-scanned snowy scenes and demonstrate the effectiveness and superiority of the proposed method. Furthermore, we provide a qualitative example of LiDAR-based 3D detection, leveraging our snow removal method to highlight its potential in enhancing downstream detection tasks.

#### 深度分析

贡献列表的组织遵循经典的**三层结构**：

**C1（方法层贡献）：** 提出CRFOR框架，强调CRF建模的新颖性。"take full advantage of the spatial and physical feature and temporal information" 将空间特征、物理特征、时序信息三者并列，呼应了前文的多维度讨论。

**C2（技术层贡献）：** 空间和时空两个版本的实现+ICM优化。这一条将C1具体化，回答了"怎么做到的"。注意 "spatial and spatial-temporal versions" 的表述——先有空间版本，再扩展到时空版本，暗示了方法的**渐进式设计哲学**。

**C3（实验层贡献）：** 在真实数据上的验证+消融实验+下游应用展示。"comprehensive experiments and ablation studies" 是向审稿人传达实验充分性的信号。"real-scanned snowy scenes" 再次强调真实数据——与Introduction第三段中对模拟数据域间差距的批评形成**逻辑闭环**。

**关键观察：** C1和C2存在一定重叠——都提到了CRF和时空信息。在更理想的写法中，C1应聚焦于**"问题建模的创新"**（将去雪问题建模为CRF信念传播），C2应聚焦于**"技术实现的创新"**（ICM优化、时序扩展），两者之间有更清晰的边界。但在RA-L的Letters格式中，略有重叠是可接受的，因为篇幅限制使得每个贡献点需要一定的自包含性。

#### 结构总结与迁移指导

**可迁移原则：**

1. **贡献的三层结构**：方法层（新问题建模/新框架）→ 技术层（具体算法/实现创新）→ 实验层（验证方式/应用展示），这是一种安全且清晰的组织方式。
2. **贡献间的正交性**：尽量使每个贡献点覆盖不同的维度，减少重叠。
3. **实验贡献中强调真实数据**：在自动驾驶领域，真实数据上的验证比模拟数据更有说服力，值得在贡献中明确标注。

---

## II. Related Works 解析

### A. Snow Removal on Images

#### 原文呈现

> Hand-crafted feature-based and learning-based algorithms are the two main categories of image snow removal algorithms. The former usually utilizes image color information such as saturation and visibility [23]. Auxiliary guidance image [24] or multi-guided filters [25] are also leveraged to extract the snow from the background. For the learning-based approaches, Desnownet [26] is the first to use CNN for de-snowing as we know it. [27] proposes to perform snow removal by image inpainting and veiling effect recovery. These methods exploit unique features of images, e.g. dark channels and bright channels, making it difficult to apply them to snow removal for LiDAR point clouds.

#### 逐句解构与功能标注

| 编号 | 句子                                                         | 功能标注             |
| ---- | ------------------------------------------------------------ | -------------------- |
| S1   | Hand-crafted feature-based and learning-based algorithms are the two main categories... | **分类框架建立**     |
| S2   | The former usually utilizes image color information such as saturation and visibility [23]. | **手工特征方法概述** |
| S3   | Auxiliary guidance image [24] or multi-guided filters [25] are also leveraged... | **手工方法补充**     |
| S4   | For the learning-based approaches, Desnownet [26] is the first to use CNN for de-snowing... | **学习方法开创者**   |
| S5   | [27] proposes to perform snow removal by image inpainting and veiling effect recovery. | **学习方法补充**     |
| S6   | These methods exploit unique features of images...making it difficult to apply them to snow removal for LiDAR point clouds. | **不可迁移性声明**   |

#### 深度分析

这一小节的战略目的不是全面综述图像去雪方法，而是**划清边界**——向审稿人解释为什么图像去雪的已有工作不能直接用于LiDAR点云去雪。

**S1** 建立了"手工特征 vs 学习"的**二分分类框架**，这是Related Work中常见的组织策略。

**S2-S3** 和 **S4-S5** 分别在两个类别中各引用2-3篇代表性工作：

- **[23] Pei et al.**：利用饱和度和可见性——图像特有的颜色空间特征
- **[24] Xu et al.**：辅助引导图像——基于图像的先验知识
- **[25] Zheng et al.**：多引导滤波器——图像处理的经典工具
- **[26] DesnowNet (Liu et al.)**：CNN去雪的开创性工作
- **[27] JSTASR (Chen et al.)**：图像修复+遮蔽效应恢复

每篇引用都刻意强调了**图像特有的技术特征**（颜色信息、引导图像、暗通道/亮通道），为S6的结论做铺垫。

**S6** 是本小节的**核心论证目标**："These methods exploit unique features of images, e.g. dark channels and bright channels, making it difficult to apply them to snow removal for LiDAR point clouds." 这一句明确了图像方法的**不可迁移性**，从而论证了LiDAR点云去雪需要独立的研究路线。"e.g. dark channels and bright channels" 是点睛之笔——暗通道和亮通道是图像去雪/去雾中最著名的先验，提及它们强化了"这些方法本质上依赖图像特性"的论点。

#### 结构总结与迁移指导

**可迁移原则：**

1. **Related Work中的"非相关领域"小节**：当你的研究问题在另一个模态（如图像）上有大量已有工作时，专门用一小段来解释为什么那些方法不能直接迁移，是**防御性写作**的重要策略——预防审稿人问"为什么不直接用图像去雪的方法"。
2. **简洁即策略**：注意这一小节非常短（约120词），因为详细综述图像去雪方法对本文没有直接帮助。在RA-L的Letters格式中，每一段都需要为核心论证服务。

---

### B. Snow Removal on Point Clouds

#### 原文呈现——规则方法部分

> **Rule-based methods:** Statistical Outlier Removal (SOR) and Radius Outlier Removal (ROR) implemented in the Point Cloud Library (PCL) [14] are representative denoising algorithms which leverage statistical spatial distribution of snow points. The SOR filter performs two iterations. In the first iteration, it searches the k-nearest neighbors (kNN) for each point and computes the mean distances to determine a threshold. Afterwards, it classifies a point as an outlier if the mean distance of the point to its neighbors is greater than the threshold. The ROR filter searches neighbors for each point with a fixed radius and classifies a point as noise if the number of its neighbors is below a given threshold. The SOR and ROR filters are both designed based on local spatial sparsity. In most cases, their performance suffers great degradation processing the points located at long distances, for these points are naturally sparse.

> Dynamic Radius Outlier Removal (DROR) [15] filter is then proposed to address the limitations above by adaptively scaling the search radius in proportion to the distance. However, it often fails to filter out lots of snow points under severe adverse weather conditions such as heavy snowfall, where snow points are densely distributed. Dynamic Statistical Outlier Removal [16] filter uses a similar technique to modify the SOR filter. Removing more snow points though, it also removes more non-snow points by mistake.

> Unlike the filters above, Low-Intensity Outlier Removal (LIOR) [28] filter first exploits the feature of snow points that they have lower intensity. The LIOR filter takes two steps, selecting candidate points with relatively low intensity, and classifying them to be inliers or outliers by spatial density. Dynamic Number of Neighbor Outlier Removal (DNNOR) [29] filter focuses on snow points and non-snow points having similar low intensity. [30] additionally introduces the temporal feature of snow points. Other methods [31], [32], [33] use the dimension reduction technique. These algorithms attempt to preprocess point clouds to accelerate and improve accuracy, but the spatial feature still plays a decisive role. When the density of snow particles increases in extremely adverse weather such as blizzards, they misclassify some densely distributed snow points.

#### 深度分析

这部分的组织逻辑非常清晰，按照**方法演进的历史线**排列，每一组方法都以 **"提出→优点→不足"** 的结构呈现：

**第一组：基础空间方法（SOR/ROR [14]）**

- 作者用大量篇幅详细描述了SOR和ROR的工作原理，这不仅仅是综述，更是为后续自己方法的设计做**技术铺垫**——CRFOR也使用了kNN搜索，理解SOR/ROR有助于读者理解CRFOR的改进之处。
- 核心局限："their performance suffers great degradation processing the points located at long distances, for these points are naturally sparse" ——远距离点天然稀疏，导致基于稀疏性的滤波器失效。

**第二组：动态空间方法（DROR [15], DSOR [16]）**

- DROR通过自适应搜索半径解决了远距离问题（"adaptively scaling the search radius in proportion to the distance"），但在大雪条件下仍然失败——因为雪点本身变得密集。
- DSOR去除了更多雪点，但也误删了更多非雪点。这再次呼应了Introduction中的**precision-recall trade-off**核心矛盾。

**第三组：融合强度的方法（LIOR [28], DNNOR [29], [30]）**

- LIOR首次利用强度特征——这是方法演进的重要里程碑。
- DNNOR关注雪点和非雪点强度相似的情况——即LIOR的失败场景。
- [30] (Li et al.) 引入时序特征——与本文的CRFOR-t形成对比。
- **关键句**："the spatial feature still plays a decisive role" 是作者对整个规则方法谱系的**总结性判断**——空间特征仍然是主导，其他特征是辅助的。

**最后的局限总结**："When the density of snow particles increases in extremely adverse weather such as blizzards, they misclassify some densely distributed snow points" 将所有规则方法的共同失败模式归结为一个原因——**高密度雪点场景**。这为CRFOR通过邻域信念传播来处理这种场景提供了直接的动机。

#### 原文呈现——学习方法部分

> **Learning-based methods:** Existing learning-based methods mostly project point clouds onto depth images or intensity images, and apply 2D deep learning methods to them. A famous one is WeatherNet [10]. It tackles the problem as a supervised point-wise multi-class classification task based on depth images using CNN. The requirement of point-wise labels for training is one of its drawbacks. SLiDE [19] is a self-supervised learning framework, which works on range images as well. It consists of PR-Net and RD-Net to reconstruct points from neighbors and predict reconstruction difficulty, respectively. If a point is difficult to be reconstructed, then it is classified as a snow point. 4DenoiseNet [20] considers trajectories of points in the temporal dimension. While these networks have great performance, their training costs and generalization remain an issue. The state-of-the-art LiSnowNet [18] also represents point clouds using range images with distance channels and intensity channels. It leverages deep convolutional neural networks and image processing tools such as Fast Fourier Transform (FFT) and the Discrete Wavelet Transform (DWT) to achieve denoising in an unsupervised manner.

#### 深度分析

**学习方法的综述策略**与规则方法不同——这里更侧重于**每种方法的特色与局限**，而非方法细节。

引用分析按出现顺序：

- **WeatherNet [10]**：监督学习代表，局限是需要逐点标注
- **SLiDE [19]**：自监督代表，通过重建难度判断雪点——巧妙但仍基于2D表示
- **4DenoiseNet [20]**：引入时序信息——与本文的时序扩展形成对比
- **LiSnowNet [18]**：无监督SoTA，使用FFT和DWT——作为**最后介绍**的方法，占据了"最强对手"的叙事位置

**关键句**："While these networks have great performance, their training costs and generalization remain an issue" 是一个**有条件的肯定**——承认学习方法性能不错，但指出训练成本和泛化性的持续问题。这种措辞比无条件否定更学术化，因为它承认了对手的价值。

LiSnowNet被放在最后且详细描述，是**策略性安排**——作为SoTA方法，它是本文需要超越的主要目标。最后介绍它，使其在读者记忆中最为鲜明，为实验部分的对比做好铺垫。

#### 结构总结与迁移指导

**可迁移原则：**

1. **按历史线组织规则方法**：展示方法的演进轨迹（基础→改进→进一步改进），揭示每一步改进解决了什么问题又引入了什么新问题。
2. **对最强基线给予最多笔墨**：详细描述你需要超越的SoTA方法，既展示你的了解深度，也为超越它建立更高的可信度。
3. **批评学习方法时保持公正**："While these networks have great performance" 这类有条件肯定，比全面否定更能赢得审稿人信任。

---

## III. Method 解析

### A. Overview

#### 原文呈现

> The framework of the proposed CRFOR is illustrated in Fig. 2. For a frame of the point cloud, it first computes the density and irregularity as spatial features and takes intensity as the physical feature. Based on the combination of these features, each point can be initially labeled as snow, non-snow or uncertain. From the upper-left part of Fig. 2, it can be found that blue uncertain points are distributed irregularly, making it challenging to determine the label by simply tuning thresholds or parameters for feature combinations. For instance, snow points may be too dense to be properly classified from spatial features alone, while non-snow points reflected from tree leaves may be too sparse to be correctly identified as non-snow. We consider this as the main reason causing the trade-off between removing snow points and preserving non-snow ones for existing approaches.

> To address this challenge, the CRFOR framework takes advantage of the observation that snow points tend to be distributed near other snow points, and so do non-snow points. Therefore, a graph is constructed for the point cloud using the kNN algorithm and the CRF [21] probabilistic graph model is introduced to further propagate the belief of classified points and discriminate the uncertain ones, as shown in the right of Fig. 2. Moreover, since the graph is constructed based on the spatial distance between points, CRFOR can be easily extended to take advantage of temporal information from sequential point cloud frames as demonstrated in the lower part of Fig. 2.

#### 深度分析

Overview段的功能是为读者提供方法的**鸟瞰图**，在进入技术细节之前建立全局理解。

**第一段的策略：** 以Fig. 2作为视觉锚点，描述了方法的输入处理和初始化阶段。最重要的论证在中间：作者通过两个具体例子——"snow points may be too dense" 和 "non-snow points reflected from tree leaves may be too sparse"——生动地展示了为什么简单的阈值方法不够。"tree leaves" 这个具体场景的引入非常精妙——它给读者一个**直觉性的反例**，比抽象的"varying density"更有说服力。"We consider this as the main reason causing the trade-off" 是一个**显式的因果归因**，将前文反复提及的precision-recall trade-off的根本原因锁定在"不确定点的处理"上。

**第二段的策略：** "To address this challenge" 承接第一段的问题，引出解决方案。核心观察是 "snow points tend to be distributed near other snow points, and so do non-snow points"——这是**空间聚类假设**，也是CRF图模型的合理性基础。这个假设虽然直观，但作者将其**显式表达**是非常重要的，因为它构成了后续所有方法设计的理论前提。

#### 结构总结与迁移指导

**可迁移原则：**

1. **Method的Overview段应做到"一段文字+一张总图"**：让读者在深入细节之前对方法有全局理解。
2. **用具体场景例子解释抽象问题**：如"树叶反射点"比"varying density"更有说服力。
3. **显式声明方法的核心假设**：如"雪点倾向于分布在其他雪点附近"，这使方法的合理性可被审稿人评估和讨论。

---

### B. Features for Label Initialization

#### 原文呈现

> Our approach initializes the labels by incorporating three observable factors that can be used as clues to distinguish snow and non-snow points: density, irregularity and intensity. The local spatial density of a point is determined by calculating the mean distance to its k nearest neighboring points. It indicates the point's proximity to other points and is typically higher for non-snow points than for snow ones [15]. The second factor, irregularity, is defined as the minimum explained variance ratio derived from Principal Component Analysis (PCA) on the point and its neighbors. A small minimum variance ratio indicates that the points fit well into a plane or even a line, making the point more likely to be a non-snow point. Finally, the intensity factor is related to the reflectivity of the point and has been found to be lower for snow points in previous studies [28], [29], [30].
>
> Therefore, a joint feature \(\mathcal{F}\) for each point is as follows.
>
> \[\mathcal{F} = \left(\frac{1}{\mathcal{I} + a}\right) * (\mathcal{D} + b) * (\mathcal{R} + c) \tag{1}\]
>
> where \(\mathcal{I}\), \(\mathcal{D}\), and \(\mathcal{R}\) denote intensity, mean distance, and minimum variance ratio correspondingly. Three constants \(a\), \(b\), and \(c\) are added to control the influence of the three factors. In each frame, after calculating \(\mathcal{F}\) for each point, we constrain all the \(\mathcal{F}\) to \([-1, 1]\) with linear normalization.

#### 深度分析

**三因子的选择逻辑：** 作者选择的三个特征（密度、不规则性、强度）分别从**空间分布**、**几何结构**和**物理反射特性**三个维度刻画雪点特征。这种多维度设计确保了对单一特征失败场景的鲁棒性。

每个特征的引用都有精确的功能：

- **密度**引用[15] DROR——DROR正是基于空间密度的方法，引用它是对密度特征有效性的**间接佐证**。
- **强度**引用[28] LIOR, [29] DNNOR, [30] Li et al.——这三篇都研究了雪点的低强度特性，是**多源佐证**。
- **不规则性**没有引用——这是作者的**原创设计**。用PCA最小方差比来衡量几何不规则性，是一个巧妙的特征工程选择。

**公式(1)的设计逻辑：** \(\mathcal{F} = \frac{1}{\mathcal{I}+a} \cdot (\mathcal{D}+b) \cdot (\mathcal{R}+c)\) 的设计意图是：

- **强度取倒数**：强度越低（雪点特征），\(\frac{1}{\mathcal{I}+a}\) 越大，\(\mathcal{F}\) 越大
- **密度（平均距离）直接使用**：距离越大（雪点特征——周围更稀疏），\(\mathcal{D}+b\) 越大
- **不规则性直接使用**：方差比越大（雪点特征——分布不规则），\(\mathcal{R}+c\) 越大

因此，\(\mathcal{F}\) 越大越可能是雪点，越小越可能是非雪点。三个常数 \(a, b, c\) 的作用是**避免除零和平衡各因子权重**。乘法组合（而非加法）的选择意味着如果任何一个因子接近零，整体 \(\mathcal{F}\) 也会很小——这实现了**任一特征的"一票否决"效应**。

线性归一化到 \([-1,1]\) 是为后续CRF的信念传播做准备——正值表示雪点置信度，负值表示非雪点置信度，接近零表示不确定。

#### 结构总结与迁移指导

**可迁移原则：**

1. **特征设计需要物理解释**：每个特征的选择都应有来自领域知识的理由，并用引用佐证。不规则性特征虽然没有引用（原创），但通过PCA的几何直觉进行了充分解释。
2. **公式设计需要直觉解释**：不仅要给出公式，还要解释为什么选择乘法而非加法、为什么取倒数等设计选择的背后逻辑。
3. **归一化是桥梁**：将特征映射到有意义的范围（如\([-1,1]\)对应置信度），为后续算法模块提供干净的接口。

---

### C. Point Cloud as Conditional Random Field

#### 原文呈现

> CRF was first proposed in [21] to build probabilistic models for segmenting and labeling sequence data without strong assumptions made such in hidden Markov models. Given an observation data sequence \(\mathbf{X}\), CRF model a distribution over the corresponding label sequence \(\mathbf{Y}\) with an undirected graphical model. Namely, the conditional distribution \(P(\mathbf{Y}|\mathbf{X})\) is modeled with CRF. Formally, let \(G = (V, E)\) be an undirected graph such that node \(v \in V\) corresponds to the element \(\mathbf{Y}_v\) of \(\mathbf{Y}\). Then \((\mathbf{Y}, \mathbf{X})\) is a CRF conditioned on the observation \(\mathbf{X}\), if each element \(\mathbf{Y}_v\) obeys the Markov property with respect to \(G\): \(P(\mathbf{Y}_v|\mathbf{X}, \mathbf{Y}_u, u \neq v) = P(\mathbf{Y}_v|\mathbf{X}, \mathbf{Y}_u, u \sim v)\), where \(u \sim v\) represents that node \(u\) is connected to \(v\) in the graph \(G\), as defined in [21].
>
> To be applicable with CRF, we treat the point cloud as a graph constructed with kNN and model the data as shown in Fig. 3. \(\mathbf{X}\) indicates the observable information of point cloud, \(\mathbf{Y}^t\) indicates the labels of points and \(\mathbf{Y}^{t-1}\) optionally indicates the labels of spatial-temporal neighbor points. Thus, the probability of the label sequence \(\mathbf{Y}\) conditioned on observation data \(\mathbf{X}\) can be defined with the following form:
> \[P(\mathbf{Y}|\mathbf{X}) = \frac{1}{Z} \exp\left(\sum_{e \in E}\sum_j \lambda_j f_j(e, \mathbf{Y}|_e, \mathbf{X}) + \sum_{v \in V}\sum_k \mu_k g_k(v, \mathbf{Y}|_v, \mathbf{X})\right) \tag{2}\]

#### 深度分析

本小节的写法采用了经典的 **"理论基础介绍→本文实例化"** 两段式结构。

**第一段（CRF理论基础）：** 作者简洁地介绍了CRF的核心概念——无向图模型、马尔可夫性质、条件分布建模。引用[21]再次出现，强化了理论溯源。"without strong assumptions made such in hidden Markov models" 这一表述点出了CRF相对于HMM的核心优势——不需要观测独立性假设。这对本文很重要，因为点云中的观测（3D坐标、强度等）之间确实存在复杂的依赖关系。

**第二段（本文实例化）：** 将点云用kNN构建图结构，使CRF的抽象框架得以**具象化**。Fig. 3的图模型表示（红色观测节点、黑色当前帧标签节点、蓝色历史帧标签节点）清晰地展示了空间和时序依赖关系。公式(2)是CRF的一般形式，包含：

- **转移特征函数** \(f_j\)：捕捉边上相邻标签之间的关系
- **状态特征函数** \(g_k\)：捕捉节点标签与观测的关系
- \(\lambda_j, \mu_k\)：CRF参数

这一公式的展示是为后续Section III-D中的具体实例化（去雪任务的\(f\)和\(g\)定义）做铺垫。

#### 结构总结与迁移指导

**可迁移原则：**

1. **"理论→实例化"两段式**：先介绍通用理论框架，再说明如何将其应用到具体问题。这种结构既尊重了理论来源，又展示了本文的应用创新。
2. **图模型图示**：当使用概率图模型时，一张清晰的图模型示意图（如Fig. 3）比大段文字更有效。
3. **公式从一般到特殊**：先给出CRF的一般形式(2)，再在后续小节中给出本问题的特化形式，这种渐进式展开有助于读者理解。

---

### D. Instantiation for Snow Removal

#### 原文呈现

> Since the snow removal task can be considered as a binary classification problem that distinguishes between snow and non-snow points, we empirically set parameters \(\lambda\) and \(\mu\) to 1. We construct a graph where an edge exists between nodes \(\mathbf{Y}_p\) and \(\mathbf{Y}_q\) only if point \(p\) is one of the k-nearest neighbors of point \(q\). For the label sequence \(\mathbf{Y}\), each label \(\mathbf{Y}_v\) is assumed to condition on its corresponding observation data \(\mathbf{X}_v\), rather than the entire observation sequence \(\mathbf{X}\). Consequently, (2) can be rewritten as
> \[P(\mathbf{Y}|\mathbf{X}) = \frac{1}{Z}\exp\left(\sum_{i=1}^{n}f(y_i, \mathcal{N}(i)) + \sum_{i=1}^{n}g(y_i, x_i)\right) \tag{3}\]

> The design of functions \(f\) and \(g\) decides how points are classified. To define \(f(y_i, \mathcal{N}(i))\), labels \(y_j\) of k-nearest neighbors of point \(i\) and distances \(d_{ij}\) from point \(i\) to these points are utilized. We use the joint feature \(\mathcal{F}\) to define \(g(y_i, x_i)\).
> \[f(y_i, \mathcal{N}(i)) = y_i * \sum_j \frac{y_j}{d_{ij}}, \quad j \in \mathcal{N}(i) \tag{6}\]
> \[g(y_i, x_i) = y_i * \mathcal{F}_i \tag{7}\]
>
> Consequently, we finally derive the expression of \(P(y_i|x_i)\) by substituting (6) and (7) into (5):
> \[P(y_i|x_i) = \exp\left(y_i * \left(\sum_j \frac{y_j}{d_{ij}} + \mathcal{F}_i\right)\right), \quad j \in \mathcal{N}(i) \tag{8}\]

#### 深度分析

本小节是方法的**核心技术贡献**，将通用CRF框架特化为去雪任务的具体形式。

**简化策略：** 将 \(\lambda = \mu = 1\) 是一个重要的简化选择。"empirically set" 表明这不是理论推导的结果，而是基于实验的务实选择。对于二分类问题，一个转移函数和一个状态函数就足够了，因此参数设为1是合理的简化。

**公式(6)的设计逻辑：** \(f(y_i, \mathcal{N}(i)) = y_i \cdot \sum_j \frac{y_j}{d_{ij}}\) 的直觉是：

- 如果点 \(i\) 的邻居大多是雪点（\(y_j = 1\)），且 \(y_i = 1\)，则 \(f\) 为正值（概率增大）
- 如果点 \(i\) 的邻居大多是非雪点（\(y_j = -1\)），且 \(y_i = -1\)，则 \(f\) 也为正值
- 距离 \(d_{ij}\) 在分母中起到**距离加权**的作用——越近的邻居影响越大

这实现了**"同类相聚"**的物理直觉——如果你的邻居大多是某一类，你也更可能是该类。

**公式(7)的设计逻辑：** \(g(y_i, x_i) = y_i \cdot \mathcal{F}_i\) 更为简洁——它利用联合特征 \(\mathcal{F}\) 的正负号与 \(y_i\) 的一致性来增大概率。如果 \(\mathcal{F}_i > 0\)（偏向雪点），且 \(y_i = 1\)（标签为雪），则 \(g\) 为正值。

**公式(8)的统一表达：** 最终的概率表达式将邻域信息（\(\sum_j \frac{y_j}{d_{ij}}\)）和自身特征（\(\mathcal{F}_i\)）统一在一个exp中。括号内的项可以理解为一个**"综合投票得分"**：自身特征的投票加上邻居的加权投票。最大化这个概率等价于让标签 \(y_i\) 的符号与综合投票得分的符号一致。

#### 结构总结与迁移指导

**可迁移原则：**

1. **从一般到特殊的公式推导链**：公式(2)→(3)→(6)(7)→(8)，每一步简化都有明确的理由（二分类、局部马尔可夫性、具体的\(f\)和\(g\)定义）。这种渐进式推导帮助读者跟随论证。
2. **为公式提供直觉解释**：不仅要给出数学形式，还要解释"这个公式在做什么"的物理直觉（如"同类相聚"）。
3. **简化选择需要声明**：\(\lambda = \mu = 1\) 的设置用 "empirically set" 声明了简化的经验性质，避免读者误以为有理论证明。

---

### E. Optimization

#### 原文呈现

> For the snow removal task, the initial labels \(\mathbf{Y}^0\) are first estimated based on the calculated feature \(\mathcal{F}_i\) as defined in (1). For each point \(i\), its label is determined by comparing with pre-defined thresholds:
> \[y_i^0 = \begin{cases} 1 & \mathcal{F}_i \geq \text{snow\_th} \\ -1 & \mathcal{F}_i \leq \text{non\_snow\_th} \\ \mathcal{F}_i & \text{otherwise} \end{cases} \tag{9}\]
>
> After the initialization, we need to determine the optimal labels for uncertain points by maximizing the probability of (4). However, directly determining the label sequence \(\mathbf{Y}\) that maximizes \(P(\mathbf{Y}|\mathbf{X})\) can be challenging. While methods such as Variational Inference [34] and Gibbs Sampling [35] are proposed, they are usually computationally demanding. An alternative approach is Iterated Conditional Modes (ICM), which was proposed in [22].

> ICM is a simple and effective method that iteratively updates each label \(y_i\) of data \(i\) based on all available information, to maximize \(P(y_i|x_i)\).
> \[y_i^{k+1} = \sum_j \frac{y_j^k}{d_{ij}} + y_i^k, \quad j \in \mathcal{N}(i) \tag{11}\]

#### 深度分析

**公式(9)的三分策略：** 初始化将点分为三类：确定雪点、确定非雪点、不确定点。这种三分法是CRFOR区别于以往二值判决方法的**核心设计创新**。不确定点保留其原始 \(\mathcal{F}\) 值（连续值），这为后续的信念传播保留了**信息量**——不是简单地赋予0，而是保留了偏向某一类的程度信息。

**优化方法的选择论证：** 作者列举了变分推断[34]和Gibbs采样[35]两种替代方案，指出它们 "usually computationally demanding"，然后选择ICM。这是一种**排除法论证**——通过否定替代方案来论证自己选择的合理性。

- **[34] Jordan et al.**：变分推断的经典综述
- **[35] Casella & George**：Gibbs采样的经典教程

引用两篇经典教程性文献而非具体应用论文，展示了作者对推断方法谱系的**系统性理解**。

**公式(11)的迭代更新：** 每次迭代中，不确定点的标签值被更新为自身值加上邻居标签的距离加权和。这个过程可以理解为**"邻域投票的逐步扩散"**——确定点的标签通过邻接关系逐步影响不确定点，就像热传导一样。迭代次数是一个超参数，控制传播的范围和程度。

#### 结构总结与迁移指导

**可迁移原则：**

1. **三分初始化策略**：在不确定性较高的场景中，不要强制二值化，而是保留不确定类别，后续通过更精细的机制处理。
2. **排除法论证优化选择**：先列举可能的替代方案，指出其缺点，再提出自己的选择。这比直接使用ICM而不解释"为什么不用其他方法"更有说服力。
3. **Algorithm伪代码的重要性**：Algorithm 1将整个流程用伪代码完整展示，这是可复现性的关键保障，也是RA-L审稿人重视的点。

---

### F. Exploit Temporal Information

#### 原文呈现

> Moreover, our approach can be readily extended to leverage temporal information, which we name CRFOR-t. When performing snow removal from the point cloud frame at time \(t\), the outcomes of the preceding frames are usually available. Accordingly, when inspecting point \(i\) at the location \((x_i, y_i, z_i)\) of frame \(t\), we can temporally expand the search range of k-nearest neighbors \(\mathcal{N}(i)\) to previous \(m\) frames.
> \[f(y_i, \mathcal{N}(i)) \rightarrow f(y_i, \mathcal{N}_j(i), j \in [t-m, t]) \tag{12}\]

#### 深度分析

时序扩展的核心思想极其简洁：将kNN搜索的范围从当前帧扩展到前 \(m\) 帧。"can be readily extended" 和 "while other procedures keep unchanged" 强调了扩展的**零成本性**——不需要修改任何其他组件，只需要扩大邻域搜索的数据范围。

这种简洁性本身就是一个**方法论优势**：它表明CRF框架具有足够的灵活性来自然地容纳时序信息。与4DenoiseNet [20]需要专门设计时序轨迹特征相比，CRFOR-t的时序扩展几乎是"免费"的。

**"applicable if the LiDAR is deployed on the top of a moving vehicle"** 这一条件说明暗示了一个实际约束：时序扩展依赖于运动带来的视角变化。如果车辆静止，前后帧的信息高度重叠，时序扩展的增益有限。

#### 结构总结与迁移指导

**可迁移原则：**

1. **方法扩展应展示"优雅性"**：如果一个扩展只需要修改一个公式/组件，而其他部分保持不变，这本身就是方法设计良好的证据。
2. **明确扩展的适用条件**：如"LiDAR部署在移动车辆上"，避免读者对方法的适用性产生误解。

---

## IV. Experiments 解析

### A. Datasets, Baselines and Implementation Details

#### 原文呈现

> While many snow removal methods are evaluated on simulated snowy scenes, it is crucial to assess their effectiveness in practical scenarios. To achieve this, we conduct experiments on the real-scanned WADS [16] dataset. WADS provides approximately 1.9 k frames of sequential LiDAR point clouds with point-wise annotation collected in severe snowy weather. There are 22 classes of labels including "active falling snow", which is utilized for evaluation. In experiments, points labeled as "active falling snow" are marked as snow, while others are marked as non-snow.

> In our experiments, we take DROR [15], LIOR [28], DDIOR [36], LiSnowNet [18] and 4DenoiseNet [20] as comparison baselines. Both DROR and LIOR are rule-based representative methods and have been widely adopted, while 4DenoiseNet and LiSnowNet are the latest learning-based SoTA methods... We retrain the LiSnowNet and 4DenoiseNet on the WADS dataset with their official implementation for a fair comparison.

#### 深度分析

**数据集选择的论证：** 开篇 "While many snow removal methods are evaluated on simulated snowy scenes, it is crucial to assess their effectiveness in practical scenarios" 直接呼应了Introduction中对模拟数据域间差距的批评。选择WADS这一真实数据集，使本文在**实验设计层面**与其方法论批评保持一致——这是学术写作中**言行一致**的重要体现。

**基线选择的策略：** 5个基线覆盖了：

- 规则方法：DROR [15]（空间密度）、LIOR [28]（强度+空间）、DDIOR [36]（动态空间）
- 学习方法：LiSnowNet [18]（无监督SoTA）、4DenoiseNet [20]（监督+时序）

这种**双阵营覆盖**确保了对比的全面性。特别重要的是 "We retrain the LiSnowNet and 4DenoiseNet on the WADS dataset with their official implementation for a fair comparison"——使用官方代码在相同数据上重训练，是**公平比较的金标准**做法。

**参数公开：** Table I列出了所有方法的参数设置，包括作者自己实现的方法。这种**透明度**是可复现性的重要保障，也向审稿人传达了学术诚信。

---

### B. Quantitative Results

#### 原文呈现

> To compare the performance of snow removal methods, we utilize precision, recall, F1-score, and runtime as quantitative metrics...
>
> DROR achieves high performance in terms of precision, indicating most identified snow points are correct. However, its recall performance is relatively low, suggesting the limitation to filter out all snow points. In contrast, DDIOR and 4DenoiseNet show the opposite trend. LIOR exhibits intermediate performance on both metrics. Although an unsupervised method, LiSnowNet achieves the best performance in F1-Score among the baselines. The trade-off between precision and recall reflects the challenge of removing snow points while preserving non-snow ones. In this regard, our CRFOR achieves a better balance and significantly outperforms all rule-based methods on F1-Score. Notably, the temporal variant CRFOR-t demonstrates more remarkable performance gains...

#### 深度分析

结果讨论的组织采用了 **"逐方法分析→总结趋势→本文方法定位"** 的三步法。

**基线分析的策略：** 作者不是简单地罗列数字，而是为每个基线提炼出**特征性的行为模式**：

- DROR：高精度低召回（保守策略）
- DDIOR/4DenoiseNet：高召回低精度（激进策略）
- LIOR：中间水平
- LiSnowNet：基线中最佳F1

这种**行为模式分析**比单纯的数值对比更有洞察力，因为它揭示了每种方法的**内在倾向**。

**核心论证句：** "The trade-off between precision and recall reflects the challenge of removing snow points while preserving non-snow ones" 将实验观察与Introduction中提出的核心矛盾进行了**显式连接**——这种前后呼应增强了论文的逻辑一致性。

"Notably" 引出CRFOR-t的优异表现，"demonstrates more remarkable performance gains" 中的 "remarkable" 比 "significant" 更具情感色彩，但在Letters格式中是可接受的。

#### 结构总结与迁移指导

**可迁移原则：**

1. **为每个基线提炼行为模式**：不要只报告数字，要解释数字背后的方法特性。
2. **将实验结果与Introduction的核心矛盾对接**：展示你的方法确实解决了开篇提出的问题。
3. **分层呈现结果**：先分析基线的行为→再展示本文方法如何打破trade-off→最后用时序变体展示额外增益。

---

### C. Qualitative Results

#### 原文呈现（关键句）

> We present the snow removal results obtained by different methods in Fig. 4 for the qualitative comparison... Points are colored red, green or blue indicating false non-snow, true snow and false snow, respectively. The method that achieves better snow removal performance should have more green points and fewer red and blue points... In contrast, our proposed CRFOR and CRFOR-t are capable of accurately identifying more snow points while also preserving non-snow ones, leading to the best snow removal performance. However, they still tend to mis-preserve sparse snow points and mis-filter low-density non-snow points as Fig. 4 indicates.

#### 深度分析

**颜色编码策略：** 红色（漏检雪点FN）、绿色（正确检出TP）、蓝色（误检FP）的三色编码使读者能快速评估方法的表现。"more green points and fewer red and blue points" 给出了**直观的视觉评判标准**。

**最后一句的诚实性：** "However, they still tend to mis-preserve sparse snow points and mis-filter low-density non-snow points" 是一个**自我批评**。这种诚实在学术写作中非常重要——它展示了作者对方法局限性的**清醒认识**，也为未来工作指明了方向。审稿人通常对能够坦诚讨论局限性的论文更加信任。

---

### D. Ablation Study

#### 原文呈现（关键发现）

> From the table, it can be found that the ablation of CRF leads to a significant performance drop, showing the effectiveness of the proposed strategy. Besides, we can find that intensity shows high significance for noise classification. Interestingly, the ablation of either density or irregularity only leads to a slight performance drop, while the ablation of both two features leads to a significant drop.

#### 深度分析

消融实验的组织遵循 **"关键组件→各特征→特征交互"** 的层次：

1. **CRF消融**（最重要）：F1从0.955降至0.894，证明CRF信念传播的核心价值
2. **单特征消融**：强度影响最大（F1降至0.871），密度和不规则性单独消融影响较小
3. **双特征消融**（密度+不规则性同时去除）：F1显著下降至0.894

**"Interestingly"** 一词的使用标志着一个值得注意的发现——密度和不规则性各自的消融影响不大，但同时去除时影响显著。这暗示了两者之间的**互补性**——它们单独看冗余度较高，但组合使用时提供了额外信息。这种非线性交互效应的发现增强了三特征组合设计的合理性。

**运行时间分析**也被纳入消融实验："the computation of irregularity \(\mathcal{R}\) takes approximately two-thirds of the time" 指出了PCA计算的主要计算瓶颈，并建议 "may be further accelerated with parallel computation"——这既是局限性的坦诚声明，也是未来优化的方向指引。

---

### E. Snow Removal for Object Detection

#### 深度分析

这一小节提供了CRFOR用于下游任务（3D目标检测）的**概念验证**。使用预训练的SECOND模型[38]和OpenPCDet工具箱[37]，展示了去雪前后检测结果的对比。

**策略性的谨慎措辞：** "qualitatively show" 而非 "quantitatively demonstrate"——作者没有进行全面的检测性能定量评估，而是选择了**定性展示**。这种谦逊的表述与Abstract中的 "has the potential to benefit" 保持一致。

**最后的免责声明：** "snow removal may fail to improve detection performance for reasons such as misdetection caused by the limitation of the detection model rather than the corruption of the point cloud" 是一个重要的**因果限定**——去雪不能解决所有检测问题，检测模型本身的局限性也是一个因素。这种区分显示了作者的学术严谨性。

---

## V. Conclusion 解析

### 原文呈现

> We present CRFOR, a novel de-snowing method for LiDAR point clouds based on CRF. Our key innovation is to formulate the snow removal problem as a CRF and leverage the neighboring points with high confidence to propagate the belief. This approach allows the label of a point to be determined not only by its initial spatial and physical features but also by its neighboring points' features, which is greatly different from existing methods. Additionally, the method can be easily extended to spatio-temporal variant CRFOR-t to incorporate temporal information. The comprehensive experiments on real-scanned snowy scenes validate the superiority of our proposed method even compared with SoTA learning-based method for snow removal. Furthermore, we demonstrate the potential of the proposed method to benefit the downstream 3D object detection task in snow weather.

### 深度分析

Conclusion的写法遵循了 **"核心贡献→创新本质→区别于已有方法→扩展性→实验验证→应用价值"** 的递进结构。

**关键句：** "This approach allows the label of a point to be determined not only by its initial spatial and physical features but also by its neighboring points' features, which is greatly different from existing methods." 这是全文最凝练的**核心差异化声明**——以往方法只看自身特征，CRFOR还利用邻域特征。"greatly different" 的措辞在Conclusion中是合适的——它总结了全文论证的核心结论。

**值得注意的是**，Conclusion没有包含**Future Work**部分。在RA-L的Letters格式中，这是可以接受的，因为篇幅有限。但如果是完整的期刊论文（如T-RO或IJRR），通常期望有一段关于未来研究方向的讨论，比如：如何处理消融实验中发现的PCA计算瓶颈、如何扩展到其他恶劣天气条件（如雨天、雾天）、如何进行全面的下游检测性能定量评估等。

### 结构总结与迁移指导

**可迁移原则：**

1. **Conclusion应重申核心差异化，而非重复摘要**：注意Conclusion的侧重点与Abstract不同——Abstract侧重流程描述，Conclusion侧重创新本质的提炼。
2. **与已有方法的对比在Conclusion中应更加鲜明**："greatly different from existing methods" 是比Introduction中更直接的差异化声明。
3. **Letters格式的Conclusion可以省略Future Work**，但应确保限制性讨论已在实验部分完成。

---

## 全文论证结构总图

本文的整体论证结构可以用以下逻辑链概括：

```
LiDAR广泛应用 → 雪天噪声问题严重 → 已有空间方法有trade-off →
已有学习方法有泛化/标注问题 → 需要融合空间+物理特征的新方法 →
CRF建模（从硬判决到软判决的范式转换）→
三特征初始化 + CRF信念传播 + ICM优化 →
自然扩展到时序版本 → 真实数据上显著超越所有基线包括SoTA学习方法 →
下游检测应用的初步验证
```

每一环节都与下一环节有明确的因果或递进关系，构成了一条**完整且自洽的论证链**。这是一篇在方法创新性、实验充分性和写作质量上都达到了RA-L标准的论文。

[11]: 