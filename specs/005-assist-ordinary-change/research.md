# Research: Assist an Ordinary Change

## 1. Where the feature lives

**Decision**: Extend the existing local Python process. The existing implementation module gains one function that records an assistant change. The existing function that records the engineer's change stays as it is. SQLite stores the new rows in the same workspace file. The existing task detail page and JSON API call the new function.

**Rationale**: The spec attaches an assistant change to a task that already exists, for one engineer and one workspace. A second process would split one task record across two writers. Principle VIII keeps this feature in the same reviewable process.

**Alternatives considered**:

- A new service that edits the named project and stores the change elsewhere. The reader would no longer see the change on the task record alone, and a replay would carry the work out again.
- A new domain module that copies the outcome rules. Those rules already live with implementation changes, and a second copy could drift from feature 002.
- Making the existing record-change command require a project and an assistant. The spec keeps the engineer's own change.

## 2. What the command stores, and what it does not do

**Decision**: The command stores the account, the project, the class, and whether an ordinary request stopped because the work would be consequential. It does not call a model. It does not open, read, or write the named project. The account in the request is the assistant's recorded output. Replay of the same command script stores the same account again in a fresh workspace. It does not ask an assistant to carry the work out.

An ordinary request with no stop is stored as class `ordinary` and is Carried out. A consequential request is stored as class `consequential` and is Awaiting approval. An ordinary request with the stop set is stored as class `consequential` and is Awaiting approval, and the assistant row records that the request stopped. The existing outcome rule then applies: ordinary with no resolution is Carried out, and consequential with no resolution is Awaiting approval.

**Rationale**: Principle V requires the assistant's non-deterministic output to be captured and the rest of the pipeline to replay from that record. The spec says a replay shows the same account and does not carry the work out again. Calling a model inside the command would hide that output and would make the second pass do the work again. The product also has no model dependency. Leaving the project untouched makes "the project is unchanged" true for every consequential request, because this command never writes there.

**Alternatives considered**:

- Invoking a model to edit the project during the command. Replay would no longer be the same command script, and the spec forbids asking the assistant to carry the work out again.
- Inferring consequential from the wording of the account. Feature 002 already says the product does not infer the class. The stop flag is the assistant's explicit report that the work would be consequential.
- Storing an ordinary class and a separate "not carried out" outcome for the stop. The existing rule would show that ordinary change as Carried out.

## 3. How the assistant is named

**Decision**: Add a configured assistant name, default `Assistant`, set when the process starts and stored in a one-row `workspace_assistant` table. Recording an assistant change copies that name onto the new `assistant_change` row. A name in the request is ignored. Changing the configured name later does not rewrite older rows. `implementation_change.engineer_name` stays the workspace engineer for every change, including an assistant change. The approval and the decline still copy the workspace engineer.

**Rationale**: The spec says the assistant has a name distinct from the engineer, and that a request must not claim a different actor. Copying the configured name matches the way feature 002 copies the engineer. Keeping `engineer_name` on the change row equal to the workspace engineer leaves the feature 002 rule intact. The reader sees the assistant in `assistant_name`.

**Alternatives considered**:

- Writing the assistant name into `engineer_name`. Existing changes would no longer have one meaning for that field, and feature 002 says the provider stored on a change is the workspace engineer.
- Accepting the assistant name from the client. A client could then claim another actor.
- A second human approver. The spec has one engineer.

## 4. How the link is stored

**Decision**: One append-only table, `assistant_change`. Each row stores the change id, the project, the assistant name, and whether an ordinary request stopped. The change id is unique, so a change has at most one assistant row. A change with no row was recorded by the engineer. Nothing updates or deletes a row.

The project and the assistant name are not copied onto `implementation_change`. Reading the change joins `assistant_change` when the row exists.

**Rationale**: The spec forbids editing or removing a saved change. A new table leaves the feature 002 columns unchanged, so an older workspace file gains the table when it is opened. `CREATE TABLE IF NOT EXISTS` does not add a column to a table that already exists.

**Alternatives considered**:

- Nullable project and assistant columns on `implementation_change`. The schema script would not add those columns to an existing file.
- A second database file for assistant changes. The change would no longer be in the task's workspace.

## 5. Two commands

**Decision**: Keep `POST /api/tasks/{id}/implementation-changes` unchanged. A `project` or `assistant_name` sent to that command is ignored, and the saved change has no assistant row. Add `POST /api/tasks/{id}/assistant-changes` for the assistant request.

**Rationale**: The spec describes two actions. The new action requires a project. The existing action still saves the engineer's change with no project and no assistant.

**Alternatives considered**:

- Optional `project` on the existing command. Omitting it would save an engineer change, so the new action could not require a project without breaking feature 002.
- Requiring `project` on the existing command. The engineer's changes would start failing.

