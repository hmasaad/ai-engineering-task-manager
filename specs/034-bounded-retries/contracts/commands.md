# Commands: Bounded Delivery Retries

`GET /api/tasks` stays the top-level task list.

The workflow object gains `retries`: `{outbox_id, attempt_count, next_eligible_at}` oldest message first.

## Delivery did not succeed

`POST /api/tasks/{id}/workflow/outbox/retry`

Body: `{"name": "once"}`. The page field is Attempt name, id `attempt-name`, name `name`. The button is `Delivery did not succeed`. It is shown when the task is In Progress and an outbox message is Pending.

| Condition | Status | Result |
|---|---|---|
| First accepted use of the name, and the message is due | 200 | One attempt. `attempt_count` increases by one. `next_eligible_at` is one minute later. The message stays Pending |
| Same name again | 200 | The same count. No second attempt |
| Before the next time | 409 | `This delivery is not due yet.` The name is not saved |
| The attempt that makes the count 3 | 200 | One dead letter with reason `The delivery was attempted too many times.` The message is shown as Dead. The count stays 3 |
| Blank name | 400 | `Name this attempt.` |
| No Pending message | 409 | `There is no outbox message to retry.` |
| Task is not In Progress | 409 | The existing status sentence. The name is not saved |
| Unknown task | 404 | `Task not found.` |

Recording an attempt does not read a file, create a folder, approve a change, advance the workflow, or change the task status.

## Deliver outbox

`POST /api/tasks/{id}/workflow/outbox` stays as it is, with one added condition.

| Condition | Status | Result |
|---|---|---|
| Before the next time | 409 | `This delivery is not due yet.` The message stays Pending. The attempt count is unchanged. The delivery name is not saved |
| The next time has arrived | 200 | The message is Delivered. The attempt count is unchanged |
| The message has a dead letter | 409 | `There is no outbox message to deliver.` when no other Pending message remains |

## Page

When `retries` is not empty, the workflow section shows Delivery attempts and the count and next time for each message. The list id is `workflow-retries`.
