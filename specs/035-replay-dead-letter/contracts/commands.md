# Commands: Replay a Dead Letter

`GET /api/tasks` stays the top-level task list.

The workflow object gains `dead_letter_replays`: `{name, outbox_id, title}` oldest first.

## Replay dead letter

`POST /api/tasks/{id}/workflow/dead-letters/replay`

Body: `{"name": "once"}`. The page field is Replay name, id `replay-name`, name `name`. The button is `Replay dead letter`. It is shown when the task is In Progress and a dead letter has not been replayed.

| Condition | Status | Result |
|---|---|---|
| First accepted use of the name | 200 | The oldest unreplayed dead letter is shown as Pending. One replay names that message. The dead letter remains. The attempt count is unchanged |
| Same name again | 200 | No second replay |
| A later delivery of that message | 200 | The message is Delivered, even when an earlier next time has not arrived |
| Blank name | 400 | `Name this replay.` |
| No dead letter left to replay | 409 | `There is no dead letter to replay.` |
| Task is not In Progress | 409 | `The task must be In Progress.` The name is not saved |
| Unknown task | 404 | `Task not found.` |

Replay does not read a file, create a folder, approve a change, advance the workflow, or change the task status.

## Page

When a replay exists, the workflow section shows Replayed dead letters. The list id is `workflow-dead-letter-replays`.
