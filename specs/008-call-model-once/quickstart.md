# Quickstart: Call the Model Once

Validation guide for one model call that proposes one file. Behavior is defined in [spec.md](spec.md) and commands in [contracts/http-api.md](contracts/http-api.md).

## Prerequisites

- Python 3.12
- Feature 001 through feature 007 behavior already in the workspace process

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
mkdir -p billing/notes
printf 'Export' > billing/notes/label.txt
```

## Automated check

```bash
pytest
```

Expected: every test passes, including feature 001 through feature 007. The new tests must fail before the model command exists, and then show:

- one call for a new ordinary file, with the returned text on disk and on the task
- no call for a blank project, a missing file read, a file outside the project, or a missing model
- one call and no write for a replacement, until the engineer approves
- a replay that shows the stored model name and text and does not call the model again

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --assistant "Guide" --model-name "Guide-model" --model-text "Export" --port 8000
```

Start this command from the directory that contains `billing`. The configured model returns the fixed text `Export` and records one call.

## Manual scenarios

Use a fresh `workspace.db`. Create an In Progress task and read `billing` / `notes/label.txt` before scenario 1.

### 1. Ask for one new file

1. Ask the model for project `billing`, class ordinary, account `Propose the export label`, file `notes/proposed.txt`, and the stored read. Confirm `notes/proposed.txt` contains `Export`. Confirm the task shows Guide-model, `Export`, Guide, and Carried out. Confirm the status stays In Progress.
2. Submit the form with no file read. Confirm the page says to choose the file read and no second file is written.

### 2. Wait before replacing a file

1. Ask the model for the existing file `notes/label.txt`. Confirm the file is unchanged and the task shows consequential and Awaiting approval.
2. Approve with evidence `The page shows the model text`. Confirm the file contains `Export` and the approval names Ada.

### 3. Read the record again

1. Open the task. Confirm the model name and the returned text are still shown.
2. Record an assistant change with the existing form. Confirm that change has no model line.
