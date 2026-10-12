# Data Model: Call the Model Once

Rules below are the stored form of `specs/008-call-model-once/spec.md`. A refused command commits nothing. A refusal before the model call does not call the model.

## Configured Model

Not a stored row. Held by the open workspace. It has a non-empty name and a `complete` operation that accepts the prompt and returns text. Tests pass a scripted model. The local app can pass one too. A workspace with no model refuses the command.

## Model Call

Insert-only. No update and no delete. At most one row per implementation change.

| Field | Required | Rules |
|---|---|---|
| change_id | yes | Exactly one implementation change. Unique. |
| file_read_id | yes | A file read stored on that same task. |
| model_name | yes | Non-empty. The configured model name, not a name sent by the client. |
| model_input | yes | The prompt that was sent. May be long. Not rewritten. |
| model_output | yes | The returned text. May be empty. Not rewritten. This is also the applied file text. |

## Validation before the call

1. The task id does not exist. `Task not found.`
2. The task is Draft, Ready, Completed, or Cancelled. The messages match feature 002.
3. The project path is blank. `Name the project this change is for.`
4. The project path is not an existing folder. `The project must already exist.`
5. The account is blank. `An account of what changed is required.`
6. The class is missing or is neither ordinary nor consequential. `Choose ordinary or consequential.`
7. The file path is blank. `Name the file this change writes.`
8. No file read is chosen. `Choose the file read this change uses.`
9. The file read id is unknown. `File read not found.`
10. The file read is on another task. `The change must name a file read on that task.`
11. The file path is outside the project, the destination folder is missing, or the existing file is not text. The messages match feature 006.
12. No model is configured. `Choose the model this change uses.`
13. The model raises or returns a non-text result. `The model did not return file text.`

## What a successful call stores

One implementation change, one assistant change, one applied file, and one model call. The applied file text is the model output. The class and the file outcome follow feature 006. The task status stays In Progress.

## Reading rules

- A change with no model call reports no model.
- A change with a model call reports the model name, the input, the output, and the file read id.
- Opening the task and approving a proposal do not call the model.
- Replay compares the stored model name and output.
