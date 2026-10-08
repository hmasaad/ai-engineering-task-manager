# Contract: File read commands

These commands extend [the feature 006 task API](../../006-apply-ordinary-file/contracts/http-api.md). Common rules from that contract still apply: JSON bodies, trimmed project and file paths, server clock, localhost only, no authentication, and a refused command leaves every stored row unchanged and leaves the project folder unchanged.

A client-supplied assistant name, engineer name, or time is ignored. The stored assistant name is the configured assistant.

The feature 005 and feature 006 assistant-change command is unchanged. Omitting `file` does not read a project. Sending `file` still writes or proposes that file. This feature does not add a file read to that command.

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
| 404 | The task id does not exist. |
| 409 | The command is well-formed and the current status or the file location forbids it. |

## Task detail field

`GET /api/tasks/{id}` adds `file_reads`. It is an empty list when the task has no reads. Reads are oldest first. Feature 005 and feature 006 fields stay. A read is not an entry in `implementation_changes`.

```json
{
  "file_reads": [
    {
      "id": 1,
      "project": "billing",
      "path": "notes/label.txt",
      "text": "Export",
      "assistant_name": "Guide",
      "read_at": "2026-10-08T12:00:00Z"
    }
  ]
}
```

`project` is the path the engineer typed. `text` may be an empty string. A parent task does not list a subtask's reads.

## Record a read

`POST /api/tasks/{id}/file-reads`

```json
{
  "project": "billing",
  "file": "notes/label.txt"
}
```

`project` and `file` are required strings. Relative `project` is resolved from the folder where this process was started. Absolute `project` is used as given.

The body is refused, the task is unchanged, and no file is written, when:

| Condition | Status | Message |
|---|---|---|
| The task id does not exist. | 404 | `Task not found.` |
| The task is Draft. | 409 | `The task must be In Progress.` |
| The task is Ready. | 409 | `Start the task first.` |
| The task is Completed. | 409 | `Reopen the task first.` |
| The task is Cancelled. | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| `project` is blank or only spaces. | 400 | `Name the project this change is for.` |
| `project` is not an existing folder. | 400 | `The project must already exist.` |
| `file` is blank or only spaces. | 400 | `Name the file this change reads.` |
| `file` is outside the project, including through a link. | 409 | `The file must stay inside the named project.` |
| `file` does not exist, including when its folder does not exist. | 400 | `The file must already exist.` |
| `file` cannot be read as text, including a folder at that path. | 400 | `The file is not text.` |
| The JSON body is the wrong shape, including a missing `project` or `file`. | 400 | `The request is missing a required field or has the wrong shape.` |

Status is considered before the project and the file. A blank project is reported before a blank file. A wrong-shaped body is the generic message rather than one of the messages above.

A successful read returns 200 and the task detail. The new read is last in `file_reads`. The file in the project still contains the text that was stored. The task status is still In Progress. `implementation_changes` is unchanged by the read.
