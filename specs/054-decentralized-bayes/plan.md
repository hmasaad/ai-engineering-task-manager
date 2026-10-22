# Implementation Plan: Distributed Bayesian Optimization and Decentralized Scheduling

**Branch**: `054-decentralized-bayes` | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/054-decentralized-bayes/spec.md`

## Summary

An engineer names up to four points and two nodes on an In Progress task. A report records one node's local score for one point. Agreeing stores each node's suggestion and the point suggested by the most nodes. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `consensus_point`, `consensus_node`, `consensus_report`, `consensus_proposal`, and `consensus_choice`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 points, 2 nodes, and 4 reports, so each suggestion and the agreement are a small comparison

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks. Scores and settings are whole numbers. No Gaussian process and no random sample.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the local nearness rule, the agreement, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the agreement code. |
| III. Explicit State | Points, nodes, reports, suggestions, and the agreement are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same points, nodes, and reports agree on the same point. The agreement is stored with the command. |
| VI. Observable Actions | The task page shows each point, each node, each report, each suggestion, and the agreement. |
| VII. Human Approval | Naming a point, naming a node, recording a report, or agreeing does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, five tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/054-decentralized-bayes/
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
src/task_manager/domain/consensus.py
src/task_manager/storage/consensus_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_decentralized_bayes.py
tests/contract/test_decentralized_bayes_api.py
```

**Structure Decision**: The agreement rules live beside the existing domain and storage modules. The task page gains a Consensus section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the five agreement tables. The suggestions and the chosen point are stored by the agree command. All eight gates still pass.
