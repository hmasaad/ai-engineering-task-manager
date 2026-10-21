# Implementation Plan: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

**Branch**: `053-asha-scheduling` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/053-asha-scheduling/spec.md`

## Summary

An engineer names up to four trials and two runners on an In Progress task. A rung score records an early or promoted result. Scheduling stores the better half of the rung 1 scores recorded so far, assigns the next promoted trial to the least-loaded runner, and names a winner once every promoted trial has a rung 2 score. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `asha_trial`, `asha_runner`, `asha_rung`, `asha_promoted`, `asha_assignment`, and `asha_winner`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 trials, 2 runners, and 6 rung scores, so promotion and the next runner are a small comparison

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks. Scores are whole numbers. No random sample and no extra bracket.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the early promotion rule, the least-loaded runner, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the scheduling code. |
| III. Explicit State | Trials, runners, rung scores, promoted names, assignments, and the winner are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same trials, runners, and scores schedule the same assignment. The schedule is stored with the command. |
| VI. Observable Actions | The task page shows each trial, each runner, each rung score, the promoted trials, the assignments, and the winner. |
| VII. Human Approval | Naming a trial, naming a runner, recording a rung score, or scheduling does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, six tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/053-asha-scheduling/
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
src/task_manager/domain/asha.py
src/task_manager/storage/asha_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_asha_scheduling.py
tests/contract/test_asha_scheduling_api.py
```

**Structure Decision**: The scheduling rules live beside the existing domain and storage modules. The task page gains a Hyperband section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the six scheduling tables. The promoted trials, the assignments, and the winner are stored by the schedule command. All eight gates still pass.
