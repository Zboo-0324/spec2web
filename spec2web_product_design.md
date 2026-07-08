# Spec2Web 产品定位与系统设计 V3

> 文档版本：V3.0
> 日期：2026-07-01
> 文档状态：产品设计已确认，待实施计划
> 适用范围：Spec2Web 第一版及最终产品演进边界
> 上一版本：V2.0（2026-06-29）

---

## 0. V2 → V3 变更说明

### 0.1 变更动机

V2 在架构方向上完全正确，但存在"第一版即终极产品"的范围膨胀问题。V3 的目标不是推翻 V2，而是在保持其核心架构优势的前提下，**让第一版真正可被交付和验证**。

### 0.2 主要变更清单

| # | 变更 | 对应 V2 章节 | 变更类型 |
|---|---|---|---|
| C1 | 定义 V1 分阶段交付计划 | §4.1, §16 | **新增** |
| C2 | Core Runtime 分层设计 | §5.3 | **重构** |
| C3 | 补充 Core 故障恢复机制 | §11, §12 | **新增** |
| C4 | Loop Engine 停止条件形式化 | §12.4 | **强化** |
| C5 | 增加模型分层成本策略 | §12.4, §5.3 | **新增** |
| C6 | 明确三层 Loop 层级协议 | §12.3 | **细化** |
| C7 | 文件化状态一致性策略 | §11 | **强化** |
| C8 | V1 单宿主优先 | §4.1, §15 | **收缩** |
| C9 | 质量门验证工具链具体化 | §13 | **强化** |
| C10 | 视觉原型推迟至 V1.1 | §7 | **推迟** |
| C11 | 定义"阶段内自治"边界 | §6.1 | **新增** |
| C12 | 定义用户可见交付面 | §4.3, §13 | **新增** |

### 0.3 未变更的内容

以下 V2 设计在 V3 中保持不变，继续有效：

- 产品的三层定义（用户认知 / 安装形态 / 内部架构）
- 目标用户与默认人工确认点
- 固定主干 + 受控分支的工作流模型
- 多智能体角色定义与职责分离原则
- Skills 体系的定位与契约
- Stack Pack 定位与第一版技术选型
- 需求追踪矩阵机制
- 权限、安全与回滚策略
- Git 检查点与审计日志

---

## 1. 文档目的

本文档重新定义 Spec2Web 的产品本体、用户边界、系统架构、固定开发流程、质量标准和版本范围。

Spec2Web 不再被定义为一个以 VS Code 界面为核心的代码生成插件，也不被定义为单个 Skill、单个 MCP Server 或某个模型的调用器。它们都只是产品的组成部分或宿主能力。

本文档回答以下核心问题：

1. Spec2Web 是什么；
2. 用户安装和使用的是什么；
3. Spec2Web 与 Codex、Claude Code、Skills、MCP 和 SDK 的关系；
4. 如何通过固定流程减少模型偏离需求；
5. 如何判断一个全栈项目已经达到可交付标准；
6. 第一版必须完成什么，最终版扩展什么；
7. **第一版如何分阶段交付和验证（V3 新增）**；
8. **Core Runtime 如何分层实现（V3 新增）**；
9. **Loop Engine 如何形式化停止条件（V3 新增）**。

---

## 2. 产品定位

### 2.1 一句话定位

> **Spec2Web 是一个可安装到 Codex、Claude Code 等开发智能体中的、工作流受控的全栈 Web 开发智能体插件。用户提供需求文档后，Spec2Web 按照预定义技术栈和标准工程流程，自动完成需求分析、系统设计、前后端开发、测试、修复与交付。**

### 2.2 三层定义

Spec2Web 需要同时从三个层面理解：

| 层面 | 定义 |
|---|---|
| 用户认知 | 一个能够根据需求文档完成全栈 Web 开发的智能体 |
| 安装形态 | 分别安装到 Codex 和 Claude Code 中的插件（V1 先交付 Claude Code） |
| 内部架构 | Core Runtime（内核 + 可插拔模块）、专业子代理、Skills、MCP/CLI 工具、Stack Pack、Validators 和 Loop Engine 组成的多智能体工作流系统 |

因此，"插件"和"智能体"并不冲突：

```text
用户把 Spec2Web 当作智能体使用；
Codex / Claude Code 把 Spec2Web 当作插件加载；
Spec2Web 内部通过受控工作流完成全栈开发。
```

### 2.3 核心价值

Codex 和 Claude Code 已经具备理解代码、修改文件、运行命令和分析错误的能力。Spec2Web 不重复实现这些通用能力，而是补充它们缺少的全栈项目交付体系：

```text
Codex / Claude Code 会分析和写代码；
Spec2Web 规定先做什么、后做什么、使用什么技术栈、
每一步必须产生什么、怎样验证、怎样修复以及何时可以交付。
```

Spec2Web 的差异化不在于"能够生成代码"，而在于：

- 将需求转化为可追踪的工程契约；
- 通过固定主干和受控分支组织长周期任务；
- 通过任务 DAG 和专业子代理并行缩短开发周期；
- 将开发、测试和审查职责分离，避免同一智能体自评；
- 将模型自主性限制在当前阶段和当前任务内；
- 通过确定性验证而不是模型自述判断完成；
- 交付可运行、可预览、可部署的完整项目。

---

## 3. 目标用户与使用方式

### 3.1 目标用户

目标用户具备明确业务需求，但开发经验有限。用户应当能够：

- 使用 Codex 或 Claude Code；
- 提供需求文档和补充材料；
- 阅读并确认系统对需求的理解；
- 查看界面原型和最终运行效果；
- 在必要时回答关键业务问题。

用户不需要理解：

- MCP、SDK、Skills、Agent Adapter；
- Vue、FastAPI、PostgreSQL 的内部实现；
- 数据库迁移、接口契约和自动化测试；
- Docker Compose 的具体编排逻辑。

### 3.2 用户入口

用户在宿主产品中直接表达目标：

```text
使用 Spec2Web，根据 requirements.docx 创建这个 Web 系统。
```

宿主插件识别请求并启动 Spec2Web 固定工作流。用户不需要逐个选择 Skill，也不需要手工调用 MCP 工具。

### 3.3 默认人工确认点

默认只设置两个强制人工确认点：

1. 需求基线确认；
2. 最终交付验收。

以下情况追加确认：

