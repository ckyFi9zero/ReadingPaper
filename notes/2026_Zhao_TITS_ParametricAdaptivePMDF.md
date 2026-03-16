# A Parametric-Adaptive Filter for Improving LiDAR Performance Under Snowfall Conditions

**论文信息**: Zhao, Sun, Sun, IEEE Transactions on Intelligent Transportation Systems, February 2026

---

## Abstract 解析

### 原文呈现

> LiDAR is widely used in autonomous driving and intelligent roadside perception systems due to its high detection accuracy and light independence. However, snowfall has a significant impact on LiDAR, increasing noise and changing object resolution in point clouds, posing a significant challenge to the task of traffic object detection using LiDAR. This paper proposes a probabilistic model-driven adaptive filter for effectively removing snowfall noise from LiDAR point clouds and improving LiDAR detection capabilities under snowfall conditions. First, the proposed filter extracts snow noise from a point cloud, creates a spatial distribution model for the snow noise, and obtains the model's key parameters. Then, the snow noise is extracted using a density filter based on the spatial model, which is iteratively optimized. Compared to existing methods, the filter is more scene-adaptable and less dependent on priori datasets, and it can effectively remove snow noise from various types of LiDAR sensors under varying snowfall intensities. Experimental evaluation on publicly available datasets, including CADC, BOREAS, and WADS, demonstrates that the proposed method achieves an F1-Score of more than 90 on all three datasets, indicating excellent accuracy and generalizability. Additionally, testing object detection algorithms under snowfall conditions reveal that the proposed filter improves the accuracy of three typical detection algorithms by 5.9, 9.7, and 6.4 percentage points, indicating that our filter improves the performance of downstream 3D target detection tasks under snowfall.

### 逐句解构与功能标注

| 编号 | 原文 | 功能标注 |
|------|------|--------|
| S1 | LiDAR is widely used in autonomous driving and intelligent roadside perception systems due to its high detection accuracy and light independence. | **背景铺垫**：确立研究对象的重要性与广泛应用 |
| S2 | However, snowfall has a significant impact on LiDAR, increasing noise and changing object resolution in point clouds, posing a significant challenge to the task of traffic object detection using LiDAR. | **问题陈述**：用转折词引出核心挑战 |
| S3 | This paper proposes a probabilistic model-driven adaptive filter for effectively removing snowfall noise from LiDAR point clouds and improving LiDAR detection capabilities under snowfall conditions. | **方法宣言**：一句话概括本文贡献的核心方法 |
| S4 | First, the proposed filter extracts snow noise from a point cloud, creates a spatial distribution model for the snow noise, and obtains the model's key parameters. | **方法步骤1**：粗去噪+建模阶段 |
| S5 | Then, the snow noise is extracted using a density filter based on the spatial model, which is iteratively optimized. | **方法步骤2**：基于模型的精去噪+迭代优化 |
| S6 | Compared to existing methods, the filter is more scene-adaptable and less dependent on priori datasets, and it can effectively remove snow noise from various types of LiDAR sensors under varying snowfall intensities. | **优势声明**：相对于现有方法的核心差异化 |
| S7 | Experimental evaluation on publicly available datasets, including CADC, BOREAS, and WADS, demonstrates that the proposed method achieves an F1-Score of more than 90 on all three datasets, indicating excellent accuracy and generalizability. | **结果呈现1**：滤波精度的量化证据 |
| S8 | Additionally, testing object detection algorithms under snowfall conditions reveal that the proposed filter improves the accuracy of three typical detection algorithms by 5.9, 9.7, and 6.4 percentage points, indicating that our filter improves the performance of downstream 3D target detection tasks under snowfall. | **结果呈现2**：下游任务的量化收益 |

### 深度分析

**S1 — 背景锚定的策略选择**

作者开篇选择了一个极为经典的"重要性声明"句式。注意作者特别提到了两个应用场景："autonomous driving"和"intelligent roadside perception systems"——这不仅仅是为了全面，而是有意扩大受众面。T-ITS（IEEE Transactions on Intelligent Transportation Systems）的读者群涵盖车端和路端两大社区，作者此举是在向两个社区同时宣告研究的相关性。同时，"high detection accuracy"和"light independence"是LiDAR相较于相机的两个公认核心优势，作者在此使用它们，不是在介绍新知识，而是在与读者建立共识基础（common ground），为后续的转折蓄力。

**S2 — "However"转折的论证力学**

"However"是摘要中最重要的逻辑枢纽之一。S1建立了"LiDAR很重要"的认知，S2立刻用转折将其打破：这么重要的传感器，在降雪条件下存在严重问题。作者在此精确描述了降雪的两个影响维度——"increasing noise"和"changing object resolution"。这是有学术考量的：前者对应点云层面的噪声问题（本文主攻方向），后者对应目标特征退化问题（延伸影响）。"posing a significant challenge"这一短语将问题的严重性进一步升级，服务于论证逻辑：问题越严重，解决它的价值越大。

**S3 — 方法宣言的信息密度控制**

这是整个摘要的核心命题句。作者用一句话完成了三个信息传递：(1) 方法的性质——"probabilistic model-driven"（概率模型驱动）；(2) 方法的类型——"adaptive filter"（自适应滤波器）；(3) 方法的目标——"removing snowfall noise"和"improving detection capabilities"。值得注意的是，"probabilistic model-driven"这个修饰语极其关键，它将本文方法与现有的启发式滤波器（heuristic filters）和深度学习方法同时区分开来——启发式方法缺乏概率模型支撑，深度学习方法缺乏可解释的概率驱动机制。这个定语实际上是整篇文章的学术定位标签。

**S4-S5 — 方法描述的"先后"逻辑链**

作者使用"First...Then..."的时序结构来描述方法流程。这在摘要中是标准做法，但此处的选择特别有效：S4对应粗去噪和参数估计阶段，S5对应精去噪和迭代优化阶段。"iteratively optimized"是一个关键短语——它暗示了该方法具有自我改进能力，这直接回应了S6中即将提到的"scene-adaptable"优势。也就是说，S4-S5不仅在描述方法步骤，还在为S6的优势声明提供技术依据。

**S6 — 差异化声明的攻防双面性**

S6是一个精心构建的"比较优势"句。"more scene-adaptable"攻击了现有启发式方法场景适应性差的痛点；"less dependent on priori datasets"攻击了深度学习方法数据依赖性强的痛点；"various types of LiDAR sensors under varying snowfall intensities"则覆盖了两个关键变量维度：传感器类型和降雪强度。这句话的攻防逻辑是：在审稿人可能质疑的所有维度上提前给出答案。一位经验丰富的审稿人在读到S3时，脑海中会自然浮现"和现有方法比有什么优势？"——S6精确回应了这个预期。

