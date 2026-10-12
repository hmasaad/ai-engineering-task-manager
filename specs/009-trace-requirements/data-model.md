# Data Model: Trace Requirements

Rules below are the stored form of `specs/009-trace-requirements/spec.md`. They extend the workspace schema. The domain module is the only writer. A refused command commits nothing. Task status, criterion verification, and feature 003 checks change only in the cases named below.

## Requirement

Not deleted. The statement and the kind may change. The id does not change.

| Field | Required | Rules |
|---|---|---|
| id | yes | Surrogate identity. Assigned at insert. Shown as `REQ-{id}`. |
| kind | yes | `functional` or `non-functional`. |
| statement | yes | Non-empty after trimming. The stored value is trimmed. |
| created_at | yes | Clock time, UTC `YYYY-MM-DDTHH:MM:SSZ`. |

A second requirement gets a new id. Ids are not reused.

## Task link

One row per requirement and task. Removing the link deletes the row. It does not delete the requirement, the task, or any run.

| Field | Required | Rules |
|---|---|---|
| requirement_id | yes | References `requirement(id)`. |
| task_id | yes | References `task(id)`. |

Primary key is `(requirement_id, task_id)`. Index `task_id` so completion can find the links for one task.

## Criterion link

One row per requirement and acceptance criterion. The criterion's task must already have a task link for that requirement.

| Field | Required | Rules |
|---|---|---|
| requirement_id | yes | References `requirement(id)`. |
| criterion_id | yes | References `acceptance_criterion(id)` with `ON DELETE CASCADE`. |

Primary key is `(requirement_id, criterion_id)`. Deleting a criterion deletes this row and does not delete the task link or any run.

## Named check

Retired in place. A retired row stays so its runs remain readable.

| Field | Required | Rules |
|---|---|---|
| id | yes | Surrogate identity. Assigned at insert. |
| requirement_id | yes | References `requirement(id)`. |
| name | yes | Non-empty after trimming. The stored value is trimmed. |
| removed_at | no | Null while the check is still named. Clock time when the engineer removes it. |

A unique index on `(requirement_id, name)` where `removed_at` is null. A retired row may keep a name that a later active row also uses.

## Verification run

Insert-only. No update and no delete.

| Field | Required | Rules |
|---|---|---|
| id | yes | Surrogate identity. Assigned at insert. |
| check_id | yes | References `requirement_check(id)`. |
| result | yes | `passed` or `failed`. Shown as Passed or Failed. |
| run_identifier | yes | Non-empty after trimming. The stored value is trimmed. |
| engineer_name | yes | Copied from the workspace engineer. Not a name sent by the client. |
| recorded_at | yes | Clock time, UTC `YYYY-MM-DDTHH:MM:SSZ`. Not a time sent by the client. |

The current result of an active check is the run with the greatest `recorded_at`, then the greatest `id`. A check with no run has no current result. Runs on a retired check stay readable and are not a current result.

## Validation before insert or update

### Record a requirement

1. The statement is blank. `A requirement statement is required.`
2. The kind is missing or is neither `functional` nor `non-functional`. `Choose functional or non-functional.`

### Change a requirement

1. The requirement id does not exist. `Requirement not found.`
2. The statement is blank. `A requirement statement is required.` The stored row stays.
3. The kind is missing or unknown. `Choose functional or non-functional.` The stored row stays.
4. The trimmed statement and the kind both match the stored row. Nothing is written.
5. Otherwise the statement and kind are stored. Each linked criterion that is Verified becomes Unverified. Each of those criteria whose task is Completed returns to In Progress, and every Completed ancestor returns to In Progress, with cause `requirement_changed` and the requirement id. One task is moved once. Runs stay.

### Link a task

1. The requirement id does not exist. `Requirement not found.`
2. The task id does not exist. `Task not found.`
3. The pair is already stored. Success, and no second row is written.

A Cancelled task may be linked. Linking does not change the task status.

### Link a criterion

1. The requirement id does not exist. `Requirement not found.`
2. The task id does not exist. `Task not found.`
3. The criterion id does not exist. `Criterion not found.`
4. The criterion is not on that task, or that task is not linked to the requirement. `The criterion must be on that task.`
5. The pair is already stored. `That criterion is already linked to this requirement.`

### Remove a link

The requirement and the named side must exist. Removing a criterion link does not change that criterion's Verified state. Removing a task link does not remove criterion links and does not delete runs.

### Name or remove a check

1. The requirement id does not exist. `Requirement not found.`
2. The name is blank. `Name the check this requirement uses.`
3. An active check on that requirement already has that trimmed name. `That check is already named on this requirement.`
4. Removal of an id that is missing or already retired. `Check not found.`

Removal sets `removed_at`. It does not delete runs and does not change task status or criterion verification.

### Record a run

1. The requirement id does not exist. `Requirement not found.`
2. The named check is missing or retired on that requirement. `Check not found.`
3. The run identifier is blank. `A run identifier is required.`
4. The result is missing or is neither Passed nor Failed. `Choose Passed or Failed.`

A run does not change task status, criterion verification, a change outcome, or a feature 003 check.

### Verify a criterion

The existing feature 001 checks run first, including observation and pass. Then, if any requirement linked to that criterion has an active check whose current result is not Passed, the criterion stays Unverified and the engineer is told `A required check has not passed.`

### Complete a task

The existing sentences stay first: unverified criteria, unfinished subtasks, awaiting approval, then a carried-out change that needs a passing check. After those, if any requirement linked to the task has an active check whose current result is not Passed, append `A required check has not passed: {identifiers}.` Identifiers use `REQ-{id}`, lowest id first, separated by a comma and a space. Several sentences are joined by `. ` with a final period, as they are today.

## Reading rules

- The gap list contains each requirement that is missing a task link, a criterion link, an active check, or a current Passed result on an active check. A requirement missing none of these is absent from that list.
- Opening a requirement returns its tasks, its criteria with Verified or Unverified, its active checks and runs, and its retired checks and runs.
- Runs on one check are oldest first, by `recorded_at` then `id`.
- A task detail includes the requirements linked to that task. A task with none includes an empty list. A subtask's links do not appear on the parent.
- Opening a task or a requirement does not record a run and does not mark a check Passed.

## What this feature does not write

- Feature 003 checks are not verification runs, and recording a run does not insert a feature 003 check.
- An assistant change, a file read, and a model call do not insert a requirement, a link, a check, or a run.
- No command starts a test process or reads a specification document.
