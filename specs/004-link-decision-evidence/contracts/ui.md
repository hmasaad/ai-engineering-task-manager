# Contract: Linked decisions on the task detail page

Extends [the feature 003 pages](../../003-verify-implementation/contracts/ui.md). No new page. The list page is unchanged.

## Task detail

`GET /tasks/{id}`

In addition to the feature 003 detail, each decision shows its `check` from [http-api.md](http-api.md). Decisions stay oldest first. A decision with a check shows the criterion wording, the account of what changed, the evidence, and Passed or Failed, with the statement, the rationale, and the time. A decision with no check shows the statement, the rationale, and the time, as it does today.

Actions, shown only when the command is legal:

| Action | Shown when | Command |
|---|---|---|
| Record a decision, with a statement and a rationale, and an optional supersede list | The task is not Cancelled | Record a decision |
| Record a decision on a check, with a statement, a rationale, a check from this task, and an optional supersede list | The task is not Cancelled | Record a decision that names a check |

The check control lists only checks on this task, oldest first, and includes an empty choice. A refused command redisplays this page with the API `message` and the same stored task as before the command. A successful command redisplays the page with the updated detail. The status shown after recording the decision is the status from before that command. The change outcome is the outcome from before that command. The named check stays Passed or Failed as it was. The criterion stays Verified or Unverified as it was.

A Cancelled task shows its decisions, including any check they name, and offers neither action. The page still says that continued work is a new task. A Completed task still offers both actions when it is not Cancelled.

Complete and cancel stay the earlier actions. Completing or cancelling a task that has a carried-out change and no decision uses the same message as before this feature.

## What the pages do not do

The pages do not treat a Passed check, a Failed check, or a Verified criterion as a decision. They do not verify a criterion because a decision was recorded. They do not record a check because a decision was recorded. They do not complete or cancel a task because a decision was recorded. They do not offer edit or delete for a decision. They do not offer a file attachment, a test run, a review link, or an assistant action. They do not show a subtask's decision on the parent.
