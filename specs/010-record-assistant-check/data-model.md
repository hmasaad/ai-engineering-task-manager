# Data Model: Record One Check by the Assistant

The implementation check stays the check. This feature adds the assistant who recorded one of those checks. Specifications 001 through 009 are not rewritten.

## Assistant check

| Field | Rule |
|---|---|
| `check_id` | Primary key. References `implementation_check(id)`. One assistant row per check. The row is not updated or deleted. |
| `assistant_name` | The workspace assistant at insert. Trimmed, length greater than zero. A name sent with the request is ignored. |

No other column. The evidence, the result, the criterion wording, the engineer, and the time stay on `implementation_check`.

`implementation_check.engineer_name` remains the workspace engineer. `implementation_check.checked_at` remains the workspace time. `result` remains `passed` or `failed`.

## Reading a check

Checks on a change stay oldest first by `checked_at`, then `id`.

Each check object gains `assistant_name`:

- null when the engineer recorded the check
- the stored assistant name when this command recorded the check

The decision's check object gains the same field. A missing link stays null for the whole check object, as it does today.

The current result is unchanged: the latest check of that change and that live criterion. A check whose criterion was removed stays visible and drops out of the passing-check test. An assistant name does not change that test.

## Validation order

The assistant command refuses, and stores neither row, in this order:

1. Unknown task: `Task not found.`
2. Draft: `The task must be In Progress.`
3. Ready: `Start the task first.`
4. Completed: `Reopen the task first.`
5. Cancelled: `A cancelled task cannot be changed. Continued work is a new task.`
6. Unknown change: `Implementation change not found.`
7. Change on another task: `The check must name a change on that task.`
8. Awaiting approval: `The change must be carried out before it can be checked.`
9. Not carried out: `A change that was not carried out cannot be checked.`
10. No criterion chosen: `Choose an acceptance criterion.`
11. Unknown criterion: `Acceptance criterion not found.`
12. Criterion on another task: `The check must name a criterion on that task.`
13. Blank evidence, including spaces only: `An account of the evidence is required.`
14. Missing or unknown result: `Choose Passed or Failed.`

Blank evidence wins over a bad result. A wrong task status wins over every later check.

Stored evidence is trimmed. Empty evidence after trimming is refused. The result is stored only as `passed` or `failed` and shown as Passed or Failed.

## What this command does not write

- No task status change, no criterion verification, and no decision.
- No requirement, requirement link, named requirement check, or verification run.
- No implementation change, approval, decline, file, or model call.
- The engineer check command inserts `implementation_check` only.

One request inserts one check and, only for this command, one assistant row.