**S7-S8 — 结果的双层量化架构**

作者选择用两个独立的结果句来覆盖两个评价层面：S7针对滤波任务本身的精度（F1-Score > 90），S8针对下游目标检测任务的收益（AP提升5.9/9.7/6.4个百分点）。这是一个非常成熟的论证策略：仅展示滤波精度可能会被审稿人质疑"滤波好了，但对实际感知有帮助吗？"；而仅展示目标检测提升又可能被质疑"提升到底来自滤波还是其他因素？"。两层结果同时呈现，构成了完整的因果链：好的滤波 → 好的下游性能。此外，三个数据集（CADC, BOREAS, WADS）的选择保证了泛化性声明的可信度——它们使用不同的LiDAR型号、来自不同地理区域。

### 结构总结与迁移指导

**摘要的整体论证结构**可归纳为：

**背景重要性(S1) → 问题严重性(S2) → 方法概述(S3) → 方法流程(S4-S5) → 比较优势(S6) → 量化结果(S7-S8)**

这遵循了经典的"CaRS + Method + Results"摘要范式（Create a Research Space + 方法概述 + 核心结果）。

**可迁移的核心原则：**

1. **受众意识**：摘要首句的应用场景选择应与目标期刊的读者群对齐，不要写对目标社区无关的场景。
2. **转折蓄力**：背景铺垫越充分，"However"后的问题就越显得有解决的价值。S1和S2是一对协同体。
3. **方法命名即定位**：方法的核心修饰语（如"probabilistic model-driven"）应同时能将自己与多个竞争路线区分开来。
4. **优势声明要预判审稿人质疑**：思考审稿人读到方法后最可能提出的疑问，在摘要中提前给出回应。
5. **结果双层呈现**：对于"工具型"研究（如滤波器、预处理方法），同时展示方法本身的评估指标和下游任务的收益指标，是建立完整说服力的标准做法。

---

## I. Introduction 解析

Introduction较长，按段落逐段分析。

### 第一段

#### 原文呈现

> LiDAR is a critical perception sensor for autonomous vehicles that can capture 3D point cloud data of their surroundings in real time by scanning the scene. This data is required for extracting important information such as the 3D shape, position, and classification of objects in the scene. LiDAR is a key component of autonomous driving, used for tasks such as obstacle detection, tracking, and the generation of high-precision maps [1], [2], [3]. To meet the growing demand for LiDAR in autonomous driving, LiDAR is becoming increasingly miniaturized, high resolution, and low-cost. However, LiDAR still faces challenges in perception tasks, particularly under adverse weather conditions such as snowfall [4], [5], [6].

#### 逐句解构与功能标注

| 编号 | 功能标注 |
|------|--------|
| S1 | **领域入口**：定义研究对象（LiDAR）及其核心能力 |
| S2 | **价值延伸**：说明点云数据的实际用途 |
| S3 | **权威佐证**：通过引用[1][2][3]确认LiDAR在自动驾驶中的关键地位 |
| S4 | **趋势铺垫**：描述LiDAR的发展趋势，暗示其重要性持续增长 |
| S5 | **问题引入**：转折引出核心挑战——恶劣天气下的感知退化 |

#### 深度分析

**S1-S2** 构成了一个从"传感器能力"到"数据价值"的两步推导。S1说LiDAR能采集3D点云，S2说这些点云能提取形状、位置、分类等信息。这种从传感器到信息的递进，是在向读者展示完整的价值链，而非仅仅描述硬件。

**S3** 中的引用 **[1][2][3]** 分别对应LiDAR在三个核心任务中的应用——检测[1]、压缩[2]、路侧检测[3]。这三篇引用的选择不是随意的：它们覆盖了车端感知（检测）、数据处理（压缩）和基础设施端（路侧）三个维度，与摘要S1中提到的"autonomous driving"和"intelligent roadside perception systems"两大场景相呼应。这是一种通过引用来"证明广泛性"的策略。

**S4** 看似是一句"行业趋势"的陈述，实际论证功能是**提升研究紧迫性**：LiDAR正在变得越来越普及（miniaturized, high resolution, low-cost），这意味着解决其在降雪下的问题变得更加紧迫——更多的LiDAR部署意味着更多系统会遭遇降雪干扰。

**S5** 中的引用 **[4][5][6]** 是关于恶劣天气对LiDAR影响的综述或调查性文献。作者在此用综述类引用而非具体实验论文，是因为此处的论证目的是"建立共识"——恶劣天气是一个被广泛认可的挑战，综述文献的引用能力恰好最适合此目的。"particularly under adverse weather conditions such as snowfall"中的"particularly"和"such as"是在从一般问题（恶劣天气）逐步聚焦到具体问题（降雪），完成了Introduction从宽到窄的经典漏斗结构的第一次收缩。

---

### 第二段

#### 原文呈现

> Previous studies have found significant differences between the spatial density of snow points and ordinary LiDAR point clouds. Based on this finding, researchers investigated density-based filtering methods, such as Dynamic Radius Outlier Removal (DROR) [9] and Dynamic Statistical Outlier Removal (DSOR) filters [10]. While these filters generally perform well in terms of snow-noise recall, there are challenges in choosing the appropriate filtering parameters (e.g., filter radius and number of search points). These parameters are often difficult to adapt to the distributional properties of the noisy point cloud, resulting in a trade-off between high recall and precision. Many existing density-based filters assume that snow points are uniformly or linearly distributed, thus using fixed or linearly transformed density thresholds [7], [8], [9], [10]. However, recent findings suggest that snow point distributions may follow a normal distribution [11], [12], [13], a more complex pattern that may result in reduced accuracy of filters based on fixed density thresholds [14]. This complexity increases the likelihood of misclassifying important objects or environmental structure points as noise, thereby reducing filter accuracy. Moreover, the parameters of existing density-based filters are typically optimized by analyzing a large amount of historical data to determine the optimal filtering parameters [8], [9], [10]. However, because these parameters are optimized for a specific dataset, they are difficult to adapt to different scenes, resulting in the algorithms' poor generalization ability.

#### 逐句解构与功能标注

| 编号 | 功能标注 |
|------|--------|
| S1 | **知识基础**：陈述已有发现（雪点与普通点云的密度差异）|
| S2 | **方法回顾**：引出基于密度的滤波方法及代表性工作[9][10] |
| S3 | **局限性1引入**：承认现有方法的优点后，转向参数选择困难 |
| S4 | **局限性1深化**：参数难以适应噪声分布特性 |
| S5 | **根因分析1**：指出假设层面的问题——均匀/线性分布假设 |
| S6 | **反证**：引用新发现[11][12][13]表明雪点分布更复杂（正态分布） |
| S7 | **后果推导**：分布假设错误导致误分类风险 |
| S8 | **局限性2引入**：参数依赖大量历史数据优化 |
| S9 | **局限性2深化**：数据集特异性导致泛化能力差 |

