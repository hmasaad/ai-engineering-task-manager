# Implementation Plan: Apply an Ordinary File

**Branch**: `006-apply-ordinary-file` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-apply-ordinary-file/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

An engineer asks the assistant to write one file for an In Progress task. The request names an existing project folder, one file inside it, the text the file should contain, and whether the change is ordinary or consequential. An ordinary request that is not stopped writes a new file and is stored as Carried out. A consequential request, a stopped request, and a request that would replace an existing file are stored as consequential and Awaiting approval, and they do not change the project until the engineer approves. Approval writes the proposed text only when the file still matches the recorded text and still lands inside the project. The assistant cannot approve or decline. Replay reads the stored record and does not write the file again.

The work stays in the existing Python 3.12 process. The text in the request is the assistant's recorded output. The command does not call a model. A new insert-only table sits beside the assistant change from feature 005. Research is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver. Filesystem access through `pathlib`. No new dependency.

**Storage**: The same SQLite workspace file. One new insert-only table, `applied_file`, with at most one row per implementation change. The project path the engineer typed stays on the existing `assistant_change` row. The startup folder used to resolve a relative project path is the process startup directory, not a stored setting.

**Testing**: pytest. Domain tests call the rules directly and use a temporary project folder. Contract tests call the HTTP commands with FastAPI's test client. The existing scripted clock supplies timestamps.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording or approving one file change completes in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 implementation changes. The command reads and writes at most one file and does not scan the project.

**Constraints**: No sign-in, no model call, no new folder, no delete, and no write outside the resolved project folder. The client cannot choose the assistant name, the engineer name, or the time. A file change does not verify a criterion, record a check, record a decision, or change task status. An ordinary change still means the file was written. Constitution v1.0.0.

**Scale/Scope**: One engineer, one assistant name, and one workspace. The existing task detail page. This feature adds one file to the assistant-change action. An assistant change with no file stays the feature 005 record and writes nothing.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the assistant, the project path, the file, ordinary and consequential, and pass/fail scenarios for every story. Clarifications fix the path, the stored class, links, and a file that is not text. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | Task status stays the five stored statuses. The change outcome stays Carried out, Awaiting approval, or Not carried out. |
| IV. Traceability | Pass | The change names one task, one project, one file, the text it had, and the text written or proposed. |
| V. Deterministic behavior | Pass | The file text in the request is the recorded output. The same stored text, path, and clock must yield the same outcome. Replay does not write the file again. |
| VI. Observable AI actions | Pass | The stored row is the assistant's record: the task, the project, the file, the text, the assistant, and the outcome. |
| VII. Human approval | Pass | Replacing a file, a consequential request, and a stopped request do not write until the engineer approves that proposal. The assistant cannot approve it. |
| VIII. Small, independently verifiable changes | Pass | The three stories can be tested on their own. The plan adds one file write, not a model, a folder creator, or sharing. |

No gate failed. Research records how this feature uses the existing process. It does not relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards, including exclusive create, the consequential class for a replacement, and the approval match check. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | Task status is unchanged. A written new file is ordinary and Carried out. A replacement, a stop, and a consequential request are consequential and Awaiting approval. |
| IV. Traceability | Pass | `applied_file` points at one `implementation_change`, which already points at the task. The row stores the file path, whether it was new, the previous text, and the proposed text. |
| V. Deterministic behavior | Pass | [research.md](research.md) treats the submitted text as the recorded output. Reading the task does not write. A second command against a file that now exists does not overwrite it. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied assistant name. The stored row keeps the file, the text, the project path the engineer typed, and the outcome. |
| VII. Human approval | Pass | Approve writes only while the change is Awaiting approval, the file still matches, and the resolved path stays inside the project. `actor` of `assistant` writes nothing. Decline does not write. |
| VIII. Small, independently verifiable changes | Pass | One process. The detail page calls the same functions as the API. An omitted file keeps the feature 005 command and does not touch the filesystem. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/006-apply-ordinary-file/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/task_manager/
├── domain/
│   └── implementation.py  # write or propose one file; existing record stays
├── storage/
│   ├── schema.sql         # applied_file
│   └── implementation_store.py
├── workspace.py           # startup folder for a relative project path
└── web/
    ├── api.py             # file fields on the assistant-change command
    ├── pages.py
    └── templates/detail.html

tests/
├── unit/test_applied_file.py
├── contract/test_applied_file_api.py
└── integration/test_replay.py   # same script twice, each with its own project folder
```

**Structure Decision**: Extend `src/task_manager`. The file rules live in the existing implementation module and do not import the web framework. Storage is the only writer of `applied_file`. The engineer's record command does not write a file. The detail page and the JSON API call the same functions. Tests pass a temporary folder as the startup directory so the suite does not write into the repository.

## Complexity Tracking

No constitution violations require justification.
