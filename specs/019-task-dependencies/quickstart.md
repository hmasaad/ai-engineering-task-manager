# Quickstart: Task Dependencies

## Checks

From the repository root:

```text
.venv/bin/pytest tests/unit/test_dependency.py tests/contract/test_dependency_api.py
```

Then the full suite:

```text
.venv/bin/pytest
```

## What a passing run shows

- A task lists a named prerequisite once. A self-link, an unknown prerequisite, and a cycle store nothing.
- `GET /api/execution-order` places each prerequisite before the task that names it.
- Starting a Ready task whose prerequisite is not Completed returns `Blocked by {title} ({status}): incomplete.` or the unverified form, and the task stays Ready.
- A task with no unfinished prerequisite can still be started. Marking Ready is unchanged.

## Page

On a task that is not Cancelled, the form names one prerequisite. The task shows that prerequisite and, while it is unfinished, the blocked sentence. The task list shows Execution order.
