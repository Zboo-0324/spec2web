# Worktree Mode

Worktree mode isolates task execution. It is a workflow protocol, not a background scheduler.

## Preconditions

- The project is a Git repository.
- The user has not disabled worktree mode.
- Each task has a task contract.
- Orchestrator controls merge decisions.
- Workers submit evidence; Orchestrator accepts, merges, and marks completion.

If the project is not a Git repository, ask the user before initializing Git.

## Default Single-Task Mode

```text
Orchestrator selects one task
-> create branch and worktree
-> Developer implements in the worktree
-> Developer submits implementation package
-> task verification runs in the worktree
-> Reviewer checks diff and evidence
-> Orchestrator evaluates the acceptance gate
-> Orchestrator merges if accepted
-> main workspace verification runs
-> state files are updated
```

## Controlled Multi-Worker Mode

```text
Orchestrator selects a no-conflict parallel group
-> create one branch and worktree per task
-> one Developer worker executes each task
-> each Developer submits an implementation package
-> each task gets Tester evidence
-> Reviewer reviews each diff separately
-> Orchestrator evaluates each acceptance gate
-> Orchestrator merges accepted tasks serially
-> after each merge, run affected verification in the main workspace
-> stop later merges if any merge fails
```

## Merge Rules

- Workers never merge their own work.
- Merges are serial, even when development was parallel.
- Developer status can advance only to `submitted_for_acceptance`.
- Orchestrator alone marks `accepted`, `merged`, or `complete`.
- Diff review is required before merge.
- Acceptance gate evaluation is required before merge.
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
