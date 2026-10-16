# Research: Workflow Snapshots and Checkpointing

## Decision: A checkpoint is an immutable snapshot

**Rationale**: The engineer names the point they may want to resume from. The snapshot stores every current step and the state it had then. The same name returns that snapshot and does not replace it after later steps run. A second task can use the same name for its own snapshot. A blank name, a task with no steps, and a running step store nothing.

**Alternatives considered**: A new snapshot on every repeat of the name. Rejected because a double submit would replace the saved point. An automatic checkpoint after every step. Rejected because the engineer is the one who chooses the resume point.

## Decision: Restore rewinds only a failed step with no stored effect

**Rationale**: A completed step has already stored a file read or a folder change. Putting it back to Pending would run it again. A failed step with a stored change, such as a declined folder, also has an effect that must stay. Restore sets a failed step back to Pending only when the snapshot recorded it as Pending and the step has no stored effect. The file read, the span, and the outbox message stay. The task status stays In Progress.

**Alternatives considered**: Copying every snapshotted state back onto the steps. Rejected because that would make a completed step run again. Deleting the work that happened after the checkpoint. Rejected because those records are the evidence of what ran.

## Decision: A changed workflow cannot be restored

**Rationale**: A step added or removed after the checkpoint means the snapshot is no longer the current workflow. Restore is refused and the steps stay as they are. A checkpoint id that belongs to another task is refused as well.
