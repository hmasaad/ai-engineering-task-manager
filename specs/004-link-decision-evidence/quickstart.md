# Quickstart: Link a Decision to Its Evidence

Validation guide for a decision that names one change check. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root
- Feature 001, feature 002, and feature 003 behavior already in the workspace process (create a task, mark it Ready, start it, record a change, record a check)

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

Expected: every test passes, including the feature 001, feature 002, and feature 003 suites. The suite must include, before the corresponding behavior is considered done:

- domain tests for a decision that names a Passed check, a decision that names a Failed check, a missing check, an unknown check, a check on another task, a blank statement, and a Cancelled task
- domain tests that a later Passed check of the same change and criterion leaves the decision showing the earlier evidence and Failed
- domain tests that a linked decision can supersede an earlier decision that names no check, that the existing decision command still saves a decision with no check, and that a subtask decision does not appear on the parent
- domain tests that completion and cancellation still follow the feature 003 rules when a carried-out change has no decision
- a replay test that runs the same linked-decision script twice from a task with one check and no decision naming it, using the same scripted clock, and compares the statement, the named check, and the order
- contract tests that call the new HTTP command and the unchanged decision command, and assert the status codes and messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --port 8000
```

Then open `http://127.0.0.1:8000/`. `--engineer` is the name already copied onto checks. Omitting it uses `Engineer`.

## Manual scenarios

Use a fresh `workspace.db`, or delete the file first. Create an In Progress task with a goal and one acceptance criterion before scenario 1. Record one ordinary change and one check of that change before scenario 1. Statuses and messages are the expected outcomes.

### 1. Record a decision that names a check

1. On the In Progress task, record a decision on the Passed check with statement `Keep the export label` and rationale `The check shows the goal is visible`. Confirm the decision shows that statement, that rationale, a time, the criterion wording, the account of what changed, the evidence, and Passed. Confirm the change stays Carried out, the check stays Passed, and the status stays In Progress.
2. Record a decision on a Failed check of that task. Confirm the decision shows that evidence and Failed, and the check stays Failed.
3. Submit a blank rationale on this action. Confirm nothing is saved and the page says both a statement and a rationale are required.
4. Submit this action with no check chosen. Confirm nothing is saved and the page says to choose the check this decision rests on.
5. On a Cancelled task, confirm neither decision action is offered. Existing decisions stay visible.
6. Complete a task that already meets the earlier completion rules, then record a decision naming a check that was stored before completion. Confirm the decision is saved and the status stays Completed.

### 2. The decision stays on the check it named

1. Record a decision naming a Failed check. Then record a later Passed check of that same change and criterion. Confirm the decision still shows the earlier evidence and Failed, and the later check is still listed.
2. Edit the criterion wording. Confirm the decision still shows the wording stored on the check.

### 3. Supersede, and leave the old decision action alone

1. Record a decision with only a statement and a rationale, using the existing decision action. Confirm it is saved and shows no check.
2. Record a later decision that names a check and supersedes that earlier decision. Confirm both remain, and only the later one shows the check.
3. On a subtask, record a decision naming that subtask's check. Confirm it appears on the subtask and does not appear on the parent.
4. On an In Progress task whose other completion rules already hold, leave a carried-out change with a passing check and no decision. Mark the task completed. Confirm the status is Completed.

## Done when

- `pytest` passes, including feature 001, feature 002, and feature 003 tests.
- Scenarios 1 through 3 match the outcomes above on a fresh workspace.
- A reader can open the task and state the criterion, what changed, the evidence, the result, the statement, and the rationale, without the original conversation.
