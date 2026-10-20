# Implementation Plan: Constraint Programming and Optimization for Workflow Scheduling

**Branch**: `043-constraint-optimization` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/043-constraint-optimization/spec.md`

## Summary

An engineer names up to four activities on an In Progress task, each with a length of 1 or 2 days, records precedence constraints, and sets a capacity of 1 or 2. Optimization stores the start day of each activity. The starts obey every constraint and the capacity, finish on the earliest possible day, and break a tie by starting earlier-named activities sooner. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `opt_activity`, `opt_constraint`, `opt_capacity`, `opt_plan`, and `opt_placement`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 activities, so every legal start can be checked

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the length, the limit of 4, the precedence pair, the capacity, the finish rule, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the optimization code. |
| III. Explicit State | Activities, constraints, capacity, and the plan are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | Equal finish days choose the earlier-named activities. The plan is stored with the optimization and is not read from the wall clock. |
| VI. Observable Actions | The task page shows each activity, its start, each constraint, the capacity, and the finish day. |
| VII. Human Approval | Naming an activity, recording a constraint, setting a capacity, or optimizing does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, five tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/043-constraint-optimization/
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
src/task_manager/domain/optimization.py
src/task_manager/storage/optimization_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_constraint_optimization.py
tests/contract/test_constraint_optimization_api.py
```

**Structure Decision**: The optimizer lives beside the existing domain and storage modules. The task page gains an Optimization section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the five optimization tables. The plan is stored by the optimization command. All eight gates still pass.
