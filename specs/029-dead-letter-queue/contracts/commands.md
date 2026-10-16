# Commands: Dead Letter Queues and Poison Messages

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains `poison` and `dead_letters`. An outbox message with a dead letter has state `Dead`.

## Reject

`POST /api/tasks/{id}/workflow/outbox/reject`

JSON body: `{"name": "once", "reason": "The reader stopped."}`. The page fields are `rejection-name` and `rejection-reason`. The button is `Reject message`.

| Condition | Status | Result |
|---|---|---|
| A Pending message is not a dead letter, and the name and reason are not blank | 200 | The task detail. The oldest such message gains one rejection. On the third rejection it is a dead letter. |
| The same name was already rejected on this task | 200 | The task detail. No new rejection and no new dead letter. |
| Blank name | 400 | `Name this rejection.` |
| Blank reason | 400 | `Name why this message is poison.` |
| No Pending message remains | 409 | `There is no outbox message to reject.` |
| Unknown task | 404 | `Task not found.` |

The task status is unchanged. A file is not read. A folder is not created.

## Delivery

Delivery is unchanged except that a dead letter is not the oldest Pending message. The next Pending message is delivered instead. When every remaining message is a dead letter, delivery is refused with `There is no outbox message to deliver.`

## Page

Reject message is shown when the task is In Progress and an outbox message is still Pending. Poison rejections are listed when any exist. Dead letters are listed when any exist, each with its message and reason.
