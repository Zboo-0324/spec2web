# Spec2Web Skill V1 Design

## 1. 背景

现有 `spec2web_product_design.md` 定义的是完整产品蓝图：Core Runtime、宿主插件、MCP/CLI、任务调度、多智能体、状态恢复和质量门。这个版本适合作为长期方向，但第一版实现成本过高。

V1 的目标是先验证工作流本身，而不是先实现工作流平台。Spec2Web V1 应交付为一个跨宿主 Skill，指导智能体按受控流程完成全栈 Web 项目开发。

## 2. 产品定义

Spec2Web V1 是一个宿主中立的全栈 Web 开发工作流 Skill。它通过轻量状态文件、任务拆解、角色协议、worktree 隔离、验证循环和交付报告，约束智能体从需求文档推进到可运行项目。

它不提供代码框架，不生成模板项目，不实现 Core Runtime，不提供 MCP Server，不做后台调度。它可以指导主控智能体使用 Git worktree 做隔离开发，并在用户或 Orchestrator 明确选择时运行受控多 worker；但它不提供自动调度器、后台 worker 池或无人值守批量合并。

一句话定位：

> Spec2Web 是一个可通过 `/spec2web ...` 显式启用的全栈开发工作流 Skill，用轻量状态文件和有限 Loop 约束智能体完成需求分析、系统设计、任务拆解、开发、验证、修复和交付。

## 3. V1 范围

V1 包含：

- 跨宿主 Skill 文件夹，Skill 名称为 `spec2web`
- `agents/openai.yaml` UI 元数据
- `/spec2web ...` 斜杠命令入口
- Claude Code 和 Hermes 安装说明
- 状态初始化脚本
- 项目规则读取机制
- 需求基线、系统设计和任务拆解流程
- 角色分离协议
- 可选 Git worktree 隔离模式
- 受控多 worker worktree 模式
- 任务级开发 Loop
- 有限修复 Loop
- 验证记录和交付报告
- Superpowers 可选增强

V1 不包含：

- Core Runtime
- MCP Server
- CLI 全局命令，例如 `spec2web init`
- SDK Worker
- 自动子代理调度器或后台 worker 池
- 自动并行任务选择、自动 worktree 池或无人值守批量合并
- 代码模板或 Stack Pack 实现
- 自动部署
- Marketplace、Hub 或插件分发配置

## 4. V2 预留

V2 可以增加：

- Codex、Claude Code、Hermes 的分发适配层
- 更完整的平台元数据和分发清单
- Hermes hub/tap 或类似分发配置
- Claude Code 插件打包配置
- 可选全局 CLI，例如 `spec2web init`
- 示例项目和示例任务
- 更强的状态检查脚本或验证器
- 自动 worktree 池、并行 worker 调度和冲突分析
- 更完整的 Skill marketplace 发布材料

V2 不应改变 V1 的核心工作流事实来源。V1 的状态文件、任务协议和角色协议应作为后续产品化的基础。

## 5. Skill 文件夹结构

V1 结构：

```text
spec2web/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── install.md
│   ├── state-files.md
│   ├── loop-engineering.md
│   ├── task-breakdown.md
│   ├── role-protocol.md
│   ├── worktree-mode.md
│   └── delivery-checklist.md
└── scripts/
    ├── init-state.py
    └── check-state.py
```

`check-state.py` 是可选但建议包含的轻量脚本。它只检查状态文件是否完整，不检查业务代码，不执行调度。

`agents/openai.yaml` 是 `skill-creator` 推荐的 UI 元数据文件。它属于 V1 交付物，但只用于发现、展示和默认提示，不承载工作流逻辑。Claude Code 和 Hermes 可以忽略它；核心行为仍由 `SKILL.md` 和 `references/` 定义。

`references/loop-engineering.md` 显式记录 Loop Engineering 模型。`SKILL.md` 只保留短入口，详细说明放入该 reference，避免核心 Skill 过长。

## 6. Skill 触发与开关

