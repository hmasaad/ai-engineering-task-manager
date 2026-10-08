# Quickstart: Read a Project File

Validation guide for one text file read for an In Progress task. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root
- Feature 001 through feature 006 behavior already in the workspace process

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create the project file before starting the app, in the same directory the app will be started from:

```bash
mkdir -p billing/notes
printf 'Export' > billing/notes/label.txt
```

## Automated check

```bash
pytest
```

Expected: every test passes, including the feature 001 through feature 006 suites. The suite must include, before the corresponding behavior is considered done:

- domain tests that one existing text file is stored with its path, text, project, and assistant, the file bytes are unchanged, and the status stays In Progress
- domain tests for a blank project, a missing project folder, a blank file name, a file outside the project, a missing file, a file that is not text, an empty file, and the Draft, Ready, Completed, and Cancelled refusals
- domain tests that a stored read is unchanged when the file is later edited or deleted, and that a second read stores the later text without changing the first
- domain tests that a read does not add an implementation change, that a subtask read does not appear on the parent, and that opening the task does not read the file again
- domain tests that an assistant change with no file still writes nothing and stores no read, and that the engineer's own change stores no read
- a replay test that runs the same read script twice, each time with a fresh project folder containing the same file text and the same scripted clock, and compares the path, the text, the project, and the assistant
- contract tests that call the HTTP command and assert the status codes and messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence. The suite must not call a model. It must read and write only inside the temporary project folder the test supplies.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --assistant "Guide" --port 8000
```

Then open `http://127.0.0.1:8000/`. Start this command from the directory that contains `billing`. A relative project path is resolved from that directory.

## Manual scenarios

Use a fresh `workspace.db`, or delete the file first. Create an In Progress task with a goal and one acceptance criterion before scenario 1. `billing/notes/label.txt` must contain `Export` before scenario 1. Statuses and messages are the expected outcomes.

### 1. Read one text file

1. On the In Progress task, read project `billing` and file `notes/label.txt`. Confirm `billing/notes/label.txt` still contains `Export`. Confirm the task shows that path, the text `Export`, the project `billing`, and Guide. Confirm the status stays In Progress and no implementation change was added.
2. Submit a blank project. Confirm nothing is saved and the file is unchanged.
3. Submit a blank file name. Confirm the page says to name the file this change reads, and nothing is stored.
4. Submit file `../outside.txt`. Confirm the page says the file must stay inside the named project, and nothing outside `billing` is stored.

### 2. Keep the stored text

1. Change `notes/label.txt` to `Newer`, then open the task again. Confirm the stored read still shows `Export` and the file still contains `Newer`.
2. Read `notes/label.txt` again. Confirm the task shows both reads, oldest first: `Export`, then `Newer`.
3. Record an assistant change with no file. Confirm no file is written and no extra read is stored.
4. Record an ordinary change with the engineer's change action. Confirm the project folder is unchanged and no read is stored.

### 3. Leave the read visible

1. Cancel the task with a reason. Confirm the read form is gone and the stored reads remain.
