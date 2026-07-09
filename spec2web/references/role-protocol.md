# Role Protocol

Spec2Web separates responsibilities around a fixed Orchestrator. The main session stays Orchestrator and delegates work when the host provides subagent or subsession capability.

Do not call external AI services or remote agent products to simulate delegation. Delegation means using the current host's available local agent/session tools.

Fallback to single-session role switching only when:

- subagents are unavailable,
- the task is too coupled to split safely,
- the task is small enough that delegation overhead would exceed the work.

Record the fallback reason in `loop-state.md`.

## Orchestrator

- read and update `loop-state.md`
- select the current task or safe parallel batch
- delegate Developer, Tester, Reviewer, and Repairer roles when available
- ensure project rules are followed
- control worktree creation decisions
- receive worker submission packages
- decide accept, repair, block, or merge
- merge serially
- mark tasks `accepted`, `merged`, `complete`, `needs_repair`, or `blocked`
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
- submit only when `completion_criteria` are met
- set or request `status: submitted_for_acceptance`
- include the required submission package
- do not self-certify completion
- do not merge to the main branch
- do not mark `accepted`, `merged`, or `complete`

Developer submission package:

- implementation summary
- changed files
- verification commands run and results
- risks, limitations, or follow-up

## Tester

- run task verification
- add or propose missing behavior tests when appropriate
- record results in `validation-log.md`
- distinguish pre-existing failures from new failures
- recommend pass, repair, or block; do not accept or merge

## Reviewer

Reviewer is read-only.

Check:

- task maps to requirements
- changed files stay inside `allowed_paths`
- implementation follows `project-rules.md`
- no unplanned full-project generation occurred
- no dependency was added without justification
- verification evidence exists
- submission package is sufficient
- acceptance gate can be evaluated
- worktree mode did not bypass merge review

Reviewer recommends approve, repair, or block. Reviewer does not merge or mark the task complete.

## Repairer

- repair only from explicit failure evidence
- change one main cause per attempt
- stay within repair budget
- update `validation-log.md`
- return the task to `submitted_for_acceptance` only after new evidence exists

## Delivery

- produce `delivery-report.md`
- include completed features, validation evidence, run instructions, known risks, and not-completed items
