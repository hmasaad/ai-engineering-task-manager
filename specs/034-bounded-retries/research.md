# Research: Bounded Delivery Retries

## Decision: Count unsuccessful deliveries in a new table

**Rationale**: A successful delivery still marks the message Delivered. An unsuccessful delivery is a different record: the name, the message, and the next time. The count is how many of those records belong to the message. The same trimmed name on the same task does not add a second record. The same name on another task does. A blank name, a task that is not In Progress, and a time that has not arrived do not add a record.

**Alternatives considered**: Changing `workflow_outbox.state` to include a retry state. Rejected because an existing workspace file cannot change that check. Counting poison rejections as retries. Rejected because a poison rejection already has its own rule.

## Decision: Wait one minute, and stop at three

**Rationale**: The next time is one minute after the workspace time of the accepted attempt. Before that time, Deliver outbox and another unsuccessful delivery return `This delivery is not due yet.` and save no name. The third accepted attempt writes one row in the existing dead-letter table with the reason `The delivery was attempted too many times.` The outbox row stays Pending and is shown as Dead by the rule that already looks for a dead letter. A later delivery skips that message. A rolled-back third attempt leaves the count at 2 and leaves no dead letter.

**Alternatives considered**: Delivering again on each attempt until the bound. Rejected because the message would already be Delivered after the first success. Replaying the dead letter in this feature. Rejected because that is a later feature.

## Decision: One new table

**Rationale**: `workflow_delivery_retry` stores one row per accepted unsuccessful delivery. No column is added to an existing table.
