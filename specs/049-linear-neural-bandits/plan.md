# Implementation Plan: Contextual Bandits with Linear Models and Neural Contextual Bandits

**Branch**: `049-linear-neural-bandits` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/049-linear-neural-bandits/spec.md`

## Summary

An engineer names up to two arms and two contexts on an In Progress task. Each context has two marks, 0 or 1. A pull adds its reward to the weights whose marks are 1, and to the pair weight when both marks are 1. A choice stores the arm with the higher linear score or the higher neural score. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `model_arm`, `model_context`, `model_pull`, and `model_choice`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 2 arms, 2 contexts, and 4 pulls, so each choice is a small count

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks. Scores are whole numbers. No learned float weights.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the two marks, the three weights, the linear score, the neural score, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the model code. |
| III. Explicit State | Arms, contexts, pulls, and the choice are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same pulls and the same model choose the same arm. The choice is stored with the command. |
| VI. Observable Actions | The task page shows each arm, each context and its marks, each pull, and the choice. |
| VII. Human Approval | Naming an arm, naming a context, recording a pull, or choosing an arm does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, four tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/049-linear-neural-bandits/
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
src/task_manager/domain/linear_bandit.py
src/task_manager/storage/linear_bandit_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_linear_bandits.py
tests/contract/test_linear_bandits_api.py
```

**Structure Decision**: The model rules live beside the existing domain and storage modules. The task page gains a Models section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the four model tables. The chosen arm and the model name are stored by the choice command. All eight gates still pass.