- 界面原型已经生成，需要进行视觉确认（V1.1 起）；
- 需求存在无法安全假设的重大歧义；
- 需要修改已确认的需求基线；
- 需要删除或覆盖已有内容；
- 需要使用真实凭据或创建付费资源；
- 需要执行不可逆数据库操作；
- 需要扩大文件、网络或命令权限；
- 自动修复无法继续且需要业务决策。

### 3.4 用户可见的交付产物（V3 新增）

V2 定义了 `.spec2web/` 的内部状态结构，但未区分哪些是用户需要理解的。V3 明确：

| 用户可见 | 用户可忽略 |
|---|---|
| 生成的业务项目源码 | `.spec2web/state/` 内部状态 |
| 需求覆盖报告 | `.spec2web/logs/` 运行日志 |
| 部署包和使用文档 | `.spec2web/checkpoints/` 检查点 |
| 已知风险清单 | `worker-runs.json` 等执行细节 |

Delivery Manager 必须生成一份**人类可读的交付摘要**（`delivery-summary.md`），包含：已完成功能、未覆盖需求、已知风险、本地运行步骤。内部状态文件不直接暴露给用户。

---

## 4. 产品边界

### 4.1 第一版范围

第一版只处理从需求文档创建全新 Web 项目的场景。

#### 4.1.1 V1 分阶段交付计划（V3 新增）

V1 被拆分为三个可独立验证的阶段：

**Phase 0 — 流程内核验证**

> 目标：证明"需求文档 → 可运行项目"的端到端流程可以跑通。

- 宿主：仅 Claude Code
- 执行模式：单 Worker 顺序执行
- Skills：仅启用 `create-project`、`requirement-analysis`、`requirement-clarification`、`system-design`、`database-design`、`api-design`、`backend-development`、`frontend-development`、`validation`、`delivery`
- 视觉原型：跳过（使用文字设计文档）
- 测试：仅后端 Pytest + 手动浏览器验证
- 并行：不支持
- 验收标准：一个真实需求文档能生成可运行系统

**Phase 1 — 质量门与多智能体**

> 目标：引入确定性质量门和职责分离。

- 新增 Test Agent（独立生成验收测试）
- 新增 Review Agent（只读审查）
- 新增 Repair Agent（有限修复 Loop）
- 启用全部 16 个 Skills
- 新增前端单元测试和 Playwright 浏览器验收
- 验收标准：B 级硬性条件的自动化验证通过

**Phase 2 — 并行与第二宿主**

> 目标：提速和多宿主覆盖。

- 引入 Worktree 隔离和 DAG 并行调度
- 引入 Codex 宿主插件
- 视觉原型能力（§7）正式启用
- 验收标准：至少两个无冲突任务并行执行；两个宿主行为一致

每个 Phase 都有独立的验收标准，可以独立发布。Phase 0 失败不影响 Phase 1 的设计方向。

#### 4.1.2 V1 每一 Phase 的共同必须项

- 作为插件安装到至少一个支持的宿主中（Phase 0/1 仅 Claude Code，Phase 2 增加 Codex）；
- 读取用户描述和需求文档；
- 生成并确认结构化需求基线；
- 按固定流程完成全栈开发；
- 使用唯一的标准 Stack Pack；
- 输出完整源码、预览和一键本地运行能力；
- Core Runtime 流程内核（Workflow Engine + State Store + Loop Engine）正常运行；
- 保存全过程状态、日志和报告；
- Core 可以从崩溃中恢复（原子写入 + 备份恢复）。

#### 4.1.3 V1 不支持

- 导入并接管任意来源的既有项目；
- 用户自由组合前端、后端、ORM 和数据库；
- 拖拽式低代码编辑器；
- 子代理脱离 Core 调度的自由协作；
- 将测试失败的项目标记为完成；
- 未经确认自动创建付费云资源。

### 4.2 最终版范围

最终版在第一版能力上增加：

- 对 Spec2Web 生成的项目持续提出变更需求；
- 需求版本、变更请求和影响分析；
- 增量任务图和局部回归测试；
- 在线预览；
- 自动部署并返回访问地址；
- 多个经过完整验证的 Stack Pack；
- Codex、Claude Code 等多个宿主适配插件。

最终版仍不将 Spec2Web 扩展为通用编程智能体，也不以维护任意既有代码库为目标。

### 4.3 交付级别

第一版以 B 级为强制合格线，最终版增加 C 级能力：

| 级别 | 交付结果 |
|---|---|
| B 级 | 完整源码、可视化预览、一键本地运行、数据库迁移、自动化测试、部署包和说明文档 |
| C 级 | 在 B 级通过后，完成在线部署、线上健康检查并返回访问地址 |

C 级部署失败不能破坏或否定已经通过的 B 级本地交付结果。

---

## 5. 总体架构

### 5.1 架构原则

> **宿主智能体及其子代理负责理解、推理、设计和编码；Spec2Web Core 负责流程、状态、任务、子代理调度、权限、验证、集成和交付。**

```text
┌─────────────────────────────────────────┐
│ Codex / Claude Code                     │
│ 对话、推理、代码生成、文件与命令能力     │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│ Spec2Web Host Plugin                    │
│ 入口 Skills、宿主适配、能力报告、Core 调用│
└───────────────────┬─────────────────────┘
                    │ MCP / CLI
┌───────────────────▼─────────────────────┐
│ Spec2Web Core Runtime                   │
│ Kernel: Workflow / State / Loop         │
│ Modules: Tasks / Agents / Validators    │
│          Integration / Delivery         │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│ Agent Execution + Tool Layer            │
│ Subagents / CLI / SDK / MCP / Host Tools│
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│ Generated Fullstack Web Project         │
└─────────────────────────────────────────┘
```

### 5.2 宿主插件

产品分别提供薄适配插件：

```text
Spec2Web for Claude Code（Phase 0 起）
Spec2Web for Codex（Phase 2 起）
```

宿主插件负责：

- 暴露主入口和辅助 Skills；
- 将宿主能力转换为统一能力描述；
- 启动或连接 Spec2Web Core；
- 加载当前任务对应的 Skill；
- 报告原生子代理、CLI/SDK Worker、隔离和最大并行能力；
- 根据 Core 指令启动、取消并监控受控 Worker；
- 将任务结果提交给 Core；
- 将进度、确认请求和交付结果显示给用户。

宿主插件不复制完整工作流，避免 Codex 和 Claude Code 形成两套行为不同的实现。

### 5.3 Core Runtime

Core Runtime 是产品的唯一流程控制中心。V3 将其分为**流程内核**与**可插拔模块**两层。

#### 5.3.1 流程内核（Phase 0 必须实现）

