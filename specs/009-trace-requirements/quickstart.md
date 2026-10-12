# Quickstart: Trace Requirements

Validation guide for requirement identity, links, stored runs, the completion hold, the gap list, and a requirement change. Behavior is defined in [spec.md](spec.md). Commands are defined in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md). Stored fields are defined in [data-model.md](data-model.md).

## Prerequisites

- Python 3.12
- Feature 001 through feature 008 behavior already in the workspace process

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

Expected: every existing test passes. The new tests must fail before the requirement commands exist, and then show:

- a new requirement receives a `REQ-` identifier that stays after the statement changes
- a task with no linked requirement still completes under the existing rules
- a Failed run, and a named check with no run, each refuse verification and completion
- a later Passed run is the current result, and the earlier run remains
- removing a named check keeps its runs, stops the hold, and puts the requirement on the gap list
- naming that check again does not reuse the retired runs
- saving the same statement and kind does not unverify a criterion or reopen a Completed task
- a different statement unverifies the linked criterion, returns that Completed task and its Completed parent to In Progress, and keeps the run
- one test fails on a single rule, and one test fails on the path from the requirement through the task and criterion to the stored run

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --port 8000
```

Use a fresh `workspace.db`.

## Manual checks

1. Create an In Progress task "Add export" with one acceptance criterion. Create the functional requirement "The export contains the goal". Confirm the identifier, the kind, and the statement. Link the task, then link the criterion. Confirm the task page shows the identifier.
2. Name the check "export shows the goal". Record run identifier `local-1` and Failed. Confirm the criterion stays Unverified and completion stays In Progress, with `A required check has not passed: REQ-1` included in the refusal. Record `local-2` and Passed. Confirm both runs remain and the current result is Passed.
3. Remove the check. Confirm the Failed and Passed runs are still readable, the requirement is on the gap list as missing a check, and the task can be completed once its existing conditions are met.
4. On a second requirement, link a Verified criterion on a Completed task. Save the same statement and kind. Confirm the criterion stays Verified, the task stays Completed, and no requirement-change history line is added. Then change the statement. Confirm the identifier is unchanged, the criterion is Unverified, the task is In Progress, and the history cause is `requirement_changed`.
5. Open a task that has no requirement and whose existing completion conditions are met. Confirm it becomes Completed and the refusal text for other tasks is unchanged when no requirement is linked.
