# Commands: Run One File Read

## Run one file read

`POST /api/tasks/{task_id}/workflow/runs`

`POST /tasks/{task_id}/workflow/runs`

```json
{ "name": "once" }
```

`name` may be omitted. The page field is Run name, `id="run-name"`. The button is Run file read.

The trimmed name is stored once. The same name returns the task detail and does not perform another step.

The task detail includes:

```json
{
  "runs": [{ "name": "once", "title": "Read the note" }],
  "can_run_read": false
}
```

`runs` is oldest first. `can_run_read` is true only while the next unfinished step is a Pending or Failed file read and no step is Running.

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank name | 400 | `Name this run.` |
| No unfinished step | 409 | `There is no file to read.` |
| The next step is not a file read | 409 | `The next step is not a file read.` |
| A step is Running | 409 | `Recover the interrupted step first.` |
| The task is not In Progress | 409 | `The task must be In Progress.` |

A refusal does not store the name. `GET /api/tasks` stays the list of tasks.

## Page

The task shows File reads run as `once read Read the note` in `#workflow-runs`. Run file read is offered when the task is In Progress and `can_run_read` is true.
