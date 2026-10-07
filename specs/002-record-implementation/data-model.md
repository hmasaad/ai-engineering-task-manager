# Data Model: Record Task Implementation

Rules below are the stored form of `specs/002-record-implementation/spec.md`. They extend `specs/001-manage-engineering-tasks/data-model.md`. The domain module is the only writer. A refused command commits nothing. Task, criterion, status-change, and decision rows are unchanged by recording, approving, or marking a change not carried out.

## Implementation Change

Insert-only. No update and no delete.

| Field | Required | Rules |
|---|---|---|
| id | yes | Integer assigned in insertion order. Stable tie-breaker for sort. |
| task_id | yes | Exactly one task. The task must be `In Progress` at insert time. |
| what_changed | yes | Non-empty after trimming. |
| class | yes | Exactly `ordinary` or `consequential`. The client must send one of these. The product does not choose it from the text. |
| engineer_name | yes | Workspace engineer name copied at insert time. Not taken from the request. |
| recorded_at | yes | Clock time of the record command. |

A change cannot be moved to another task. What changed, the class, the engineer name, and `recorded_at` are never rewritten.

Changes on a task are read oldest first (`recorded_at`, then `id`).

Refused, and no row is written, when:

- `what_changed` is empty or only spaces.
- `class` is missing or not `ordinary` or `consequential`.
- The task is `Draft`. The engineer is told the task must be In Progress.
- The task is `Ready`. The engineer is told to start the task first.
- The task is `Completed`. The engineer is told to reopen the task first.
- The task is `Cancelled`. The engineer is told that continued work is a new task.
- The task id does not exist.

## Implementation Resolution

Insert-only. At most one row per change. No update and no delete.

| Field | Required | Rules |
|---|---|---|
| change_id | yes | One implementation change. Unique in this table. |
| kind | yes | Exactly `approved` or `not_carried_out`. |
| evidence | when approved | Non-empty account of the evidence reviewed. Empty when kind is `not_carried_out`. |
| reason | when not carried out | Non-empty. Empty when kind is `approved`. |
| engineer_name | yes | Workspace engineer name copied at this command. Not taken from the request. |
| resolved_at | yes | Clock time of this command. |

A resolution is refused unless the change's task is `In Progress` and the change's outcome is Awaiting approval. A second resolution is refused. An ordinary change never receives a resolution.

## Outcome

Outcome is not a separate column and is not inferred from wording. It is:

| Class | Resolution | Outcome |
|---|---|---|
| ordinary | none | Carried out |
| consequential | none | Awaiting approval |
| consequential | `approved` | Carried out |
| consequential | `not_carried_out` | Not carried out |

Any other combination must not be stored. An ordinary change has no approval. A change that is Awaiting approval or Not carried out has no approval.

### Approve

Allowed only for an Awaiting approval change on an In Progress task. Inserts `kind = approved` with a non-empty evidence account. The change becomes Carried out. The task status does not change.

Refused, with no row written, when:

- The evidence account is empty or only spaces.
- The change is not Awaiting approval. An ordinary change is told that an ordinary change does not wait for approval. A consequential change that is already Carried out is told that it is already carried out. A change that is Not carried out is told that it cannot be carried out.
- The task is not In Progress.
- The change belongs to a different task. The engineer is told the approval must name a change on that task.
- The change id does not exist.

### Mark not carried out

Allowed only for an Awaiting approval change on an In Progress task. Inserts `kind = not_carried_out` with a non-empty reason. The change stays visible as Not carried out and never becomes Carried out. The task status does not change.

Refused, with no row written, when:

- The reason is empty or only spaces.
- The task is not In Progress.
- The change is not Awaiting approval. A Carried out change is told that a carried-out change stays in the record.
- The change belongs to a different task, or the change id does not exist.

## Status guard added to feature 001

Completion and cancellation keep every guard in the feature 001 data model. They gain one guard: if any change on **this** task has outcome Awaiting approval, the command is refused, the status stays `In Progress`, and no status-change row is written. The refusal names each waiting change by `what_changed`, oldest first.

Carried out and Not carried out changes do not block either command. After the waiting changes on this task are approved or marked not carried out, completion and cancellation follow the feature 001 rules again.

Waiting changes on a subtask are not copied onto the parent. A subtask that is still In Progress already blocks its parent.

Recording, approving, and marking not carried out do not append a status change, do not verify or unverify a criterion, and do not insert a decision.

## Invariants

- A change serves exactly one task.
- An ordinary change is Carried out and has no resolution row.
- A consequential change has either no resolution (Awaiting approval), one approval (Carried out), or one not-carried-out resolution (Not carried out).
- A task whose status is Completed or Cancelled has no change still Awaiting approval. Those exits are refused while one exists, and a change can be recorded only while the task is In Progress.
- Change rows and resolution rows are never deleted or updated.
- Two workspaces that receive the same commands at the same clock times end with the same outcomes and the same change order.
