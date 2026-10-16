# Research: Transactional Outbox and Inbox

## Decision: The message is written with the completion

**Rationale**: A Refusal rolls back the transaction that produced it. Inserting the outbox row in the same transaction as the step becoming Completed means a rolled-back completion does not leave a message, and a committed completion does not lose one. A second completion of that step finds the existing row and does not insert another.

**Alternatives considered**: Writing the message after the transaction commits. Rejected because a crash between the two writes would keep the step and lose the message. Writing it before the step is Completed. Rejected because a failed or waiting step would have a message for work that has not finished.

## Decision: Delivery accepts one oldest Pending message

**Rationale**: The engineer types a delivery name. The oldest Pending message for that task becomes Delivered, and the inbox records the name with that message. The same name later finds the inbox row and does not mark another message. A different name takes the next oldest Pending message. Delivery does not read a file or create a folder.

**Alternatives considered**: Delivering every Pending message under one name. Rejected because one request should accept one message. Using the name as a global key across tasks. Rejected because the spec says the same name on another task can deliver that task's own message.

## Decision: A waiting step has no message yet

**Rationale**: The folder change is waiting for approval. The step is not Completed, so there is no outbox message. Approval does not complete the step. The existing next advance completes it without performing it again, and that completion stores the one message.

**Alternatives considered**: Storing the message when the change starts waiting. Rejected because delivery would then refer to a change the engineer has not accepted.

## Decision: No column is added to the step

**Rationale**: An existing workspace file is opened with `CREATE TABLE IF NOT EXISTS` and is not altered. The outbox and inbox are new tables. A step that completed before this feature has no message until a later completion inserts one. Opening the task does not invent a message.
