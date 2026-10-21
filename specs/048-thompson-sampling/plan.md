# Implementation Plan: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

**Branch**: `048-thompson-sampling` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/048-thompson-sampling/spec.md`

## Summary

An engineer names up to two arms and two contexts on an In Progress task. A pull records a win or a loss for one arm in one context. A draw stores the arm with the higher middle, high, or low score in that context. The samples cycle in that order. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `explore_arm`, `explore_context`, `explore_pull`, and `explore_draw`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 2 arms, 2 contexts, and 4 pulls, so each draw is a small count

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks. Scores are whole numbers. No random draw.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the win and loss rule, the three scores, the sample order, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the exploration code. |
| III. Explicit State | Arms, contexts, pulls, and the draw are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same pulls and the same draw count choose the same arm. The sample name is stored with the draw. |
| VI. Observable Actions | The task page shows each arm, each context, each pull, and the draw. |
| VII. Human Approval | Naming an arm, naming a context, recording a pull, or drawing an arm does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, four tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/048-thompson-sampling/
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
src/task_manager/domain/exploration.py
src/task_manager/storage/exploration_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_thompson_sampling.py
tests/contract/test_thompson_sampling_api.py
```

**Structure Decision**: The exploration rules live beside the existing domain and storage modules. The task page gains an Exploration section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the four exploration tables. The chosen arm and the sample name are stored by the draw command. All eight gates still pass.
