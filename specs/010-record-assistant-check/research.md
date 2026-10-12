# Research: Record One Check by the Assistant

## Decision: Store the assistant on a new row, not a new column

**Decision**: Add `assistant_check` with `check_id` as its primary key, referencing `implementation_check(id)`, and `assistant_name` copied from the workspace assistant. Do not alter `implementation_check`.

**Rationale**: The workspace applies `schema.sql` with `CREATE TABLE IF NOT EXISTS`. A new column on an existing table would not appear in a workspace that already has `implementation_check`. A separate row can be created on every open. An engineer-recorded check simply has no row, so older checks do not gain an assistant.

**Alternatives considered**: Adding `assistant_name` to `implementation_check` was rejected because existing workspace files would keep the old table shape. A second check table that copies the evidence and the result was rejected because the passing-check rule already reads `implementation_check`, and a copy could disagree with it.

## Decision: Reuse the existing check guards and insert

**Decision**: The assistant command runs the same refusal order as the engineer's check, then inserts one `implementation_check` row and one `assistant_check` row in the same command. `POST /api/tasks/{id}/implementation-changes/{change_id}/checks` stays the engineer command and writes no `assistant_check` row.

**Rationale**: The spec reuses those messages and that order. One insert path keeps the current result, the criterion wording, and the passing-check rule unchanged. The engineer command must keep writing checks that do not name an assistant.

**Alternatives considered**: Teaching the existing check command to accept an actor was rejected because a client could then label the engineer's check as the assistant's. A flag on that command was rejected for the same reason.

## Decision: The check counts immediately

**Decision**: An assistant check is a normal check. The current result of a change and a criterion stays the latest check by `checked_at`, then `id`. Completion keeps its existing sentences. There is no approval step and no new completion sentence.

**Rationale**: The spec says a later check can replace the current result while the earlier check stays, and verifying, deciding, approving, completing, and cancelling remain the engineer's actions. The passing-check function already ignores who recorded the check.

**Alternatives considered**: Holding the assistant check until the engineer accepts it was rejected because the spec does not add that wait, and the check does not delete or overwrite durable data.

## Decision: Show both names only when the assistant recorded the check

**Decision**: Every check payload gains `assistant_name`. It is null when no `assistant_check` row exists. When a row exists, the task shows the assistant, and the line still names the workspace engineer. A decision that rests on the check uses the same `assistant_name`.

**Rationale**: The reader must be able to see that the assistant recorded the check. The spec also says every check names the workspace engineer. Engineer-recorded checks stay on the line they have today.

**Alternatives considered**: Replacing `engineer_name` with the assistant was rejected because the spec says the check still names the workspace engineer. Omitting the assistant from the decision's check object was rejected because a later reader of that decision would lose who recorded the evidence.

## Decision: Do not call a model, open a file, or record a requirement run

**Decision**: The command reads the task, the change, and the criterion already stored in the workspace. It copies `assistant_name` and `engineer_name` from the workspace and the time from the workspace clock. It does not call the configured model, resolve a project path, or insert a requirement run.

**Rationale**: The engineer submits the evidence and the result the assistant already produced. Specification 009 runs stay a separate record. This command must not satisfy or clear a required requirement check.

**Alternatives considered**: Calling the model to judge the change was rejected because this class stores a submitted result, and the model call already has its own feature. Treating the check as a requirement run was rejected because that would mix two records the spec keeps apart.
