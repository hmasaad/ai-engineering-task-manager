# Implementation Plan: Safe Exploration, Causal Inference, and Counterfactual Evaluation

**Branch**: `047-safe-exploration` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/047-safe-exploration/spec.md`

## Summary

An engineer names up to two actions on an In Progress task, each with a risk of 1 or 2. A probe is allowed only for a risk of 1. A comparison stores the effect of taking one action instead of another in the same state: the earliest reward of the named action minus the earliest reward of the action it replaces. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `safe_action`, `safe_probe`, and `safe_effect`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 2 actions and 4 probes, so the earliest probe of each action is a small scan

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the risk, the limit of 2 actions and 4 probes, the safe-probe rule, the effect rule, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the safety code. |
| III. Explicit State | Actions, probes, and the effect are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The earliest probe of each action in the state is the one that counts. The effect is stored with the comparison and is not read from the wall clock. |
| VI. Observable Actions | The task page shows each action, its risk, each probe, and the effect. |
| VII. Human Approval | Naming an action, recording a probe, or comparing actions does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, three tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/047-safe-exploration/
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
src/task_manager/domain/safety.py
src/task_manager/storage/safety_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_safe_exploration.py
tests/contract/test_safe_exploration_api.py
```

**Structure Decision**: The safety rules live beside the existing domain and storage modules. The task page gains a Safety section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the three safety tables. The effect is stored by the comparison command. All eight gates still pass.
