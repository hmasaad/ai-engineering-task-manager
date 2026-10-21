# Implementation Plan: Adaptive Resource Allocation for Workflow and Agent Optimization

**Branch**: `052-adaptive-allocation` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/052-adaptive-allocation/spec.md`

## Summary

An engineer names up to four agents on an In Progress task. A yield records how much an agent returned from the workflow budget. Allocating the pool stores four units across those agents. Each unit goes to the agent with the larger whole-number product. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `allocation_agent`, `allocation_yield`, and `allocation_share`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 agents and 4 yields, so the 4 units are a small comparison

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks. Yields and shares are whole numbers. No random sample and no division.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the pool of 4, the product rule, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the allocation code. |
| III. Explicit State | Agents, yields, and shares are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same agents and yields store the same shares. The shares are stored with the command. |
| VI. Observable Actions | The task page shows each agent, each yield, and each share. |
| VII. Human Approval | Naming an agent, recording a yield, or allocating the pool does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, three tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/052-adaptive-allocation/
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
src/task_manager/domain/allocation.py
src/task_manager/storage/allocation_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_adaptive_allocation.py
tests/contract/test_adaptive_allocation_api.py
```

**Structure Decision**: The allocation rules live beside the existing domain and storage modules. The task page gains an Allocation section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the three allocation tables. The shares are stored by the allocation command. All eight gates still pass.