| 组件 | 职责 | 最小实现 |
|---|---|---|
| Workflow Engine | 控制固定阶段、受控分支和状态转换 | 阶段状态机 + 转换规则表 |
| State Store | 保存文件化项目状态和历史记录 | 文件读写 + 原子替换 + 备份恢复 |
| Loop Engine | 控制执行、验证、诊断、修复和停止 | 三层 Loop + 形式化停止条件 + 层级协议 |

这三个组件是 Spec2Web 的"心脏"——没有它们，系统无法运行。它们必须首先实现、首先测试、首先稳定。

#### 5.3.2 可插拔模块（Phase 1/2 逐步启用）

| 组件 | 职责 | 启用阶段 | Phase 0 替代 |
|---|---|---|---|
| Task Contract Manager | 生成当前任务的输入、输出、路径和完成条件 | Phase 1 | 硬编码任务定义 |
| Agent Scheduler | 根据任务 DAG、写入范围和资源预算调度专业子代理 | Phase 2 | 顺序执行器 |
| Worker Pool | 管理 Developer、Test、Review、Integration 和 Repair Worker | Phase 1 | 单 Worker 顺序调用 |
| Isolation Manager | 为并行 Worker 创建隔离工作区并防止共享文件竞争 | Phase 2 | 无隔离（单 Worker） |
| Result Integrator | 按依赖顺序验证、审查、合并 Worker 产物并执行回归检查 | Phase 1 | 简单结果传递 |
| Policy Engine | 执行技术栈、权限、审批和依赖策略；模型分层成本策略 | Phase 1 | 白名单硬编码 |
| Validators | 执行结构、契约、测试、构建和浏览器验证 | Phase 1 | 基础测试运行器 |
| Delivery Manager | 生成运行器、部署包、报告和交付清单 | Phase 0 | 最小部署包生成 |

**设计原则：** 每个可插拔模块在 Phase 0 都有一个"最小替代"实现，使流程内核可以在没有完整模块的情况下运行。模块的完整版和最小替代必须实现相同的接口契约，可以无缝替换。

### 5.4 Core 统一接口

Core 通过 MCP 或 CLI 提供宿主无关的接口：

```text
start_project
get_project_status
get_next_task
submit_task_result
get_agent_capabilities
spawn_worker
stream_worker_events
cancel_worker
collect_worker_result
validate_stage
approve_requirement_baseline
submit_ui_review
resume_project
cancel_project
deliver_project
```

Core 为每个 Worker 分别返回一个边界明确、可以验证的任务，并可同时派发多个互不冲突的任务；Core 不向任何 Worker 提交"一次生成完整系统"的开放式指令。

### 5.5 多智能体编排

Spec2Web 由 Core 确定性调度的专业子代理组成。多智能体用于并行提速和职责分离，不用于取代固定工作流。

| 角色 | 职责 | 写入权限 | 启用阶段 |
|---|---|---|---|
| Requirement Agent | 解析需求、歧义和假设 | 仅需求产物 | Phase 0 |
| Architecture Agent | 设计页面、数据、API 和权限 | 仅设计产物 | Phase 0 |
| Developer Agent | 实现一个边界明确的开发任务 | 仅任务允许路径 | Phase 0 |
| Test Agent | 根据需求基线独立编写验收测试 | 仅测试路径 | Phase 1 |
| Review Agent | 检查需求覆盖、代码质量和风险 | 只读 | Phase 1 |
| Integration Agent | 合并模块并处理接口联调 | 仅集成任务范围 | Phase 1 |
| Repair Agent | 根据明确失败修复代码 | 仅失败相关路径 | Phase 1 |

开发者可以为自己的模块编写局部单元测试，但最终验收测试由独立 Test Agent 根据需求基线生成，实际通过与否由 Validators 运行测试后判定。Review Agent 不修改生产代码和测试，只输出结构化审查结果。

需求基线和总体架构采用单一责任人顺序产出，再由 Review Agent 独立审查，避免多个代理同时修改核心契约。主要并行区间位于契约冻结后的模块开发、独立测试、只读审查和无冲突修复阶段。

Core 只有在以下条件全部满足时才允许并行（Phase 2 起）：

```text
任务依赖已经完成
共享需求和技术契约已经冻结
写入路径不重叠
任务具有独立验证命令
Worker 工作区相互隔离
合并、回滚和资源预算明确
```

每个 Worker 必须获得完整 Task Contract：

```text
task_id
role
input_artifacts
allowed_paths
read_only_paths
forbidden_paths
expected_outputs
required_validations
tool_permissions
execution_budget
max_retries
max_duration
max_cost
base_checkpoint
```

并行 Worker 在独立 Worktree 或等价沙箱中执行。Core 分别验证产物，由 Review Agent 只读审查，再按 DAG 顺序逐个合并；每次合并后运行受影响范围回归测试。发生写入冲突、契约冲突或回归失败时停止合并并重新规划，禁止 Worker 直接覆盖彼此结果。

---

## 6. 固定工作流模型

### 6.1 工作流原则

Spec2Web 采用：

> **固定主干 + 受控分支 + 有界自治**

- 固定主干：所有项目必须经历相同的工程阶段；
- 受控分支：只有预定义条件满足时才能进入特定分支；
- **有界自治（V3 细化）**：模型可以在当前任务边界内选择具体实现方式，但不得跨越以下边界。

#### 6.1.1 有界自治的边界（V3 新增）

模型在阶段内可以**自由选择**：
- 具体算法实现
- 组件内部结构
- 变量命名和代码组织
- 局部测试的编写方式

模型在阶段内**不得自由**：
- Stack Pack 规定的框架、库和工具
- 目录结构和命名规范
- 已冻结的 API 契约和数据模型
- 其他任务的写入路径
- 验证命令和通过标准

Policy Engine 在任务执行前、中、后均有拦截能力：
- **执行前**：Task Contract 明确允许路径和禁止路径
- **执行中**：工具调用经过白名单过滤
- **执行后**：Validators 检查产物是否超出允许范围

其余原则不变：
- 质量门：只有验证通过才能进入下一阶段；
- 人工门：需要确认时，Core 必须等待用户明确决定。

### 6.2 固定主流程

