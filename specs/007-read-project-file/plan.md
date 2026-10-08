# Implementation Plan: Read a Project File

**Branch**: `007-read-project-file` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/007-read-project-file/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

An engineer asks for one existing text file to be read for an In Progress task. The request names an existing project folder and one file inside it. The product stores the text it read, the path, the project, and the assistant. It does not call a model, and it does not write, replace, or delete the file. A later replay shows that stored text and does not read the file again. A read is not an implementation change, so it does not wait for approval and it does not change completion.

The work stays in the existing Python 3.12 process. A new insert-only table holds the read. The existing assistant-change command is unchanged: naming a file there still writes or proposes that file, and omitting the file still does not touch the project. Research is in [research.md](research.md).

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, pytest. SQLite through the standard-library `sqlite3` driver. Filesystem access through `pathlib`. No new dependency.

**Storage**: The same SQLite workspace file. One new insert-only table, `file_read`, with one row per read. The project path the engineer typed is stored on that row. The startup folder used to resolve a relative project path is the process startup directory already captured when the workspace opens, not a new stored setting.

**Testing**: pytest. Domain tests call the rules directly and use a temporary project folder. Contract tests call the HTTP commands with FastAPI's test client. The existing scripted clock supplies timestamps.

**Target Platform**: Local machine. The server binds to `127.0.0.1` only.

**Project Type**: Local web application with a domain library in the same process

**Performance Goals**: Recording one read completes in under 200 milliseconds on a workspace of 5,000 tasks and 5,000 implementation changes. The command reads at most one file and does not scan the project.

**Constraints**: No sign-in, no model call, no new folder, no write, and no read of a file that resolves outside the project. The client cannot choose the assistant name or the time. A read does not verify a criterion, record a check, record a decision, or change task status. Constitution v1.0.0.

**Scale/Scope**: One engineer, one assistant name, and one workspace. The existing task detail page. This feature adds one read action. An assistant change with no file stays the feature 005 record and does not read a file.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution: `.specify/memory/constitution.md` v1.0.0.

### Before research

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | The spec names the engineer, the assistant, the project path, the file, the stored text, and pass/fail scenarios for every story. Refusals name the message and the order. |
| II. Test-first verification | Pass | This phase produces no application code. Implementation is not started until tests exist for the scenario they prove. |
| III. Explicit task state | Pass | Task status stays the five stored statuses. A read adds no outcome and does not change a change's outcome. |
| IV. Traceability | Pass | The read names one task, one project, one file, the text read, and the assistant. |
| V. Deterministic behavior | Pass | The stored text is the file's text. The same file text, path, and clock must yield the same record. Replay does not read the file again. |
| VI. Observable AI actions | Pass | The stored row is the record: the task, the project, the file, the text, the assistant, and the time. No model is called. |
| VII. Human approval | Pass | This class does not change the project, so it does not wait for approval. It does not approve or write a waiting file proposal. |
| VIII. Small, independently verifiable changes | Pass | The three stories can be tested on their own. The plan adds one read, not a model, a file write, or sharing. |

No gate failed. Research records how this feature uses the existing process. It does not relax a rule.

### After design

| Gate | Result | Evidence |
|---|---|---|
| I. Clear requirements | Pass | [data-model.md](data-model.md) and the contracts restate the spec guards, including the inside-project check, the missing-file refusal, and the text rule. They do not add a behavior the spec does not name. |
| II. Test-first verification | Pass | [quickstart.md](quickstart.md) requires failing tests mapped to spec scenarios before a behavior is done. |
| III. Explicit task state | Pass | Task status is unchanged. A read is not Carried out, Awaiting approval, or Not carried out. |
| IV. Traceability | Pass | `file_read` points at one task. The row stores the project path, the file path, the text, the assistant, and the time. |
| V. Deterministic behavior | Pass | [research.md](research.md) stores the bytes read as the record. Opening the task does not read the file. A later change to the file does not change the stored row. |
| VI. Observable AI actions | Pass | The API ignores a client-supplied assistant name. The stored row keeps the file, the text, the project path the engineer typed, and the assistant. |
| VII. Human approval | Pass | The read command never writes. Approve and decline stay the existing commands and are not invoked by a read. |
| VIII. Small, independently verifiable changes | Pass | One process. The detail page calls the same function as the API. The feature 005 and feature 006 commands do not gain a read. |

No gate failed after design. No exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/007-read-project-file/
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
│   ├── implementation.py  # existing path and text checks; unchanged write rules
│   └── file_read.py       # read one file and store it
├── storage/
│   ├── schema.sql         # file_read
│   ├── file_read_store.py
│   └── task_store.py      # file_reads on the task detail
├── workspace.py           # startup folder already captured
└── web/
    ├── api.py             # file-read command
    ├── pages.py
    └── templates/detail.html

tests/
├── unit/test_file_read.py
├── contract/test_file_read_api.py
└── integration/test_replay.py   # same script twice, each with its own project folder
```

**Structure Decision**: Extend `src/task_manager`. The read rules live in a new domain module and do not import the web framework. They reuse the existing path and text checks rather than defining a second meaning of text or of staying inside the project. Storage is the only writer of `file_read`. The engineer's record command and the assistant-change command do not read a file into this table. The detail page and the JSON API call the same function. Tests pass a temporary folder as the startup directory so the suite does not read or write the repository.

## Complexity Tracking

No constitution violations require justification.
