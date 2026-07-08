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
