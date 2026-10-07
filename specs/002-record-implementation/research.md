# Research: Record Task Implementation

## 1. Where the feature lives

**Decision**: Extend the existing local Python process from feature 001. A new domain module owns record, approve, and mark-not-carried-out. The existing status module consults that module before completing or cancelling. SQLite stores the new rows in the same workspace file. The existing task detail page and JSON API call the new functions.

**Rationale**: The spec attaches changes to tasks that already exist, for one engineer and one workspace. A second process would split one status machine across two writers. Principle VIII keeps this feature in the same reviewable process.

**Alternatives considered**:

- A new service that stores changes elsewhere. The reader would no longer see the change on the task record alone.
- A command-line-only addition. The success criteria are about opening the task and reading the change there.

## 2. How a change and its outcome are stored

**Decision**: Two append-only tables. `implementation_change` is inserted once and never updated: the task, the account of what changed, the class (`ordinary` or `consequential`), the workspace engineer name, and the clock time. `implementation_resolution` has at most one row per change, also insert-only: either an approval (evidence, engineer, time) or a decision not to carry it out (reason, engineer, time).

The outcome a reader sees is defined from those rows, the same way Verified is defined from the four verification fields:

| Class | Resolution row | Outcome |
|---|---|---|
| ordinary | none | Carried out |
| consequential | none | Awaiting approval |
| consequential | approval | Carried out |
| consequential | not carried out | Not carried out |

An ordinary change never receives a resolution row. A change never receives a second resolution. Nothing deletes either table.

**Rationale**: The spec forbids editing or removing a saved change or a saved approval, and it also requires the outcome to move from Awaiting approval to Carried out or Not carried out. A later row records that move without rewriting what changed. The class is the engineer's declaration, so the outcome is not inferred from the wording. Principle III is met because both the class and the resolution are stored.

**Alternatives considered**:

- An outcome column that is updated in place. That rewrites the saved change, which the spec forbids, and can leave the column stale if a second fact is also stored.
- Deriving consequential from phrases in the text. The spec says the product must not do that.
- Storing a diff, a file list, or a review link. The spec says the engineer writes what changed in their own words.

## 3. Who the record names, and when

**Decision**: Reuse the workspace engineer name from feature 001. Recording a change copies that name onto the change. Approving or marking it not carried out copies the name onto the resolution at that later time. A name in the request body is ignored. Changing the configured name later does not rewrite older rows. The clock time of each command is stored on that command's row. The client does not send the time.

**Rationale**: The spec says only the workspace engineer may record, approve, or decline, and the record must not name a different person. Copying the name at the moment of the command matches verification in feature 001.

**Alternatives considered**:

- A second approver. The spec has one engineer and says that same engineer approves in a later action.
- Accepting an engineer name from the client. A client could then claim another actor.

## 4. Order and replay

**Decision**: Reuse the injected clock from feature 001. Changes on a task are listed by `recorded_at` ascending, then `id` ascending. The same command script against the same in-progress task, with the same scripted clock and no prior implementation rows, produces the same outcomes and the same order.

**Rationale**: Principle V and spec SC-005. A tie on the clock still has one order because integer ids increase with insertion.

**Alternatives considered**:

- A second clock inside the new module. Two clocks would let one command store two unrelated times.
- Sorting only by id. The spec requires the recorded time to be visible, and equal scripted times must still be stable.

## 5. Completion and cancellation

**Decision**: Keep the feature 001 guards. Add one more: if any change on that task has outcome Awaiting approval, completion and cancellation are refused, the task stays In Progress, and no status-change row is written. The refusal message includes `Awaiting approval: ` and each waiting account of what changed, oldest first, separated by commas. Existing phrases for unverified criteria and unfinished subtasks stay in the same message when those also apply. Carried out and Not carried out changes do not block. Waiting changes on a subtask are not listed on the parent; the subtask's own In Progress status already blocks the parent.

Messages when these are the only blockers:

- Completion: `Awaiting approval: {accounts}.`
- Cancellation: `Awaiting approval: {accounts}.`

When a subtask also blocks cancellation, the existing sentence remains first: `Subtasks must be finished or cancelled first: {names}. Awaiting approval: {accounts}.`

**Rationale**: The 2026-10-07 clarification says the task cannot be completed or cancelled until every waiting change is approved or marked not carried out. Naming the account of what changed is the spec's required text. Keeping the existing sentences unchanged when no change is waiting avoids a new failure in feature 001 tests.

**Alternatives considered**:

- A new task status such as Blocked. The spec keeps the five statuses and says these commands must not change status by themselves.
- Automatically marking waiting changes not carried out on complete or cancel. The spec requires an explicit action with a reason.
- Freezing waiting changes on a Completed task so they can never be approved. That leaves an unresolved consequential action on a finished task, which the clarification rejected.

## 6. Interface

**Decision**: Add three JSON commands and show them on the existing task detail page when they are legal. No new page and no new dependency. FastAPI, Jinja2, and the test client stay as they are. The page and the API call the same domain functions. Binding stays `127.0.0.1`.

**Rationale**: The reader checks the change by opening the task. A new page would hide it from the record the spec already uses. One domain function per command keeps the page and the API from diverging.

**Alternatives considered**:

- HTML only. Harder to assert refusal messages and unchanged rows.
- A new frontend application. A second codebase for three forms.

## 7. Existing workspace files

**Decision**: Add the two tables with `CREATE TABLE IF NOT EXISTS` in the existing schema script. That script already runs when a workspace file is opened, so an older file gains the tables. No task column changes.

**Rationale**: Engineers may already have a workspace from feature 001. New tables do not rewrite their tasks, criteria, history, or decisions.

**Alternatives considered**:

- A second database file for changes. The change would no longer be in the task's workspace.
- Requiring the engineer to delete `workspace.db`. That throws away the history this product keeps.

## Resolved clarifications

No Technical Context item remains open. The process, storage shape, naming, ordering, completion guard, interface, and existing-file behavior are the decisions above.
