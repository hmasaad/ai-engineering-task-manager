# Implementation Plan: Offline Reinforcement Learning and Policy Evaluation

**Branch**: `046-policy-evaluation` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/046-policy-evaluation/spec.md`

## Summary

An engineer records up to four logged steps on an In Progress task. Each step names a state, an action, and a reward of 1 or 2. The engineer then names one action for each state that appears in the log. Evaluation stores the total reward and the count of the logged steps whose action matches that rule. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `eval_log`, `eval_rule`, and `eval_score`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 logged steps, so the score stays a small total and count

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the reward, the limit of 4, the one-action rule, the matching score, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the evaluation code. |
| III. Explicit State | Logged steps, rules, and the score are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same log and the same rules produce the same total and count. The score is stored with the evaluation and is not read from the wall clock. |
| VI. Observable Actions | The task page shows each logged step, each rule, and the score. |
| VII. Human Approval | Recording a logged step, naming a rule, or evaluating a policy does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, three tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/046-policy-evaluation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── commands.md
└── tasks.md
```

### Source Code (repository root)

```text
src/task_manager/domain/evaluation.py
src/task_manager/storage/evaluation_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_policy_evaluation.py
tests/contract/test_policy_evaluation_api.py
```

**Structure Decision**: The evaluation lives beside the existing domain and storage modules. The task page gains a Policy section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the three evaluation tables. The score is stored by the evaluation command. All eight gates still pass.
