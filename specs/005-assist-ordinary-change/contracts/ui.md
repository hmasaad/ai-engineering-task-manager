# Contract: Assistant changes on the task detail page

Extends [the feature 004 pages](../../004-link-decision-evidence/contracts/ui.md). No new page. The list page is unchanged.

## Task detail

`GET /tasks/{id}`

In addition to the feature 004 detail, each implementation change shows its assistant fields from [http-api.md](http-api.md). Changes stay oldest first. An assistant change shows the project, the assistant name, the account of what changed, and Carried out or Awaiting approval. An engineer change shows the engineer, as it does today.

Actions, shown only when the command is legal:

| Action | Shown when | Command |
|---|---|---|
| Record a change, with an account and a class | The task is In Progress | Record a change |
| Record an assistant change, with a project, a class, an account, and a stop choice | The task is In Progress | Record an assistant change |

The stop choice records that an ordinary request must not be carried out. A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful command redisplays the page with the updated detail. The status shown after the command is the status from before that command. The page does not open or write the named project.

A Cancelled task shows its changes, including any project and assistant name already stored, and offers neither record action. The page still says that continued work is a new task.

Approve and decline stay the engineer's actions. The page does not offer them to the assistant.

Complete and cancel stay the earlier actions. A carried-out assistant change still needs a passing check. A waiting assistant change still blocks completion and cancellation.

## What the pages do not do

The pages do not call an assistant, edit a project, or treat the assistant's account as a check or a decision. They do not verify a criterion because an assistant change was recorded. They do not complete or cancel a task because an assistant change was recorded. They do not offer edit or delete for an assistant change. They do not show a subtask's change on the parent.
