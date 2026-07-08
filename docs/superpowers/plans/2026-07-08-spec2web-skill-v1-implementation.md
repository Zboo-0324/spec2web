# Spec2Web Skill V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the V1 `spec2web` cross-host Skill folder with workflow instructions, references, safe state initialization, state checking, and script tests.

**Architecture:** The Skill is a portable folder, not a runtime product. `SKILL.md` owns the core workflow and progressive-disclosure routing; `references/` holds detailed templates and protocols; `scripts/` provides idempotent state initialization and lightweight state validation. Tests exercise only deterministic script behavior.

**Tech Stack:** Markdown Skill files, Python 3 standard library, `unittest`, Claude Code/Hermes-compatible `SKILL.md` frontmatter.

---

## File Structure

- Create: `spec2web/SKILL.md`
  - Required Skill entry point with portable frontmatter and concise workflow rules.
- Create: `spec2web/agents/openai.yaml`
  - UI metadata recommended by `skill-creator`; does not carry workflow logic.
- Create: `spec2web/references/install.md`
  - Claude Code and Hermes installation instructions plus recommended `/spec2web` usage.
- Create: `spec2web/references/state-files.md`
  - State file purposes, templates, and update rules.
- Create: `spec2web/references/loop-engineering.md`
  - Explicit Loop Engineering model and state-driven loop protocol.
- Create: `spec2web/references/task-breakdown.md`
  - Mixed task decomposition rules and task contract template.
- Create: `spec2web/references/role-protocol.md`
  - Orchestrator, Planner, Developer, Tester, Reviewer, Repairer, Delivery responsibilities.
- Create: `spec2web/references/worktree-mode.md`
  - Optional Git worktree isolation and controlled multi-worker merge protocol.
- Create: `spec2web/references/delivery-checklist.md`
  - Delivery report and validation checklist.
- Create: `spec2web/scripts/init-state.py`
  - Idempotently creates `spec2web/` project state files in a target project.
- Create: `spec2web/scripts/check-state.py`
  - Checks required `spec2web/` state files and critical markers.
- Create: `tests/test_spec2web_state_scripts.py`
  - Standard-library tests for the two scripts.

Git note: `E:\Projects\WebBuilder` currently has no initial commit. Do not commit, merge, or create worktrees in this implementation run unless the user explicitly asks for Git integration.

---

### Task 1: Initialize Skill Scaffold and Entry Point

**Files:**
- Create: `spec2web/SKILL.md`
- Create: `spec2web/agents/openai.yaml`

- [ ] **Step 1: Initialize the Skill with `skill-creator`**

Run:

```powershell
python 'C:\Users\15581\.codex\skills\.system\skill-creator\scripts\init_skill.py' spec2web --path 'E:\Projects\WebBuilder' --resources scripts,references --interface display_name='Spec2Web' --interface short_description='Guide full-stack web delivery with stateful loops.' --interface default_prompt='Use $spec2web to initialize or continue a full-stack web project workflow.'
```

Expected: `E:\Projects\WebBuilder\spec2web` exists with `SKILL.md`, `agents/openai.yaml`, `references/`, and `scripts/`.

- [ ] **Step 2: Write `SKILL.md`**

Create `E:\Projects\WebBuilder\spec2web\SKILL.md` with:

