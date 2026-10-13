# Commands: Verification Evidence and Trace Gaps

No new task status. `GET /api/requirements` stays a JSON list of requirements, each with its existing `missing` phrases.

## Verify a criterion

`POST /api/tasks/{task_id}/criteria/{criterion_id}/verify`

Body: `observation` (string), `pass_result` (string), `method` (string, default empty), `run_identifier` (string, default empty). Extra fields are ignored. A missing `observation` or `pass_result` key is the existing wrong-shape message. A missing `method` or `run_identifier` key is the blank-field message below.

The page form posts the same fields while the task is In Progress and the criterion is Unverified. Field ids: `observation-{id}`, `method-{id}`, `run-{id}`. The pass control stays the existing checkbox.

Success is 200 and the task detail. The verified criterion includes `method` and `run_identifier`.

Refusals, in order:

| Condition | Status | Message |
|---|---|---|
| Unknown task | 404 | `Task not found.` |
| Cancelled task | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| Unknown criterion | 404 | `Criterion not found.` |
| Not In Progress | 409 | `A criterion can be verified only while the task is In Progress.` |
| Blank observation | 400 | `An observation of what was seen is required.` |
| Pass is not `pass` | 400 | `An explicit pass result is required.` |
| A required check has not passed | 409 | `A required check has not passed.` |
| Blank method | 400 | `A verification method is required.` |
| Blank test-run identifier | 400 | `A test-run identifier is required.` |

A refusal does not write the verification and does not write `criterion_evidence`.

The task page shows `{{ method }}, run {{ run_identifier }}` under the existing observation line when both are present.

## Trace gaps

`GET /api/traceability`

Success is 200:

```json
{
  "tasks_without_requirement": [{"id": 1, "title": "Add export", "status": "Draft"}],
  "criteria_without_verification": [
    {"id": 1, "task_id": 1, "task_title": "Add export", "text": "The export contains the goal"}
  ]
}
```

The requirements page shows two sections when the matching list is not empty: "Tasks without a requirement" and "Criteria without verification". The existing Gaps section and its phrases stay. "No requirements yet." still appears when no requirement exists.

Opening this read does not verify a criterion or change a task.
