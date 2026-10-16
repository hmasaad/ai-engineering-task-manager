# Research: Dead Letter Queues and Poison Messages

## Decision: Three named rejections make one dead letter

**Rationale**: The outbox has no separate consumer that fails on its own. The engineer rejects the oldest Pending message and names why. The first and second rejection leave the message Pending, so it can still be delivered. The third rejection of that same message sets it aside. A newer message keeps its own count.

**Alternatives considered**: Moving the message aside on the first rejection. Rejected because one failure is not yet poison, and the message can still be delivered. An automatic retry loop. Rejected because nothing in this workspace delivers a message except the named delivery the engineer already has.

## Decision: A dead letter is a separate record

**Rationale**: The outbox message already has a stored state of Pending or Delivered. Existing workspace files keep that check. A dead letter is a new row for that message. Delivery and the next rejection skip any message that has a dead letter. The outbox row stays, so the original notice is not lost. The dead letter keeps the reason from the third rejection.

**Alternatives considered**: Adding Dead to the outbox state check. Rejected because a workspace file that already has the table would not accept the new state. Deleting the outbox row. Rejected because the original message is the evidence of what the step stored.

## Decision: A rejection name is accepted once per task

**Rationale**: The inbox already accepts a delivery name once. A rejection name works the same way. Repeating it does not add another poison count and does not create a dead letter. A blank name and a blank reason are refused before any row is stored. A refusal rolls the rejection back, including a dead letter that was stored in that same result. The same name on another task is a different rejection.

**Alternatives considered**: Counting every repeat of the same name. Rejected because a double submit would dead-letter a message that was rejected only once on purpose.