```markdown
---
name: spec2web
description: Use when the user asks to initialize, enable, start, resume, or run Spec2Web for a web project, or when the current project contains spec2web/loop-state.md with status active. Guides full-stack web delivery through project rules, requirement baseline, system design, task breakdown, role-separated loops, worktree isolation, validation, repair, and delivery reporting.
---

# Spec2Web

Use this Skill to guide a coding agent through full-stack web project delivery without a heavy runtime, code generator, MCP server, or background scheduler.

## Activation

Use this Skill when the user explicitly asks to initialize, enable, start, resume, continue, or run Spec2Web, including natural-language variants such as:

- `/spec2web initialize this project`
- `/spec2web enable workflow`
- `/spec2web start from requirements.md`
- `/spec2web continue current task`
- `/spec2web show status`
- `/spec2web generate delivery report`
- "use Spec2Web for this project"
- "start Spec2Web mode"

If the current project contains `spec2web/loop-state.md` with `status: active`, continue to use this Skill for full-stack project work. If the workflow is not initialized and the user asks for an ordinary coding task, do not take over the task automatically.

For localized invocation examples and install paths, read `references/install.md`.

## Hard Gates

Do not write application code until all of these exist:

- `spec2web/project-rules.md`
- `spec2web/requirements-baseline.md`
- `spec2web/system-design.md`
- `spec2web/task-plan.md`
- `spec2web/loop-state.md`

Do not mark a task complete until:

- the task maps to requirement IDs,
- the task has a clear verification method,
- verification results are recorded in `spec2web/validation-log.md`,
- Reviewer has checked scope, quality, and workflow compliance,
- `spec2web/loop-state.md` is updated.

## Workflow

Follow this sequence:

1. Project Rules
2. Requirement Baseline
3. System Design
4. Task Breakdown
5. Task Execution Loop
6. Integration Validation
7. Delivery

Each task-level loop follows:

```text
Read State
→ Select Next Task or Parallel Batch
→ Prepare Worktree(s) when enabled
→ Plan
→ Act
→ Verify
→ Review
→ Serial Merge or Repair or Record
→ Update State
```

## Project Rules

Before requirements or coding, read project-level rule files when present:

- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `README.md`

Summarize implementation-relevant rules into `spec2web/project-rules.md`. User instructions take priority over project rules; project rules take priority over this Skill; this Skill takes priority over default agent habits.

## State Files

Maintain the project memory in `spec2web/`:

- `project-rules.md`
- `requirements-baseline.md`
- `system-design.md`
- `task-plan.md`
- `loop-state.md`
- `validation-log.md`
- `delivery-report.md`

Conversation context does not replace these files. On resume, first read `project-rules.md`, `task-plan.md`, and `loop-state.md`.

For templates and update rules, read `references/state-files.md`.

## Loop Engineering Model

Spec2Web owns the loop. The agent must repeatedly read state, select bounded work, execute, verify, review, repair or record, and update state. For the full protocol, read `references/loop-engineering.md`.

## Task Breakdown

Use mixed decomposition:

- first freeze shared cross-cutting contracts,
- then deliver vertical business slices.

Every task must have:

- `task_id`
- `requirement_ids`
- `goal`
- `dependencies`
- `allowed_paths`
- `expected_outputs`
- `verification`
- `completion_criteria`
- `risks_or_blockers`
- `execution_workspace`
- `parallel_group`
- `merge_policy`

For task rules and templates, read `references/task-breakdown.md`.

## Roles

Use role separation even when only one agent is available:

- Orchestrator maintains state, selects tasks, chooses safe parallel batches, and controls merges.
- Planner analyzes requirements, designs the system, and decomposes tasks.
- Developer implements one task inside its boundary.
- Tester verifies behavior and requirement coverage.
- Reviewer performs read-only review of scope, code quality, risk, and workflow compliance.
- Repairer fixes failures using explicit evidence.
- Delivery prepares final reporting.

When subagents are available, use separate agents for Developer, Tester, and Reviewer. When they are not available, explicitly switch roles. Developer may not self-certify completion.

For detailed role rules, read `references/role-protocol.md`.

## Worktree Mode

Prefer Git worktree isolation for development tasks when the project is a Git repository. If the project is not a Git repository, ask the user before initializing Git.

Default to one task at a time. Controlled multi-worker mode is allowed only when Orchestrator explicitly selects a no-conflict batch from `task-plan.md`.

Parallel tasks must satisfy:

- dependencies are complete,
- `allowed_paths` do not overlap,
- no shared contract files are modified,
- each task has independent verification,
- each task uses an independent worktree,
- Orchestrator records the batch in `loop-state.md`.

Even when development is parallel, merges are serial. Each merge requires diff review, task verification, main-workspace verification, and state updates.

For worktree details, read `references/worktree-mode.md`.

## Repair Budget

Use finite repair loops:

- task-level repair: at most 3 attempts,
- integration-level repair: at most 5 attempts,
- same error fingerprint 3 times: stop.

Each repair must cite new evidence, change one main cause, rerun verification, and update `validation-log.md`. If fixing requires changing confirmed requirements, expanding scope, adding high-risk dependencies, using real credentials, or creating paid resources, stop and ask the user.

## Optional Superpowers

Superpowers are optional step-level helpers, not the workflow owner.

Use them when available:

- requirement baseline: `superpowers:brainstorming`
- task planning: `superpowers:writing-plans`
- debugging and repair: `superpowers:systematic-debugging`
- completion claims: `superpowers:verification-before-completion`

All outputs from external Skills must be written back to Spec2Web state files. External Skills may not skip requirements baseline, task breakdown, validation logging, or delivery reporting.

## Delivery

Before final delivery, run the project-specific verification commands, update `validation-log.md`, and generate `delivery-report.md`.

For final checks and report structure, read `references/delivery-checklist.md`.
```

- [ ] **Step 3: Write `agents/openai.yaml`**

Create or replace `E:\Projects\WebBuilder\spec2web\agents\openai.yaml` with:

