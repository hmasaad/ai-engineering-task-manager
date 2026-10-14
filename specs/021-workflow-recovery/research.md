# Research: Workflow Recovery and Replay

## Decision: Record the start in its own committed transaction

**Rationale**: An advance that records the start and the result in one transaction cannot leave a running step. The start commits first. The result commits second. A stop between them leaves the step running, which is what recovery reads.

**Alternatives considered**: One transaction for the whole advance. Rejected because a running step would never remain stored.

## Decision: The baseline of an attempt is a separate row

**Rationale**: `workflow_step` already exists, and a new column would not appear in a workspace that already created that table. `workflow_attempt` stores how many file reads, or the highest change id, existed before the attempt. Recovery compares the current records with that number.

**Alternatives considered**: A new column on `workflow_step`. Rejected because existing workspace files would keep the old table.

## Decision: Recovery does not call the action when the effect is present

**Rationale**: A file read counted past the baseline marks the step completed. A change id above the baseline is settled with the same completed, waiting, or failed outcome the advance already uses. The action is not called.

**Alternatives considered**: Running the action again and ignoring a duplicate. Rejected because a second read or a second folder change would be a second effect.

## Decision: A missing baseline is an interruption

**Rationale**: Recovery does not guess. With no attempt row, the step is marked failed with `the step was interrupted.` and the action is not called.

**Alternatives considered**: Treating a missing baseline as zero. Rejected because an older file read could be mistaken for this attempt.

## Decision: Replay is the event list

**Rationale**: Each start and each result is one `workflow_event`. Reading them does not use the clock and does not write. An advance that leaves a waiting step waiting does not add an event.

**Alternatives considered**: Rebuilding the replay by running the steps. Rejected because a replay must not perform a step.
