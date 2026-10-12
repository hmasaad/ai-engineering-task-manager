# Contract: Requirements on the local pages

Extends the task list and the task detail page. The page and the API call the same domain commands. A refusal redisplays the API message.

## Navigation

The task list links to the requirements page. The requirements page links back to all tasks.

## Requirements page

`GET /requirements` shows the gap list first. A requirement appears there only when `missing` is not empty. Each row shows the identifier, the kind, the statement, and the missing phrases from the API. A second list shows every requirement so a fully traced one can be opened. An empty workspace says no requirements yet.

The create form has a statement and a kind choice of functional or non-functional. Submitting it opens the new requirement.

## Requirement page

`GET /requirements/{id}` shows the identifier, the kind, the statement, the linked tasks and their statuses, the linked criteria and Verified or Unverified, the active checks with their current result and runs, and the retired checks with their runs.

| Action | Command |
|---|---|
| Save the statement and the kind | Change the requirement |
| Link a task by its id | Link a task |
| Link a criterion by its task id and criterion id | Link a criterion |
| Remove a task link or a criterion link | Unlink |
| Name a check | Name a check |
| Remove a named check | Remove that check |
| Record Passed or Failed with a run identifier for a named check | Record a run |

Saving the same statement and kind leaves the page's Verified criteria and does not add a history line on the task. A real change shows those criteria as Unverified. Opening the linked task then shows In Progress when that task had been Completed, and the history cause `requirement_changed`.

A missing requirement says `Requirement not found.`

## Task detail

A task with linked requirements lists each identifier and links it to the requirement page. A task with none shows no requirement line. The existing verify and complete actions stay. Their new refusals use the API sentences. The page does not offer a way to record a run.

## What the pages do not do

The pages do not run a named check. They do not read a specification document. They do not mark a check Passed when the requirement is opened. They do not let the assistant create a requirement, link one, name a check, or record a run.
