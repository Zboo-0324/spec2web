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
-> create branch and worktree
-> Developer implements in the worktree
-> task verification runs in the worktree
-> Reviewer checks diff and evidence
-> Orchestrator merges if approved
-> main workspace verification runs
-> state files are updated
```

## Controlled Multi-Worker Mode

```text
Orchestrator selects a no-conflict parallel group
-> create one branch and worktree per task
-> one Developer worker executes each task
-> each worker runs task verification
-> Reviewer reviews each diff separately
-> Orchestrator merges tasks serially
-> after each merge, run affected verification in the main workspace
-> stop later merges if any merge fails
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
