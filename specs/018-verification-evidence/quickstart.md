# Quickstart: Verification Evidence and Trace Gaps

## Checks

From the repository root:

```text
.venv/bin/pytest tests/unit/test_criterion_evidence.py tests/unit/test_traceability.py tests/contract/test_criterion_evidence_api.py tests/contract/test_traceability_api.py
```

Then the full suite:

```text
.venv/bin/pytest
```

## What a passing run shows

- A criterion verified with method `inspection` and test-run identifier `local-1` shows both, the observation, the pass, the engineer, and the time.
- A blank method returns `A verification method is required.` and leaves the criterion Unverified.
- A blank test-run identifier returns `A test-run identifier is required.` and leaves the criterion Unverified.
- `GET /api/requirements` is still a list. A task with no requirement is not an item in that list.
- `GET /api/traceability` lists that task and lists an Unverified criterion. Linking the task and verifying the criterion removes each from its list.

## Page

On an In Progress task, the verify form asks for the observation, the method, the test-run identifier, and the pass. After a successful verify, the criterion shows the method and the identifier. The Requirements page lists a task with no requirement and an Unverified criterion while those gaps exist.
