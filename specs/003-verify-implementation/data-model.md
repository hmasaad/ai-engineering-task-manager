# Data Model: Verify a Recorded Change

Rules below are the stored form of `specs/003-verify-implementation/spec.md`. They extend `specs/002-record-implementation/data-model.md`. The domain module is the only writer. A refused command commits nothing. Task, criterion, status-change, decision, implementation-change, and implementation-resolution rows are unchanged by recording a check.

## Implementation Check

Insert-only. No update and no delete. Many rows may name one change.

| Field | Required | Rules |
|---|---|---|
| id | yes | Integer assigned in insertion order. Stable tie-breaker for sort. |
| change_id | yes | Exactly one implementation change. The change's outcome must be Carried out at insert time. |
| criterion_id | yes at insert | Exactly one acceptance criterion of that change's task at insert time. Not a foreign key. After the criterion row is removed, this id may point at nothing. The check row stays. |
| criterion_text | yes | The criterion wording copied at insert time. Never rewritten when the live criterion text changes. |
| evidence | yes | Non-empty after trimming. |
| result | yes | Exactly `passed` or `failed`. The client must send `Passed` or `Failed`. The product does not choose it from the evidence. |
| engineer_name | yes | Workspace engineer name copied at insert time. Not taken from the request. |
| checked_at | yes | Clock time of the check command. |

A check cannot be moved to another change or another criterion. Evidence, result, engineer name, criterion wording, and `checked_at` are never rewritten.

Checks on a change are read oldest first (`checked_at`, then `id`).

Refused, and no row is written, when:

- The task id does not exist.
- The task is `Draft`. The engineer is told the task must be In Progress.
- The task is `Ready`. The engineer is told to start the task first.
- The task is `Completed`. The engineer is told to reopen the task first.
- The task is `Cancelled`. The engineer is told that continued work is a new task.
- The change id does not exist.
- The change belongs to a different task. The engineer is told the check must name a change on that task.
- The change is Awaiting approval. The engineer is told the change must be carried out before it can be checked.
- The change is Not carried out. The engineer is told a change that was not carried out cannot be checked.
- The criterion id does not exist.
- The criterion belongs to a different task. The engineer is told the check must name a criterion on that task.
- The criterion id is missing. The engineer is told to choose an acceptance criterion.
- The evidence is empty or only spaces. The engineer is told an account of the evidence is required.
- The result is missing or neither `Passed` nor `Failed`. The engineer is told to choose Passed or Failed.

Status is considered before the change, the criterion, the evidence, and the result. A wrong status writes nothing even when the body is also blank.

## Current result

The current result of one change and one criterion that still exists on the task is the latest check of that pair. Checks whose `criterion_id` no longer matches a criterion on the task stay in the list and are not a current result.

| Latest stored result for that live pair | Current result |
|---|---|
| `passed` | Passed |
| `failed` | Failed |
| no row | no current result |

## Passing check

A carried-out change has a passing check only when both of these hold:

- At least one check names a criterion that still exists on that change's task.
- Every such criterion has a current result of Passed.

A current Failed result for any of those criteria means the change lacks a passing check. No checks, or only checks whose criteria are gone, also means the change lacks a passing check. Awaiting approval and Not carried out changes are not required to have a passing check.

`passing_check` is not a column. Readers derive it from the rows above.

## Status guard added to completion

Completion keeps every guard in the feature 001 and feature 002 data models. It gains one guard: if any carried-out change on **this** task lacks a passing check, the command is refused, the status stays `In Progress`, and no status-change row is written. The refusal names each such change by `what_changed`, oldest first.

Cancellation does not gain this guard. Not carried out changes do not block completion. A change that is Awaiting approval continues to block completion and cancellation under the feature 002 rule, and is not listed again as lacking a passing check.

After every carried-out change on this task has a passing check, completion follows the earlier rules again.

Checks on a subtask are not copied onto the parent. A subtask that is still In Progress already blocks its parent. A subtask cannot itself be completed until its own carried-out changes have a passing check.

Recording a check does not append a status change, does not verify or unverify a criterion, does not insert a decision, and does not insert an implementation resolution.

## Criterion text and removal

Editing a criterion's text does not update `criterion_text` on existing checks. The pair remains the same criterion id. If that criterion was Verified, feature 001 still returns it to Unverified. The check result stays.

Removing a criterion does not delete checks. Those checks remain readable with the wording they stored. They drop out of the passing-check test because the criterion is no longer on the task.

## Invariants

- A check serves exactly one change and, at insert time, exactly one acceptance criterion on that change's task.
- A saved check is never deleted or updated.
- A change has a passing check only under the rule in Passing check.
- A task whose status is Completed has no carried-out change that lacks a passing check. That exit is refused while one exists. A check can be recorded only while the task is In Progress.
- Two workspaces that receive the same commands at the same clock times end with the same results and the same check order.
