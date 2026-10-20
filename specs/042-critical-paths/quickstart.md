# Quickstart: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

## Prerequisites

Python 3.12 and the repository virtual environment. No new package.

## Checks

```bash
.venv/bin/pytest tests/unit/test_critical_paths.py tests/contract/test_critical_paths_api.py
.venv/bin/pytest
```

The first command covers a length, a dependency, a cycle, a rolled-back link, the critical path, deadline propagation, another task, and the page. The second command confirms the existing suite stays green.

## Expected

- Design stays at length 1. A repeated name does not change it.
- Build follows design. A cycle is refused with `Those steps would form a cycle.`
- The critical path is design, build.
- With the deadline `2026-12-03T00:00:00Z`, design's latest time is `2026-12-01T00:00:00Z` and build's latest time is `2026-12-03T00:00:00Z`.
- The page shows `Critical path: design, build`.
- `GET /api/tasks` stays a list of tasks.
