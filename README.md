这是用来学习 langgraph 的项目

我想要参考 deep research 的项目，基于 langgraph 制作一个研究应用。

用户可以配置：

1. 关注的网站（research 的时候会优先搜索这些网站中的内容）
2. 关注的客户端
   2.1. 例如关注 x.com，用户可以设定关注的推主，检索时会检索他们最近发的推文
   2.2. 可以拓展支持的客户端，例如其他支持 api 调用的客户端，开发者可扩展

用户可操作：

1. 提出需求，比如用户会请求：“本周以色列伊朗冲突的最新进展”

deepresearch 操作：

1. 分析用户要求，拆分为步骤，让用户评估是否正确，例如案例中药分析以色列伊朗冲突，应该按照如下操作进行：
   1.1. 优先搜索用户关注的网站中查找相关内容
   1.2. 优先从用户关注的客户端中查找
   1.3. 制定研究方案：
   1.3.1. 识别伊朗和以色列或其代理人之间最近的直接和间接军事交战或重大事件。
   1.3.2. 收集伊朗、以色列政府以及主要国际机构或国家对这些最新进展的官方声明和反应。
   ...
2. 如果用户需要修改，则和用户沟通如何修改，以此来调整上述操作
3. 按照步骤进行调查，并随着调查的深入，拓展调查范围和方向
4. 研究完成后输出本次调查检索的站点列表，如果有用户的关注网站、关注网站，也应该列出
5. 研究后提供关于用户请求的分析报告

项目结构可参考：

1. https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart?tab=readme-ov-file
2. https://github.com/bytedance/deer-flow

## Gemini 方案

你有一个非常棒且实际的项目构想！基于 LangGraph 制作一个深度研究应用，并结合用户定制化的信息源，这将极大地提升研究的效率和精准度。你的设计思路清晰，涵盖了从用户输入到最终报告输出的整个流程，并且考虑到了可扩展性。

---

### 项目构想概述

你的项目目标是创建一个能够进行**定制化深度研究**的 LangGraph 应用，核心特点包括：

- **个性化信息源配置：** 用户可以指定优先搜索的网站和客户端（如 X.com 特定推主）。
- **智能研究方案制定：** 应用能将用户需求分解为详细的研究步骤，并与用户确认。
- **迭代式深度探索：** 研究过程能根据初步发现，动态调整和扩展研究范围。
- **透明化信息来源：** 最终报告会列出所有检索过的站点和客户端。
- **结构化分析报告：** 提供一份关于用户请求的深度分析报告。

---

### 项目结构与 LangGraph 实现思路

参考 `google-gemini/gemini-fullstack-langgraph-quickstart` 和 `bytedance/deer-flow`，你的项目结构会围绕 LangGraph 的**节点（Nodes）**和**边（Edges）**来构建，以实现复杂的逻辑流转。

以下是基于你的构想，我建议的 LangGraph 核心模块和流程：

---

#### 核心模块（LangGraph 节点）

1.  **`UserConfigNode` (用户配置节点)**

    - **职责：** 管理和存储用户的定制化配置，包括：
      - **`priority_websites`**: 优先搜索的网站列表。
      - **`priority_clients`**: 优先搜索的客户端及其配置（例如，X.com 的推主列表）。
    - **输入：** 用户配置数据。
    - **输出：** 更新后的用户配置状态。
    - **触发方式：** 用户主动进行配置操作时触发。

2.  **`RequestAnalysisNode` (需求分析节点)**

    - **职责：** 接收用户提出的研究请求，并将其分解为初步的研究子目标或步骤。
    - **输入：** 用户的自然语言研究请求（例如：“本周以色列伊朗冲突的最新进展”）。
    - **输出：**
      - 初步研究方案（例如你示例中的 1.3.1, 1.3.2 等）。
      - 一个布尔标志，指示是否需要用户评估 (`needs_user_review = True`)。
    - **核心逻辑：** 利用 LLM 对请求进行语义理解和任务拆解。

