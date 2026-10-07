# Data Model: Link a Decision to Its Evidence

Rules below are the stored form of `specs/004-link-decision-evidence/spec.md`. They extend `specs/001-manage-engineering-tasks/data-model.md` and `specs/003-verify-implementation/data-model.md`. The domain module is the only writer. A refused command commits nothing. Task, criterion, status-change, implementation-change, implementation-resolution, and implementation-check rows are unchanged by recording a decision.

## Implementation Decision

Unchanged from feature 001. Insert-only. No update and no delete. A decision still has a statement, a rationale, a time, one task, and zero or more earlier decisions on that task that it supersedes.

The existing command still records a decision with only a statement and a rationale. That decision has no row in Decision Check.

## Decision Check

Insert-only. No update and no delete. At most one row per decision. Many rows may name one check.

| Field | Required | Rules |
|---|---|---|
| decision_id | yes | Exactly one implementation decision. Unique. The decision and the check are written in the same command. |
| check_id | yes | Exactly one implementation check. The check's change must belong to the decision's task at insert time. |

A decision cannot be moved to another check. A saved link is never rewritten and never removed.

Two decisions on the same task may name the same check. A decision on a subtask names a check on that subtask only. It is not copied onto the parent.

Refused, and no decision row and no link row are written, when:

- The task id does not exist. The engineer is told the task was not found.
- The task is `Cancelled`. The engineer is told decisions cannot be added to a cancelled task.
- The statement or the rationale is empty or only spaces. The engineer is told both a statement and a rationale are required.
- The check id is missing. The engineer is told to choose the check this decision rests on.
- The check id does not exist. The engineer is told the check was not found.
- The check belongs to a different task. The engineer is told the decision must name a check on that task.
- A named earlier decision does not exist. The engineer is told the decision was not found.
- A named earlier decision belongs to a different task. The engineer is told a decision can only supersede earlier decisions on the same task.
- A named earlier decision is this decision or was recorded after it. The engineer is told a decision cannot supersede itself or a decision that comes after it.

The task is considered before Cancelled. Cancelled is considered before the statement, the rationale, and the check. A blank statement or rationale is considered before a missing, unknown, or wrong-task check. The check is considered before the supersede list.

Draft, Ready, In Progress, and Completed are allowed when the named check is on that task. The named check may be Passed or Failed. It need not be the current result of that change and criterion.

## Reading a decision

Decisions on a task are read oldest first (`recorded_at`, then `id`). Linked and unlinked decisions are in that one list.

| Decision | What the reader gets |
|---|---|
| No Decision Check row | Statement, rationale, time, and supersede list. The named check is absent. |
| One Decision Check row | Those same fields, plus the named check's id, its change, the account of what changed, the criterion id, the criterion wording stored on the check, the evidence, and Passed or Failed. |

Those check facts come from the named check and its change. They are not a second copy. A later check of the same change and criterion does not change them. Editing the live criterion text does not change them. Removing the criterion does not remove the decision or the check, and the decision still shows the wording stored on the check.

## What this command does not change

Recording a decision that names a check does not append a status change, does not verify or unverify a criterion, does not insert a check, and does not insert an implementation resolution. The task status, the change outcome, and the named check's evidence and result stay as they were.

Completion and cancellation do not gain a guard. A carried-out change with no decision, and a decision that names no check, do not by themselves refuse either command.

## Invariants

- A decision names at most one check, and that check is on the decision's task.
- A saved decision and its link are never deleted or updated.
- The evidence and result shown for a linked decision are the evidence and result of the check it named.
- A decision that names no check remains a valid decision.
- A parent task's decision list does not include a subtask's decisions.
- Two workspaces that receive the same commands at the same clock times end with the same statements, the same named checks, and the same decision order.