#### 深度分析

这一段是整篇Introduction中论证密度最高的段落之一，其核心任务是**系统性地瓦解现有密度滤波方法的可信度**，为本文方法创造学术空间。

**S1-S2** 首先承认现有工作的贡献——密度差异是一个有效的观察，DROR[9]和DSOR[10]是基于此观察的代表性方法。这种"先扬后抑"的结构在学术写作中至关重要：如果直接批评而不先承认前人贡献，会显得不尊重同行，也会降低论证的可信度。

**引用[9] DROR 和 [10] DSOR** 在此被选为密度滤波方法的代表，因为它们是该子领域引用量最高、认知度最广的两个基线方法。选择它们作为靶标，保证了后续批评的影响力——攻击最强的对手才能彰显自己方法的价值。

**S3-S4** 构成第一层批评：**参数选择困难**。作者使用了"trade-off between high recall and precision"这一表述，这在信息检索和机器学习社区是一个被广泛理解的概念，读者能立即领会问题的严重性。

**S5** 是关键的**根因分析句**。作者指出现有方法的底层假设是"snow points are uniformly or linearly distributed"，然后通过引用 **[7][8][9][10]** 四篇文献来证明这个假设在现有方法中是普遍的。注意这四篇引用的排列：[7]PCL库（最基础的工具）、[8]DROR的原始论文、[9]DSOR、[10]DDIOR——从基础工具到具体算法，覆盖面很广。这种"批量引用"策略的目的是表明：这不是某一个方法的问题，而是**整个方法族**的系统性缺陷。

**S6** 是一个精彩的论证转折。"recent findings suggest"引出了新的科学证据 **[11][12][13]**，表明雪点分布实际上遵循正态分布——比均匀/线性分布更复杂。这三篇引用为作者的批评提供了**实证支持**：不是作者主观认为假设有问题，而是有科学证据表明假设不成立。**[14]** 则被引用来强调固定密度阈值在面对更复杂分布时精度下降的后果。

**S8-S9** 构成第二层批评：**参数对数据集的依赖性**。引用 **[8][9][10]** 再次出现，但此处的引用目的不同于S5——在S5中它们被引用来说明"假设错误"，在S8中它们被引用来说明"参数优化流程有缺陷"。同一组文献在同一段落中被从两个不同角度引用，这是一种高效的引用复用策略。

整段的论证结构可归纳为：

**承认前人贡献 → 批评点1（参数选择难）→ 根因揭示（分布假设错误）→ 新证据支持批评 → 批评点2（数据依赖性强）→ 泛化能力差**

---

### 第三段

#### 原文呈现

> In addition to heuristic algorithms, some recent studies have also attempted to develop deep learning methods to solve the snow noise filtering problem [15], [16], [17], [18], [19]. However, due to the lack of a large number of different labeled datasets under snowfall conditions, the performance of these deep learning models is limited, and they cannot be effectively generalized to different environments. Therefore, over-reliance on prior data is a common issue that limits the filtering accuracy and generalization performance of current heuristic and deep learning algorithms.

#### 逐句解构与功能标注

| 编号 | 功能标注 |
|------|--------|
| S1 | **第二条路线引入**：从启发式方法过渡到深度学习方法 |
| S2 | **深度学习路线的局限性**：数据稀缺导致泛化受限 |
| S3 | **统一性总结**：将启发式和深度学习的共同弱点归结为一个问题 |

#### 深度分析

这一段非常短但论证功能极为关键——它完成了对**第二条竞争路线**（深度学习方法）的批评，并用 **S3** 将两条路线的弱点**统一为一个共同问题**：过度依赖先验数据。

**S1** 中的引用 **[15]-[19]** 覆盖了当时已有的主要深度学习降雪去噪方法：WeatherNet[15]、LiLaNet框架[16]、4DenoiseNet[17]、LiDAR降雪模拟方法[18]、LiSnowNet[19]。作者一次性列出五篇，目的是表明自己对该领域的了解是全面的，同时也说明"即使有这么多尝试，问题仍未被解决"。

**S3** 是整个Introduction前半部分最重要的**枢纽句**。"over-reliance on prior data"是作者提炼出的**统一性研究空白**——不论是启发式方法需要大量实验调参，还是深度学习方法需要大量标注数据，本质上都是"依赖先验数据"的问题。这个统一性总结的学术功能是：为本文方法（不依赖先验数据的概率模型驱动方法）创造了一个清晰的、唯一的研究空白。

这是一种非常高级的Introduction写作技巧：**将多个竞争方法的不同缺陷归纳为同一个根本问题**，然后用自己的方法一次性解决这个根本问题。

---

### 第四段

#### 原文呈现

> To address the above challenges, this study proposes a probabilistic model-driven snow noise filter (PMDF) that can automatically adapt to various snowfall scenarios without relying on prior information. The core idea of the PMDF is to develop a model of the spatial distribution of snow noise through theoretical studies and data analysis. Based on this model, a parametric adaptive filter is designed to filter out snow-containing noise from the point cloud, significantly reducing dependence on priori data. Additionally, the proposed PMDF uses a self-iterative optimization mechanism to dynamically adjust the filtering parameters, ensuring the accuracy and stability of the entire filtering process. The contributions of this study are as follows:
> (1) A probabilistic model-driven snowfall noise filter method is proposed...
> (2) Compared with previous de-snowing filters, the proposed PMDF can adjust model parameters based on different LiDAR types and snowfall intensities...
> (3) Demonstration of superior generalization and precision across diverse benchmarks...

#### 深度分析

**S1** 以"To address the above challenges"开头，这是一个标准的"空白填充"信号句，它在语法上直接将本文方法与前文揭示的研究空白连接起来。"without relying on prior information"精确回应了上一段S3中提炼的核心问题"over-reliance on prior data"。

**贡献列表的三层架构**：

- **C1（方法贡献）** 回答"你做了什么？"——提出了一个新的三阶段滤波方法。
- **C2（特性贡献）** 回答"比前人好在哪里？"——适应性更强，不依赖特定LiDAR或降雪强度。
- **C3（验证贡献）** 回答"你怎么证明的？"——在三个不同数据集上验证，特别是在数据受限场景下也有效。