```yaml
interface:
  display_name: "Spec2Web"
  short_description: "Guide full-stack web delivery with stateful loops."
  default_prompt: "Use $spec2web to initialize or continue a full-stack web project workflow."

policy:
  allow_implicit_invocation: true
```

This file is UI metadata. Do not put workflow rules, host-specific install instructions, or task protocols in it.

- [ ] **Step 4: Check frontmatter and metadata manually**

Run:

```powershell
Get-Content -First 5 -LiteralPath 'E:\Projects\WebBuilder\spec2web\SKILL.md'
Get-Content -Raw -LiteralPath 'E:\Projects\WebBuilder\spec2web\agents\openai.yaml'
```

Expected first lines:

```text
---
name: spec2web
description: Use when the user asks to initialize, enable, start, resume, or run Spec2Web for a web project, or when the current project contains spec2web/loop-state.md with status active. Guides full-stack web delivery through project rules, requirement baseline, system design, task breakdown, role-separated loops, worktree isolation, validation, repair, and delivery reporting.
---
```

Expected metadata includes:

```text
display_name: "Spec2Web"
short_description: "Guide full-stack web delivery with stateful loops."
default_prompt: "Use $spec2web to initialize or continue a full-stack web project workflow."
allow_implicit_invocation: true
```

---

### Task 2: Create Reference Documentation

**Files:**
- Create: `spec2web/references/install.md`
- Create: `spec2web/references/state-files.md`
- Create: `spec2web/references/loop-engineering.md`
- Create: `spec2web/references/task-breakdown.md`
- Create: `spec2web/references/role-protocol.md`
- Create: `spec2web/references/worktree-mode.md`
- Create: `spec2web/references/delivery-checklist.md`

- [ ] **Step 1: Write `install.md`**

Create `E:\Projects\WebBuilder\spec2web\references\install.md` with:

```markdown
# Installation

Spec2Web V1 is a portable Skill folder. Install the whole `spec2web/` directory, not only `SKILL.md`.

## Claude Code

Personal install:

```text
~/.claude/skills/spec2web/
```

Project install:

```text
.claude/skills/spec2web/
```

## Hermes

Personal install:

```text
~/.hermes/skills/spec2web/
```

## Recommended Entry

Use the dynamic slash command when available:

```text
/spec2web 初始化当前项目
/spec2web 启用工作流
/spec2web 根据 requirements.md 开始开发
/spec2web 继续当前任务
/spec2web 查看状态
/spec2web 生成交付报告
```

Equivalent natural-language requests are also valid:

```text
use Spec2Web for this project
start Spec2Web mode
enable Spec2Web workflow
resume Spec2Web
```

## Optional Project Hook

Add this to `CLAUDE.md` or `AGENTS.md` only when the project should keep using Spec2Web after initialization:

```text
Use the spec2web Skill only when explicitly requested or when spec2web/loop-state.md exists with status active. Do not let it override ordinary coding tasks when the workflow has not been initialized.
```
```

- [ ] **Step 2: Write `state-files.md`**

Create `E:\Projects\WebBuilder\spec2web\references\state-files.md` with:

```markdown
# State Files

Spec2Web stores project memory in `spec2web/`. These files are the source of truth after initialization.

## Required Files

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

## project-rules.md

Purpose: summarize implementation-relevant instructions from `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, README, and user-provided rules.

Template:

```markdown
# Project Rules

## Sources Read

- [ ] CLAUDE.md
- [ ] AGENTS.md
- [ ] GEMINI.md
- [ ] README.md

## Active Rules

- Read existing code before writing.
- State assumptions before implementation.
- Keep changes small and focused.
- Verify before claiming completion.
- Avoid new dependencies unless justified.

## Open Rule Conflicts

- None.
```

## requirements-baseline.md

Purpose: hold confirmed requirements. Do not change without user approval.

Template:

```markdown
# Requirements Baseline

## Status

status: draft

## Requirements

| ID | Requirement | Priority | Acceptance Signal |
|---|---|---|---|
| REQ-001 | Describe the first confirmed requirement. | Must | How it will be verified. |

## Assumptions

- List explicit assumptions.

## Open Questions

- List questions that block safe implementation.
```

## system-design.md

Purpose: freeze design facts before task execution.

Template:

```markdown
# System Design

## Pages

- Page name: purpose, key actions, requirement IDs.

## Data Model

- Entity: fields, relationships, validation.

## API Contract

- Method path: request, response, errors, requirement IDs.

## Permissions

- Role: allowed actions.

## Verification Strategy

- Build command:
- Test command:
- Browser or manual verification:
```

## task-plan.md

