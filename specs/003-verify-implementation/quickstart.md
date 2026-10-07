# Quickstart: Verify a Recorded Change

Validation guide for checks on a carried-out implementation change. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root
- Feature 001 and feature 002 behavior already in the workspace process (create a task, mark it Ready, start it, record a change)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Automated check

```bash
pytest
```

Expected: every test passes, including the feature 001 and feature 002 suites. The suite must include, before the corresponding behavior is considered done:

- domain tests for a Passed check, a Failed check, a later check of the same pair, a check of a second criterion, and the refusals in the spec
- domain tests that completion stays In Progress while a carried-out change lacks a passing check, including when one checked criterion is currently Failed and another is Passed, and that completion succeeds once every checked criterion is currently Passed and the earlier guards hold
- domain tests that cancellation still succeeds while a carried-out change lacks a passing check
- a replay test that runs the same check script twice from an In Progress task with one carried-out change and no checks, using the same scripted clock, and compares results and order
- contract tests that call the new HTTP command and the completion refusal, and assert the status codes and messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --port 8000
```

Then open `http://127.0.0.1:8000/`. `--engineer` is the name copied onto checks. Omitting it uses `Engineer`.

## Manual scenarios

Use a fresh `workspace.db`, or delete the file first. Create an In Progress task with a goal and two acceptance criteria before scenario 1. Record one ordinary change before scenario 1. Statuses and messages are the expected outcomes.

### 1. Check a carried-out change

1. On the In Progress task, record a check of the ordinary change against the first criterion, with evidence `The detail page shows the goal in the export` and result Passed. Confirm the check shows that criterion wording, the evidence, Passed, Ada, and a time. Confirm the change stays Carried out and the status stays In Progress.
2. Record a check of the same change against the second criterion with non-empty evidence and result Failed. Confirm both checks appear in that order and the second is Failed.
3. Submit a blank evidence account. Confirm nothing is saved and the page says an account of the evidence is required.
4. Submit a check with no result. Confirm nothing is saved and the page says to choose Passed or Failed.
5. On a Completed task, record a check. Confirm nothing is saved and the page says to reopen the task first.
6. Record a consequential change and leave it Awaiting approval. Confirm it offers no check. Record a consequential change and mark it not carried out. Confirm it offers no check.

### 2. Completion waits for a passing check

1. On an In Progress task whose criteria are Verified and that has no unfinished subtask, record an ordinary change and do not check it. Mark the task completed. Confirm it stays In Progress and the message names that change as needing a passing check.
2. Check that change against one criterion with result Failed, and against the other with result Passed. Mark the task completed. Confirm it stays In Progress and the message names that change.
3. Record a later check of the failed criterion with result Passed. Confirm the earlier Failed check is still listed. Mark the task completed. Confirm the status is Completed.
4. On another In Progress task with no unfinished subtask, record an ordinary change and do not check it. Cancel with a reason. Confirm the status is Cancelled.

### 3. A later check stays beside the earlier one

1. On one carried-out change, record a Failed check against one criterion, then a Passed check against that same criterion. Confirm both remain in that order and the current result of that pair is Passed.
2. Confirm the task can be completed when its other guards hold and no checked criterion is currently Failed.

## Done when

- `pytest` passes, including feature 001 and feature 002 tests.
- Scenarios 1 through 3 match the outcomes above on a fresh workspace.
- A reader can open the task and state what was checked, the evidence, and whether the change passed, without the original conversation.
