# Quickstart: Workspace Boundaries and Capability-Based Permissions

Validation guide for workspace separation, restart, and one capability per target. Behavior is defined in [spec.md](spec.md), the records in [data-model.md](data-model.md), and the commands in [contracts/commands.md](contracts/commands.md).

## Prerequisites

- Python 3.12
- Features 001 through 016 already in the workspace process
- A temporary repository with one commit, used only by the tests

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

No application code is added. The tests call the existing commands.

## Automated check

```bash
pytest tests/unit/test_workspace_boundary.py tests/unit/test_capability.py
```

Expected: both files pass, and the full `pytest` run stays green. The new tests must fail if a boundary is broken. They show:

- a task, a status, and evidence written in workspace A absent from workspace B
- a task written in B absent from A
- the same title, status, and evidence after the workspace file is closed and opened again
- task records leaving a repository's files, current commit, and current branch unchanged
- approval of one waiting branch leaving a waiting commit on that task still waiting
- a file read leaving the file text unchanged

## Run the local app

```bash
python -m task_manager --workspace /tmp/workspace-a.db --engineer "Ada" --assistant "Guide" --port 8000
```

The server binds to `127.0.0.1` only. Name the workspace outside the repository you are managing. A second start uses a different `--workspace` path and a different port.