Purpose: list tasks, dependencies, allowed paths, validation, parallel groups, and merge policies.

Template:

```markdown
# Task Plan

## Current Strategy

Default to one task at a time. Use controlled multi-worker mode only for no-conflict tasks.

## Tasks

### TASK-001: Task title

- requirement_ids: REQ-001
- goal: Specific result.
- dependencies: none
- allowed_paths:
  - path/pattern
- expected_outputs:
  - path or behavior
- verification:
  - exact command or manual check
- completion_criteria:
  - observable condition
- risks_or_blockers:
  - none
- execution_workspace: main or worktree
- parallel_group: none
- merge_policy: orchestrator_review_then_serial_merge
```

## loop-state.md

Purpose: record current workflow status and active constraints.

Template:

```markdown
# Loop State

workflow: spec2web
status: active
current_phase: project_rules
current_task: null
active_parallel_group: null

## Active Constraints

- one task per worker
- no unplanned full-project generation
- every task maps to requirements
- update state before moving on
- verify before claiming done
- follow project-rules.md
- Orchestrator controls merges

## Worktrees

| Task | Branch | Path | Status |
|---|---|---|---|

## Next Step

Read project rules and update project-rules.md.
```

## validation-log.md

Purpose: preserve verification evidence.

Template:

```markdown
# Validation Log

## Entries

### YYYY-MM-DD HH:MM - TASK-001

- command: exact command
- result: passed or failed
- evidence: summary of output
- next_action: continue, repair, blocked
```

## delivery-report.md

Purpose: final user-facing handoff.

Template:

````markdown
# Delivery Report

## Completed

- List completed user-facing features.

## Validation

- List commands and outcomes.

## Run Instructions

- Exact local run steps.

## Known Risks

- List risks or limitations.

## Not Completed

- List intentional omissions or blockers.
```
```

- [ ] **Step 3: Write `loop-engineering.md`**

Create `E:\Projects\WebBuilder\spec2web\references\loop-engineering.md` with:

````markdown
# Loop Engineering

Spec2Web uses Loop Engineering as a workflow discipline, not as a background runtime.

## Core Rule

Spec2Web owns the loop. Other tools, Skills, subagents, and shell commands can assist a step, but they do not own the project state or decide that the project is complete.

Every loop follows:

```text
Read State
-> Select Bounded Work
-> Plan
-> Act
-> Verify
-> Review
-> Repair or Record
-> Update State
```

## External Memory

Conversation is not memory. The project memory lives in `spec2web/`.

On resume, read `project-rules.md`, `task-plan.md`, and `loop-state.md` before acting.

## Bounded Work

Do not ask a worker to build the entire project. The Orchestrator selects one task or a safe parallel batch from `task-plan.md`.

If the work cannot be bounded, split it before implementation.

## Maker and Checker Split

The Developer creates changes. The Tester and Reviewer check them. Developer must not self-certify completion.

## Worktree Isolation

Controlled multi-worker mode is allowed only for dependency-complete, no-overlap, independently verifiable tasks. Workers never merge their own work. Orchestrator merges serially.

## Finite Repair

Repair loops must be evidence-driven and bounded:

- task-level repair: at most 3 attempts
- integration-level repair: at most 5 attempts
- same error fingerprint 3 times: stop

## State Update Requirement

Every loop ends by updating `loop-state.md`, `validation-log.md`, and, when task status changes, `task-plan.md`.

## Completion Rule

Completion requires mapped requirements, recorded verification evidence, Reviewer sign-off or documented exceptions, main-workspace validation after merges, and `delivery-report.md`.
````

- [ ] **Step 4: Write `task-breakdown.md`**

Create `E:\Projects\WebBuilder\spec2web\references\task-breakdown.md` with:

```markdown
# Task Breakdown

Use mixed decomposition:

```text
First freeze cross-cutting contracts.
Then deliver vertical business slices.
```

## Cross-Cutting Tasks

Use these only when needed:

- project skeleton and run commands
- data model
- API contract
- permission model
- page map
- validation command setup

These tasks are usually serial because they affect shared contracts.

## Vertical Slice Tasks

Prefer small user-visible slices:

- login loop
- list view loop
- create/edit loop
- core business action loop
- report/export loop

Each vertical task should be independently verifiable.

## Task Contract

Each task must include:

```markdown
### TASK-000: Title

- requirement_ids: REQ-000
- goal: One concrete outcome.
- dependencies: TASK-000 or none
- allowed_paths:
  - path/pattern
- expected_outputs:
  - path or behavior
- verification:
  - exact command or manual check
- completion_criteria:
  - observable condition
- risks_or_blockers:
  - none