3.  **`UserReviewNode` (用户评估节点)**

    - **职责：** 暂停流程，等待用户评估并确认或修改研究方案。
    - **输入：** `RequestAnalysisNode` 提供的初步研究方案。
    - **输出：**
      - 用户确认或修改后的最终研究方案。
      - 一个布尔标志，指示是否通过评估 (`is_approved = True/False`)。
    - **触发方式：** `RequestAnalysisNode` 输出 `needs_user_review = True` 时。

4.  **`InformationGatheringNode` (信息收集节点)**

    - **职责：** 根据当前研究步骤，执行信息检索。
    - **输入：** 单个研究步骤（例如：“识别伊朗和以色列或其代理人之间最近的直接和间接军事交战或重大事件”）。
    - **输出：**
      - 检索到的原始信息片段。
      - 检索来源列表（URL、客户端名称、推文链接等）。
      - 一个布尔标志，指示是否需要进一步深入研究 (`needs_deep_dive = True/False`)。
    - **核心逻辑：**
      - **优先检索逻辑：** 首先查询 `priority_websites` 和 `priority_clients`。
      - **通用搜索：** 若优先源不足，则进行通用网络搜索。
      - **客户端 API 调用：** 对于 X.com 等，调用相应的 API 检索指定推主的推文。这部分需要开发者进行扩展，可以抽象出一个 `ClientAPIAdapter` 接口。

5.  **`SynthesisAndAnalysisNode` (综合分析节点)**

    - **职责：** 对收集到的信息进行整合、去重、提炼和初步分析，形成结构化的报告内容。
    - **输入：** `InformationGatheringNode` 提供的原始信息片段。
    - **输出：**
      - 结构化、去重和总结后的研究内容。
      - 潜在的后续研究方向或未解决的问题。
    - **核心逻辑：** 利用 LLM 进行信息归纳、关键信息提取和初步洞察生成。

6.  **`DeepDiveDecisionNode` (深度探索决策节点)**

    - **职责：** 根据当前研究的深度和广度，判断是否需要进一步探索或调整研究方案。
    - **输入：** `SynthesisAndAnalysisNode` 的输出（总结内容、未解决问题）以及 `InformationGatheringNode` 的 `needs_deep_dive` 标志。
    - **输出：**
      - 新的或调整后的研究步骤列表。
      - 一个布尔标志，指示是否完成研究 (`is_research_complete = True/False`)。
    - **核心逻辑：** 再次利用 LLM 判断当前信息是否满足用户请求，或是否需要针对特定方面进行更深入的挖掘。

7.  **`ReportGenerationNode` (报告生成节点)**
    - **职责：** 整理所有收集和分析的信息，生成最终的深度研究报告。
    - **输入：** 整个研究过程中积累的结构化内容和来源列表。
    - **输出：** 格式化的研究报告（Markdown 或可导出格式）。
    - **核心逻辑：** 结合 LLM 的文本生成能力和预设的报告模板。

---

#### LangGraph 流程（边和条件）

---

##### 初始流程：

1.  **`START` -> `RequestAnalysisNode`**: 用户提出请求。
2.  **`RequestAnalysisNode` -> `UserReviewNode`**: 提出初步方案后，总是先让用户评估。
3.  **`UserReviewNode`**:
    - **条件边 (Conditional Edge):**
      - 如果 `is_approved = True`（用户批准），则跳转到 `InformationGatheringNode`（开始执行研究方案的第一个步骤）。
      - 如果 `is_approved = False`（用户要求修改），则跳转回 `RequestAnalysisNode`（用户可以提供修改意见，重新分析）。

---

##### 研究循环：

1.  **`InformationGatheringNode` -> `SynthesisAndAnalysisNode`**: 收集到信息后，进行初步整合。
2.  **`SynthesisAndAnalysisNode` -> `DeepDiveDecisionNode`**: 初步分析后，判断是否需要深入。
3.  **`DeepDiveDecisionNode`**:
    - **条件边 (Conditional Edge):**
      - 如果 `is_research_complete = False`（需要深入），则根据 `新的或调整后的研究步骤列表`，再次触发 `InformationGatheringNode`（进入下一轮信息收集）。
      - 如果 `is_research_complete = True`（研究完成），则跳转到 `ReportGenerationNode`。