这三个贡献分别对应审稿人评估论文价值时的三个核心维度：方法新颖性（novelty）、技术优越性（superiority）、实验充分性（thoroughness）。

### Introduction整体结构总结与迁移指导

**Introduction的宏观论证结构（漏斗型）：**

```
第1段：LiDAR的重要性 + 降雪挑战（从广到窄）
    ↓
第2段：密度滤波方法的系统性批评（两个局限）
    ↓
第3段：深度学习方法的批评 + 统一性问题提炼
    ↓
第4段：本文方法提出 + 三层贡献声明
    ↓
第5段：结构导览
```

**可迁移的核心原则：**

1. **"先扬后抑"的批评策略**：批评前人工作时，必须先承认其贡献，再指出局限。
2. **多路线批评的统一性归纳**：将多条竞争路线的不同缺陷归纳为同一个根本问题，然后一次性解决。
3. **引用的多角度复用**：同一篇文献可以在不同语境下从不同角度被引用。
4. **贡献列表应覆盖审稿维度**：方法贡献（新颖性）+ 性能贡献（优越性）+ 验证贡献（充分性），三者缺一不可。

---

## II. Related Work 解析

### 导入段

#### 原文呈现

> Snow-induced LiDAR point cloud noise differs significantly from conventional point cloud noise. Conventional noise is usually caused by minor sensor errors, which appear as a small number of scattered points spread across the surface. In contrast, snow noise appears as a large number of outliers clustered near the LiDAR sensor, with significantly different point cloud density and spatial distribution than typical noise. Therefore, specialized de-noising methods are required to filter snow noise effectively. Currently, algorithms for snow noise removal in LiDAR point clouds can be broadly classified into two types: ones based on heuristic filters designed using empirical rules, which typically provide good interpretability, and those based on deep learning, which can provide higher filtering accuracy.

#### 深度分析

这段是Related Work的"框架建立段"，其核心功能是为后续的文献回顾提供**组织逻辑**。S1-S3构成了一个对比结构：普通噪声（少量、分散、表面）vs. 降雪噪声（大量、聚集、近传感器）。这个对比有两个目的：第一，向不熟悉降雪噪声的读者解释其独特性；第二，为S4的结论"需要专门方法"提供逻辑基础。

S5的分类——"heuristic filters"和"deep learning"——与Introduction第2-3段的结构完全一致。"先给框架，再填细节"的Related Work写法是最清晰、最友好的结构选择。

---

### A. Heuristic-Based De-Noising Method for Snowfall

作者按时间顺序回顾了密度滤波方法的演进：

1. **ROR/SOR基线**（[7] PCL库）：最早期的方法，固定阈值无法适应LiDAR点云"近密远疏"的特性。
2. **DROR[8]/DSOR[9]改进**：引入动态阈值，提升远距点识别精度，但参数仍未考虑雪点空间分布特性，且3D搜索复杂度高。
3. **更多改进**：强度特征引入（[20] Park, [10] DDIOR, [12] LIDSOR）、降维加速（[21] DCOR）、时空特征（[14] Li）。
4. **统一性总结**：所有启发式方法共享两个核心缺陷——(1) 未充分利用雪噪声空间分布特性；(2) 参数依赖大量先验数据。

Related Work中每一个"局限性"的指出，都在后续方法部分有对应的解决方案。特别值得注意的是"preprocessing times measured in hours or even days"——将抽象的"泛化能力差"转化为具体可感知的时间成本。

---

### B. Deep Learning-Based De-Noising Method for Snowfall

三个方法的局限性呈现了**递进关系**：

1. **WeatherNet[15]**：需要标注数据 → 但标注数据不够
2. **4DenoiseNet[17]**：用仿真数据弥补 → 但仿真与真实有差距
3. **LiSnowNet[19]**：无监督规避标注需求 → 但只适用于特定场景

这种递进暗示：深度学习社区一直在尝试解决数据问题，但每次"解决"都带来新的局限。数据依赖是深度学习路线的结构性困难。

---

### Related Work 总结过渡段

总结段同时"杀死"两条竞争路线：启发式方法参数难设、深度学习方法数据依赖。"sunk cost of manual labeling"借用经济学术语强调不可回收投入，增强表达冲击力。

### Related Work 整体结构总结与迁移指导

**可迁移的核心原则：**

1. **Related Work的组织应服务于论证，而非仅仅罗列**。
2. **时间顺序+递进结构**：展示方法间的"继承-改进"关系，让读者看到一个演进但仍未解决的问题链。
3. **总结段的"双杀"功能**：好的Related Work总结段应该同时杀死多条竞争路线，为本文方法创造独一无二的学术空间。

---

## III. Approach 解析

Section III是全文技术密度最高的部分，分为导引段、三个核心子节（A. 空间概率分布建模、B. 粗去噪、C. 精去噪与参数自适应），以及伪代码。以下按逻辑段落逐段深度分析。

### 导引段（问题观察与方法动机）

#### 原文呈现

> Fig. 1 shows a point cloud captured in a snowfall environment. The left panel of Fig. 1 shows that the snow noise is densely distributed near the LiDAR sensor, with little to no noise in regions further away. This observation suggests that establishing an appropriate regional threshold can significantly reduce the amount of data that the filters must process.
>
> The statistics of the spatial distribution of snow noise are depicted on the right side of Fig. 1. According to the statistics, noise density varies with distance in a quasi-normal manner, with snow noise density increasing and then decreasing. A similar trend can be seen in the vertical dimension...
>
> However, most existing heuristic filters do not account for the spatial characteristics of snow noise. Instead, they typically represent noise density as a linear function of distance or as a fixed value. For example, the filtering formula used by the DROR filter is as follows: [公式(1)]

#### 逐句解构与功能标注

| 编号 | 功能标注 |
|------|--------|
| S1-S2 | **经验观察**：从Fig.1可视化出发，建立"雪噪声集中在传感器附近"的直觉 |
| S3 | **设计启示1**：区域阈值可减少数据量（为后续裁剪策略铺垫）|
| S4-S6 | **统计发现**：雪噪声在距离和高度方向均呈类正态分布 |
| S7-S8 | **现有方法批评**：DROR等方法将噪声密度建模为线性函数，不符合实际分布 |

#### 深度分析

**从数据观察到方法动机的叙事策略**

这段的写作策略堪称教科书级别：作者不是直接给出方法，而是先引导读者"看见"数据中的模式。通过Fig. 1的可视化，读者能直观理解两个关键观察：(1) 雪噪声集中在传感器附近——这为"区域裁剪"提供了动机；(2) 噪声密度随距离呈非线性（类正态）变化——这为"概率分布建模"提供了动机。

**公式(1)的"靶标"功能**