```text
项目初始化
→ 需求接收
→ 需求结构化与歧义检查
→ 用户确认需求基线
→ 系统、页面、数据和交互设计
→ [V1.1 起] 界面原型生成与视觉确认
→ 数据库、API 和权限契约定稿
→ 任务 DAG 与并行计划生成
→ 项目骨架创建
→ [Phase 2 起] 独立 Developer Agents 并行完成前后端任务
→ [Phase 0/1] 单个 Developer Agent 顺序完成开发
→ [Phase 1 起] 独立 Test Agent 生成验收测试
→ [Phase 1 起] Review Agent 审查任务产物
→ Core 验证并按依赖顺序合并
→ 前后端联调
→ 测试与浏览器验收
→ 有限修复 Loop
→ 本地运行与部署包生成
→ 用户最终验收
```

### 6.3 状态转换约束

示例约束：

```text
需求未确认                 → 禁止生成正式代码
系统设计不一致             → 禁止生成任务图
当前任务局部测试失败       → 禁止将任务标记为完成
API 契约未定稿             → 禁止实现依赖该契约的页面
任务依赖或写入范围冲突     → 禁止并行调度
Worker 未通过局部验证       → 禁止合并
Review Agent 发现阻断问题   → 禁止进入集成阶段
系统验收失败               → 只能进入修复、回退或阻塞状态
B 级交付条件未满足         → 禁止生成完成报告
视觉能力不可用             → 允许记录降级后继续
高风险操作未获用户批准     → 禁止执行
```

宿主智能体不能自行修改 Core 状态，也不能仅凭自然语言声明任务完成。

### 6.4 受控分支示例

```text
存在多用户角色     → 进入认证与权限分支
包含文件上传       → 进入文件存储分支
包含报表导出       → 进入导出与文件验证分支
包含第三方服务     → 进入外部集成与凭据确认分支
测试失败           → 进入修复分支
部署被用户请求     → 在 B 级通过后进入 C 级部署分支
```

分支影响任务内容，不改变主流程的工程纪律。

### 6.5 并行开发阶段

> **V3 标注为 Phase 2 目标。** Phase 0/1 以顺序执行替代。

任务 DAG 决定并行批次。契约冻结后可以同时执行：

```text
Developer A：设备后端模块
Developer B：巡检后端模块
Developer C：设备前端页面
Developer D：巡检前端页面
Test Agent：基于需求生成独立验收测试
```

数据库迁移、共享路由入口、全局状态、OpenAPI 契约等共享产物必须由单一任务串行修改。并行只影响执行速度，不改变阶段顺序、质量门和用户确认点。

---

## 7. 界面原型与视觉确认

> **V3 变更：完整视觉原型阶段推迟至 V1.1（Phase 2 之后）。V1 使用替代方案。**

### 7.1 V1 替代方案

V1（Phase 0/1）使用以下替代机制：

```text
页面与交互设计（文字文档）
→ 前端直接按设计文档实现
→ 用户通过浏览器查看实际页面
→ 反馈修改意见进入修复 Loop
```

### 7.2 推迟理由

1. V1 的核心验证目标是"需求文档 → 可运行系统"的流程闭环，视觉原型不是必要条件
2. 视觉原型需要浏览器渲染能力，增加环境依赖和失败面
3. Element Plus 作为成熟组件库，默认视觉效果有基本保障
4. 将视觉原型推迟可以释放 Phase 0/1 的开发资源聚焦于流程内核和质量门

### 7.3 V1.1 视觉原型（保留设计，Phase 2 后启用）

#### 7.3.1 阶段位置

界面原型阶段位于页面、数据和交互设计完成之后，正式任务图和前端编码之前。

```text
需求基线
→ 页面与交互设计
→ 界面原型和视觉确认
→ 契约定稿
→ 任务规划与开发
```

#### 7.3.2 能力检测

宿主插件必须报告能力，不得通过模型名称硬编码推断：

```text
vision_input
image_generation
browser_render
screenshot
```

#### 7.3.3 降级策略

按以下优先级执行：

1. 支持代码生成和浏览器渲染：生成可运行界面原型、截图和预览地址；
2. 支持图片生成：额外生成视觉概念图，作为风格参考；
3. 不支持生图但支持浏览器渲染：继续使用代码原型完成视觉确认；
4. 生图和浏览器渲染均不可用：提示用户、记录 `skipped_unsupported`、保留文字设计并继续流程。

缺少图像能力不能导致整个开发任务停止。

#### 7.3.4 用户评审循环

```text
生成 UI 原型 v1
→ 用户查看
├── 同意：冻结为 UI 设计基线
├── 修改：记录反馈，生成新版本，再次评审
└── 跳过：记录 skipped_by_user 并继续
```

阶段状态：

```text
pending
awaiting_review
changes_requested
approved
skipped_by_user
skipped_unsupported
```

主要产物：

```text
ui-spec.json
ui-prototype/
ui-screenshots/
ui-review-history.json
```

只有 `approved` 的视觉设计才成为前端实现的强约束。跳过时，前端仍必须遵守文字版页面、交互和设计规范。

---

## 8. 阶段产物与需求追踪

### 8.1 阶段契约

| 阶段 | 必须产物 | 放行条件 |
|---|---|---|
| 需求接收 | 原始文档、附件清单 | 输入可读取 |
| 需求分析 | 结构化需求、歧义、假设 | 结构校验通过 |
| 需求确认 | 已批准需求基线 | 用户确认 |
| 系统设计 | 页面、数据、API、权限、验收设计 | 一致性校验通过 |
| UI 评审 | 原型、截图、评审记录或跳过记录 | 批准或合法降级 |
| 任务规划 | 带依赖任务图 | 所有需求已映射 |
| 项目骨架 | 固定 Stack Pack 项目 | 安装和启动检查通过 |
| 模块开发 | 代码和局部测试 | 单任务验证通过 |
| 系统联调 | 可运行完整项目 | 核心业务链路连通 |
| 验收修复 | 验收报告 | 强制质量门通过 |
| 项目交付 | 源码、运行器、部署包、文档 | 用户最终验收 |

每个阶段只读取已批准的正式产物，不能把对话中的临时推测当作工程事实。

### 8.2 需求追踪

每条需求生成稳定编号：

```text
REQ-001 用户可以创建设备
REQ-002 用户只能查看自己创建的设备
REQ-003 管理员可以查看全部设备
```

每条需求必须映射到实现和验收：

```text
REQ-002
├── 页面：设备列表
├── API：GET /api/devices
├── 权限规则：owner_id = current_user.id
├── 后端任务：TASK-BE-004
├── 前端任务：TASK-FE-006
└── 验收测试：TEST-E2E-003
```

系统自动检查：

- 未被实现的需求；
- 没有需求来源的额外功能；
- 没有前端消费者的 API；
- 页面存在但缺少后端能力；
- 权限只在前端隐藏而没有后端校验；
- 已实现但没有验收测试的核心流程。

