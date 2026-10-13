# Implementation Plan: Verification Evidence and Trace Gaps

**Branch**: `018-verification-evidence` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/018-verification-evidence/spec.md`

## Summary

Verifying a criterion stores the method and the test-run identifier the engineer entered, with the observation, the pass, the time, and the workspace engineer. The gap analysis also lists tasks with no linked requirement and criteria that are Unverified. Requirement identifiers, gap phrases, and completion rules stay as they are.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through `sqlite3`. No new dependency.

**Storage**: The existing SQLite workspace file. One new table, `criterion_evidence`, because `acceptance_criterion` cannot gain a column. No change to `requirement` or `verification_run`.

**Testing**: pytest. Unit tests cover one verification or one gap rule at a time. Contract tests cover the verify command and the trace read. Existing feature tests stay green.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Listing the gap analysis finishes in under 200 milliseconds on a workspace of 5,000 tasks. The new read is one query for tasks and one query for criteria.

**Constraints**: One engineer, no sign-in. Constitution v1.0.0. Specifications 001 through 017 are not rewritten. `GET /api/requirements` stays a list of requirements.

**Scale/Scope**: One engineer and one workspace file per start. Two new fields on a criterion verification, and two lists on the existing gap analysis.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the method, the test-run identifier, and the two gap lists. |
| II. Test-first verification | Pass | The spec says the rules are covered by automated checks. This phase produces no application code. |
| III. Explicit task state | Pass | Task statuses stay Draft, Ready, In Progress, Completed, and Cancelled. Verified stays a criterion state. |
| IV. Traceability | Pass | The method and the test-run identifier are stored on the criterion. The gap lists name tasks and criteria the requirement list misses. |
| V. Deterministic behavior | Pass | Opening the task and opening the gap analysis do not rewrite stored evidence. |
| VI. Observable AI actions | Pass | The engineer enters the method and the identifier. The product does not infer them. |
| VII. Human approval | Pass | This feature does not carry out a consequential action. Verification stays an engineer command. |
| VIII. Small, independently verifiable changes | Pass | Two stories. Specifications 001 through 017 are not rewritten. |

No gate failed.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) names `criterion_evidence` and the two trace lists. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) names the tests that must pass. |
| III. Explicit task state | Pass | [research.md](research.md) adds no task status. |
| IV. Traceability | Pass | [contracts/commands.md](contracts/commands.md) keeps the requirement list and adds the trace read. |
| V. Deterministic behavior | Pass | A later start reads the stored method and identifier. Clearing verification deletes that row. |
| VI. Observable AI actions | Pass | The stored method and identifier are the trimmed text the engineer entered. |
| VII. Human approval | Pass | No new consequential command. The assistant still does not verify a criterion. |
| VIII. Small, independently verifiable changes | Pass | One table and one read. Existing requirement phrases stay. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/018-verification-evidence/
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
src/task_manager/
├── domain/capture.py
├── storage/schema.sql
├── storage/task_store.py
├── storage/requirement_store.py
├── web/api.py
├── web/pages.py
├── web/templates/detail.html
├── web/templates/requirements.html
└── workspace.py

tests/unit/test_criterion_evidence.py
tests/unit/test_traceability.py
tests/contract/test_criterion_evidence_api.py
tests/contract/test_traceability_api.py
```

**Structure Decision**: The domain and the pages already used by verification and by the requirement list. No new module.
