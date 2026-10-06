# Data Model: Manage Engineering Tasks

Rules below are the stored form of `specs/001-manage-engineering-tasks/spec.md`. The domain module is the only writer. A refused command commits nothing.

## Workspace

One row. Created when the workspace file is created.

| Field | Required | Rules |
|---|---|---|
| engineer_name | yes | Non-empty name copied onto a criterion at verification time. Default `Engineer` when configuration does not set one. Not an account. |

## Task

| Field | Required | Rules |
|---|---|---|
| id | yes | Integer assigned in creation order. Stable tie-breaker for sort. |
| title | yes | Non-empty after trimming. Duplicate titles are allowed. |
| goal | no | Trimmed text. Missing or blank means the task has no goal. |
| status | yes | Exactly one of `Draft`, `Ready`, `In Progress`, `Completed`, `Cancelled`. |
| parent_id | no | Another task's id, or empty for a top-level task. At most one parent. |
| created_at | yes | Clock time of creation. |
| cancel_reason | when Cancelled | Non-empty reason. Empty unless status is `Cancelled`. |

Relationships:

- A task has many child tasks (`parent_id`).
- A task has many acceptance criteria, status changes, and implementation decisions.
- Top-level list: `parent_id` is empty, ordered by `created_at`, then `id`.
- Subtask list: children of one parent, same order.

Validation:

- Title, goal, criterion text, observation, decision statement, rationale, cancel reason, and reopen reason that are empty or only spaces are refused.
- `parent_id` cannot be the task itself, cannot point at a descendant, and cannot be changed onto a second parent. A task is created with its only parent, or with none.
- A new subtask is refused when the parent is `Completed` or `Cancelled`.
- Stored status is the only status. Nothing is inferred from a goal, a decision, or a criterion being present.

## Acceptance Criterion

| Field | Required | Rules |
|---|---|---|
| id | yes | Integer in creation order. |
| task_id | yes | The owning task. |
| text | yes | Non-empty trimmed text. |
| position | yes | Creation order on that task. |
| observation | only when Verified | Non-empty. Absent when Unverified. |
| pass_result | only when Verified | The only stored value is pass. Absent when Unverified. |
| verified_at | only when Verified | Clock time of the verify command. Absent when Unverified. |
| provider_name | only when Verified | Engineer name copied from the workspace. Absent when Unverified. |

A criterion is **Verified** only when observation, pass result, verified time, and provider are all present. It is **Unverified** only when all four are absent. Any other combination is invalid and must not be stored.

An observation submitted without a pass result does not write those fields and leaves the criterion Unverified.

Verification is refused unless the task is `In Progress`. Clearing verification (explicit unverify, or any edit of the criterion text) sets the four fields back to absent.

Adding a criterion is allowed on a task that is not `Cancelled`. The new criterion is Unverified. Removing the last criterion, or clearing the goal, is refused while the task is `In Progress` or `Completed`. While `Draft` or `Ready`, that removal is allowed, and a `Ready` task that no longer has a goal and at least one criterion returns to `Draft`.

## Status Change

Append-only. One row per transition.

| Field | Required | Rules |
|---|---|---|
| id | yes | Integer in insert order. |
| task_id | yes | The task whose status changed. |
| from_status | yes | Status before the command. |
| to_status | yes | Status after the command. |
| occurred_at | yes | Clock time of the command. |
| cause_code | yes | One of the codes below. |
| cause_detail | when the cause needs it | Reopen reason, cancel reason, or the criterion id whose text changed. |

History is read oldest first (`occurred_at`, then `id`).

### Cause codes

| Code | When |
|---|---|
| `marked_ready` | Engineer marks Draft as Ready. |
| `goal_or_last_criterion_removed` | A Ready task loses its goal or its last criterion. |
| `started` | Engineer starts a Ready task. |
| `completed` | Engineer marks an In Progress task completed. |
| `cancelled` | Engineer cancels. `cause_detail` is the reason. |
| `reopened` | Engineer reopens, or a Completed ancestor is carried along by that reopen. `cause_detail` is the reason. |
| `criterion_text_edited` | Criterion text changed. Also used on each Completed ancestor carried along. `cause_detail` is the criterion id. |

## Implementation Decision

Append-only. No update and no delete.

| Field | Required | Rules |
|---|---|---|
| id | yes | Integer in creation order. |
| task_id | yes | Exactly one task. Refused on a Cancelled task. |
| statement | yes | Non-empty. |
| rationale | yes | Non-empty. |
| recorded_at | yes | Clock time of the command. |

A decision may name zero or more earlier decisions on the **same** task through a link:

| Field | Rules |
|---|---|
| decision_id | The new decision. |
| earlier_decision_id | An older decision on that same task. |

Refused when the named decision is itself, is on another task, or was recorded after this decision (`recorded_at`, then `id`). Named decisions stay stored and unchanged. A later decision may name several earlier ones. The same earlier decision may be named by more than one later decision.

Decisions are read oldest first.

## Status transitions

Only these changes are written. Anything else is refused, the task stays as it was, and no status-change row is added.

| From | To | Guard |
|---|---|---|
| Draft | Ready | Engineer action. Title, goal, and at least one criterion are non-empty. |
| Draft | Cancelled | Engineer confirms and gives a reason. Every direct subtask is Completed or Cancelled. |
| Ready | Draft | Goal becomes empty or the last criterion is removed. |
| Ready | In Progress | Engineer starts work. |
| Ready | Cancelled | Same cancel guard as Draft. |
| In Progress | Completed | Engineer action. Every criterion is Verified. Every direct subtask is Completed or Cancelled. A refusal names the unmet criteria and the unfinished subtasks. |
| In Progress | Cancelled | Same cancel guard as Draft. |
| Completed | In Progress | Engineer reopens with a reason, or the text of a Verified criterion on this task changes, or a descendant leaves Completed for one of those two causes. |

Cancelled has no outward transition. Restore is refused. Continued work is a new task. A Completed task must be reopened before it can be cancelled.

When a reopen or a criterion-text edit moves a task from Completed to In Progress, every Completed ancestor also moves to In Progress in the same transaction. Each ancestor gets its own status-change row with the same cause as the originating change. Verified criteria on those ancestors stay Verified. The reopened task's own verified criteria stay Verified until their text changes or the engineer unverifies them.

Completion, cancellation, reopening, starting work, and verification happen only as explicit engineer commands. Removing a goal or editing criterion text may also change status, and that change is still recorded. The product must not mark work complete because a goal, a decision, or a criterion merely exists.

## Invariants

- A Completed task has no direct subtask in Draft, Ready, or In Progress.
- A Cancelled task is immutable: no goal or criterion edits, no new subtasks, no new decisions, no new verifications, no status change.
- Unverified criteria store none of observation, pass result, time, or provider.
- Status-change rows and decisions are never deleted.
- Two workspaces that receive the same commands at the same clock times end with the same statuses, verification states, and ordering.
