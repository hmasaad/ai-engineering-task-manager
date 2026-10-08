# Contract: File reads on the task detail page

Extends [the feature 006 pages](../../006-apply-ordinary-file/contracts/ui.md). No new page. The list page is unchanged.

## Task detail

`GET /tasks/{id}`

In addition to the feature 006 detail, the task shows its file reads, oldest first. Each read shows the file path, the text that was read, the project, the assistant, and the time. Reads are separate from implementation changes. An empty text is shown as empty. A task with no reads shows no read lines.

Actions, shown only when the command is legal:

| Action | Shown when | Command |
|---|---|---|
| Record a change, with an account and a class | The task is In Progress | Record a change |
| Record an assistant change, with a project, a class, an account, a file path, the file text, and a stop choice | The task is In Progress | Record an assistant change |
| Read a file, with a project and a file path | The task is In Progress | Read a file |

The read form has a project and a file path and no file text. An empty project or an empty file path is refused with the API message. A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful read redisplays the page with the stored text and leaves the status In Progress. The project file is unchanged.

A Cancelled task shows stored reads and does not offer the read form.

The assistant-change form still writes or proposes a file when a path and a text are submitted. It does not become the read form.

## What the pages do not do

The pages do not call an assistant, create a project folder, create a missing folder inside the project, write a file, or delete a file because a read was requested. They do not verify a criterion, record a check, record a decision, or complete or cancel a task because a file was read. They do not offer edit or delete for a stored read. They do not show a subtask's read on the parent. They do not invent a read for an assistant change stored before this feature.
