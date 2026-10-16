# Data Model: Workflow Replay and Deterministic Execution

No new table. No column is added to an existing table.

## Execution report

Derived from the current version and the effects already stored for its steps.

| Field | Rule |
|---|---|
| `version` | The current version number. `1` when steps exist and no version row is stored. |
| `matched` | Completed steps, in version order, whose stored effect is present. Each entry has `title`, `action`, `state` of `Completed`, and `effect` as the file or folder path. |
| `stopped` | `null` when every current step is matched. Otherwise the sentence for the first step that is not matched. |

A read matches the next stored file read of that path. A folder matches the change already linked to that step. Steps after the first stop are omitted.

## Task page

`GET /api/tasks` stays the top-level task list. The workflow on the task detail gains `execution` with this report when the current version has steps and none is running. It is `null` when there are no steps or a step is running.
