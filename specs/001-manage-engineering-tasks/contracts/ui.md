# Contract: Engineer pages

Two server-rendered pages. They submit to the commands in [http-api.md](http-api.md) and display that command's result. They do not apply a separate status rule.

The application binds to `127.0.0.1` and a configured port (default `8000`).

## Task list

`GET /`

Shows every top-level task, oldest first, with its title and status. The page offers a title field and a create action. After a successful create, the new task appears on this list as Draft.

A blank title leaves the list unchanged and shows that a title is required.

## Task detail

`GET /tasks/{id}`

Shows, from the task detail in the API contract:

- title, goal, and current status
- acceptance criteria and whether each is Unverified or Verified, including observation, pass, time, and provider when Verified
- status history, oldest first, including the cause
- subtasks, oldest first, each opening its own detail page
- decisions, oldest first, including which earlier decisions each one supersedes
- cancel reason when the status is Cancelled

Actions on the page, shown only when the command is legal for the current status:

| Action | Command |
|---|---|
| Edit goal | Set the goal |
| Add, edit, or remove a criterion | Criterion commands |
| Mark ready, start, complete | Status command |
| Cancel, with a reason field | Status command `cancel` |
| Reopen, with a reason field | Status command `reopen` |
| Verify, with observation and an explicit pass | Verify command |
| Mark a criterion Unverified | Unverify command |
| Add a subtask by title | Add a subtask |
| Record a decision, with statement, rationale, and optional earlier decisions | Record a decision |

A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful command redisplays the page with the updated detail.

A Cancelled task shows its record and offers none of the mutating actions. The page tells the engineer that continued work is a new task.

## What the pages do not do

The pages do not complete, cancel, reopen, start, or verify a task because a field was filled in. Each of those is a separate action. The pages do not offer delete, restore, sign-in, or an assistant action.
