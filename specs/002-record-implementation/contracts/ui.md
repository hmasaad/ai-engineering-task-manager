# Contract: Implementation changes on the task detail page

Extends [the feature 001 pages](../../001-manage-engineering-tasks/contracts/ui.md). No new page. The list page is unchanged.

## Task detail

`GET /tasks/{id}`

In addition to the feature 001 detail, the page shows `implementation_changes` from [http-api.md](http-api.md), oldest first. Each change shows what changed, whether it is ordinary or consequential, the outcome, the engineer, and the time it was recorded.

When the outcome is Carried out and the class is consequential, the page also shows the evidence reviewed and the approval time. When the outcome is Not carried out, the page also shows the reason and the time of that decision. An ordinary change shows no approval and no reason.

Actions, shown only when the command is legal:

| Action | Shown when | Command |
|---|---|---|
| Record a change, with what changed and a choice of ordinary or consequential | Task is In Progress | Record a change |
| Approve, with an evidence field | That change is Awaiting approval and the task is In Progress | Approve a change |
| Mark not carried out, with a reason field | That change is Awaiting approval and the task is In Progress | Mark a change not carried out |

A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful command redisplays the page with the updated detail. The status shown after record, approve, or mark-not-carried-out is the status from before that command.

A Cancelled task shows its changes and offers none of these actions, and none of the feature 001 mutating actions. The page still says that continued work is a new task.

Complete and cancel stay the feature 001 actions. If the engineer uses them while a change is Awaiting approval, the page shows the API refusal and the status stays In Progress.

## What the pages do not do

The pages do not treat saving a change as approval. They do not complete, cancel, or verify a task because a change was recorded. They do not offer edit or delete for a change. They do not offer a file attachment, a review link, or an assistant action.