- execution_workspace: main or worktree
- parallel_group: none or PG-000
- merge_policy: orchestrator_review_then_serial_merge
```

## Parallel Eligibility

Tasks can run in the same parallel group only when:

- all dependencies are complete,
- `allowed_paths` do not overlap,
- neither task modifies shared contract files,
- each task has independent verification,
- each task has an independent worktree,
- Orchestrator records the group in `loop-state.md`.

Shared contract files are serial by default:

- requirements baseline
- system design
- task plan
- database migrations
- API contract or OpenAPI files
- global router entry
- global state store
- build configuration

## Required Refusal

If a task is too broad, do not implement it. Split it first.

Do not implement features without requirement IDs.
```

- [ ] **Step 5: Write `role-protocol.md`**

Create `E:\Projects\WebBuilder\spec2web\references\role-protocol.md` with:

```markdown
# Role Protocol

Spec2Web separates responsibilities. Use real subagents when available; otherwise switch roles explicitly in the same agent.

## Orchestrator

- read and update `loop-state.md`
- select the current task or safe parallel batch
- ensure project rules are followed
- control worktree creation decisions
- review merge readiness
- merge serially
- stop on conflicts, failed validation, or scope drift

## Planner

- analyze requirements
- state assumptions
- produce `requirements-baseline.md`
- produce `system-design.md`
- produce `task-plan.md`

## Developer

- implement exactly one task
- stay within `allowed_paths`
- do not self-certify completion
- do not merge to the main branch
- record implementation summary for Reviewer

## Tester

- run task verification
- add or propose missing behavior tests when appropriate
- record results in `validation-log.md`
- distinguish pre-existing failures from new failures

## Reviewer

Reviewer is read-only.

Check:

- task maps to requirements
- changed files stay inside `allowed_paths`
- implementation follows `project-rules.md`
- no unplanned full-project generation occurred
- no dependency was added without justification
- verification evidence exists
- worktree mode did not bypass merge review

## Repairer

- repair only from explicit failure evidence
- change one main cause per attempt
- stay within repair budget
- update `validation-log.md`

## Delivery

- produce `delivery-report.md`
- include completed features, validation evidence, run instructions, known risks, and not-completed items
```

- [ ] **Step 6: Write `worktree-mode.md`**

Create `E:\Projects\WebBuilder\spec2web\references\worktree-mode.md` with:

```markdown
# Worktree Mode

Worktree mode isolates task execution. It is a workflow protocol, not a background scheduler.

## Preconditions

- The project is a Git repository.
- The user has not disabled worktree mode.
- Each task has a task contract.
- Orchestrator controls merge decisions.

If the project is not a Git repository, ask the user before initializing Git.

## Default Single-Task Mode

```text
Orchestrator selects one task
→ create branch and worktree
→ Developer implements in the worktree
→ task verification runs in the worktree
→ Reviewer checks diff and evidence
→ Orchestrator merges if approved
→ main workspace verification runs
→ state files are updated
```

## Controlled Multi-Worker Mode

```text
Orchestrator selects a no-conflict parallel group
→ create one branch and worktree per task
→ one Developer worker executes each task
→ each worker runs task verification
→ Reviewer reviews each diff separately
→ Orchestrator merges tasks serially
→ after each merge, run affected verification in the main workspace
→ stop later merges if any merge fails
```

## Merge Rules

- Workers never merge their own work.
- Merges are serial, even when development was parallel.
- Diff review is required before merge.
- Main-workspace verification is required after each merge.
- Conflicts stop the merge queue.
- Scope drift rejects the merge.
- Failed verification enters repair or blocked state.

## Naming

Use predictable names:

```text
branch: spec2web/TASK-001-short-title
worktree: ../<repo-name>-TASK-001
```

Record actual branch and worktree path in `loop-state.md`.
```

- [ ] **Step 7: Write `delivery-checklist.md`**

Create `E:\Projects\WebBuilder\spec2web\references\delivery-checklist.md` with:

```markdown
# Delivery Checklist

Before final delivery, verify and record evidence.

## Required Checks

- requirements are mapped to tasks
- all tasks are complete or explicitly listed as not completed
- validation commands have been run
- failures are resolved or documented
- project run instructions are current
- known risks are documented
- credentials are not committed
- local absolute paths are not embedded in deliverables

## Delivery Report Template

```markdown
# Delivery Report

## Summary

One paragraph describing what was delivered.

## Completed Features

- Feature mapped to requirement ID.

## Validation Evidence

| Check | Command or Method | Result |
|---|---|---|
| Build | command | passed/failed |
| Tests | command | passed/failed |
| Manual flow | method | passed/failed |

