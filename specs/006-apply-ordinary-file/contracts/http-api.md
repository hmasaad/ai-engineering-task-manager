# Contract: Applied file commands

These commands extend [the feature 005 assistant-change API](../../005-assist-ordinary-change/contracts/http-api.md). Common rules from that contract still apply: JSON bodies, trimmed text, server clock, localhost only, no authentication, and a refused command leaves every stored row unchanged and leaves the project folder unchanged.

A client-supplied assistant name, engineer name, or time is ignored. `engineer_name` on the change remains the workspace engineer.

## Error body

Same shape as feature 001:

```json
{
  "refused": true,
  "message": "Human-readable explanation of what is missing or illegal."
}
```

| Status | When |
|---|---|
| 400 | A required field is missing, blank, or the wrong shape. |
| 404 | The task id or the change id does not exist. |
| 409 | The command is well-formed and the current status, the file, or the actor forbids it. |

## Task detail field

`GET /api/tasks/{id}` adds `file` on each object in `implementation_changes`. Feature 005 fields stay. `file` is `null` when the change has no applied file.

An ordinary new file:

```json
{
  "id": 9,
  "what_changed": "Rename the export label",
  "class": "ordinary",
  "outcome": "Carried out",
  "engineer_name": "Ada",
  "recorded_at": "2026-10-08T12:00:00Z",
  "approval": null,
  "not_carried_out": null,
  "project": "billing",
  "assistant_name": "Guide",
  "recorded_by": "assistant",
  "stopped": false,
  "file": {
    "path": "notes/label.txt",
    "was_new": true,
    "previous_text": null,
    "text": "Export"
  }
}
```

A replacement waiting for approval uses `"class": "consequential"`, `"outcome": "Awaiting approval"`, `"file.was_new": false`, and `"file.previous_text"` set to the text the file held. A stopped ordinary request uses `"stopped": true` and `"class": "consequential"`. `project` is the path the engineer typed.

## Record a file

`POST /api/tasks/{id}/assistant-changes`

```json
{
  "project": "billing",
  "class": "ordinary",
  "what_changed": "Rename the export label",
  "stopped": false,
  "file": "notes/label.txt",
  "file_text": "Export"
}
```

`file` and `file_text` are optional. Omitting `file` keeps the feature 005 command: no applied file is stored, and the project is not opened or written. Sending `file` as a blank string is `Name the file this change writes.` Sending `file` and omitting `file_text` stores an empty text. `file_text` without `file` is ignored.

Relative `project` is resolved from the folder where this process was started. Absolute `project` is used as given.

The body is refused, the task is unchanged, and no file is written, when:

| Condition | Status | Message |
|---|---|---|
| The task id does not exist. | 404 | `Task not found.` |
| The task is Draft. | 409 | `The task must be In Progress.` |
| The task is Ready. | 409 | `Start the task first.` |
| The task is Completed. | 409 | `Reopen the task first.` |
| The task is Cancelled. | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| `project` is missing, blank, or only spaces. | 400 | `Name the project this change is for.` |
| `project` is not an existing folder, and `file` was sent. | 400 | `The project must already exist.` |
| `what_changed` is missing, blank, or only spaces. | 400 | `An account of what changed is required.` |
| `class` is missing or is neither `ordinary` nor `consequential`. | 400 | `Choose ordinary or consequential.` |
| `file` was sent and is blank or only spaces. | 400 | `Name the file this change writes.` |
| `file` is outside the project, including through a link. | 409 | `The file must stay inside the named project.` |
| The folder for `file` does not exist. | 400 | `The folder for that file must already exist.` |
| `file` exists and cannot be read as text. | 400 | `The file is not text.` |
| The JSON body is the wrong shape, including a non-boolean `stopped`. | 400 | `The request is missing a required field or has the wrong shape.` |

Status is considered before the project, the account, the class, and the file. A blank project is reported before a missing folder and before a blank file. A wrong-shaped body is the generic message rather than one of the messages above.

A successful ordinary write returns 200 and the task detail. The new change is last. The file in the project contains `file_text`. The task status is still In Progress.

A successful wait returns 200 and the task detail. The change is consequential and Awaiting approval. The project file is unchanged.

## Approve a waiting file

`POST /api/tasks/{id}/implementation-changes/{change_id}/approve`

The feature 002 body still applies. `actor` of `assistant` is refused with 409 and `The assistant cannot approve a change.` before any file is read or written.

When the change has an applied file and is Awaiting approval, success writes the proposed text and returns 200. The approval `engineer_name` is the workspace engineer. The outcome is Carried out.

| Condition | Status | Message |
|---|---|---|
| The resolved file would land outside the project. | 409 | `The file must stay inside the named project.` |
| The file no longer matches the recorded text, including a file that is no longer text, a new file that has appeared, or a file whose text changed. | 409 | `The file no longer matches the text this change was proposed against.` |
| The change is ordinary and already Carried out. | 409 | `An ordinary change does not wait for approval.` |

Those refusals write no resolution and do not change the file. The other feature 002 approval refusals are unchanged.

## Decline a waiting file

`POST /api/tasks/{id}/implementation-changes/{change_id}/not-carried-out`

Unchanged from feature 005, except that success and refusal both leave the project file unchanged. `actor` of `assistant` is 409 and `The assistant cannot decline a change.`
