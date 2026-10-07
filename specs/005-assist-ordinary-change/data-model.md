# Data Model: Assist an Ordinary Change

Rules below are the stored form of `specs/005-assist-ordinary-change/spec.md`. They extend `specs/002-record-implementation/data-model.md`. The domain module is the only writer. A refused command commits nothing. Task, criterion, status-change, decision, check, and implementation-resolution rows are unchanged by recording an assistant change.

## Workspace Assistant

One row. The configured assistant name. Set when the workspace is opened. Default `Assistant` when the engineer does not set one.

| Field | Required | Rules |
|---|---|---|
| id | yes | Always 1. |
| assistant_name | yes | Non-empty after trimming. Not taken from a change request. |

Changing this name later does not rewrite `assistant_change` rows already stored.

## Implementation Change

Unchanged columns from feature 002. `engineer_name` remains the workspace engineer, including when an assistant change points at this row. Class is `ordinary` or `consequential`. Outcome is still derived: ordinary with no resolution is Carried out; consequential with no resolution is Awaiting approval.

The engineer's existing record command still inserts a change with no Assistant Change row.

## Assistant Change

Insert-only. No update and no delete. At most one row per implementation change.

| Field | Required | Rules |
|---|---|---|
| change_id | yes | Exactly one implementation change. Unique. The change and this row are written in the same command. |
| project | yes | Non-empty after trimming. The project the engineer named. The command does not open or write that project. |
| assistant_name | yes | Configured assistant name copied at insert time. Not taken from the request. |
| stopped | yes | `0` or `1`. `1` only when the request class was ordinary and the assistant stopped because the work would be consequential. The implementation change is then stored as `consequential`. |

A saved assistant change cannot be moved to another task or another project.

Refused, and no implementation-change row and no assistant row are written, when:

- The task id does not exist. The engineer is told the task was not found.
- The task is `Draft`. The engineer is told the task must be In Progress.
- The task is `Ready`. The engineer is told to start the task first.
- The task is `Completed`. The engineer is told to reopen the task first.
- The task is `Cancelled`. The engineer is told that a cancelled task cannot be changed and continued work is a new task.
- The project is empty or only spaces. The engineer is told to name the project this change is for.
- The account of what changed is empty or only spaces. The engineer is told an account of what changed is required.
- The class is missing or neither ordinary nor consequential. The engineer is told to choose ordinary or consequential.

The task is considered before the status. The status is considered before the project, the account, and the class. A blank project is considered before a blank account. The account is considered before a bad class.

## What is stored for each request

| Request | Stored class | stopped | Outcome before a resolution |
|---|---|---|---|
| Ordinary, and the assistant did not stop | `ordinary` | `0` | Carried out |
| Consequential | `consequential` | `0` | Awaiting approval |
| Ordinary, and the assistant stopped | `consequential` | `1` | Awaiting approval |

A consequential request is not carried out. An ordinary request that stopped is not carried out. The named project is not opened or written by this command.

## Reading a change

Implementation changes on a task stay oldest first (`recorded_at`, then `id`). Engineer changes and assistant changes are in that one list.

| Change | What the reader gets |
|---|---|
| No Assistant Change row | The feature 002 change. `project` is absent, `assistant_name` is absent, and `recorded_by` is `engineer`. |
| One Assistant Change row | Those same fields, plus the project, the assistant name, `recorded_by` of `assistant`, and whether the request stopped. |

`engineer_name` on the change remains the workspace engineer. The approval and the decline, when present, still name the workspace engineer.

## Approval and decline

The existing resolution row is unchanged. The engineer approves or declines a waiting change, including one the assistant recorded.

An approval or decline whose actor is `assistant` is refused. No resolution row is written. The change stays Awaiting approval when that was its outcome. The engineer is told the assistant cannot approve a change, or cannot decline a change.

A request that omits the actor is the engineer's command and follows the feature 002 rules.

## What this command does not change

Recording an assistant change does not append a status change, does not verify or unverify a criterion, does not insert a check, and does not insert a decision. The task status stays as it was.

Completion and cancellation do not gain a guard. A carried-out assistant change is covered by the feature 003 passing-check guard. A waiting assistant change is covered by the feature 002 awaiting-approval guard.

## Invariants

- An assistant change serves exactly one task and names exactly one project and one assistant.
- A saved assistant change is never deleted or updated.
- An ordinary assistant change that did not stop is Carried out. A consequential assistant change, and an ordinary request that stopped, is Awaiting approval until the engineer resolves it.
- The assistant does not approve or decline a change.
- A parent task's change list does not include a subtask's changes.
- Two workspaces that receive the same commands at the same clock times end with the same accounts, projects, assistant names, outcomes, and order.
