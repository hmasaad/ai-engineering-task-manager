# Implementation Plan: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

**Branch**: `045-contextual-bandits` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/045-contextual-bandits/spec.md`

## Summary

An engineer names up to two actions and up to four contexts on an In Progress task, then records up to four trials. Each trial gives one action a reward of 1 or 2 in one context. A choice tries the earliest-named action that has no trial in that context. When every action has a trial there, the choice is the action with the higher average reward, and a tie keeps the action named first. The choice is stored with the request. These commands do not advance the workflow or change the task status.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Jinja2, SQLite, pytest. No new package.

**Storage**: SQLite tables `bandit_action`, `bandit_context`, `bandit_trial`, and `bandit_choice`. No column is added to an existing table.

**Testing**: pytest, unit and contract

**Target Platform**: Local web application on `127.0.0.1`

**Project Type**: Web application

**Performance Goals**: At most 2 actions, 4 contexts, and 4 trials, so the totals stay small

**Constraints**: Localhost only. One engineer. No new dependencies. `GET /api/tasks` stays a list of tasks.

**Scale/Scope**: One workspace and one task at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
|---|---|
| I. Clear Requirements | The spec names the limits, the reward, the untried-action rule, the average-reward rule, and every refusal sentence. |
| II. Test-First | Unit and contract checks are written before the bandit code. |
| III. Explicit State | Actions, contexts, trials, and the choice are rows. The totals are counted from the stored trials. |
| IV. Traceability | Each requirement maps to a check in tasks.md. |
| V. Deterministic Behavior | An equal average chooses the action named first. The choice is stored with the request and is not read from the wall clock. |
| VI. Observable Actions | The task page shows each action, each context, each trial, each learned total, and the choice. |
| VII. Human Approval | Naming an action, naming a context, recording a trial, or choosing does not approve, deliver, commit, or open a pull request. |
| VIII. Small Changes | One domain module, one store, four tables, and the task page section. |

## Project Structure

### Documentation (this feature)

```text
specs/045-contextual-bandits/
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
src/task_manager/domain/bandit.py
src/task_manager/storage/bandit_store.py
src/task_manager/storage/schema.sql
src/task_manager/web/templates/detail.html
tests/unit/test_contextual_bandits.py
tests/contract/test_contextual_bandits_api.py
```

**Structure Decision**: The bandit lives beside the existing domain and storage modules. The task page gains a Bandit section.

## Complexity Tracking

No constitution violation requires an exception.

## Post-Design Constitution Check

The design adds only the four bandit tables. The choice is stored by the choose command. The totals are counted from stored trials. All eight gates still pass.
