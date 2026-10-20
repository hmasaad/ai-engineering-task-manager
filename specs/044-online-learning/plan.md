# Implementation Plan: Online Learning and Predictive Workflow Scheduling

**Branch**: `044-online-learning` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/044-online-learning/spec.md`

## Summary

An engineer records up to four outcomes on an In Progress task. Each outcome names a kind of work and an actual length of 1 or 2 days. The predicted length of a kind is 2 only when its 2-day outcomes outnumber its 1-day outcomes. The engineer then names up to four forecasts of learned kinds. Predicting the schedule stores a start day for each forecast. Forecasts run one at a time, oldest first, using the predicted length of each kind. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `learn_outcome`, `learn_forecast`, `learn_plan`, and `learn_placement`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 outcomes and 4 forecasts, so the counts and the schedule stay small

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the length, the limit of 4, the prediction count, the one-at-a-time order, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the learning code. |
| III. Explicit State | Outcomes, forecasts, and the predicted schedule are rows. The kind prediction is counted from the stored outcomes. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | A tie predicts 1 day. Forecasts run oldest first. The schedule is stored with the prediction and is not read from the wall clock. |
| VI. Observable Actions | The task page shows each outcome, each learned kind, each forecast, and the finish day. |
| VII. Human Approval | Recording an outcome, naming a forecast, or predicting a schedule does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, four tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/044-online-learning/
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
src/task_manager/domain/learning.py
src/task_manager/storage/learning_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_online_learning.py
tests/contract/test_online_learning_api.py
```

**Structure Decision**: The learner lives beside the existing domain and storage modules. The task page gains a Learning section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the four learning tables. The schedule is stored by the prediction command. The kind prediction is counted from stored outcomes. All eight gates still pass.
