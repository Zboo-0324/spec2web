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
- handoff_mode: pr_worktree
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
  - branch name and commit hash
  - worktree path
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

## Handoff Mode

Use `handoff_mode: pr_worktree` for implementation tasks when the project is a Git repository. This means:

- Orchestrator creates the task branch and worktree,
- Developer works only in that worktree,
- Developer commits only to the task branch,
- Developer submits a local or remote PR package,
- Orchestrator reviews, tests, accepts, and merges.

Use `handoff_mode: single_session` only when subagents are unavailable, the task is too coupled to isolate safely, or the task is small enough that delegation overhead exceeds the work. Record the reason in `loop-state.md`.

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
