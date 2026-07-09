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
- status: pending
- allowed_paths:
  - path/pattern
- expected_outputs:
  - path or behavior
- verification:
  - exact command or manual check
- completion_criteria:
  - worker-observable condition for submitting the task
- acceptance_gate:
  - Orchestrator check required before accepting or merging
- submission_package:
  - implementation summary
  - changed files
  - verification evidence
  - known risks or follow-up
- risks_or_blockers:
  - none
- execution_workspace: main or worktree
- parallel_group: none or PG-000
- merge_policy: orchestrator_review_then_serial_merge
```

## Completion vs Acceptance

`completion_criteria` describes when a worker can submit the task for acceptance. It is not permission to mark the task complete.

Use these status values:

- `pending`: task is ready or waiting on dependencies.
- `in_progress`: a worker is executing the task.
- `submitted_for_acceptance`: Developer has submitted the task package.
- `needs_repair`: Orchestrator or Reviewer rejected the submission with evidence.
- `accepted`: Orchestrator accepted the task before merge.
- `merged`: Orchestrator merged the accepted task.
- `complete`: post-merge verification passed and state is updated.
- `blocked`: task cannot proceed without user input or external change.

Only Orchestrator may set `accepted`, `merged`, or `complete`. Developer, Tester, and Reviewer provide evidence; they do not self-certify completion.

## Acceptance Gate

Each `acceptance_gate` must be specific enough for Orchestrator to decide accept, repair, or block. Include:

- required verification command or manual check,
- Reviewer scope and quality check,
- requirement IDs covered,
- main-workspace verification needed after merge,
- rejection conditions such as scope drift, missing evidence, conflict, or failed tests.

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
