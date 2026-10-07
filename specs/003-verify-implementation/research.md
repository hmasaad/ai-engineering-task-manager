# Research: Verify a Recorded Change

## 1. Where the feature lives

**Decision**: Extend the existing local Python process. A new domain module owns recording a check and naming the carried-out changes that lack a passing check. The existing status module consults that module before completing, and does not consult it before cancelling. SQLite stores the new rows in the same workspace file. The existing task detail page and JSON API call the new function.

**Rationale**: The spec attaches checks to implementation changes that already exist, for one engineer and one workspace. A second process would split one task record across two writers. Principle VIII keeps this feature in the same reviewable process.

**Alternatives considered**:

- A new service that stores checks elsewhere. The reader would no longer see the check on the task record alone.
- Folding the rules into the feature 002 implementation module. The check has its own result and its own completion guard, and keeping it separate leaves the record, approve, and decline rules unchanged.

## 2. How a check is stored

**Decision**: One append-only table, `implementation_check`. Each insert stores the change, the criterion id, the criterion wording at that moment, the evidence, the result (`passed` or `failed`), the workspace engineer name, and the clock time. Many rows may name the same change. Nothing updates or deletes a row.

The result a reader sees is `Passed` or `Failed`. The stored codes are `passed` and `failed`, mapped at the boundary the same way feature 002 maps `ordinary` to the words the reader sees. The product does not infer the result from the evidence text.

**Rationale**: The spec forbids editing or removing a saved check, and it requires a later check to leave the earlier one in place. A new row is the later check. Copying the criterion wording keeps the record of what was checked after the live criterion text changes.

**Alternatives considered**:

- One row per change and criterion that is updated in place. That rewrites the saved check, which the spec forbids.
- A free-text "what was checked" field with no criterion id. The spec says what was checked is an acceptance criterion, and a result that does not name one is not stored.
- Storing a file, a diff, or a test-runner log. The spec says the engineer writes the evidence in their own words.

## 3. What counts as a passing check

**Decision**: The current result of one change and one criterion is the latest check of that pair (`checked_at`, then `id`). A change has a passing check only when at least one of its checks names a criterion that still exists on that task, and every such criterion has a current result of Passed. A current Failed result on any of those criteria means the change lacks a passing check, even if another criterion is currently Passed. A later Passed result for the failed pair makes that pair Passed. The earlier Failed row stays.

Checks whose criterion id no longer exists stay visible and are left out of this test. If that leaves the change with no check against a criterion that still exists, the change lacks a passing check.

**Rationale**: The 2026-10-07 clarification says every criterion already checked must have a current Passed result. Using the latest row per pair lets a later pass clear a failure without erasing history. Ignoring a deleted criterion keeps feature 001's removal of a non-last criterion working, because foreign keys are enabled and a hard reference would make that deletion fail.

**Alternatives considered**:

- One current Passed result is enough. The clarification rejected that. A current failure would no longer block completion.
- Only the single newest check on the change counts, across criteria. An older pass on another criterion would disappear from the gate as soon as a newer check was recorded.
- A foreign key from the check to the criterion with delete restricted. Removing a checked criterion would start failing with a storage error, and feature 001 allows that removal when the criterion is not the last one.
- Deleting checks when a criterion is removed. The spec forbids removing a saved check.

## 4. Who the record names, and when

**Decision**: Reuse the workspace engineer name. Recording a check copies that name and the clock time onto the new row. A name or a time in the request is ignored. Changing the configured name later does not rewrite older rows.

**Rationale**: The spec says only the workspace engineer may record a check, and the record must not name a different person. Copying the name at the command matches feature 001 verification and feature 002 changes.

**Alternatives considered**:

- A second checker. The spec has one engineer.
- Accepting an engineer name from the client. A client could then claim another actor.

## 5. Order and replay

**Decision**: Reuse the injected clock. Checks on a change are listed by `checked_at` ascending, then `id` ascending. The same command script against the same in-progress task, with the same scripted clock and no prior checks, produces the same results and the same order.

**Rationale**: Principle V and spec SC-005. A tie on the clock still has one order because integer ids increase with insertion.

**Alternatives considered**:

- A second clock inside the new module. Two clocks would let one command store two unrelated times.
- Sorting only by id. The spec requires the check time to be visible, and equal scripted times must still be stable.

## 6. Completion and cancellation

**Decision**: Keep the feature 001 and feature 002 guards. Add one completion guard: if any carried-out change on that task lacks a passing check, completion is refused, the task stays In Progress, and no status-change row is written. The refusal message includes `Needs a passing check: ` and each such account of what changed, oldest first, separated by commas. Existing sentences stay in this order when they also apply: unverified criteria, unfinished subtasks, awaiting approval, then this sentence. Cancellation does not gain this sentence. Not carried out changes do not block. A change that is Awaiting approval is not also listed here, because it is not carried out. Missing checks on a subtask are not listed on the parent.

When this is the only blocker, completion returns:

```text
Needs a passing check: {accounts}.
```

**Rationale**: The spec refuses completion while a carried-out change lacks a passing check, and it does not refuse cancellation for that reason. Naming the account of what changed is the required text. Keeping the existing sentences unchanged when every carried-out change has a passing check avoids a new failure in the feature 001 and feature 002 tests.

**Alternatives considered**:

- Blocking cancellation as well. The spec says cancellation does not require a passing check.
- A new task status such as Blocked. The spec keeps the five statuses and says recording a check must not change status.
- Treating the check as the criterion's Verified state. The spec says verifying a criterion remains a separate action.

## 7. Interface

**Decision**: Add one JSON command and show it on the existing task detail page when it is legal. No new page and no new dependency. The page and the API call the same domain function. Binding stays `127.0.0.1`.

The command is `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` with the criterion id, the evidence, and `Passed` or `Failed`. Task detail adds `checks` on each implementation change, oldest first, and a derived `passing_check` boolean.

**Rationale**: The reader checks the change by opening the task. A new page would hide the check from the record the spec already uses. One domain function keeps the page and the API from diverging.

**Alternatives considered**:

- HTML only. Harder to assert refusal messages and unchanged rows.
- A new frontend application. A second codebase for one form.

## 8. Existing workspace files

**Decision**: Add `implementation_check` with `CREATE TABLE IF NOT EXISTS` in the existing schema script. That script already runs when a workspace file is opened, so an older file gains the table. No change to task, criterion, or implementation-change columns. `criterion_id` is stored without a foreign key.

**Rationale**: Engineers may already have a workspace from feature 001 or 002. A new table does not rewrite their tasks, criteria, history, decisions, or changes. Omitting the foreign key lets a criterion row be removed without deleting or blocking the check that quoted it.

**Alternatives considered**:

- A second database file for checks. The check would no longer be in the task's workspace.
- Requiring the engineer to delete `workspace.db`. That throws away the history this product keeps.

## Resolved clarifications

The 2026-10-07 clarification is decided: every criterion already checked must have a current Passed result. No Technical Context item remains open. The process, storage shape, passing-check rule, naming, ordering, completion guard, interface, and existing-file behavior are the decisions above.