V1 支持显式启用模式。未初始化时，Spec2Web 不自动接管普通开发任务。初始化后，通过 `spec2web/loop-state.md` 维持激活状态。

推荐 `SKILL.md` frontmatter：

```yaml
---
name: spec2web
description: Use when the user asks to initialize, enable, start, resume, or run Spec2Web for a web project, or when the current project contains spec2web/loop-state.md with status active. Guides full-stack web delivery through project rules, requirement baseline, system design, task breakdown, role-separated loops, validation, repair, and delivery reporting.
---
```

应识别自然语言初始化意图，例如：

- `/spec2web 初始化当前项目`
- `/spec2web 启用工作流`
- `/spec2web 根据 requirements.md 开始开发`
- `/spec2web 继续当前任务`
- `/spec2web 查看状态`
- `/spec2web 生成交付报告`
- “使用 Spec2Web 管理这个项目”
- “开启 Spec2Web 模式”

开关规则：

```text
未启用：
- 项目中不存在 spec2web/loop-state.md
- 或 loop-state.md 中 status 不是 active
- Skill 只在用户显式调用时运行

已启用：
- 项目中存在 spec2web/loop-state.md
- 且 status = active
- 后续与该项目全栈开发相关的任务继续遵守 Spec2Web 流程

暂停：
- status = paused

关闭：
- status = disabled
```

## 7. 初始化脚本

`scripts/init-state.py` 提供 init-like 体验，但不是全局 CLI。

它只做：

- 在当前项目中创建 `spec2web/`
- 创建缺失的状态文件模板
- 默认不覆盖已有状态文件
- 不生成业务代码
- 不安装依赖
- 不修改项目源码
- 不启动子代理
- 不做调度

初始化后生成：

```text
spec2web/
├── project-rules.md
├── requirements-baseline.md
├── system-design.md
├── task-plan.md
├── loop-state.md
├── validation-log.md
└── delivery-report.md
```

`loop-state.md` 初始内容应包含：

```yaml
workflow: spec2web
status: active
current_phase: project_rules
current_task: null
```

## 8. 项目规则优先级

Spec2Web 必须读取项目级规则文件，并将其中影响实现的规则摘要写入 `spec2web/project-rules.md`。

规则来源包括：

- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `README.md`
- 其他项目级开发规范

优先级：

```text
用户当前明确指令
> 项目级规则文件
> Spec2Web Skill 工作流
> 智能体默认习惯
```

在当前项目中，`CLAUDE.md` 的核心质量规则应被纳入 `project-rules.md`，包括：

- 先读现有代码再写
- 明确假设和权衡
- 保持简单
- 小范围改动
- 验证优先
- 系统化调试
- 谨慎引入依赖
- 清晰沟通
- 结构性代码问题优先使用 CodeGraph

## 9. 工作流阶段

V1 固定流程：

```text
1. Project Rules
2. Requirement Baseline
3. System Design
4. Task Breakdown
5. Single Task Loop
6. Integration Validation
7. Delivery
```

阶段说明：

1. Project Rules
   读取项目规则文件，生成或更新 `project-rules.md`。

2. Requirement Baseline
   读取需求和附件，结构化为 `requirements-baseline.md`。重大歧义必须询问用户。

3. System Design
   生成 `system-design.md`，包括页面、数据模型、API、权限、技术约束和验收方式。

4. Task Breakdown
   生成 `task-plan.md`。先做必要横切任务，再按业务功能纵向切片。

5. Task Execution Loop
   默认一次执行一个任务。启用受控多 worker 模式时，可以同时执行一批无冲突任务，但每个 worker 仍然只执行一个小任务：

   ```text
   Read State
   → Select Next Task or Parallel Batch
   → [Optional] Prepare Task Worktree(s)
   → Plan
   → Act
   → Verify
   → Review
   → Serial Merge or Repair or Record
   → Update State
   ```

6. Integration Validation
   所有任务完成后运行整体构建、测试、联调和核心流程验证。