### 8.3 正式产物优先级

```text
用户确认的需求基线
    ↓
系统设计与契约
    ↓
任务图
    ↓
代码与测试
    ↓
验收报告
```

模型不得自行修改已确认需求。最终版中的新增或变更需求必须形成变更请求、影响分析和新需求基线版本。

---

## 9. Skills 体系

### 9.1 Skills 的定位

Skills 是宿主智能体执行当前任务时使用的专业工作说明书。Skills 负责"怎样完成"，Core 负责"现在完成什么"和"是否完成"。

### 9.2 第一版 Skills

```text
skills/
├── create-project/
├── requirement-analysis/
├── requirement-clarification/
├── system-design/
├── ui-prototype/
├── database-design/
├── api-design/
├── task-planning/
├── backend-development/
├── frontend-development/
├── test-authoring/
├── code-review/
├── integration/
├── validation/
├── repair/
└── delivery/
```

### 9.3 Skills 分阶段启用

| Phase | 启用的 Skills |
|---|---|
| Phase 0 | `create-project`, `requirement-analysis`, `requirement-clarification`, `system-design`, `database-design`, `api-design`, `backend-development`, `frontend-development`, `validation`, `delivery` |
| Phase 1 | 全部 16 个 Skills |
| Phase 2 | 全部 16 个 Skills（无新增） |

### 9.4 Skill 契约

每个 Skill 必须明确：

- 触发条件；
- 当前阶段；
- 输入文件；
- 允许使用的工具；
- 允许和禁止修改的路径；
- 必须生成的产物；
- 必须执行的验证；
- 成功、失败和阻塞输出格式；
- 不得自行改变的正式契约。

Skills 不保存唯一状态，不决定全局阶段，不直接宣布整个项目完成。

同一个 Skill 可以被多个同角色 Worker 使用；角色、权限和隔离范围由 Task Contract 决定，而不是由 Skill 自行扩大。

---

## 10. Stack Pack

### 10.1 定位

技术栈不是一组任意组合的配置，而是一套经过验证、能够稳定生成和交付项目的工程能力包。

```text
stack-packs/
└── vue-fastapi/
    ├── stack-policy.yaml
    ├── project-template/
    ├── skills/
    ├── coding-rules/
    ├── validation-rules/
    ├── commands/
    └── delivery-template/
```

### 10.2 第一版唯一 Stack Pack

```text
前端
- Vue 3
- TypeScript
- Vite
- Element Plus
- Vue Router
- Pinia
- Axios

后端
- FastAPI
- Python
- SQLAlchemy
- Alembic
- Pydantic
- REST API

数据库
- PostgreSQL

测试与验收
- Pytest
- 前端单元测试（Vitest）
- Playwright 浏览器验收

交付
- Docker Compose
- Nginx
- 环境变量模板
- 一键启动和停止脚本
```

第一版不提供其他技术栈选项。

### 10.3 Stack Pack 规则

模型必须：

- 从标准模板创建项目；
- 遵守规定目录和命名；
- 只使用允许的依赖；
- 使用规定迁移、测试、构建和运行命令；
- 不得擅自更换框架、数据库或包管理策略；
- 不得通过删除测试或降低校验强度使任务通过。

未来新增技术栈时，必须发布完整且独立验证的 Stack Pack，不允许用户将未经验证的前后端组件随意混搭。

---

## 11. Spec2Web 工作状态

Spec2Web 自身不引入 SQLite。状态使用可查看、可迁移、可版本化的文件保存：

```text
.spec2web/
├── input/
│   ├── requirement.md
│   └── attachments/
├── state/
│   ├── project.json
│   ├── tool-capabilities.json
│   ├── requirements.json
│   ├── requirement-baseline.json
│   ├── workflow-state.json
│   ├── task-graph.json
│   ├── agent-capabilities.json
│   ├── worker-runs.json
│   ├── decisions.json
│   └── traceability.json
├── design/
│   ├── system-design.json
│   ├── ui-spec.json
│   ├── openapi.yaml
│   └── db-schema.json
├── ui-prototype/
├── ui-screenshots/
├── logs/
│   ├── events.jsonl
│   ├── commands.jsonl
│   └── validation.jsonl
├── reports/
│   ├── requirement-coverage.md
│   ├── validation-report.md
│   ├── blocked-report.md
│   └── delivery-report.md
└── checkpoints/
```

生成的业务项目从开发、测试到部署统一使用 PostgreSQL，避免本地 SQLite、生产 PostgreSQL 所造成的行为差异。

### 11.1 状态一致性策略

文件化状态的核心风险是**多文件间不一致**和**并发写入冲突**。V3 定义以下策略：

**原子替换：** 所有状态文件写入使用"写入临时文件 → 原子重命名"模式，防止写入过程中崩溃导致文件损坏。

```python
# 写入模式
temp_path = path + ".tmp"
write(temp_path, json.dumps(data))
os.replace(temp_path, path)  # 原子替换
```

**状态分层：**

| 类别 | 文件 | 写入频率 | 一致性要求 |
|---|---|---|---|
| 契约类 | `requirements.json`, `requirement-baseline.json`, `openapi.yaml`, `db-schema.json` | 低（仅在用户确认后） | 强一致（多契约间必须兼容） |
| 流程类 | `workflow-state.json`, `task-graph.json` | 中（阶段转换时） | 自洽（单文件内一致即可） |
| 执行类 | `worker-runs.json`, `traceability.json` | 高（每次 Worker 执行后） | 最终一致（允许短暂不一致，合并时校验） |

**状态恢复：** Core 启动时执行状态完整性检查：
1. 所有必须文件是否存在
2. 契约类文件间是否一致（如 `task-graph.json` 中的任务是否都引用了 `requirements.json` 中存在的需求）
3. 如果不一致，Core 进入恢复模式：回退到最后有效检查点，并报告损坏状态

---

## 12. Loop Engine 与异常处理

### 12.1 统一 Loop

```text
准备任务
→ Core 根据 DAG 调度一个或多个专业 Worker
→ Worker 在隔离环境执行
→ 收集各 Worker 的修改、命令和日志
→ 独立 Review Agent 审查
→ 执行确定性验证
→ 分类结果
→ 继续、修复、回退、降级或阻塞
```

### 12.2 结果分类