## 6. Refusal order

**Decision**: Consider the task, then the status, then the project, then the account, then the class. A blank project is `Name the project this change is for.` and is reported before a blank account. A blank account is `An account of what changed is required.` A missing class, or a class other than `ordinary` or `consequential`, is `Choose ordinary or consequential.` Status messages match feature 002: Draft is `The task must be In Progress.`, Ready is `Start the task first.`, Completed is `Reopen the task first.`, and Cancelled is `A cancelled task cannot be changed. Continued work is a new task.` A refusal writes no change row and no assistant row.

**Rationale**: Feature 002 refuses status before it inspects the account. The spec says a blank project is reported when the account is also blank, and a wrong status is reported before either.

**Alternatives considered**:

- Reporting the blank account first. A blank project would then be hidden whenever the account was also blank, which the spec forbids.
- New status sentences for the assistant. This action is still a change to an In Progress task, and the existing sentences already say what to do.

## 7. Approval and decline

**Decision**: Keep the existing approve and decline commands for the engineer. Add one refusal: if the body says the actor is `assistant`, the command writes nothing, the change stays as it was, and the engineer is told `The assistant cannot approve a change.` or `The assistant cannot decline a change.` A body that omits the actor is the engineer's command, as it is today. The assistant has no separate approve or decline command.

**Rationale**: The spec says the engineer approves in a separate action and the assistant must not approve or decline its own change. A silent ignore of `actor` would store an approval the assistant appeared to make.

**Alternatives considered**:

- Ignoring `actor` the way a client-supplied engineer name is ignored. The approval would succeed and would look like the assistant's approval if the client sent that field.
- A second approval that the assistant can complete. The spec forbids that.

## 8. Order and replay

**Decision**: Reuse the injected clock. Assistant changes and engineer changes stay in the one implementation-change list, ordered by `recorded_at` ascending, then `id` ascending. The same command script against the same task, with the same scripted clock and the same account, produces the same account, project, assistant name, outcome, and order. The script does not contain a model call.

**Rationale**: Principle V and spec SC-005. A tie on the clock still has one order because integer ids increase with insertion.

**Alternatives considered**:

- A second clock inside the new function. Two clocks would let one command store two unrelated times.
- Listing assistant changes ahead of engineer changes. The spec requires one oldest-first list.

## 9. Completion, checks, and decisions

**Decision**: Do not add a completion guard, a check command, or a decision command. A carried-out assistant change is an ordinary carried-out change, so feature 003 already refuses completion until it has a passing check. A waiting assistant change is Awaiting approval, so feature 002 already refuses completion and cancellation. Recording the assistant change does not verify a criterion, insert a check, insert a decision, or append a status change.

**Rationale**: The spec says the assistant does not take those actions, and completion of a carried-out assistant change still waits for a passing check. The existing guards already say that once the class and outcome are stored correctly.

**Alternatives considered**:

- A new completion sentence for assistant changes. The existing sentences already name the account of what changed.
- Letting the assistant record the passing check. The spec says the engineer chooses Passed or Failed.

## 10. Interface

**Decision**: Add one JSON command and one form on the existing task detail page. No new page and no new dependency. The page and the API call the same domain function. Binding stays `127.0.0.1`.

The command is `POST /api/tasks/{id}/assistant-changes` with the project, the class, the account, and an optional stop flag. The form is shown only when the task is In Progress. A Cancelled task shows any assistant fields already stored and does not offer the form. The process start option `--assistant` sets the name, default `Assistant`.

**Rationale**: The reader follows the change by opening the task. A new page would hide it from the record the spec already uses. One domain function keeps the page and the API from diverging.

**Alternatives considered**:

- HTML only. Harder to assert refusal messages and unchanged rows.
- A new frontend that edits the project. A second codebase, and a write the spec's replay rule does not allow inside this command.

## 11. Existing workspace files

**Decision**: Add `assistant_change` and `workspace_assistant` with `CREATE TABLE IF NOT EXISTS` in the existing schema script. That script already runs when a workspace file is opened, so an older file gains the tables. No change to task, criterion, decision, check, or implementation-change columns. Existing changes have no assistant row.

**Rationale**: Engineers may already have a workspace from earlier features. A new table does not rewrite their tasks, criteria, history, decisions, changes, or checks.

**Alternatives considered**:

- A second database file. The assistant change would no longer be in the task's workspace.
- Requiring the engineer to delete `workspace.db`. That throws away the history this product keeps.

## Resolved clarifications

The spec left no `[NEEDS CLARIFICATION]` markers. No Technical Context item remains open. The process, the stored account as the assistant's output, the assistant name, the link table, the separate command, the refusal order, approval, ordering, unchanged completion, the interface, and existing-file behavior are the decisions above.