7. Delivery
   生成 `delivery-report.md`，列出完成项、未完成项、风险、验证结果和本地运行步骤。

## 10. 任务拆解策略

默认采用混合策略：

```text
先横切冻结基础契约，再纵切交付业务功能。
```

横切任务示例：

- 项目骨架和运行方式
- 数据模型
- API 契约
- 权限规则
- 页面地图
- 验证命令

纵切任务示例：

- 登录闭环
- 核心资源列表闭环
- 核心资源创建/编辑闭环
- 核心报表或业务动作闭环

每个任务必须包含：

```text
task_id
requirement_ids
goal
dependencies
allowed_paths
expected_outputs
verification
completion_criteria
risks_or_blockers
execution_workspace
parallel_group
merge_policy
```

约束：

- 不允许一次性生成完整项目
- 任务必须绑定需求编号
- 任务必须能独立验证
- 任务过大时必须先拆小
- 默认一次只执行一个任务
- 受控多 worker 模式下，只允许无冲突任务并行
- 未经确认不得修改需求基线
- 不得实现无需求来源的额外功能

任务可并行的条件：

- 依赖任务已完成
- `allowed_paths` 不重叠
- 不修改共享契约文件
- 每个任务有独立验证方式
- 每个任务有独立 worktree
- Orchestrator 明确记录并行批次

共享契约文件默认串行修改，包括：

- `requirements-baseline.md`
- `system-design.md`
- `task-plan.md`
- 数据库迁移
- API 契约或 OpenAPI 文件
- 全局路由入口
- 全局状态管理
- 构建配置

## 11. 角色协议

Spec2Web 定义角色协议，但不实现调度器。

角色：

- Orchestrator：维护状态、选择阶段和下一任务；在 worktree 模式下选择并行批次、负责合并前审查和合并决策
- Planner：需求分析、系统设计、任务拆解
- Developer：执行单个任务范围内的实现
- Tester：运行或补充验证，检查需求覆盖
- Reviewer：只读审查流程合规、代码质量、需求偏差和风险
- Repairer：根据失败证据做有限修复
- Delivery：整理最终交付

如果宿主支持子代理，优先让 Developer、Tester、Reviewer 由不同子代理承担。受控多 worker 模式下，每个 Developer worker 只能执行一个任务。

如果宿主不支持子代理，同一个智能体也必须显式切换角色。Developer 不能用自己的主观判断替代 Tester 或 Reviewer 的检查。

Reviewer 不应修改代码，只输出问题、风险、阻塞状态和建议。

所有角色输出必须回写状态文件。

## 12. 可选 Git Worktree 隔离模式

V1 支持 Git worktree 隔离。默认是单任务 worktree；当用户或 Orchestrator 明确选择并行，且任务满足无冲突条件时，V1 支持受控多 worker worktree 模式。

V1 不支持后台自动调度器、无人值守 worker 池或自动批量合并。并行批次必须由 Orchestrator 根据 `task-plan.md` 显式选择并记录。

启用条件：

- 当前项目是 Git 仓库
- 用户未禁用 worktree 模式
- 当前任务或并行批次有明确任务契约和验证方式

如果当前项目不是 Git 仓库，智能体不得自行初始化 Git；必须询问用户是否允许初始化。

默认单任务流程：

```text
主工作区：Orchestrator / Reviewer / 集成区
任务 worktree：Developer 执行区

选择一个任务
→ 创建任务分支和 worktree
→ Developer 在任务 worktree 中实现
→ 在任务 worktree 中运行任务验证
→ 回到主工作区
→ Orchestrator / Reviewer 审查 diff 和验证结果
→ 通过后合并回主分支
→ 合并后在主工作区运行受影响验证
→ 更新状态文件
```

受控多 worker 流程：