| 状态 | 含义 | 处理 |
|---|---|---|
| `passed` | 当前任务验证通过 | 进入下一任务 |
| `retryable` | 编译、测试等可修复失败 | 进入修复 Loop |
| `replan_required` | 契约或任务规划存在冲突 | 回到相应设计阶段 |
| `user_decision_required` | 缺少业务决策 | 暂停并询问用户 |
| `capability_unavailable` | 可选能力不可用 | 记录降级并继续 |
| `policy_denied` | 操作违反权限策略 | 禁止并请求授权 |
| `environment_blocked` | 缺少不可替代环境 | 输出处理建议和阻塞报告 |

### 12.3 三层 Loop

1. 单任务 Loop：实现一个有限任务，执行局部验证和修复；
2. 阶段 Loop：检查同一阶段全部任务的契约一致性；
3. 系统 Loop：启动完整系统，执行集成和浏览器验收。

局部问题不得触发无依据的整项目重新生成。

同一阶段存在多个互不冲突的失败时，Core 可以派发多个 Repair Agent 并行修复。涉及同一共享契约、同一迁移或重叠写入路径的失败必须串行处理。

#### 12.3.1 层级协议

**层级调用规则：**

```text
系统 Loop (L3)
  └── 调用 阶段 Loop (L2)
        └── 调用 单任务 Loop (L1)
```

**向上冒泡规则：**

| 当前层 | 异常类型 | 冒泡目标 | 冒泡条件 |
|---|---|---|---|
| L1 单任务 | `retryable` | 不冒泡 | L1 自行进入修复 |
| L1 单任务 | 修复次数耗尽 | L2 阶段 | L1 无法解决 |
| L1 单任务 | `replan_required` | L2 阶段 | 任务规划冲突 |
| L2 阶段 | 多个 L1 同时 `replan_required` | L3 系统 | 契约需要变更 |
| L2 阶段 | 契约回滚后仍失败 | L3 系统 | 设计阶段需要回溯 |
| L3 系统 | 集成失败 | 用户决策 | 需要业务判断 |
| L3 系统 | B 级条件始终不满足 | 用户决策 | 需求可能需要调整 |

**向下恢复规则：**

- L2 回滚时，L2 内所有已完成的 L1 任务产物保留，但标记为"待重验证"
- L3 回滚到设计阶段时，L2/L1 产物全部冻结，等待新契约生成
- 任何层级恢复后，必须从检查点重新验证，不得跳过

### 12.4 重试与停止

#### 12.4.1 形式化停止条件

每个停止条件必须对应一个**可程序化检查的谓词**，由独立判定模块检查，不由执行 Worker 自身判断：

| 停止条件 | 形式化谓词 | 检查方式 |
|---|---|---|
| 同一错误重复出现 | `error_fingerprint(current_failure) ∈ previous_failures[-3:]` | 错误指纹哈希比对 |
| 修复导致更多失败 | `validation_count(after) > validation_count(before)` | 验证结果计数比较 |
| 需要改变已确认需求 | `proposed_fix.modifies(requirement_baseline)` | 影响分析 |
| 需要高风险权限 | `requested_action.risk_level > task_contract.max_risk` | 策略引擎检查 |
| 缺少关键业务决策 | `failure.requires_user_input == True` | 失败分类器 |
| 达到次数上限 | `retry_count >= task_contract.max_retries` | 计数器 |
| 达到时间上限 | `elapsed_time > task_contract.max_duration` | 计时器 |
| 达到成本上限 | `accumulated_cost > task_contract.max_cost` | 成本追踪器 |

**独立判定原则：** 停止条件由一个**独立的轻量判定模块**检查。这与 Loop Engineering 中 `/goal` 的独立验证模型理念一致——制作者不能同时是检查者。

#### 12.4.2 模型分层成本策略

| 任务类型 | 推荐模型层级 | 理由 |
|---|---|---|
| 需求分析与结构化 | 强模型 | 影响全局，错误成本高 |
| 系统设计与契约 | 强模型 | 影响所有后续阶段 |
| 标准 CRUD 开发 | 中等模型 | 任务边界明确，模式固定 |
| 修复（已知错误） | 中等或快速模型 | 有明确错误上下文，无需强推理 |
| 验证判定 | 独立轻量模型 | 仅需判断条件是否满足，无需生成 |
| 代码审查 | 强模型 | 需要发现隐藏问题 |
| 文档生成 | 快速模型 | 模板化工作 |

**成本预算分配：** 每个项目设定总成本预算，按阶段分配配额。Phase 0 可以硬编码配额，Phase 1 由 Policy Engine 动态调整。

#### 12.4.3 重试控制

每次重试必须包含新的诊断依据：

- 失败日志；
- 失败测试；
- 相关文件；
- 文件差异；
- 上一次修复结果。

Loop 必须控制：

- 最大修复次数；
- 最大执行时间；
- 最大模型和工具成本；
- 错误指纹；
- 重复错误停止条件；
- 修复前检查点；
- 失败后的回滚路径；
- 最大并行 Worker 数量；
- CPU、内存和并发命令预算。

出现以下情况时停止自动修复：

- 同一错误重复出现；
- 修复导致更多验证失败；
- 需要改变已确认需求；
- 需要高风险权限；
- 缺少关键业务决策；
- 缺少不可替代的环境或能力；
- 达到次数、时间或成本上限。

停止后必须生成阻塞报告，并允许用户处理后从当前检查点恢复。

### 12.5 Core 故障恢复

V2 未涉及 Core 自身故障的处理。V3 补充：

**Core 崩溃恢复流程：**

```
Core 启动
  → 检查 .spec2web/state/ 完整性
  → 完整：从 workflow-state.json 恢复当前阶段
  → 不完整：
      → 检查 checkpoints/ 是否有有效快照
      → 有：恢复到最新快照，标记快照之后的工作为"待重验证"
      → 无：报告 Core 状态损坏，需要用户决策
```

**Worker 结果幂等性：** Worker 提交结果时携带 `task_id + execution_id`。Core 根据 `execution_id` 去重——同一 `execution_id` 的结果只处理一次。Core 崩溃后重启不会重复处理已完成的 Worker 结果。

**状态文件恢复：** 每个状态文件维护一个 `.backup` 副本。写入新状态前先备份旧状态。如果新状态写入失败，Core 可以从 `.backup` 恢复。

---

## 13. 质量门与验收

### 13.1 强制质量门

