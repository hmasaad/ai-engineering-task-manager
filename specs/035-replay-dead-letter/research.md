# Research: Replay a Dead Letter

## Decision: Record the replay without deleting the dead letter

**Rationale**: The dead letter is the reason the message was set aside. Replay returns the message to delivery by recording a name for that dead letter. The outbox row stays Pending. It is shown as Pending again because a replay exists. The dead letter remains visible. The same trimmed name on the same task does not record a second replay. A different name returns the next dead letter that has no replay. The same name on another task is a different replay.

**Alternatives considered**: Deleting the dead letter. Rejected because the reason would disappear. Changing the outbox state. Rejected because an existing workspace cannot change that check.

## Decision: A replayed message can be delivered immediately

**Rationale**: The engineer asked for the message back. A delivery after the replay accepts it, even when an earlier next time has not arrived. Replay does not add an attempt and does not clear the attempt count, so it does not start another round of three. A rolled-back replay stores nothing, the message stays Dead, and delivery still skips it.

**Alternatives considered**: Waiting out the old next time after a replay. Rejected because the engineer would not yet be able to deliver the message they just returned. Resetting the attempt count. Rejected because that would start a new round by itself.

## Decision: One new table

**Rationale**: `workflow_dead_letter_replay` stores one row per accepted replay. No column is added to an existing table.