---

##### 结束流程：

1.  **`ReportGenerationNode` -> `END`**: 报告生成后，流程结束。

---

### 可扩展性与技术栈建议

- **客户端扩展：** 为 `InformationGatheringNode` 设计一个**插件式架构**。定义一个 `ClientAdapter` 接口，包含 `search(query, client_config)` 方法。每新增一个客户端（如 Twitter, Reddit, Notion 等），只需实现这个接口并注册到系统中。
  - 例如，X.com 适配器可以利用其 API（如果开放且可用）来检索特定用户的推文。
  - 对于没有 API 但有公共内容抓取需求的客户端，可能需要结合**网络爬虫**技术（如 `Playwright`, `Selenium` 或 `BeautifulSoup`），但这会增加复杂性和维护成本。
- **网站优先搜索：** `InformationGatheringNode` 在执行搜索时，可以优先将 `priority_websites` 作为搜索范围限定（如果搜索引擎支持）或在通用搜索结果中对这些网站的链接进行优先级排序和精读。
- **持久化：** LangGraph 的状态管理可以通过 `checkpointer` 机制实现，确保流程中断后可以恢复。用户配置和研究历史可以存储在数据库中。
- **前端交互：** 结合 `streamlit`, `gradio` 或一个简单的 `React/Vue` 应用作为前端，与后端 LangGraph 服务进行交互，实现用户配置、需求提交、方案评估和报告展示。

---

### 示例流程细化（“本周以色列伊朗冲突的最新进展”）

1.  **用户提交：** “本周以色列伊朗冲突的最新进展”。
2.  **`RequestAnalysisNode`：** LLM 分析后，生成以下研究方案：
    - 识别伊朗和以色列或其代理人之间最近的直接和间接军事交战或重大事件。
    - 收集伊朗、以色列政府以及主要国际机构或国家对这些最新进展的官方声明和反应。
    - 评估最新冲突发展对地区和全球市场（如油价、股市）的即时地缘政治和经济影响。
    - 调查旨在缓和或解决冲突的国际外交努力和回应。
    - 综合地缘政治专家和智库对冲突当前状态和潜在未来走向的分析。
    - 识别冲突最新阶段双方正在采用的任何新的或演变的战略或战术。
    - 检查主要区域和国际行为者（例如美国、俄罗斯、中国、欧盟、沙特阿拉伯、卡塔尔、土耳其、联合国等）在冲突最新发展中的作用和影响。
    - `needs_user_review = True`。
3.  **`UserReviewNode`：** 用户看到方案，点击“确认”。`is_approved = True`。
4.  **`InformationGatheringNode` (循环执行)：**
    - **步骤 1.1：识别军事交战。**
      - 首先在用户配置的 `priority_websites` (如 Al Jazeera, Reuters) 和 `priority_clients` (如特定推特军事分析员的推文) 中搜索关键词。
      - 如果信息不足，进行通用网络搜索。
      - 收集到相关新闻报道、冲突时间线等。
    - **步骤 1.2：收集官方声明。**
      - 搜索各国政府官网、联合国新闻稿等。
    - ... (依此类推，执行所有研究步骤)
    - 每次执行后，`SynthesisAndAnalysisNode` 会进行信息整理。
    - `DeepDiveDecisionNode` 评估是否需要对某个方面（例如，某个新出现的代理人团体）进行更深入的挖掘。如果需要，生成新的子任务。
5.  **`ReportGenerationNode`：** 所有研究步骤完成后，生成报告。报告中会列出：
    - 本次研究涉及的站点列表（例如：`aljazeera.com`, `reuters.com`, `un.org`, `x.com/analyst_a`, `x.com/iran_foreign_ministry` 等）。
    - 报告主体内容：按分析步骤进行结构化阐述。

---

这个项目构想非常有潜力，因为它结合了大型语言模型的强大分析能力和用户对信息来源的精细控制，能够提供高度定制化和高质量的深度研究服务。祝你的项目顺利！
