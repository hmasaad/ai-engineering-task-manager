# Commands: Real Model

`GET /api/tasks` stays the top-level task list.

## Model service

`GET /api/model`

`{"name": null, "base_url": null, "api_key": null}` when none is saved. Otherwise the saved `name`, `base_url`, and `api_key`. `api_key` is null when no key was saved.

`POST /api/model`

JSON body: `{"name": "Guide", "base_url": "http://127.0.0.1:11434/v1", "api_key": ""}`. Extra fields are ignored. A `text` field is ignored.

| Condition | Status | Result |
|---|---|---|
| Name and an `http` or `https` address | 200 | The saved name, address, and key or null |
| Blank name | 400 | `Choose the model this change uses.` The saved service stays. |
| Blank or non-http address | 400 | `Name the model service.` The saved service stays. |

The page fields are `model-name`, `model-address`, and `model-key`. There is no `model-text` field. The button is `Save model`.

## Start work

`POST /api/instructions` is unchanged in shape.

The saved service is asked once. The request contains the task title, the goal, the acceptance criterion, what changed, and the file text. The reply is the file text.

| Condition | Status | Message |
|---|---|---|
| Service cannot be reached, returns an error, or does not answer within 120 seconds | 400 | `The model service could not be reached.` Nothing is stored. |
| Empty reply | 400 | `The model did not return file text.` Nothing is stored. |
| Existing file | 200 | The task detail. The file is unchanged. The change is Awaiting approval and shows the reply. |
| New ordinary file | 200 | The task detail. The file contains the reply. |

Approving that waiting change writes the stored reply and does not ask the service again.

## Page

`GET /instructions` shows Model name, Model address, and API key. It does not show Model text. Success opens the task, which shows the reply.