```text
Orchestrator 选择无冲突任务批次
→ 为每个任务创建独立分支和 worktree
→ 每个 Developer worker 在自己的 worktree 中实现
→ 每个 worktree 独立运行任务验证
→ Orchestrator 收集结果
→ Reviewer 分别审查每个 diff
→ Orchestrator 按依赖顺序串行合并
→ 每合并一个任务后，在主工作区运行受影响验证
→ 任一合并失败则停止后续合并并进入修复或阻塞
→ 更新状态文件
```

约束：

- Developer 不应直接在主分支完成开发任务。
- 每个 worker 只能修改其任务契约允许的路径。
- 并行任务的 `allowed_paths` 不得重叠。
- 修改共享契约文件的任务不得并行。
- worker 不得自行合并回主分支。
- Orchestrator 必须串行合并，即使开发是并行完成的。
- 合并前必须查看 diff。
- 合并前必须确认修改范围符合 `allowed_paths`。
- 合并前必须确认任务验证已记录到 `validation-log.md`。
- 合并后必须在主工作区重新运行受影响验证。
- 出现冲突、越界修改、验证失败或需求偏差时不得合并。
- 不允许 force merge、hard reset 或覆盖主分支来消除冲突。

失败处理：

- 任务 worktree 验证失败：该任务进入任务级修复 Loop。
- 主工作区合并后验证失败：进入集成级修复 Loop。
- 合并冲突无法安全解决：停止后续合并，标记 `blocked` 并询问用户。
- 修改超出任务边界：拒绝合并，要求拆分任务或重新规划。

状态记录：

- `task-plan.md` 应记录任务的 branch/worktree 命名建议和 `parallel_group`。
- `loop-state.md` 应记录当前任务或并行批次的 worktree 路径和分支。
- `validation-log.md` 应记录 worktree 内验证和合并后验证。

## 13. Loop Engineering 融合方式

Spec2Web V1 不实现 Loop 平台，但实现 Loop 协议。

核心要素：

- 外部状态：`spec2web/` 状态文件
- 明确目标：需求基线和当前任务契约
- 任务拆解：`task-plan.md`
- 执行循环：任务级 Loop；并行时每个 worker 独立执行一个任务级 Loop
- 独立检查：Tester 和 Reviewer
- 停止条件：有限修复预算和阻塞规则
- 下一步决策：`loop-state.md`

对话内容不能替代状态文件。上下文丢失后，应能通过状态文件恢复项目进度。

## 14. 有限修复 Loop

修复预算：

```text
单任务修复：最多 3 次
集成/联调修复：最多 5 次
同一错误指纹出现 3 次：停止
```

每次修复必须：

- 基于明确失败证据
- 引用新的诊断信息
- 一次只处理一个主要失败原因
- 修复后重新验证
- 更新 `validation-log.md`
- 更新 `loop-state.md`

提前停止条件：

- 需要改变已确认需求
- 需要扩大任务范围
- 需要新增高风险依赖
- 需要访问真实凭据
- 需要付费外部资源
- 无法复现问题
- 连续修复没有新证据

修复预算耗尽后，必须进入 `blocked` 状态，不能假装完成。

## 15. Superpowers 可选增强

Superpowers 是步骤级增强，不是运行前提。

原则：

```text
Spec2Web owns the loop.
Superpowers can assist a step.
```

如果可用，推荐映射：

- 需求分析：`superpowers:brainstorming`
- 任务计划：`superpowers:writing-plans`
- 调试修复：`superpowers:systematic-debugging`
- 交付前验证：`superpowers:verification-before-completion`

外部 Skill 的结果必须写回 Spec2Web 状态文件。任何外部 Skill 都不能跳过需求基线、任务拆解、验证记录或交付报告。

## 16. 约束保持协议

V1 不能像 Core Runtime 一样硬性拦截智能体行为。它通过状态、任务契约、阶段门和审查让偏离可见、可纠正。

每轮继续前必须读取：

```text
spec2web/project-rules.md
spec2web/task-plan.md
spec2web/loop-state.md
```

`loop-state.md` 必须包含 Active Constraints：

