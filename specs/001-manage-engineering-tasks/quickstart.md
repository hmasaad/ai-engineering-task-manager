# Quickstart: Manage Engineering Tasks

Validation guide for the local task manager. Implementation details and test bodies belong in the implementation phase. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root

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

Expected: every test passes. The suite must include, before the corresponding behavior is considered done:

- domain tests for each allowed transition and for the refusals in the spec
- a replay test that runs the same command script twice against empty workspaces with the same scripted clock and compares statuses and ordering
- contract tests that call the HTTP commands and assert the status codes and error messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --port 8000
```

Then open `http://127.0.0.1:8000/`. The process must refuse connections that are not from the local machine. `--engineer` is the name copied onto verifications. Omitting it uses `Engineer`.

## Manual scenarios

Use a fresh `workspace.db` for each scenario, or delete the file first. Times below are whatever the clock records. Statuses and messages are the expected outcomes.

### 1. Capture a task

1. Create a task titled `Add export` with goal `An engineer can take a finished task record with them` and two acceptance criteria.
2. Confirm the list shows it as Draft, and the detail shows both criteria as Unverified.
3. Submit a blank title. Confirm nothing is created and the page says a title is required.
4. Mark the task Ready. Confirm the status is Ready.
5. On a second Draft task that has a goal and no criterion, mark Ready. Confirm it stays Draft and the message asks for an acceptance criterion.
6. On a Ready task with one criterion, remove that criterion. Confirm the status returns to Draft.

### 2. Complete and reopen

1. Start a Ready task. Confirm the history records Ready to In Progress and the cause `started`.
2. Verify one of two criteria with an observation and pass. Confirm that criterion names the engineer, and the task stays In Progress.
3. Submit an observation without pass. Confirm that criterion stays Unverified.
4. Mark the task completed while a criterion is Unverified. Confirm it stays In Progress and the message names the unmet criterion.
5. From a Ready task, mark completed. Confirm it stays Ready.
6. Verify every criterion, then mark completed. Confirm the status is Completed.
7. Reopen with reason `A missed case was found`. Confirm In Progress, the reason in history, and the criteria still Verified.
8. On a Completed parent whose only subtask is Completed, reopen the subtask with a reason. Confirm both are In Progress and both histories record that reopen.
9. Cancel an In Progress task that has no unfinished subtask, with a reason. Confirm Cancelled.
10. Try to move that Cancelled task back to any active status. Confirm it stays Cancelled and the message says continued work is a new task.

### 3. Subtasks

1. Add two subtasks to an In Progress parent. Confirm they are Draft and listed in the order created.
2. Verify the parent's own criteria and leave one subtask Ready. Mark the parent completed. Confirm the parent stays In Progress and the message names that subtask.
3. Complete the subtask, then complete the parent. Confirm the parent is Completed.
4. Try to add a subtask to a Completed parent. Confirm the message says to reopen the parent first.
5. Try to make a parent a subtask of its own child. Confirm the link is unchanged.

### 4. Decisions

1. Record a decision with a statement and a rationale. Confirm it appears with a time.
2. Record a later decision that supersedes two earlier decisions on that task. Confirm all three remain visible and the later one names both.
3. Submit a decision with a blank rationale. Confirm it is not saved.
4. Point a decision at a decision on another task. Confirm it is not saved.
5. On a Cancelled task, record a decision. Confirm it is not saved.

## Done when

- `pytest` passes.
- Scenarios 1 through 4 match the outcomes above on a fresh workspace.
- A reader can open a completed task and name its status and the cause of the latest status change without asking the person who did the work.
