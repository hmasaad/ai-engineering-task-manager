# Contract: Model file commands

Extends the feature 006 assistant-change API. A client-supplied model name, assistant name, engineer name, or time is ignored.

`POST /api/tasks/{id}/assistant-changes` is unchanged and does not call a model.

## Record a model file

`POST /api/tasks/{id}/model-files`

```json
{
  "project": "billing",
  "class": "ordinary",
  "what_changed": "Propose the export label",
  "stopped": false,
  "file": "notes/proposed.txt",
  "file_read_id": 1
}
```

`file_read_id` may be omitted. Omitting it is `Choose the file read this change uses.` A non-integer `file_read_id` is the wrong-shape message.

| Condition | Status | Message |
|---|---|---|
| The task id does not exist. | 404 | `Task not found.` |
| The task is Draft. | 409 | `The task must be In Progress.` |
| The task is Ready. | 409 | `Start the task first.` |
| The task is Completed. | 409 | `Reopen the task first.` |
| The task is Cancelled. | 409 | `A cancelled task cannot be changed. Continued work is a new task.` |
| `project` is blank or only spaces. | 400 | `Name the project this change is for.` |
| `project` is not an existing folder. | 400 | `The project must already exist.` |
| `what_changed` is blank or only spaces. | 400 | `An account of what changed is required.` |
| `class` is missing or is neither `ordinary` nor `consequential`. | 400 | `Choose ordinary or consequential.` |
| `file` is blank or only spaces. | 400 | `Name the file this change writes.` |
| `file_read_id` is omitted. | 400 | `Choose the file read this change uses.` |
| `file_read_id` is unknown. | 404 | `File read not found.` |
| The file read is on another task. | 409 | `The change must name a file read on that task.` |
| `file` is outside the project. | 409 | `The file must stay inside the named project.` |
| The folder for `file` does not exist. | 400 | `The folder for that file must already exist.` |
| `file` exists and cannot be read as text. | 400 | `The file is not text.` |
| No model is configured. | 400 | `Choose the model this change uses.` |
| The model does not return text. | 400 | `The model did not return file text.` |
| The JSON body is the wrong shape. | 400 | `The request is missing a required field or has the wrong shape.` |

A successful ordinary write returns 200 and the task detail. The new change is last. `model.name` is the configured model name. `model.output` is the returned text. `file.text` is that same text. The project file contains it.

A waiting proposal returns 200. The project file is unchanged. `model.output` is the returned text.

`GET /api/tasks/{id}` adds `model` on each implementation change. It is `null` when that change did not call the model.

```json
{
  "model": {
    "name": "Guide-model",
    "input": "Task: Add export\n",
    "output": "Export",
    "file_read_id": 1
  }
}
```

Approval and decline are unchanged. Neither calls the model.