作者在此处呈现DROR滤波器的公式 $SR_p = \beta \times r_p \times \alpha$，目的不是介绍DROR，而是将其作为**对比靶标**——这是一个线性公式，搜索半径与距离成正比。作者通过将此公式与Fig. 1中的实际分布并置，让读者自行得出结论："线性模型不够准确"。这种"让证据说话"的写法比直接断言"DROR不好"要有说服力得多。

紧接着，作者提出PMDF方法的三阶段工作流（Fig. 2）：**粗去噪 → 参数估计 → 精去噪与参数自适应**。Fig. 2是全文方法的"路线图"，将整个系统的数据流和模块关系可视化。对审稿人而言，这张图的存在大幅降低了理解门槛。

**"冷启动问题"的提前声明**

作者在此段就主动提出了一个潜在的技术缺陷：在时间序列初始帧，缺乏历史噪声数据来估计模型参数。然后立即说明了解决方案：设计了一个粗去噪模块来解决初始参数估计问题。这种**先声明问题、再给出解决方案**的写法，是一种高级的论证防御策略——如果审稿人在阅读过程中自己发现了这个问题，会对文章产生不信任感；但如果作者提前声明并解决了它，审稿人反而会认为作者考虑周到。

---

### A. Modeling the Spatial Probability Distribution of Snow Noise

#### 原文呈现（核心逻辑概要）

> In clear weather, laser beams are typically transmitted through air and a small amount of free-floating dust... However, in snowfall weather, the high concentration of snowflake ice crystals in the air can cause backscattering of the laser beams...
>
> [蒙特卡洛仿真分析 → Fig. 3仿真结果]
>
> As shown in the first row of Fig. 3, the amount of snow noise increases and then decreases with distance, following a normal distribution...
>
> [从物理机制解释分布形成原因 → Fig. 4 LiDAR检测示意图]
>
> However, simulation data has limitations...
>
> [引用真实数据统计分析：Michaud et al. [11] → Sun et al. [13]]
>
> Therefore, based on a combination of simulation analysis and statistical fitting results from real data, the algorithm proposed in this study uses the gamma distribution and the t-location-scale (t l-s) distribution to characterize the spatial distribution of snow noise.

#### 逐句解构与功能标注

| 逻辑段 | 功能标注 |
|--------|--------|
| 物理机制段 | **因果解释**：从激光传播物理机制解释为什么降雪产生噪声 |
| 仿真分析段 | **初步证据**：通过蒙特卡洛仿真建立雪噪声空间分布的初步认知 |
| 物理解释段 | **直觉构建**：通过Fig. 4的LiDAR锥形视场解释分布形成原因 |
| 仿真局限段 | **诚实声明**：承认仿真数据的局限性 |
| 真实数据段 | **实证验证**：引用[11][13]的统计拟合结果确认分布模型 |
| 模型选择段 | **技术决策**：确定使用gamma分布和t-location-scale分布 |

#### 深度分析

**"仿真+真实数据"的双重验证策略**

这一整节的论证架构是精心设计的。作者没有直接说"根据文献，雪噪声服从gamma分布"，而是构建了一条从物理直觉到仿真验证再到实证确认的**完整证据链**：

1. **物理直觉（Why）**：激光在降雪环境中发生后向散射，这是噪声产生的物理根因。
2. **仿真验证（How it looks）**：通过蒙特卡洛仿真，使用Velodyne VLP-32C的参数模拟雪噪声分布。Fig. 3展示了4种不同雪花数量下的分布直方图和3D可视化——距离方向呈类正态分布，高度方向集中于传感器中心高度。
3. **物理解释（Why it looks like this）**：Fig. 4通过LiDAR锥形视场的几何关系，解释了为什么近处噪声少（视场小）、中间噪声多（视场扩展）、远处噪声少（信号衰减）。这种从"现象"到"原因"的解释，让模型选择有了物理依据而非纯统计拟合。
4. **诚实声明（Limitation）**：作者主动承认"simulation data has limitations, and simulation results can only approximate the spatial distribution trend"。这种诚实不仅不会削弱论证，反而增强了可信度——读者会认为作者是严谨的。
5. **实证确认（Real data）**：引用 **[11] Michaud et al.** 的六种降雪条件统计和 **[13] Sun et al.** 的四个真实数据集统计拟合结果。[13]的结论——gamma分布比log-normal分布更准确描述雪噪声距离分布，t-location-scale分布更准确描述高度分布——成为本文模型选择的最终依据。

**引用[11]和[13]的差异化角色**

[11]是该领域第一篇用统计方法揭示雪噪声分布特征的研究，但其场景覆盖范围有限。[13]是一项更全面的研究，使用了四个不同数据集（CADC, BOREAS, WADS, RADIATE），覆盖了32、64、128波束LiDAR和多个地理区域。作者引用[11]建立"先驱性发现"的历史线索，引用[13]作为"更完善的证据"，两者构成了一个递进关系。值得注意的是，[13]的作者与本文作者有交叉——这说明本文是建立在作者团队前期工作基础上的深入研究，进一步增强了方法选择的合理性。

**模型选择的写作策略**

最终的模型选择——gamma分布（距离方向）和t-location-scale分布（高度方向）——被呈现为仿真和实证的**自然汇合结论**，而非作者的主观选择。这是一种"让证据引导决策"的叙事方式，比"我们选择使用gamma分布因为..."的直接陈述更有说服力。

---

### B. Coarse De-Noising for Parameter Initialization

#### 原文呈现（核心逻辑概要）

> According to the previous analysis, the PMDF faces difficulties in estimating filter parameters during the initial stage due to a lack of adequate historical noise data. To address this issue, we created a coarse de-noising module...
>
> [两步流程：初始滤波（使用DSOR）+ 目标点云恢复]
>
> [引入OSC（Ordered Sampling Consensus）算法替代RANSAC用于目标恢复]

#### 深度分析

**冷启动问题的正式解决**

粗去噪模块的设计目标是解决一个工程化的实际问题：系统启动时没有历史数据。作者的解决思路很务实——用现有的SOTA滤波器（DSOR）先粗略处理前几帧，获取初始噪声数据，然后将这些数据喂给参数估计模块。

**"不确定噪声点"概念的引入**

作者将DSOR初始滤波得到的噪声点命名为"uncertain noise points"（$P_u$），并通过Fig. 5展示了这些"不确定点"可能包含建筑等有用目标。这个命名是有深意的——它承认了初始滤波的不完美，并为引入"目标恢复"步骤提供了逻辑必要性。

**OSC算法替代RANSAC的论证逻辑**

