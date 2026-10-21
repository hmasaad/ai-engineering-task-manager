# Implementation Plan: Multi-Fidelity Bayesian Optimization and Successive Halving

**Branch**: `051-fidelity-halving` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/051-fidelity-halving/spec.md`

## Summary

An engineer names up to four candidates on an In Progress task. A measurement records a cheap fidelity 1 score or an expensive fidelity 2 score. Halving stores the better half of the cheap scores. The winner is the kept candidate with the highest expensive score, and only after every kept candidate has one. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `fidelity_candidate`, `fidelity_measurement`, `fidelity_round`, and `fidelity_kept`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 4 candidates and 6 measurements, so the kept half and the winner are a small comparison

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks. Scores are whole numbers. No Gaussian process and no random sample.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the two fidelities, the half that is kept, the winner rule, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the fidelity code. |
| III. Explicit State | Candidates, measurements, the kept names, and the winner are rows. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | The same candidates and measurements keep the same names and name the same winner. The halving is stored with the command. |
| VI. Observable Actions | The task page shows each candidate, each measurement, the kept names, and the winner. |
| VII. Human Approval | Naming a candidate, recording a measurement, or halving the field does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, four tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/051-fidelity-halving/
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
src/task_manager/domain/fidelity.py
src/task_manager/storage/fidelity_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_fidelity_halving.py
tests/contract/test_fidelity_halving_api.py
```

**Structure Decision**: The fidelity rules live beside the existing domain and storage modules. The task page gains a Fidelity section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the four fidelity tables. The kept names and the winner are stored by the halving command. All eight gates still pass.
