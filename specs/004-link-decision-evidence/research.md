# Research: Link a Decision to Its Evidence

## 1. Where the feature lives

**Decision**: Extend the existing local Python process. The existing decision module gains one function that records a decision and names one check. The existing function that records a decision without a check stays as it is. SQLite stores the new link in the same workspace file. The existing task detail page and JSON API call the new function.

**Rationale**: The spec attaches a decision to a check that already exists, for one engineer and one workspace. A second process would split one task record across two writers. Principle VIII keeps this feature in the same reviewable process.

**Alternatives considered**:

- A new service that stores the chain elsewhere. The reader would no longer see the decision on the task record alone.
- A new domain module that copies the supersede rules. Those rules already live with decisions, and a second copy could drift from feature 001.
- Making the existing decision command require a check. The spec keeps the decision that has only a statement and a rationale.

## 2. How the link is stored

**Decision**: One append-only table, `decision_check`. Each row stores the decision id and exactly one check id. The decision id is unique in that table, so a decision names at most one check. A decision with no row there names no check. Many decisions may name the same check. Nothing updates or deletes a row.

The criterion wording, the account of what changed, the evidence, and the result are not copied onto the decision. Reading the decision joins the named check and that check's change. Those rows are insert-only, so the joined facts stay the ones stored when the check was recorded.

**Rationale**: The spec forbids editing or removing a saved decision, and it requires the decision to keep showing the check it named after a later check exists. A new row is the link. Joining the named check id, rather than "the latest check of that pair," leaves the earlier evidence and result in place. A new table leaves the feature 001 decision columns unchanged, so an older workspace file gains the table when it is opened.

**Alternatives considered**:

- A nullable check column on `implementation_decision`. The schema script uses `CREATE TABLE IF NOT EXISTS`, which does not add a column to a table that already exists.
- Copying the criterion wording, evidence, and result onto the decision. Those facts already cannot change on the check. A second copy could disagree with the check the decision names.
- Pointing the decision at the change and the criterion, and showing the current result. The spec says the decision names one stored check, not whatever the latest result is.
- A foreign key from the decision to the criterion. Removing a criterion must not remove the decision or the check. The check already stores the wording without a foreign key to the criterion.

## 3. Two commands

**Decision**: Keep `POST /api/tasks/{id}/decisions` unchanged. A `check_id` sent to that command is ignored, and the saved decision names no check. Add `POST /api/tasks/{id}/linked-decisions` for a decision that names one check. If that command omits the check, it stores nothing and tells the engineer to choose the check this decision rests on.

**Rationale**: The spec describes two actions. The new action refuses a missing check. The existing action still saves a decision that does not name one. One route with an optional check cannot do both.

**Alternatives considered**:

- Optional `check_id` on the existing command. Omitting it would save an unlinked decision, so the new action could not refuse a missing check.
- Requiring `check_id` on the existing command. Feature 001 decisions, and the spec's existing action, would start failing.

## 4. What the reader sees

**Decision**: Task detail lists decisions oldest first, as it does now. Each decision gains `check`. It is null when the decision names no check. When the decision names a check, `check` includes that check's id, the change id, the account of what changed, the criterion id, the criterion wording, the evidence, Passed or Failed, the engineer who recorded the check, and the check time. A later check of the same change and criterion does not change this object.

**Rationale**: The spec requires one list and requires the linked decision to show the chain. Null keeps an unlinked decision in that list without inventing a check. The displayed result is the named row's result, not the current result of the pair.

**Alternatives considered**:

- A second list for linked decisions. The spec says both kinds appear in one list.
- Omitting `check` on old decisions. Callers would have to treat a missing field and a null field as different, for the same fact.

## 5. Who may record it, and when

**Decision**: Reuse the workspace. The command does not store a new engineer name on the decision. Feature 001 decisions do not have one, and this workspace has one engineer. A name or a time in the request is ignored. The time on the decision is the injected clock. The engineer and time already stored on the named check stay on that check.

The command is allowed while the task is Draft, Ready, In Progress, or Completed, and refused while it is Cancelled, with the existing message `Decisions cannot be added to a cancelled task.` The named check must be on that task. A check is normally recorded only while the task is In Progress, and a task does not return to Draft or Ready, so a Draft or Ready task usually has no check of its own. The status rule still matches feature 001: any status except Cancelled may receive a decision.

**Rationale**: The spec allows the linked decision on every status except Cancelled, including Completed. It does not ask the decision row to name a person beyond the workspace engineer who already owns the task record.

**Alternatives considered**:

- Allowing the command only while In Progress. The spec explicitly allows Completed, and feature 001 already allows a decision on Completed.
- Copying the engineer name onto the decision. That would add a field the spec does not require and that existing decisions do not have.
- Accepting an engineer name from the client. A client could then claim another actor.