作者指出经典RANSAC算法[26]的随机采样策略在密集点云中表现不佳，然后提出了利用点云在水平角度维度上的连续性的有序采样共识（OSC）算法。OSC的五个步骤——数据编码、有序采样、直线拟合、一致性检查、目标恢复——构成了一个从激光束组织结构出发的、充分利用LiDAR数据先验知识的算法设计。

这个设计选择反映了一个重要的方法论原则：**在可以利用数据先验结构的地方，不要使用通用算法**。RANSAC是一个通用的鲁棒拟合算法，而OSC是一个利用LiDAR点云特殊结构（激光束的有序排列）的定制算法。

**粗去噪模块的"过渡性"设计**

作者明确指出："from this point onward, the coarse de-noising module is no longer used to filter the subsequent time series point cloud data"。粗去噪模块只在前N帧工作，之后由精去噪模块接管。这种"用完即弃"的设计哲学说明作者将粗去噪模块定位为一个**初始化工具**而非核心算法组件，这种清晰的定位有助于审稿人理解系统架构。

---

### C. Fine De-Noising With Parameter Self-Adaptation

#### 原文呈现（核心逻辑概要）

> The core principle of the fine de-noising module to distinguish between noise and normal point clouds lies in the density difference between the two types of point clouds.
>
> [三步流程：点云裁剪 → 体素化编码 → 基于空间密度的滤波]
>
> [1) 基于概率模型的噪声区域裁剪：公式(3)(4)(5)(6)]
>
> [2) 基于概率模型的参数自适应滤波：蒙特卡洛估计$k_{p\ min}$，公式(7)(8)(9)]
>
> [体素化优化策略：Fig. 6]
>
> [Algorithm 1 伪代码]

#### 深度分析

**C.1 概率模型驱动的噪声区域裁剪**

公式(3)和(4)分别定义了gamma分布和t-location-scale分布的概率密度函数：

$$F_{Gamma}(d, k, \theta) = \frac{d^{k-1} e^{-d/\theta}}{\theta^k \Gamma(k)}$$

$$F_{tlc}(h) = \frac{\Gamma(\frac{v+1}{2})}{\sigma\sqrt{v\pi}\Gamma(\frac{v}{2})} \left[\frac{v + (\frac{h-\mu}{\sigma})^2}{v}\right]^{-\frac{v+1}{2}}$$

作者使用历史噪声数据拟合这两个分布的参数，然后通过显著性水平检验（$\omega = 0.01$）计算距离阈值$T_d$和高度阈值$T_h$：

$$T_d = F^{-1}_{Gamma}(1 - \omega, k, \theta)$$
$$T_h = F^{-1}_{tlc}(1 - \omega, \mu, \sigma, v)$$

这个设计的精髓在于：**裁剪阈值不是固定的超参数，而是从数据中自动推导出来的**。$\omega = 0.01$意味着当雪噪声出现概率低于1%时，该区域被判定为无噪声区域。这个显著性水平的选择引用了[12]的参数设计，为其提供了外部依据。

**C.2 基于概率模型的参数自适应滤波**

这是PMDF的核心创新所在。与DROR使用固定的$k_{p\ min}$不同，PMDF通过蒙特卡洛方法为每个点动态估计$k_{p\ min}$。五个步骤的逻辑链条是：

1. **构建概率模型**：使用III-A节确定的gamma和t-l-s分布
2. **拟合参数**：用历史噪声数据$P_h$拟合分布参数
3. **蒙特卡洛采样**：从拟合的分布中生成大量样本点$P_m$
4. **建立估计器**：对当前帧每个点$p$，计算搜索半径$SR_p$内的样本点数$N_p$，通过公式(9)得到$k_{p\ min}$：

$$k_{p\ min} = \left\lceil \frac{N_p}{N_m} \times \frac{N_{P_n}}{N_h} \right\rceil$$

5. **执行滤波**：若点$p$邻域内点数$k_p \leq k_{p\ min}$，则判定为噪声

公式(9)的设计逻辑值得深入分析：$N_p/N_m$代表样本点中落在该位置搜索半径内的比例（反映空间概率密度），$N_{P_n}/N_h$是历史噪声总量的归一化因子（反映噪声强度）。两者的乘积给出了在当前噪声条件下，该位置预期出现的最大噪声点数——这就是动态的密度阈值。

**体素化优化的效率-精度权衡**

作者坦诚指出逐点计算密度阈值的效率问题，然后通过体素化策略解决：将3D空间划分为等高等长的2D扇形体素（Fig. 6），同一体素内所有点共享相同的密度阈值。这个设计基于一个合理的假设："snowflakes are assumed to be uniformly distributed in the real world, and snow noise detected by LiDAR is roughly uniformly distributed in azimuth"。

作者后文（Section IV-B）也诚实地指出了这一策略的代价："PMDF suffers from a lack of precision when removing snow noise...it may misclassify low-density objects, such as trees near the LiDAR, as snow points"。这种在方法部分做出效率-精度权衡，并在实验部分坦诚分析其负面影响的做法，是高质量论文的标志。

**Algorithm 1 伪代码的结构**

伪代码清晰地展示了PMDF的完整流程：第1-5行处理冷启动阶段（粗去噪），第6-30行处理稳态阶段（参数估计+精去噪）。伪代码的存在对审稿人和后续研究者都极其重要——它将自然语言描述转化为了可执行的精确算法规范。

### Approach整体结构总结与迁移指导

**Section III的宏观叙事结构：**

```
数据观察（Fig.1）→ 现有方法局限（公式1对比）
    ↓
PMDF工作流概览（Fig.2）
    ↓
A. 空间概率分布建模（物理→仿真→实证→模型选择）
    ↓
B. 粗去噪（冷启动解决方案：DSOR+OSC目标恢复）
    ↓
C. 精去噪（概率裁剪→蒙特卡洛密度估计→体素化加速）
    ↓
Algorithm 1（完整伪代码）
```

**可迁移的核心原则：**

1. **"从观察到方法"的叙事顺序**：先展示数据中的模式和现有方法的不足，再引出你的方法设计。让读者感受到方法选择的"不得不"，而非主观偏好。
2. **证据链的层次性**：物理直觉 → 仿真验证 → 真实数据确认，三层证据构成的论证比任何单一层面都更可信。
3. **主动暴露问题并解决**：冷启动问题、效率问题都由作者主动提出并解决，这远好于等审稿人发现。
4. **权衡的透明性**：体素化策略的效率-精度权衡被清晰说明，这建立了学术诚信。
5. **伪代码的必要性**：对于包含多阶段、多条件分支的算法，伪代码是确保可复现性的关键工具。

---

