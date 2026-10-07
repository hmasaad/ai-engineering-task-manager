# Contract: Implementation checks on the task detail page

Extends [the feature 002 pages](../../002-record-implementation/contracts/ui.md). No new page. The list page is unchanged.

## Task detail

`GET /tasks/{id}`

In addition to the feature 002 detail, each implementation change shows its `checks` from [http-api.md](http-api.md), oldest first. Each check shows the criterion wording stored on that check, the evidence, Passed or Failed, the engineer, and the time.

Actions, shown only when the command is legal:

| Action | Shown when | Command |
|---|---|---|
| Record a check, with a criterion from this task, an evidence field, and a choice of Passed or Failed | That change is Carried out and the task is In Progress | Record a check |

A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful command redisplays the page with the updated detail. The status shown after recording a check is the status from before that command. The change outcome is the outcome from before that command. The criterion stays Verified or Unverified as it was.

A change that is Awaiting approval or Not carried out shows any checks it already has and does not offer Record a check. A task that is not In Progress does not offer Record a check. A Cancelled task shows its checks and offers none of these actions, and none of the earlier mutating actions. The page still says that continued work is a new task.

Complete and cancel stay the earlier actions. If the engineer completes the task while a carried-out change lacks a passing check, the page shows the API refusal and the status stays In Progress. Cancel does not refuse for that reason.

## What the pages do not do

The pages do not treat saving a change, or approving a change, as a check. They do not verify a criterion because a check was recorded. They do not complete or cancel a task because a check was recorded. They do not offer edit or delete for a check. They do not offer a file attachment, a test run, a review link, or an assistant action.