| 质量门 | 验证内容 | 验证工具/方式 | 通过条件 |
|---|---|---|---|
| 需求门 | 每条需求已映射 | Core 自动检查 traceability.json | 覆盖率为 100% |
| 设计门 | 页面、权限、API、数据库设计一致 | JSON Schema 验证 + 自定义一致性检查器 | Schema 验证通过 |
| 骨架门 | 依赖可安装，目录符合 Stack Pack | `pip install -r requirements.txt` + 目录结构检查脚本 | 安装成功 + 结构匹配 |
| 模块门 | 前后端局部测试通过 | Pytest（后端）+ Vitest（前端） | 退出码为 0 |
| 集成门 | 前端正确调用后端，迁移执行成功 | Alembic 升级 + API 端到端冒烟测试 | 迁移成功 + 冒烟通过 |
| 系统门 | 完整系统可以启动，核心链路可用 | Docker Compose 启动 + 健康检查脚本 | 健康检查通过 |
| 浏览器门 | Playwright 完成核心用户操作 | Playwright 测试套件 | 全部测试通过 |
| 交付门 | 源码、运行器、部署包和文档完整 | 文件清单检查 + 启动脚本执行测试 | 清单匹配 + 启动成功 |

### 13.2 干净环境验收

最终验收必须从干净状态执行：

```text
清理临时状态
→ 根据锁文件重新安装依赖
→ 创建空 PostgreSQL 数据库
→ 执行全部迁移
→ 启动 Docker Compose
→ 等待健康检查
→ 运行后端测试
→ 构建前端
→ 运行浏览器验收
→ 停止并重新启动
```

### 13.3 B 级硬性条件

1. `docker compose up` 可以启动完整系统；
2. PostgreSQL 自动初始化并完成迁移；
3. 后端健康检查通过；
4. 前端页面可以访问；
5. 核心需求具有浏览器验收场景；
6. 前端构建和后端测试通过；
7. 项目不包含明文密钥和本机绝对路径；
8. 项目提供环境变量示例；
9. 项目提供一键启动和停止脚本；
10. 交付包含源码、迁移、部署包和使用文档；
11. 交付包含需求覆盖报告；
12. 交付明确列出未完成事项和已知风险。

### 13.4 C 级部署

C 级流程只能在 B 级通过后运行：

```text
选择部署目标
→ 检查凭据和配置
→ 请求高风险操作确认
→ 自动部署
→ 运行线上健康检查
→ 返回访问地址和部署报告
```

---

## 14. 权限、安全与回滚

### 14.1 文件权限

每个任务必须声明：

```text
allowed_paths
read_only_paths
forbidden_paths
expected_outputs
```

默认禁止访问项目外文件、SSH 密钥、浏览器凭据、系统配置、其他项目目录和真实 `.env` 密钥。

### 14.2 命令策略

Stack Pack 提供命令白名单和风险分级。

默认允许：

- 项目依赖安装；
- 测试、构建、格式和类型检查；
- Alembic 迁移；
- Docker Compose 项目操作；
- Git 状态和差异查看；
- Playwright 本地验收。

需要确认：

- 删除或覆盖已有内容；
- 访问项目外目录；
- 使用部署凭据；
- 推送远程仓库；
- 创建付费资源；
- 执行破坏性数据库迁移。

默认禁止：

- 提权命令；
- 修改操作系统安全配置；
- 读取凭据目录；
- 关闭安全软件；
- 未经确认执行不受信任的远程脚本。

### 14.3 Git 与检查点

新生成项目自动初始化本地 Git，但不连接远程仓库：

```text
项目骨架完成 → 基线提交
每个阶段完成 → 阶段检查点
修复前         → 临时快照
最终交付       → 交付标签
```

Spec2Web 同时保存任务级文件差异，防止模型通过删除功能、测试或校验规则来消除错误。

### 14.4 敏感信息

生成项目只包含 `.env.example`。真实凭据不得写入 Prompt、日志、Git 或交付包，应由用户输入或通过宿主安全存储提供。

### 14.5 审计

结构化日志必须记录：

- 任务发起者；
- 宿主、Skill 和 Core 版本；
- 工具调用和命令；
- 文件修改；
- 用户批准操作；
- 验证结果；
- 修复、回退或阻塞原因。

---

## 15. 插件与目录结构

### 15.1 共享核心

```text
spec2web/
├── core/
│   ├── kernel/              # Phase 0 必须
│   │   ├── workflow/
│   │   ├── state/
│   │   └── loops/
│   ├── modules/             # Phase 1/2 逐步启用
│   │   ├── tasks/
│   │   ├── orchestration/
│   │   ├── workers/
│   │   ├── isolation/       # Phase 2
│   │   ├── integration/
│   │   ├── policies/
│   │   ├── validators/
│   │   └── delivery/
│   └── recovery/            # Phase 0 必须
├── skills/
├── stack-packs/
│   └── vue-fastapi/
├── mcp-server/
├── cli/
├── adapters/
│   ├── claude-code/         # Phase 0
│   └── codex/               # Phase 2
├── executors/
│   ├── native-subagent/
│   ├── cli-worker/
│   └── sdk-worker/
└── tests/
```

### 15.2 分发包

```text
Spec2Web Claude Code Plugin（Phase 0 起）
├── Claude Code 插件清单
├── 入口 Skills
├── MCP / Core 配置
└── 共享 Core 依赖

Spec2Web Codex Plugin（Phase 2 起）
├── Codex 插件清单
├── 入口 Skills
├── MCP / Core 配置
└── 共享 Core 依赖
```

两个插件共享同一套工作流、Stack Pack、验证器和状态格式。宿主差异只能存在于适配层。

---

## 16. 第一版验收目标

### 16.1 Phase 0 验收目标

```text
安装 Spec2Web Claude Code 插件
→ 提交一个真实需求文档
→ 生成并确认需求基线
→ 完成系统和页面设计（文字文档）
→ 单个 Developer Agent 顺序完成开发
→ 后端 Pytest 测试通过
→ 从干净环境一键启动
→ 用户手动浏览器验证核心功能
→ 输出最小部署包
```

Phase 0 完成的判断依据：
1. 至少一个真实需求文档完成端到端流程
2. 生成的系统可以从干净环境启动
3. 后端测试自动化通过
4. Core 状态可以从崩溃中恢复

### 16.2 Phase 1 验收目标

在 Phase 0 基础上增加：
1. Test Agent 独立生成需求驱动的验收测试
2. Review Agent 以只读方式输出审查结果
3. Repair Agent 在有限 Loop 内修复可修复失败
4. Playwright 浏览器验收自动化
5. 全部 16 个 Skills 启用
6. B 级硬性条件的自动化验证

### 16.3 Phase 2 验收目标

