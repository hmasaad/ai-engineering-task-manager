# Commands: Instruction Page

`GET /api/tasks` stays the top-level task list.

## Saved model

`GET /api/model`

`{"name": null, "text": null}` when none is saved. Otherwise `name` and `text`.

`POST /api/model`

JSON body: `{"name": "Guide", "text": "Export"}`. Extra fields are ignored.

| Condition | Status | Result |
|---|---|---|
| Name and text present | 200 | `{"name": "Guide", "text": "Export"}` |
| Blank name | 400 | `Choose the model this change uses.` The saved model stays. |
| Blank text | 400 | `Name the text the model returns.` The saved model stays. |

The page fields are `model-name` and `model-text`. The button is `Save model`.

## Start work

`POST /api/instructions`

JSON body: `title`, `goal`, `criterion`, `project`, `read_path`, `file`, `class`, `what_changed`.

| Condition | Status | Message |
|---|---|---|
| Success | 200 | The task detail. Status is In Progress. |
| No saved model | 400 | `Choose the model this change uses.` |
| Blank title | 400 | `A title is required.` |
| Blank goal | 400 | `A goal is required.` |
| Blank criterion | 400 | `An acceptance criterion is required.` |
| Blank project | 400 | `Name the project this change is for.` |
| Missing project | 400 | `The project must already exist.` |
| Blank file to read | 400 | `Name the file this change reads.` |
| Blank file to change | 400 | `Name the file this change writes.` |
| Missing class | 400 | `Choose ordinary or consequential.` |
| Blank account | 400 | `An account of what changed is required.` |
| Missing file to read | 400 | `The file must already exist.` |

A refusal stores no task and writes no file.

## Page

`GET /instructions` shows the saved model and the instruction form. The task list links to it. Field ids: `model-name`, `model-text`, `instruction-title`, `instruction-goal`, `instruction-criterion`, `instruction-project`, `instruction-read`, `instruction-file`, `instruction-class`, `instruction-what`. The start button is `Start work`. Success opens the task.
