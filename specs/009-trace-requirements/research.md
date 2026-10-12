# Research: Trace Requirements

## 1. Where a requirement lives

**Decision**: Store requirements in the same SQLite workspace. Add new tables only. Do not alter `task`, `acceptance_criterion`, `implementation_check`, or `implementation_change`. Do not read specification documents. The identifier the engineer sees is `REQ-` plus the numeric id assigned at insert. It is not a second stored code.

**Rationale**: The workspace is already the record a later reader opens. A derived identifier cannot drift from the row, and an unused id is not reused because requirements are not deleted. New tables match the rule that existing databases are opened with `CREATE TABLE IF NOT EXISTS`.

**Alternatives considered**:

- Parsing `specs/*/spec.md` for requirement text. That couples the workspace to files that are not the engineer's task record, and it would rewrite the meaning of Draft specifications.
- Treating an acceptance criterion as the requirement. A criterion has no kind, no stable public identifier, and its text edit already means something else.

## 2. What a run is

**Decision**: A verification run is a row the engineer records: one still-named check, Passed or Failed, a run identifier, the workspace engineer, and the clock time. The product does not start a test process. A client-supplied engineer name or time is ignored. The current result is the latest run for that check by `recorded_at`, then by id. A check with no run has no current pass.

**Rationale**: Principle V asks for a recorded non-deterministic boundary. The boundary is the result the engineer reports from a check that ran outside this product. Executing the check would be a new class of action.

**Alternatives considered**:

- Running pytest inside the task manager. That can change the project and is outside this feature.
- Reusing a feature 003 check. That check judges one carried-out change against one criterion and has no run identifier.

## 3. How a named check is removed

**Decision**: Removal sets a retired time on the check row. The row and its runs stay. Retired checks do not count as named, do not supply the current result, and do not block verification or completion. The same name may be added again as a new row with no runs. A partial unique index keeps the name unique among checks that are not retired. Removing an unknown or already retired check is `Check not found.`

**Rationale**: The spec says earlier runs stay readable and the removed check no longer blocks. Deleting the row would either delete the runs or leave them pointing at nothing. A new row for the same name keeps the old runs from becoming the new check's result.

**Alternatives considered**:

- Hard-deleting the check and keeping runs with no check. A later reader could not tell which name those runs belonged to.
- Refusing removal. A typo would block every linked task until a pass was recorded under the wrong name.

## 4. When verification and completion are refused

**Decision**: The existing verify preconditions run first. Only then, if any requirement linked to that criterion has a still-named check whose current result is not Passed, refuse with `A required check has not passed.` and write no verification. Completion keeps its current sentence order and appends `A required check has not passed: REQ-1, REQ-2.` for requirements linked to that task whose still-named checks are not all currently Passed. Identifiers are sorted by numeric id. A requirement with no still-named check does not add that sentence. A task with no linked requirement keeps the existing completion message exactly.

**Rationale**: A blank observation must still be refused with the existing sentence. The new hold applies only where a named check exists, which is the clarified rule. Appending the sentence leaves features 001 through 003 unchanged for unlinked tasks.

**Alternatives considered**:

- Blocking completion when a linked requirement has no named check. The spec puts that case on the gap list and does not treat it as a failed check.
- Putting the new sentence ahead of unverified criteria. That would change the existing combined refusal.

## 5. What a requirement change does to a Completed task

**Decision**: Trim the statement. A blank result is `A requirement statement is required.` and the row is unchanged. The kind must be `functional` or `non-functional`. If the trimmed statement and the kind both match the stored row, save nothing: no criterion changes, no status change, and no history row. Otherwise update the row, clear verification on each linked criterion that was Verified, and reuse the existing leave-completed path with cause code `requirement_changed` and the requirement id as the detail. Ancestors that are Completed follow that same path. Runs are not rewritten. Criteria that are not linked stay as they are.

**Rationale**: This is the same durable effect as editing the text of a Verified criterion, and the engineer is the person submitting it. An unchanged save is not a cause. Specification 001 is not edited; the new cause is recorded here.

**Alternatives considered**:

- A second approval before the criterion becomes Unverified. The engineer is already the actor, as with a criterion text edit.
- Leaving a Completed task Completed after its criterion becomes Unverified. That would break the existing rule that a Completed task's criteria are Verified.

## 6. How links behave

**Decision**: Linking a task that is already linked is a success and writes no second row. Linking a criterion requires the requirement to already be linked to that criterion's task; otherwise the refusal is `The criterion must be on that task.` The same refusal is used when the criterion belongs to another task. A duplicate criterion link is `That criterion is already linked to this requirement.` Removing a criterion deletes its link through a foreign key that cascades, and leaves the task link and the runs in place. Unlinking does not change a criterion's Verified state. An unknown task is `Task not found.` An unknown criterion is `Criterion not found.`

**Rationale**: The gap list can show a task with no criterion. A criterion link without a task link would make that list and the completion rule disagree. Cascade keeps a deleted criterion from leaving a dangling link without altering the criterion table's own definition.

**Alternatives considered**:

- Linking a criterion also inserts the task link. The spec allows a task link with no criterion, and the two actions stay separate.
- Leaving the criterion link in application code only. A missed call in the existing delete path would keep a link to a criterion that is gone.
