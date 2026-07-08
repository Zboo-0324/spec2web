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