## 6. Refusal order

**Decision**: Consider the task, then Cancelled, then the statement and rationale, then the check, then the supersede rules. A blank statement or rationale is `Both a statement and a rationale are required.` and is reported before a missing, unknown, or wrong-task check. A missing check is `Choose the check this decision rests on.` An unknown check is `Check not found.` A check on another task is `The decision must name a check on that task.` Supersede keeps the feature 001 messages. A refusal writes no decision row and no link row.

**Rationale**: Feature 001 already refuses Cancelled before it inspects the text. The spec says a blank statement is reported when the check is also missing. Checking the text before the check keeps that sentence stable.

**Alternatives considered**:

- Reporting the missing check first. A blank statement would then be hidden whenever the check was also missing, which the spec forbids.
- Reporting a wrong status with the feature 003 check messages. This action is a decision, and Cancelled already has a decision message.

## 7. Supersede

**Decision**: The linked command accepts the same `supersedes` list as the existing command. A later linked decision may name earlier decisions on the same task, including decisions that do not name a check. It cannot name itself, a later decision, or a decision on another task. Each named decision stays. The link row does not replace `decision_supersedes`.

**Rationale**: The spec keeps the feature 001 supersede rules and explicitly allows a linked decision to supersede an unlinked one.

**Alternatives considered**:

- A separate supersede store for linked decisions. The reader would no longer see one chain of decisions on the task.
- Forbidding a linked decision from superseding an unlinked one. The spec's third story requires that case.

## 8. Order and replay

**Decision**: Reuse the injected clock. Decisions on a task stay ordered by `recorded_at` ascending, then `id` ascending. The same command script against the same task, with the same scripted clock and the same check, produces the same statements, the same named check, and the same order.

**Rationale**: Principle V and spec SC-004. A tie on the clock still has one order because integer ids increase with insertion.

**Alternatives considered**:

- A second clock inside the new function. Two clocks would let one command store two unrelated times.
- Sorting linked decisions ahead of unlinked ones. The spec requires one oldest-first list.

## 9. Completion and cancellation

**Decision**: Do not add a completion guard and do not add a cancellation guard. A carried-out change with no decision does not change the feature 003 completion message. Recording the decision does not append a status change, does not verify a criterion, does not insert a check, and does not insert an implementation resolution.

**Rationale**: The spec says a missing decision is not a reason to refuse completion or cancellation, and recording the decision must not change status, outcome, check result, or verification.

**Alternatives considered**:

- Refusing completion until every carried-out change has a linked decision. The spec forbids that new refusal.
- Treating the decision as the criterion's Verified state. Verifying a criterion remains a separate action.

## 10. Interface

**Decision**: Add one JSON command and one form on the existing task detail page. No new page and no new dependency. The page and the API call the same domain function. Binding stays `127.0.0.1`.

The command is `POST /api/tasks/{id}/linked-decisions` with the statement, the rationale, the check id, and an optional supersede list. The form is shown whenever the task is not Cancelled, beside the existing decision form. Its check list contains only checks on that task, plus an empty choice so a missing check can be refused. A Cancelled task shows decisions and the checks they name, and offers neither decision form.

**Rationale**: The reader follows the chain by opening the task. A new page would hide the decision from the record the spec already uses. One domain function keeps the page and the API from diverging. The empty choice makes the missing-check refusal reachable on the page.

**Alternatives considered**:

- HTML only. Harder to assert refusal messages and unchanged rows.
- Putting the check id only in the URL. A missing check would be a different route, and the spec's missing-check sentence would not be the response.
- Hiding the form until a check exists. The engineer could not submit the missing-check case from the page.

## 11. Existing workspace files

**Decision**: Add `decision_check` with `CREATE TABLE IF NOT EXISTS` in the existing schema script. That script already runs when a workspace file is opened, so an older file gains the table. No change to task, criterion, decision, check, or implementation-change columns. `check_id` references `implementation_check`, which is never deleted. `decision_id` references `implementation_decision`.

**Rationale**: Engineers may already have a workspace from feature 001, 002, or 003. A new table does not rewrite their tasks, criteria, history, decisions, changes, or checks. Existing decisions simply have no link row.

**Alternatives considered**:

- A second database file for links. The decision would no longer be in the task's workspace.
- Requiring the engineer to delete `workspace.db`. That throws away the history this product keeps.

## Resolved clarifications

The spec left no `[NEEDS CLARIFICATION]` markers. No Technical Context item remains open. The process, storage shape, separate command, readable chain, status rule, refusal order, supersede behavior, ordering, unchanged completion, interface, and existing-file behavior are the decisions above.