## Run Instructions

```text
exact commands
```

## Known Risks

- Risk and impact.

## Not Completed

- Item and reason.

## Resume Instructions

- Next recommended task or follow-up.
````
```

- [ ] **Step 8: Check reference files exist**

Run:

```powershell
Get-ChildItem -LiteralPath 'E:\Projects\WebBuilder\spec2web\references' | Select-Object -ExpandProperty Name
```

Expected:

```text
delivery-checklist.md
install.md
loop-engineering.md
role-protocol.md
state-files.md
task-breakdown.md
worktree-mode.md
```

---

### Task 3: Implement State Initialization Script

**Files:**
- Create: `spec2web/scripts/init-state.py`

- [ ] **Step 1: Write `init-state.py`**

Create `E:\Projects\WebBuilder\spec2web\scripts\init-state.py` with:

```python
#!/usr/bin/env python3
"""Initialize lightweight Spec2Web state files."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATES = {
    "project-rules.md": """# Project Rules

## Sources Read

- [ ] CLAUDE.md
- [ ] AGENTS.md
- [ ] GEMINI.md
- [ ] README.md

## Active Rules

- Read existing code before writing.
- State assumptions before implementation.
- Keep changes small and focused.
- Verify before claiming completion.
- Avoid new dependencies unless justified.

## Open Rule Conflicts

- None.
""",
    "requirements-baseline.md": """# Requirements Baseline

## Status

status: draft

## Requirements

| ID | Requirement | Priority | Acceptance Signal |
|---|---|---|---|
| REQ-001 | Replace with the first confirmed requirement. | Must | Replace with verification method. |

## Assumptions

- None recorded yet.

## Open Questions

- None recorded yet.
""",
    "system-design.md": """# System Design

## Pages

- None recorded yet.

## Data Model

- None recorded yet.

## API Contract

- None recorded yet.

## Permissions

- None recorded yet.

## Verification Strategy

- Build command: not recorded
- Test command: not recorded
- Browser or manual verification: not recorded
""",
    "task-plan.md": """# Task Plan

## Current Strategy

Default to one task at a time. Use controlled multi-worker mode only for no-conflict tasks.

## Tasks

### TASK-001: Replace with first task title

- requirement_ids: REQ-001
- goal: Replace with one concrete outcome.
- dependencies: none
- allowed_paths:
  - replace/with/path
- expected_outputs:
  - replace with expected output
- verification:
  - replace with exact command or manual check
- completion_criteria:
  - replace with observable condition
- risks_or_blockers:
  - none
- execution_workspace: main
- parallel_group: none
- merge_policy: orchestrator_review_then_serial_merge
""",
    "loop-state.md": """# Loop State

workflow: spec2web
status: active
current_phase: project_rules
current_task: null
active_parallel_group: null

## Active Constraints

- one task per worker
- no unplanned full-project generation
- every task maps to requirements
- update state before moving on
- verify before claiming done
- follow project-rules.md
- Orchestrator controls merges

## Worktrees

| Task | Branch | Path | Status |
|---|---|---|---|

## Next Step

Read project rules and update project-rules.md.
""",
    "validation-log.md": """# Validation Log

## Entries

No validation has been recorded yet.
""",
    "delivery-report.md": """# Delivery Report

## Completed

- Nothing delivered yet.

## Validation

- No validation recorded yet.

## Run Instructions

- Not recorded yet.

## Known Risks

- None recorded yet.

## Not Completed

- Work has not started.
""",
}


def initialize(target: Path) -> tuple[list[Path], list[Path]]:
    state_dir = target / "spec2web"
    state_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    skipped: list[Path] = []

    for filename, content in TEMPLATES.items():
        path = state_dir / filename
        if path.exists():
            skipped.append(path)
            continue
        path.write_text(content, encoding="utf-8", newline="\n")
        created.append(path)

    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize Spec2Web state files.")
    parser.add_argument(
        "--target",
        default=".",
        help="Project directory where the spec2web state folder should be created.",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    created, skipped = initialize(target)

    print(f"Spec2Web state directory: {target / 'spec2web'}")
    for path in created:
        print(f"created: {path}")
    for path in skipped:
        print(f"exists:  {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run script in a temporary directory**

Run:

```powershell
$tmp = Join-Path $env:TEMP 'spec2web-init-plan-check'
Remove-Item -Recurse -Force -LiteralPath $tmp -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
python 'E:\Projects\WebBuilder\spec2web\scripts\init-state.py' --target $tmp
Get-ChildItem -LiteralPath (Join-Path $tmp 'spec2web') | Select-Object -ExpandProperty Name
```

Expected output includes all seven state files.

- [ ] **Step 3: Verify idempotency**

Run:

```powershell
python 'E:\Projects\WebBuilder\spec2web\scripts\init-state.py' --target $tmp
```

Expected: output uses `exists:` for the seven files and does not overwrite them.

---

### Task 4: Implement State Check Script

**Files:**
- Create: `spec2web/scripts/check-state.py`

- [ ] **Step 1: Write `check-state.py`**

Create `E:\Projects\WebBuilder\spec2web\scripts\check-state.py` with:

```python
#!/usr/bin/env python3
"""Check lightweight Spec2Web state files."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_FILES = [
    "project-rules.md",
    "requirements-baseline.md",
    "system-design.md",
    "task-plan.md",
    "loop-state.md",
    "validation-log.md",
    "delivery-report.md",
]

