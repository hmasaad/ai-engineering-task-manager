# Research: Workflow Versioning and Migration

## Decision: A version is a new row, not a new column

**Rationale**: The workspace file already has `workflow_step`. Opening the workspace applies `CREATE TABLE IF NOT EXISTS` and does not alter an existing table. A new `workflow_version` row points at the steps that belong to that version. A workflow saved before this feature has no version row. Opening it still shows version 1, and the first revise stores that version. Reading the task does not write.

**Alternatives considered**: Adding a version column to `workflow_step`. Rejected because an existing workspace file would keep the old table.

## Decision: The draft shares the step that already ran

**Rationale**: The completed, waiting, or failed step stays one row. The draft points at that same row. Advance of the new version sees the stored state and does not perform it again. A pending step is not copied, so the new version does not point at it. The old row remains on the superseded version.

**Alternatives considered**: Copying the step into a new row. Rejected because a second row could store a second effect. Deleting the pending step. Rejected because the superseded version is the record of what was planned.

## Decision: Migration is one explicit write

**Rationale**: The engineer types a reason. The draft becomes current, the previous version becomes superseded, and one migration row stores the reason and the time. The task status stays as it is. No step is performed. The replay is not changed. A waiting step stays waiting.

**Alternatives considered**: Migrating on the next advance. Rejected because the spec requires the engineer to name the reason first. Treating migration as approval. Rejected because approval stays on the waiting change.

## Decision: Advance reads the current version only

**Rationale**: Until migration, the draft is not the current version, so advance still performs the current version. After migration, a pending step that only the superseded version points at is not selected.

**Alternatives considered**: Hiding advance while a draft exists. Rejected because the spec says advance keeps using the current version until migration.
