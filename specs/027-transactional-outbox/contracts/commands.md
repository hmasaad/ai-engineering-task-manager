# Commands: Transactional Outbox and Inbox

`GET /api/tasks` stays the top-level task list.

The workflow object on a task detail gains:

- `outbox`: a list, oldest first, of `{"id": 1, "title": "Read the note", "effect": "note.txt", "state": "Pending"}`.
- `inbox`: a list, in delivery order, of `{"name": "once", "outbox_id": 1}`.

## Deliver

`POST /api/tasks/{id}/workflow/outbox`

JSON body: `{"name": "once"}`. The page field is `delivery-name`. The button is `Deliver outbox`.

| Condition | Status | Result |
|---|---|---|
| A Pending message exists and the name is new | 200 | The task detail. The oldest Pending message is Delivered. The inbox records that name. |
| The name is already in the inbox | 200 | The task detail. No other message changes state. |
| Blank name | 400 | `Name this delivery.` Messages stay as they were. |
| A new name and no Pending message | 409 | `There is no outbox message to deliver.` |
| Unknown task | 404 | `Task not found.` |

The task status is unchanged. No file is read and no folder is created. The same name on another task can deliver that task's oldest Pending message.

## Page

The workflow section shows the outbox. When it is empty, the copy is `No outbox messages yet.` A Pending message on an In Progress task shows Deliver outbox. The inbox shows each accepted name.