在 Phase 1 基础上增加：
1. 至少两个无写入冲突的开发任务能够并行执行
2. 每个 Worker 使用独立任务契约和隔离工作区
3. Test Agent 独立产生需求驱动的验收测试
4. Review Agent 以只读方式输出审查结果
5. Core 能够按 DAG 顺序合并并执行回归验证
6. Codex 宿主插件行为与 Claude Code 插件一致
7. 视觉原型能力启用

---

## 17. 最终版迭代模型

最终版只维护由 Spec2Web 创建的项目：

```text
需求基线 v1
→ 用户提交变更请求 CR-001
→ 影响分析
→ 用户确认
→ 需求基线 v2
→ 增量任务图
→ 局部开发
→ 影响范围回归测试
→ 新版本交付
```

每次迭代必须保留：

- 原始变更请求；
- 受影响需求、页面、API、数据和测试；
- 新旧基线差异；
- 增量任务图；
- 回归验证结果；
- 新版本交付记录。

---

## 18. 主要风险与控制

| 风险 | 控制方式 |
|---|---|
| 模型误解需求 | 结构化需求、显式假设、用户确认基线 |
| 长任务逐步漂移 | 固定阶段、正式产物、需求追踪矩阵 |
| 模型提前宣布完成 | Core 状态机和确定性质量门 |
| 前后端不一致 | OpenAPI、数据模型和页面动作一致性检查 |
| UI 与用户预期不符 | 可运行原型和用户视觉确认 |
| 修复陷入循环 | 错误指纹、次数/时间/成本上限 |
| 不支持视觉能力时任务停止 | 能力检测、降级状态、自动继续 |
| 修改范围失控 | Task Contract、路径权限、Git 检查点 |
| 子代理并行修改冲突 | DAG 依赖、写入集合分析、隔离工作区、顺序合并 |
| 开发代理自测自评 | 独立 Test Agent、只读 Review Agent、确定性 Validators |
| 并行消耗超过本机资源 | 能力报告、最大 Worker 数、CPU/内存/成本预算 |
| 宿主不支持原生子代理 | CLI/SDK Worker 适配或无损顺序降级 |
| 环境差异导致无法运行 | Docker Compose、锁文件、干净环境验收 |
| 本地通过但生产失败 | PostgreSQL 开发生产一致、C 级线上健康检查 |
| 凭据泄露 | `.env.example`、宿主安全存储、日志脱敏 |
| Core 崩溃导致状态损坏 | 原子写入 + 备份恢复 + 检查点 |
| 模型成本超支 | 模型分层策略 + 阶段配额 |
| 文件状态不一致 | 状态分层 + 完整性检查 |
| 第一版范围失控 | 分阶段交付计划 |
| 停止条件判定不准 | 独立判定模块 + 形式化谓词 |

---

## 19. 核心产品决策

1. Spec2Web 的最终交付形态是插件，不是单个 Skill；
2. Skills 是插件内部的专业工作说明书；
3. Codex 和 Claude Code 是宿主智能体，不是被 Spec2Web 替代的组件；
4. Spec2Web Core 是唯一工作流和状态控制中心；
5. Core 在第一版即提供任务 DAG、专业 Worker、隔离、审查和结果集成能力；
6. 多子代理用于并行提速和职责分离，不能脱离 Core 自由协作；
7. Developer、Test、Review、Integration 和 Repair 由不同角色的 Worker 承担；
8. 并行任务必须依赖已满足、写入范围不重叠并具有独立验证；
9. 采用固定主干、受控分支、有界自治；
10. 模型不能自行跳过阶段或宣布整个项目完成；
11. 第一版只从零生成项目，最终版支持生成项目的持续迭代；
12. 第一版只提供 Vue 3 + FastAPI + PostgreSQL + Docker Compose Stack Pack；
13. Spec2Web 状态使用文件保存，不引入 SQLite；
14. UI 评审优先使用可运行代码原型，生图只是辅助；
15. 视觉能力不足必须降级继续，不能卡死任务；
16. B 级交付是第一版硬性合格线，C 级是最终部署能力；
17. Loop 必须由验证证据驱动，并设置明确停止条件；
18. 默认只有需求基线和最终交付两个强制人工确认点；
19. 高风险操作、重大歧义和视觉评审按条件追加确认；
20. V1 分三个阶段交付，每个阶段有独立验收标准；
21. Core Runtime 分为流程内核与可插拔模块，内核优先实现；
22. Loop Engine 的停止条件必须可程序化验证，由独立模块判定；
23. 模型按任务类型分层使用，验证判定使用独立轻量模型；
24. V1 先发布 Claude Code 插件，Phase 2 增加 Codex 插件；
25. 视觉原型推迟至 V1.1，V1 使用文字设计文档替代；
26. 状态文件使用原子替换写入，维护备份副本；
27. 每个可插拔模块必须有最小替代实现，支持渐进式启用。

---

## 20. 参考资料

- Codex Agent Skills：<https://developers.openai.com/codex/skills>
- Codex Plugins：<https://developers.openai.com/codex/plugins>
- Codex Build Plugins：<https://developers.openai.com/codex/plugins/build>
- Claude Code Plugins：<https://code.claude.com/docs/en/plugins>
- Claude Code Plugins Reference：<https://code.claude.com/docs/en/plugins-reference>
- Model Context Protocol：<https://modelcontextprotocol.io/specification/latest>

---

## 21. 最终结论

Spec2Web 的最终产品定义为：

> **一个通过插件安装到 Claude Code（及后续 Codex 等）开发智能体中，以 Core Runtime 流程内核控制固定开发流程，以可插拔模块提供任务 DAG 调度和并行能力，以专业子代理分阶段完成开发、测试、审查、集成与修复，以 Skills 约束专业方法，以 MCP、CLI、SDK 和宿主工具执行工程操作，以形式化质量门和有限 Loop 保证交付结果的全栈 Web 开发智能体。**

V3 相对于 V2 的核心变化不在于"做什么"，而在于"怎么分阶段做"：

```text
V2: 一次性交付完整系统
V3: 先让流程跑通（Phase 0）
    → 再加入质量门和多智能体（Phase 1）
    → 最后实现并行和第二宿主（Phase 2）
```

对用户而言，使用方式保持不变：

```text
提交需求文档
→ 确认需求
→ 等待自动开发与验收
→ 预览系统
→ 一键本地运行或部署
```

对系统而言，V3 的每一步都有更明确的**验证工具、停止条件、恢复机制和成本策略**。Spec2Web 的产品价值不仅是让模型在可控流程中交付项目，更是让这个流程本身**可以被增量实现、独立验证和可靠恢复**。