## IV. Experiments and Results 解析

Section IV分为四个子部分：A. 定性评估、B. 定量评估、C. PMDF对目标检测的收益。

### 实验设置段

#### 原文呈现

> To validate the proposed snow filtering algorithm's accuracy and generalizability, we evaluated it on the publicly available CADC, BOREAS, and WADS datasets, with snow point annotations from the MSP dataset. All experiments were carried out on a desktop computer equipped with an Intel i7-12700 processor and 32GB of RAM.
>
> We benchmarked the proposed PMDF against classic methods (ROR, SOR) and state-of-the-art filters (DROR, DSOR, DDIOR)...

#### 深度分析

**数据集选择的策略性**

三个公开数据集的选择不是随意的：CADC使用32波束LiDAR、BOREAS使用128波束LiDAR、WADS使用32波束LiDAR但数据采集地点不同。这三者在LiDAR类型、地理区域、降雪强度上形成了差异化组合，为"泛化能力"声明提供了坚实基础。

**基线方法的层次化选择**

作者将基线分为"classic methods"（ROR, SOR）和"state-of-the-art filters"（DROR, DSOR, DDIOR）。这种分层有两个作用：(1) 与经典方法的比较证明"需要专门方法"；(2) 与SOTA方法的比较证明"我们的方法更好"。

**开源代码的提供**

"The source code for all filtering algorithms used in this study is available at..."——这不仅是学术规范，也是增强可信度的有力手段。开源意味着所有结果都可以被独立验证。

---

### A. Qualitative Evaluation of Snowfall De-Noising

#### 原文呈现（核心逻辑概要）

> Fig. 7 shows the performance of six filtering algorithms on three public datasets...
>
> Overall, the ROR and SOR algorithms perform poorly because they over-filter both snow noise and a large number of target and ground points...
>
> DROR, DSOR, and DDIOR algorithms use dynamic filtering thresholds... outperform ROR and SOR...
>
> However, the enlarged boxes in each subfigure highlight an issue: the performance of these three algorithms varies across snowfall scenarios...
>
> In contrast, the proposed PMDF demonstrates the capability to adaptively set filtering thresholds and iteratively optimize them.

#### 深度分析

**定性评估的论证结构**

Fig. 7是一个精心设计的6×3可视化矩阵（6种算法 × 3个数据集）。作者使用颜色编码（紫色=被滤除的噪声，绿色=保留的非噪声点）和放大框突出关键细节。

定性分析的论证遵循**三级递进**：
1. ROR/SOR → 过滤过度，性能差
2. DROR/DSOR/DDIOR → 改进明显但跨场景不稳定
3. PMDF → 三个数据集上表现一致且准确

这种递进结构与Related Work中的方法回顾形成了对应：Related Work中按时间顺序指出各方法的局限，实验部分用视觉证据验证了这些局限确实存在。

**跨数据集不一致性的精准描述**

作者非常精确地描述了每个算法在不同数据集上的差异表现："DROR performs particularly well on the CADC dataset... However, it has lower recall on the BOREAS and WADS datasets"。这种细粒度的分析比笼统地说"DROR不好"要有说服力得多——它展示了作者对实验结果的深入理解。

---

### B. Quantitative Evaluation of Snowfall De-Noising

#### 原文呈现（Table I及分析）

Table I展示了六种算法在三个数据集上的Precision、Recall、F1-Score和平均执行时间。

#### 深度分析

**指标选择的周密考虑**

作者先定义了Precision（非噪声点保留能力）、Recall（噪声去除能力）和F1-Score（综合评估），然后专门花了一段文字解释这三个指标在雪噪声滤波语境下的具体含义。这对不熟悉信息检索指标体系的ITS领域读者尤其重要。

**冷启动阶段的透明化处理**

作者额外报告了PMDF在冷启动阶段的性能数据，但明确说明"these data serve solely as a supplementary reference"，且"all subsequent discussions regarding the performance of PMDF default to the steady-state data"。这种处理方式是诚实且聪明的——不隐瞒冷启动阶段的性能差距，但也不让它影响主要结论的表述。

**核心量化结论**

PMDF在三个数据集上F1-Score分别为92.8、89.9、89.3，均为最高。更重要的是，其**跨数据集的方差最小**——这直接证明了"泛化能力强"的声明。相比之下，DROR在WADS上Recall仅49.1%，DDIOR在BOREAS上F1-Score仅77.2——这些"断崖式下降"恰恰是泛化能力差的证据。

**执行效率分析**

PMDF稳态阶段的执行时间（45/67/48毫秒）是所有方法中最快的。作者将此归因于体素化策略和点云裁剪减少了不必要的计算。冷启动阶段的较高延迟（239-298毫秒）被合理化为"transient"且"can be executed as a background task"——这是一种将工程限制转化为可接受的部署方案的论证策略。

**自我批评的体现**

Fig. 8和相关文字坦诚指出PMDF的精度不足：可能将靠近LiDAR的低密度目标（如树木）误判为雪噪声。作者将此归因于网格化方法的精度损失。这种自我批评不仅不会削弱论文，反而增强了整体可信度，并为未来改进指明了方向。

---

### C. Benefits of PMDF for LiDAR Object Detection Algorithms

#### 深度分析

这一节是全文论证架构的"闭环"部分——将滤波精度提升与下游目标检测性能改善建立因果关系。

**双场景实验设计**

作者设计了两种实验场景，这是一个非常周到的实验方案：

1. **数据受限场景**：检测模型仅用正常天气数据训练（NuScenes），在CADC降雪数据上测试。这模拟了"没有降雪训练数据"的真实部署场景。
2. **数据不受限场景**：用CADC数据7:3分割训练和测试。这消除了域偏移因素，更直接评估滤波的影响。

这两个场景分别回答了两个不同的问题：场景1回答"在没有降雪数据的情况下，PMDF能否作为即插即用的预处理提升检测精度？"场景2回答"即使有降雪训练数据，PMDF预处理是否仍有价值？"

**检测算法选择**

VoxelNeXt[27]（纯体素方法）、PV-RCNN[28]（点-体素混合方法）、LION[29]（线性RNN方法）——三种算法代表了当前3D目标检测的三个主流技术路线。在三种不同架构上都获得一致性提升，这极大增强了结论的普适性。

**Table II — 数据受限场景结果**

AP提升分别为5.9、9.7、6.4个百分点。作者还分别报告了轻雪和重雪条件下的AP，两种条件下都有一致性提升。PV-RCNN获得了最大提升（9.7个百分点），这可能是因为其点-体素混合架构对噪声更敏感。

**Table III — 点级量化分析**

