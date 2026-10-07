# Quickstart: Record Task Implementation

Validation guide for implementation changes on an existing task. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root
- Feature 001 behavior already in the workspace process (create a task, mark it Ready, start it)

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

Expected: every test passes, including the feature 001 suite. The suite must include, before the corresponding behavior is considered done:

- domain tests for ordinary record, consequential record, approve, mark not carried out, and the refusals in the spec
- domain tests that completion and cancellation stay In Progress while a change is Awaiting approval, and succeed once that change is approved or marked not carried out and the feature 001 guards hold
- a replay test that runs the same record, approve, and mark-not-carried-out script twice from an In Progress task with no implementation changes, using the same scripted clock, and compares outcomes and order
- contract tests that call the new HTTP commands and the complete and cancel refusals, and assert the status codes and messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --port 8000
```

Then open `http://127.0.0.1:8000/`. `--engineer` is the name copied onto changes and resolutions. Omitting it uses `Engineer`.

## Manual scenarios

Use a fresh `workspace.db`, or delete the file first. Create an In Progress task with a goal and one acceptance criterion before scenario 1. Statuses and messages are the expected outcomes.

### 1. Attach an ordinary change

1. On the In Progress task, record an ordinary change `Rename the export label`. Confirm it is listed as Carried out, names the task, names Ada, shows a time, and the status is still In Progress.
2. Submit a blank account of what changed. Confirm nothing is saved and the page says an account of what changed is required.
3. Submit a change with no class. Confirm nothing is saved and the page says to choose ordinary or consequential.
4. On a Draft task, a Ready task, a Completed task, and a Cancelled task, record a change. Confirm nothing is saved, and the messages say the task must be In Progress, to start the task first, to reopen the task first, and that continued work is a new task.
5. Record a second ordinary change `Write the export steps`. Confirm both appear in that order and neither appears on a different task.

### 2. Approve a consequential change

1. Record a consequential change `Replace the stored export name`. Confirm it is Awaiting approval, no approval is stored, and the status is still In Progress.
2. Leave it. Confirm it stays Awaiting approval.
3. Approve it with evidence `The detail page shows the new export name`. Confirm it is Carried out, the evidence, Ada, and the approval time are visible, and the status is still In Progress.
4. Approve an ordinary change. Confirm it stays Carried out and the page says an ordinary change does not wait for approval.
5. Approve the consequential change again. Confirm the first approval is unchanged and the page says the change is already carried out.
6. Approve with a blank evidence account. Confirm the change stays Awaiting approval.

### 3. Leave a change uncarried

1. Record a consequential change `Drop the old export path`. Mark it not carried out with reason `The old path is still required`. Confirm it stays visible as Not carried out, the reason is shown, and the status is still In Progress.
2. Try to approve it. Confirm it stays Not carried out and the page says it cannot be carried out.
3. Try to mark a Carried out change not carried out. Confirm it stays Carried out and the page says a carried-out change stays in the record.
4. Mark a waiting change not carried out with a blank reason. Confirm it stays Awaiting approval.

### 4. Completion waits for every waiting change

1. On an In Progress task whose criterion is Verified and that has no unfinished subtask, record a consequential change and do not approve it. Mark the task completed. Confirm it stays In Progress and the message names that change as Awaiting approval.
2. Cancel that task with a reason. Confirm it stays In Progress and the message names that change.
3. Approve the change. Mark the task completed. Confirm the status is Completed.
4. On another In Progress task with no unfinished subtask, record a consequential change, mark it not carried out, then cancel with a reason. Confirm the status is Cancelled.

## Done when

- `pytest` passes, including feature 001 tests.
- Scenarios 1 through 4 match the outcomes above on a fresh workspace.
- A reader can open the task and state what changed, which task it serves, and whether a consequential change was carried out, without the original conversation.
