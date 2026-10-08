# Quickstart: Apply an Ordinary File

Validation guide for one ordinary file written for an In Progress task. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root
- Feature 001 through feature 005 behavior already in the workspace process

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create the project folder before starting the app, in the same directory the app will be started from:

```bash
mkdir -p billing/notes
```

## Automated check

```bash
pytest
```

Expected: every test passes, including the feature 001 through feature 005 suites. The suite must include, before the corresponding behavior is considered done:

- domain tests that an ordinary new file is created with the submitted text, the task shows that file and Carried out, and the status stays In Progress
- domain tests for a blank project, a missing project folder, a blank account, a bad class, a blank file name, a file outside the project, a missing destination folder, a file that is not text, and the Draft, Ready, Completed, and Cancelled refusals
- domain tests that a replacement, a consequential request, and a stopped request leave the file unchanged and show class consequential and Awaiting approval
- domain tests that the engineer can approve a matching proposal and the approval names the engineer, that a changed file is not written, and that an assistant actor cannot approve or decline
- domain tests that an omitted file keeps the feature 005 record and writes nothing, that the engineer's own change writes nothing, and that a subtask file does not appear on the parent
- a replay test that runs the same file script twice, each time with a fresh project folder and the same scripted clock, and compares the file, the text, the assistant, and Carried out
- contract tests that call the HTTP command and assert the status codes and messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence. The suite must not call a model. It must write only inside the temporary project folder the test supplies.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --assistant "Guide" --port 8000
```

Then open `http://127.0.0.1:8000/`. Start this command from the directory that contains `billing`. A relative project path is resolved from that directory.

## Manual scenarios

Use a fresh `workspace.db`, or delete the file first. Create an In Progress task with a goal and one acceptance criterion before scenario 1. `billing/notes` must exist, and `billing/notes/label.txt` must not, before scenario 1. Statuses and messages are the expected outcomes.

### 1. Write one new file

1. On the In Progress task, record an assistant change with project `billing`, class ordinary, account `Rename the export label`, file `notes/label.txt`, and text `Export`. Confirm `billing/notes/label.txt` contains `Export`. Confirm the task shows that file, that it was new, the text `Export`, Guide, and Carried out. Confirm the status stays In Progress.
2. Submit a blank project. Confirm nothing is saved and no file is written.
3. Submit a blank file name. Confirm the page says to name the file this change writes, and nothing is written.
4. Submit file `../outside.txt`. Confirm the page says the file must stay inside the named project, and nothing outside `billing` is written.

### 2. Wait before replacing a file

1. With `notes/label.txt` containing `Old`, record an ordinary assistant change that would write `Export` into that file. Confirm the file still contains `Old` and the task shows class consequential and Awaiting approval, with previous text `Old` and proposed text `Export`.
2. Change the file to `Newer`, then approve the proposal. Confirm the file stays `Newer` and the page says the file no longer matches the text this change was proposed against.
3. Put `Old` back, then approve with evidence `The page shows the new name`. Confirm the file contains `Export` and the approval names Ada.
4. Record a consequential request for a new file `notes/other.txt`. Confirm that file is not created until the engineer approves it.

### 3. Read the record again

1. Open the task after scenario 1. Confirm the file, the text, the project, and the assistant are visible without another request.
2. Record an assistant change with no file, using the existing feature 005 shape. Confirm no additional file is written.
3. Record an ordinary change with the engineer's change action. Confirm the project folder is unchanged.
