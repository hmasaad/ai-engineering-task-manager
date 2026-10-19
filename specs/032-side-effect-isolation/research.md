# Research: Deterministic Replay and Side-Effect Isolation

## Decision: Seal the effect in the same result as completion

**Rationale**: The step, its outbox message, and the file or folder it stored already commit together. The seal belongs in that same result. A failed step and a waiting step have not stored the effect yet, so they seal nothing. A rolled-back completion drops the seal. Completing the step again does not add a second seal.

**Alternatives considered**: Sealing when the engineer asks for a replay. Rejected because the project file may already have changed by then. Copying the file contents into the seal. Rejected because the file read is already stored, and the seal only needs to name the path so replay can avoid opening it.

## Decision: Replay reads the seals and does not open the project

**Rationale**: The existing execution replay matches stored file reads and folder changes. This replay matches the seals instead. Removing the file or the folder after the step completes does not change the report, and replay does not put either one back. A second call returns the same report and does not call the clock. The walk stops at the first step that is not completed, using the same stop sentences the engineer already sees for a step that has not run, is waiting, or has failed.

**Alternatives considered**: Replaying by opening the project and comparing it with the seal. Rejected because that performs the side effect again. Replacing the existing execution replay. Rejected because that replay stays the check against the stored file read and the folder change.

## Decision: One new table

**Rationale**: An existing workspace file is not altered. `workflow_isolated_effect` stores one seal per completed step.
