# Quickstart: Record One Check by the Assistant

Validation guide for one check recorded by the assistant. Behavior is defined in [spec.md](spec.md), the record shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md).

## Prerequisites

- Python 3.12
- Features 001 through 009 already in the workspace process

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

No project folder is required. This command does not open a file and does not call a model.

## Automated check

```bash
pytest
```

Expected: every test passes, including features 001 through 009. The new tests must fail before the assistant check command exists, and then show:

- one Passed check that names the workspace assistant and leaves the task In Progress
- no check for blank evidence, a bad result, a change that is not carried out, or a criterion on another task
- the engineer's own check command storing a check with no assistant name
- a later Passed check becoming current while the earlier Failed check remains
- a replay that shows the same evidence, result, and assistant and does not store a second check

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --assistant "Guide" --port 8000
```

The server binds to `127.0.0.1` only.

## Manual check

1. Open `http://127.0.0.1:8000/`. Create "Add export", set the goal "Take the record", add the criterion "The export contains the goal", mark it Ready, and start it.
2. Record an ordinary change "Rename the export label".
3. On that change, choose the criterion, enter "The detail page shows the goal in the export", choose Passed, and press **Record assistant check**.
4. Confirm the task stays In Progress, the change stays Carried out, the criterion stays Unverified, and the check reads `Checked by Guide at {time} for Ada`.
5. With the engineer's **Record check** button, record a Failed check of that same change and criterion. Confirm that line names Ada and does not name Guide, and that both checks remain.