```text
- one task at a time
- no unplanned full-project generation
- every task maps to requirements
- update state before moving on
- verify before claiming done
- follow project-rules.md
```

阶段门：

- 需求基线不存在时，不得进入系统设计
- 系统设计不存在时，不得进入任务拆解
- 任务计划不存在时，不得写应用代码
- 当前任务未验证时，不得标记完成
- worktree 模式下，任务未审查和合并后未验证时，不得标记完成
- 验证未记录时，不得进入交付

Reviewer 必须检查：

- 是否跳过任务拆解
- 是否越过任务边界
- worktree 模式下是否绕过合并前审查
- 是否实现无需求来源的功能
- 是否没有验证就宣布完成
- 是否违反项目规则
- 是否违反 Spec2Web 状态流程

`scripts/check-state.py` 可检查：

- 必需状态文件是否存在
- `loop-state.md` 是否有当前阶段和状态
- `task-plan.md` 是否包含任务字段
- `validation-log.md` 是否记录当前任务结果

## 17. 安装支持

V1 支持 Claude Code 和 Hermes。

Claude Code 安装目标：

```text
~/.claude/skills/spec2web/
.claude/skills/spec2web/
```

Hermes 安装目标：

```text
~/.hermes/skills/spec2web/
```

安装后推荐入口：

```text
/spec2web 初始化当前项目
/spec2web 启用工作流
/spec2web 继续当前任务
```

安装说明应放在 `references/install.md`，但核心逻辑仍由 `SKILL.md` 承载。

## 18. 验收标准

V1 通过验收应满足：

1. Skill 文件夹可被 Claude Code 或 Hermes 安装。
2. Skill 名称为 `spec2web`，可通过 `/spec2web ...` 调用。
3. `SKILL.md` frontmatter 简洁、通用、可触发。
4. `agents/openai.yaml` 存在，并且只包含 UI 元数据、默认提示和可选调用策略。
5. 初始化脚本可创建缺失状态文件，且不覆盖已有状态。
6. Skill 明确要求读取项目规则文件。
7. Skill 明确要求生成并维护 `spec2web/` 状态文件。
8. Skill 有显式 Loop Engineering reference。
9. Skill 明确禁止未拆解的一次性完整项目生成。
10. Skill 明确规定任务拆解规则。
11. Skill 明确规定角色协议。
12. Skill 明确规定可选 Git worktree 隔离模式。
13. Skill 明确规定受控多 worker 的并行条件。
14. Skill 明确规定合并前 Orchestrator/Reviewer 审查。
15. Skill 明确规定合并后主工作区验证。
16. Skill 明确规定任务级 Loop。
17. Skill 明确规定有限修复预算。
18. Skill 明确规定验证和交付报告。
19. Skill 说明 Superpowers 是可选增强，不是硬依赖。
20. references 中的模板足够让另一个智能体按流程执行。
21. V2 分发适配不污染 V1 核心结构。

## 19. 与原 V3 的关系

原 V3 是最终产品蓝图，新 V1 是最小可验证入口。

旧方向：

```text
先实现 Core Runtime，再跑通流程。
```

新方向：

```text
先用 Skill 跑通流程，再把稳定流程产品化。
```

V1 不推翻 V3。V1 产出的状态文件、任务拆解、角色协议、worktree 隔离与受控多 worker 协议、停止条件和验证清单，可以在后续版本升级为 Core Runtime、调度器和验证器。

## 20. 设计结论

Spec2Web V1 应是：

```text
跨宿主 Skill
+ /spec2web 显式入口
+ 轻量初始化脚本
+ 项目规则约束
+ 外部状态记忆
+ 混合任务拆解
+ 角色分离协议
+ 可选 Git worktree 隔离
+ 受控多 worker 模式
+ 任务级 Loop
+ 有限修复
+ 验证和交付报告
+ Superpowers 可选增强
```

它的核心价值不是自动生成代码，而是让智能体在完整全栈项目中保持方向、边界、验证和记忆。
