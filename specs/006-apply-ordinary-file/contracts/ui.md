# Contract: Applied files on the task detail page

Extends [the feature 005 pages](../../005-assist-ordinary-change/contracts/ui.md). No new page. The list page is unchanged.

## Task detail

`GET /tasks/{id}`

In addition to the feature 005 detail, an assistant change that has a file shows the file path, whether the file was new, the text it had when it was not new, and the text written or proposed. Changes stay oldest first. An engineer change, and an assistant change with no file, show no file.

Actions, shown only when the command is legal:

| Action | Shown when | Command |
|---|---|---|
| Record a change, with an account and a class | The task is In Progress | Record a change |
| Record an assistant change, with a project, a class, an account, a file path, the file text, and a stop choice | The task is In Progress | Record an assistant change |

The file path and the file text are part of the assistant form. An empty file path is refused with the API message. An empty file text is a real empty file when the path is present. A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful ordinary write redisplays the page with Carried out and leaves the status In Progress. A waiting proposal redisplays the page with Awaiting approval and does not change the file.

A Cancelled task shows stored file fields and does not offer the assistant form.

Approve and decline stay the engineer's actions on a waiting change. Approving a waiting file writes it only when the API would write it. The page does not offer approve or decline to the assistant. A mismatch or an outside path redisplays the API message and leaves the file unchanged.

Complete and cancel stay the earlier actions. A carried-out file change still needs a passing check. A waiting file change still blocks completion and cancellation.

## What the pages do not do

The pages do not call an assistant, create a project folder, create a missing folder inside the project, or delete a file. They do not verify a criterion, record a check, record a decision, or complete or cancel a task because a file was written. They do not offer edit or delete for a stored file record. They do not show a subtask's file on the parent. They do not write a file for an assistant change that has no file record.