TASK_PLAN_MARKERS = [
    "requirement_ids:",
    "allowed_paths:",
    "verification:",
    "completion_criteria:",
    "merge_policy:",
]

LOOP_STATE_MARKERS = [
    "workflow: spec2web",
    "status:",
    "current_phase:",
    "## Active Constraints",
]


def check_state(target: Path) -> list[str]:
    state_dir = target / "spec2web"
    errors: list[str] = []

    if not state_dir.exists():
        return [f"missing state directory: {state_dir}"]

    for filename in REQUIRED_FILES:
        path = state_dir / filename
        if not path.exists():
            errors.append(f"missing required file: {path}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required file: {path}")

    loop_state = state_dir / "loop-state.md"
    if loop_state.exists():
        text = loop_state.read_text(encoding="utf-8")
        for marker in LOOP_STATE_MARKERS:
            if marker not in text:
                errors.append(f"loop-state.md missing marker: {marker}")
        if not any(status in text for status in ["status: active", "status: paused", "status: disabled", "status: blocked"]):
            errors.append("loop-state.md status must be active, paused, disabled, or blocked")

    task_plan = state_dir / "task-plan.md"
    if task_plan.exists():
        text = task_plan.read_text(encoding="utf-8")
        for marker in TASK_PLAN_MARKERS:
            if marker not in text:
                errors.append(f"task-plan.md missing marker: {marker}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Spec2Web state files.")
    parser.add_argument(
        "--target",
        default=".",
        help="Project directory containing the spec2web state folder.",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    errors = check_state(target)

    if errors:
        print("Spec2Web state check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Spec2Web state check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run check script against initialized temp directory**

Run:

```powershell
python 'E:\Projects\WebBuilder\spec2web\scripts\check-state.py' --target $tmp
```

Expected:

```text
Spec2Web state check passed.
```

- [ ] **Step 3: Verify failure on missing state**

Run:

```powershell
$missing = Join-Path $env:TEMP 'spec2web-missing-plan-check'
Remove-Item -Recurse -Force -LiteralPath $missing -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $missing | Out-Null
python 'E:\Projects\WebBuilder\spec2web\scripts\check-state.py' --target $missing
```

Expected: command exits non-zero and prints `missing state directory`.

---

### Task 5: Add Script Tests

**Files:**
- Create: `tests/test_spec2web_state_scripts.py`

- [ ] **Step 1: Create tests directory**

Run:

```powershell
New-Item -ItemType Directory -Force -Path 'E:\Projects\WebBuilder\tests'
```

Expected: `tests` directory exists.

- [ ] **Step 2: Write standard-library tests**

Create `E:\Projects\WebBuilder\tests\test_spec2web_state_scripts.py` with:

```python
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "spec2web" / "scripts" / "init-state.py"
CHECK_SCRIPT = ROOT / "spec2web" / "scripts" / "check-state.py"


class Spec2WebStateScriptTests(unittest.TestCase):
    def test_init_creates_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            state_dir = Path(tmp) / "spec2web"
            self.assertTrue((state_dir / "project-rules.md").exists())
            self.assertTrue((state_dir / "requirements-baseline.md").exists())
            self.assertTrue((state_dir / "system-design.md").exists())
            self.assertTrue((state_dir / "task-plan.md").exists())
            self.assertTrue((state_dir / "loop-state.md").exists())
            self.assertTrue((state_dir / "validation-log.md").exists())
            self.assertTrue((state_dir / "delivery-report.md").exists())

    def test_init_does_not_overwrite_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "spec2web"
            state_dir.mkdir()
            project_rules = state_dir / "project-rules.md"
            project_rules.write_text("custom content", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(INIT_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(project_rules.read_text(encoding="utf-8"), "custom content")
            self.assertIn("exists:", result.stdout)

    def test_check_state_passes_after_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, str(INIT_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=True,
            )

            result = subprocess.run(
                [sys.executable, str(CHECK_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Spec2Web state check passed.", result.stdout)

    def test_check_state_fails_without_state_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CHECK_SCRIPT), "--target", tmp],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing state directory", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run tests**

Run:

```powershell
python -m unittest discover -s 'E:\Projects\WebBuilder\tests' -p 'test_spec2web_state_scripts.py' -v
```

Expected: 4 tests pass.

---

### Task 6: Validate Skill Packaging

**Files:**
- Validate: `spec2web/SKILL.md`
- Validate: `spec2web/agents/openai.yaml`
- Validate: `spec2web/references/*.md`
- Validate: `spec2web/scripts/*.py`

- [ ] **Step 1: Run skill frontmatter validation**

Run:

```powershell
python 'C:\Users\15581\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'E:\Projects\WebBuilder\spec2web'
```

Expected: validation passes for the Skill folder.

- [ ] **Step 2: Scan for placeholders**

Run:

```powershell
Select-String -Path 'E:\Projects\WebBuilder\spec2web\**\*' -Pattern 'TBD|TODO|待定|占位'
```

Expected: no matches. The phrase "Replace with" in initial state templates is acceptable because those are user-editable template instructions, not implementation placeholders.

- [ ] **Step 3: Check references are reachable from `SKILL.md`**

Run:

```powershell
Select-String -LiteralPath 'E:\Projects\WebBuilder\spec2web\SKILL.md' -Pattern 'references/state-files.md|references/loop-engineering.md|references/task-breakdown.md|references/role-protocol.md|references/worktree-mode.md|references/delivery-checklist.md'
```

Expected: matches for all six detailed reference files.

- [ ] **Step 4: Check `agents/openai.yaml` metadata**

Run:

```powershell
Select-String -LiteralPath 'E:\Projects\WebBuilder\spec2web\agents\openai.yaml' -Pattern 'display_name: "Spec2Web"|short_description: "Guide full-stack web delivery with stateful loops\\."|default_prompt: "Use \\$spec2web to initialize or continue a full-stack web project workflow\\."|allow_implicit_invocation: true'
```

Expected: matches for display name, short description, default prompt, and implicit invocation policy.

- [ ] **Step 5: Run script smoke checks**

Run:

```powershell
$tmp = Join-Path $env:TEMP 'spec2web-final-smoke'
Remove-Item -Recurse -Force -LiteralPath $tmp -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
python 'E:\Projects\WebBuilder\spec2web\scripts\init-state.py' --target $tmp
python 'E:\Projects\WebBuilder\spec2web\scripts\check-state.py' --target $tmp
```

Expected: initialization prints created files and state check passes.

---

### Task 7: Final Review Against Design

**Files:**
- Review: `docs/superpowers/specs/2026-07-08-spec2web-skill-v1-design.md`
- Review: `spec2web/SKILL.md`
- Review: `spec2web/agents/openai.yaml`
- Review: `spec2web/references/*.md`
- Review: `spec2web/scripts/*.py`

- [ ] **Step 1: Confirm design coverage**

Check each design requirement maps to an implemented file:

```text
cross-host Skill folder -> spec2web/SKILL.md
/spec2web entry -> spec2web/SKILL.md
OpenAI UI metadata -> spec2web/agents/openai.yaml
install docs -> spec2web/references/install.md
state initialization -> spec2web/scripts/init-state.py
state checking -> spec2web/scripts/check-state.py
project rules -> SKILL.md and state-files.md
Loop Engineering -> spec2web/references/loop-engineering.md
task breakdown -> task-breakdown.md
role protocol -> role-protocol.md
worktree and multi-worker -> worktree-mode.md
delivery -> delivery-checklist.md
tests -> tests/test_spec2web_state_scripts.py
```

- [ ] **Step 2: Run all verification commands**

Run:

```powershell
python -m unittest discover -s 'E:\Projects\WebBuilder\tests' -p 'test_spec2web_state_scripts.py' -v
python 'C:\Users\15581\.codex\skills\.system\skill-creator\scripts\quick_validate.py' 'E:\Projects\WebBuilder\spec2web'
```

Expected: tests pass and Skill validation passes.

- [ ] **Step 3: Report completion**

Report:

```text
Created Skill folder: E:\Projects\WebBuilder\spec2web
Created OpenAI UI metadata: agents/openai.yaml
Created state scripts: init-state.py, check-state.py
Created references: install, state files, loop engineering, task breakdown, role protocol, worktree mode, delivery checklist
Verification: unittest and quick_validate results
Git: no commit because the user did not request an initial commit
```
