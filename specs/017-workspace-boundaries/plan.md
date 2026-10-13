# Implementation Plan: Workspace Boundaries and Capability-Based Permissions

**Branch**: `017-workspace-boundaries` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-workspace-boundaries/spec.md`

## Summary

One start reads and writes one workspace file. A second workspace file stays separate. Closing and opening the same file preserves tasks, statuses, and evidence. Task records do not create, delete, or modify project files and do not run a repository command. Each repository command remains one capability for one named target. Approving one waiting change does not carry out another.

No new table, no new command, and no permission screen. The work is tests that lock those boundaries. Specifications 001 through 016 keep their commands.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file named at start. No new table and no new column.

**Testing**: pytest. Unit tests cover one workspace boundary or one capability rule at a time. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Listing tasks in one workspace finishes in under 200 milliseconds on a workspace of 5,000 tasks. This feature adds no query.

**Constraints**: One engineer, no sign-in. The client cannot choose the workspace file after start. Constitution v1.0.0. Specifications 001 through 016 are not rewritten. Task-record commands do not call a repository command.

**Scale/Scope**: One engineer and one workspace file per start. This feature adds no task status and no repository command.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names workspace separation, restart, task records, and one capability per target. |
| II. Test-first verification | Pass | This phase produces no application code. |
| III. Explicit task state | Pass | Task statuses stay Draft, Ready, In Progress, Completed, and Cancelled. |
| IV. Traceability | Pass | A capability remains the stored command on its task. |
| V. Deterministic behavior | Pass | Reopening a workspace reads stored records. It does not run a repository command again. |
| VI. Observable AI actions | Pass | Evidence stays in the workspace that recorded it. |
| VII. Human approval | Pass | A consequential capability still waits. One approval does not cover another change. The assistant cannot approve. |
| VIII. Small, independently verifiable changes | Pass | Tests only. Earlier specifications are not rewritten. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names the workspace file and the existing capability records. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires the new tests to fail if a boundary is broken. |
| III. Explicit task state | Pass | [research.md](research.md) adds no status. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) maps each capability to the command that already stores it. |
| V. Deterministic behavior | Pass | A later start with the same workspace file reads the stored rows. Stored evidence is not rewritten. |
| VI. Observable AI actions | Pass | The assistant name and the evidence stay on the record that already stores them. |
| VII. Human approval | Pass | The contract says an approval names one change. Waiting capabilities on that task stay waiting. |
| VIII. Small, independently verifiable changes | Pass | No new module. Tests call the existing workspace commands. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/017-workspace-boundaries/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/task_manager/
├── workspace.py          # one connection to the named workspace file
└── domain/               # existing commands; this feature adds none

tests/
├── unit/test_workspace_boundary.py
└── unit/test_capability.py
```

**Structure Decision**: Do not add a domain module. `Workspace` already opens only the file it is given, and each repository command already names one target. The tests call those commands.

## Complexity Tracking

No constitution violations require justification.
