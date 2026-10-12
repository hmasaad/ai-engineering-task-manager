# Contract: Assistant check on the task page

The task page at `/tasks/{id}` gains one form for each carried-out change while the task is In Progress. The engineer's check form stays where it is and still posts to the engineer check command.

## Form

Shown only when the task is In Progress and that change is Carried out.

| Field | Name | Id |
|---|---|---|
| Change | `change_id` | `assistant-check-change-{change.id}` |
| Acceptance criterion | `criterion_id` | `assistant-check-criterion-{change.id}` |
| Evidence | `evidence` | `assistant-check-evidence-{change.id}` |
| Result | `result` | `assistant-check-result-{change.id}` |

`change_id` is hidden and carries that change's id. The criterion control lists the task's criteria and starts on an empty choice. The result control offers an empty choice, Passed, and Failed. There is no assistant-name field, no engineer-name field, and no time field.

The button label is `Record assistant check`. The form posts to `/tasks/{task_id}/assistant-checks`.

A value that is not a whole number is treated as missing. A missing change id uses `The request is missing a required field or has the wrong shape.` A missing criterion uses `Choose an acceptance criterion.`

A refusal is shown on the task page with the message from [http-api.md](http-api.md). A success returns to `/tasks/{id}`.

A Cancelled task hides the form and keeps every stored check visible.

## Check line

An engineer-recorded check stays:

`Checked by {engineer_name} at {checked_at}: {evidence}`

An assistant-recorded check reads:

`Checked by {assistant_name} at {checked_at} for {engineer_name}: {evidence}`

The result stays Passed or Failed beside the criterion wording. Checks stay oldest first. A subtask's check does not appear on the parent.
