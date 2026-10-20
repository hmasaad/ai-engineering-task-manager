# Implementation Plan: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

**Branch**: `042-critical-paths` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/042-critical-paths/spec.md`

## Summary

An engineer names a schedule step on an In Progress task with a length of 1 or 2 days, records that one step follows another, and sets one UTC deadline. The critical path is the chain with the greatest total length. A tie chooses the chain whose first step was named first. The last step of every chain finishes at the deadline, and each earlier step finishes earlier by the days of the steps after it. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `path_step`, `path_link`, and `path_deadline`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: One task's steps are a short list

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the length, the single predecessor, the critical path, the deadline form, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the schedule code. |
| III. Explicit State | Steps, links, and the deadline are rows. Latest times and the critical path are derived from those rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | Equal lengths choose the chain named first. A deadline is stored with the command and is not read from the wall clock later. |
| VI. Observable Actions | The task page shows each step, what it follows, its latest time, the critical path, and the deadline. |
| VII. Human Approval | Naming a step, recording a link, or setting a deadline does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, two tables plus a deadline row, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/042-critical-paths/
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
src/task_manager/domain/paths.py
src/task_manager/storage/path_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_critical_paths.py
tests/contract/test_critical_paths_api.py
```

**Structure Decision**: The schedule lives beside the existing domain and storage modules. The task page gains a Workflow schedule section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only `path_step`, `path_link`, and `path_deadline`. Latest times are derived from the stored deadline and the lengths. All eight gates still pass.