这是一个"机制性证据"表格：噪声去除率（89.7%）和目标保留率（93.2%）。特别值得注意的是，目标保留率在轻雪到重雪间仅从93.5%变化到92.8%——这说明PMDF在保守策略下优先保证目标完整性。这种点级分析弥合了"滤波精度"和"检测提升"之间的逻辑鸿沟。

**Table IV — 数据不受限场景结果**

AP提升为4.2%-4.8%——比数据受限场景略低，但仍然显著。这证明了即使检测模型已经在降雪数据上训练过，PMDF预处理仍能提供额外收益。

**Table V — 六种滤波器对检测性能的影响**

这是一个"最终闭环"实验：用LION算法在经过六种不同滤波器处理的点云上进行检测。PMDF+LION获得最高AP（64.9%），证明PMDF不仅在滤波指标上最优，在实际感知任务中也最有效。

### Experiments整体结构总结与迁移指导

**Section IV的宏观实验设计：**

```
定性评估（Fig.7可视化对比）
    ↓
定量评估（Table I：Precision/Recall/F1/Time）
    ↓
自我批评（Fig.8：精度不足的诚实分析）
    ↓
下游任务评估：
  ├── 数据受限场景（Table II + Table III点级分析）
  └── 数据不受限场景（Table IV + Table V六滤波器对比）
```

**可迁移的核心原则：**

1. **定性先行，定量跟进**：先用可视化让读者直观感受方法效果，再用数字精确量化。
2. **基线的层次化**：将基线分为"经典方法"和"SOTA方法"两层，分别承担不同的论证角色。
3. **多数据集+多指标**：泛化能力的声明需要多数据集支持，方法的全面性需要多指标支持。
4. **冷启动/初始化的透明化**：对系统的暂态行为（如冷启动）诚实报告，同时合理化其对实际部署的有限影响。
5. **下游任务验证是工具型论文的必修课**：滤波器论文必须展示其对下游任务的实际收益。
6. **多场景覆盖**：数据受限和不受限两种场景覆盖了实际部署中的两个极端，让结论更全面。
7. **机制性证据**（如Table III的点级分析）弥合滤波精度和检测提升之间的因果链。

---

## V. Conclusion 解析

### 原文呈现

> This study proposes a probability model-driven filter (PMDF) for accurately removing snow noise from LiDAR point clouds across a variety of snowfall scenarios without relying on prior data. Experimental evaluations on publicly available CADC, BOREAS, and WADS datasets demonstrate that the PMDF outperforms other noise removal algorithms in terms of precision, recall, and computational efficiency. Compared to five state-of-the-art filters, the PMDF consistently outperformed them all in terms of accuracy and robustness, with F1-Scores above 90 across all three datasets...
>
> Furthermore, object detection experiments were used to validate the PMDF's effectiveness in improving LiDAR perception accuracy under snowfall conditions...
>
> In addition, PMDF has some inherent disadvantages. To strike a balance between accuracy and efficiency, PMDF employs a voxelization strategy. Although this strategy increases filtering efficiency, it reduces filtering accuracy near the sensor, particularly for low-density targets like trees. Future research will focus on optimizing the voxelization strategy, such as introducing an adaptive gridded approach...

### 逐句解构与功能标注

| 编号 | 功能标注 |
|------|--------|
| S1 | **方法回顾**：一句话重述PMDF的核心定位 |
| S2-S3 | **滤波评估总结**：重申F1-Score > 90的核心结果 |
| S4-S5 | **下游任务总结**：重申AP提升的两组数据 |
| S6-S7 | **局限性与未来方向**：坦诚不足+具体改进路径 |

### 深度分析

**Conclusion的"回顾-证据-展望"三段式**

结论部分严格遵循了"方法贡献回顾 → 核心结果复述 → 局限性与未来方向"的标准结构。

**结果复述的策略**

作者在Conclusion中精确复述了两组关键数字：滤波F1-Score（>90）和目标检测AP提升（数据受限：5.9/9.7/6.4%；数据不受限：4.8/4.5/4.2%）。注意这些数字与摘要中的数字完全对应——摘要和结论的数字一致性是学术论文的基本要求。

**局限性声明的"可操作性"**

作者不仅指出了体素化策略导致的精度损失问题，还给出了具体的改进方向："introducing an adaptive gridded approach that allows the grid division to be dynamically adjusted based on the density and characteristics of the targets"。这种具体的未来方向比笼统的"future work will address..."要有价值得多——它表明作者已经在思考解决方案，也为后续研究者提供了明确的起点。

### 结构总结与迁移指导

**可迁移的核心原则：**

1. **Conclusion应是Abstract的"镜像"**：摘要中承诺的每一个贡献，在结论中都应有对应的结果证据。
2. **数字的一致性**：摘要、实验部分、结论中提到的关键数字必须保持一致。
3. **局限性+未来方向应具体可操作**：不要说"还有改进空间"，要说"可以通过X方法解决Y问题"。

---

## 全文论证架构总览

```
Abstract（承诺）
    ↓
Introduction（建立空间：LiDAR重要→降雪挑战→现有方法缺陷→PMDF）
    ↓
Related Work（扫清竞争者：启发式方法×2局限 + 深度学习×数据依赖 = 统一空白）
    ↓
Approach:
  A. 分布建模（物理→仿真→实证→gamma+t-l-s）
  B. 粗去噪（冷启动方案：DSOR+OSC）
  C. 精去噪（概率裁剪→蒙特卡洛密度估计→体素化加速）
    ↓
Experiments:
  A. 定性（6×3可视化矩阵）
  B. 定量（F1>90, 最快执行时间）
  C. 下游（数据受限+不受限, 3检测器一致提升）
    ↓
Conclusion（兑现承诺 + 诚实局限 + 具体展望）
```

## 全文写作技巧精华总结

1. **"证据链"思维**：每个技术决策都应有多层证据支撑（物理→仿真→实证），而非仅凭单一来源。
2. **"预判审稿人"思维**：在每个可能被质疑的位置提前给出回应（冷启动、效率、精度权衡）。
3. **"统一空白"策略**：将多个竞争方法的不同缺陷归纳为同一个根本问题，用一个方法一次性解决。
4. **"双层结果"架构**：工具型论文同时展示方法本身和下游任务两层结果。
5. **"诚实+"策略**：坦诚方法的局限不会削弱论文，反而增强可信度——前提是同时给出解决或改进方向。
6. **引用的多角度复用**：同一篇文献在不同语境下从不同角度被引用，高效利用有限的引用空间。
7. **可视化的"不言自明"力量**：好的图表（如Fig.1, Fig.7）能让读者自己得出结论，比文字断言更有说服力。
