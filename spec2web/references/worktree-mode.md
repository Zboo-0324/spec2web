# PR/Worktree Mode

PR/worktree mode isolates task execution and makes each worker handoff reviewable. It is a workflow protocol, not a background scheduler.

## Definition

`PR` means a reviewable handoff. It can be:

- a real remote pull request when the repo has a configured remote and the user permits pushing, or
- a local PR package: task branch, worktree path, commit hash, diff command, verification evidence, and submission summary.

Do not call Claude, external AI services, remote agent products, or another model provider for worker execution. Workers must be host-provided subagents, subsessions, or the documented single-session fallback.

## Preconditions

- The project is a Git repository.
- The user has not disabled PR/worktree mode.
- Each task has a task contract.
- Each implementation task has `handoff_mode: pr_worktree`.
- Orchestrator controls branch, worktree, PR, and merge decisions.
- Workers submit evidence; Orchestrator accepts, merges, and marks completion.

If the project is not a Git repository, ask the user before initializing Git.

## Default Single-Task Mode

```text
Orchestrator selects one task
-> Orchestrator creates task branch and worktree
-> Orchestrator delegates Developer with task contract, branch, worktree, and allowed_paths
-> Developer edits only in the assigned worktree
-> Developer runs task verification
-> Developer commits only to the task branch
-> Developer submits local or remote PR package
-> Tester verifies the submitted branch or worktree
-> Reviewer checks diff, evidence, scope, and project rules
-> Orchestrator evaluates the acceptance gate
-> Orchestrator merges if accepted
-> main workspace verification runs
-> state files are updated
```

## Controlled Multi-Worker Mode

```text
Orchestrator selects a no-conflict parallel group
-> Orchestrator creates one branch and worktree per task
-> Orchestrator delegates one Developer worker per task
-> each Developer works only in its assigned worktree
-> each Developer commits only to its task branch
-> each Developer submits a PR package
-> each task gets Tester evidence and Reviewer review
-> Orchestrator evaluates each acceptance gate
-> Orchestrator merges accepted tasks serially
-> after each merge, run affected verification in the main workspace
-> stop later merges if any merge fails or conflicts
```

## Orchestrator Duties

- create task branch and worktree from the approved base,
- give the worker only the bounded task contract and allowed write scope,
- record branch, worktree, and handoff status in `loop-state.md`,
- receive the PR package,
- review diff and evidence before merge,
- run or delegate verification,
- merge serially,
- run post-merge verification in the main workspace,
- clean up worktrees only after state and validation evidence are updated.

## Worker Duties

- work only in the assigned worktree,
- edit only `allowed_paths`,
- do not pull unrelated changes into the task branch unless Orchestrator instructs it,
- do not touch the main workspace,
- do not merge to the main branch,
- do not push or open a remote PR unless Orchestrator explicitly permits it,
- commit task changes to the task branch before submitting,
- submit the PR package and stop.

## PR Package

Every Developer submission must include:

- task ID and requirement IDs,
- branch name,
- worktree path,
- commit hash,
- changed files,
- summary of implementation,
- verification commands and results,
- known risks, limitations, or follow-up,
- diff command, such as `git diff <base>...<branch>`.

For a real remote PR, also include the PR URL. For a local PR package, record the package in `loop-state.md` or the task entry.

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
local_pr: TASK-001/<short-title>
```

Record actual branch, worktree path, handoff status, and PR URL when present in `loop-state.md`.
