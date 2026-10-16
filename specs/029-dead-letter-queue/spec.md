# Feature Specification: Dead Letter Queues and Poison Messages

**Feature Branch**: `029-dead-letter-queue`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Dead Letter Queues and Poison Messages."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The third rejection dead-letters the oldest message (Priority: P1)

The engineer rejects the oldest Pending outbox message by naming the rejection and why the message is poison. The first and second rejection leave that message Pending. The third rejection of that same message makes it a dead letter and keeps the latest reason. A dead letter is not delivered. The next Pending message can then be delivered or rejected on its own. Rejecting does not read a file, does not create a folder, and does not change the task status.

**Why this priority**: A message that keeps failing must leave the queue, or every later message stays stuck behind it.

**Independent Test**: Complete "Read the note" and "Read the extra". Reject the note three times, with three different names and the reason `The reader stopped.` The note is a dead letter. Deliver `ship`. The extra is Delivered and the note stays a dead letter. Each file was read only once.

**Acceptance Scenarios**:

1. **Given** two Pending messages, **When** the engineer rejects the oldest one once, **Then** that message stays Pending and the newer one is not rejected.
2. **Given** two rejections of the oldest message, **When** the engineer rejects it a third time, **Then** that message is a dead letter with the latest reason and the newer message stays Pending.
3. **Given** that dead letter, **When** the engineer delivers a new name, **Then** the newer message is Delivered and the dead letter stays.
4. **Given** one rejection of a message, **When** the engineer delivers that message, **Then** it becomes Delivered and the rejection remains on record.

---

### User Story 2 - A rejection is counted once (Priority: P2)

The same rejection name does not count a second time. A blank name is refused with `Name this rejection.` A blank reason is refused with `Name why this message is poison.` When no Pending message remains, a new name is refused with `There is no outbox message to reject.` A rejection that is rolled back leaves no poison record and no dead letter. The same name on another task can reject that task's own oldest Pending message.

**Why this priority**: A repeated name, or a rejection that was discarded, must not push a message into the dead letter by accident.

**Independent Test**: Reject `once` with `The reader stopped.` Reject `once` again. The message still has one rejection. Reject with a blank reason. Nothing new is recorded, and the engineer is told `Name why this message is poison.`

**Acceptance Scenarios**:

1. **Given** a rejection named `once`, **When** the engineer rejects `once` again, **Then** the message still has one rejection.
2. **Given** a blank name, **When** the engineer rejects, **Then** nothing is recorded and the engineer is told `Name this rejection.`
3. **Given** a blank reason, **When** the engineer rejects, **Then** nothing is recorded and the engineer is told `Name why this message is poison.`
4. **Given** no Pending message, **When** the engineer rejects a new name, **Then** the engineer is told `There is no outbox message to reject.`
5. **Given** a rejection that is rolled back, **When** the engineer opens the task, **Then** that rejection and any dead letter from it are gone.
6. **Given** the same name on another task, **When** the engineer rejects it there, **Then** that task rejects its own oldest Pending message.

---

### User Story 3 - The task shows poison messages and dead letters (Priority: P3)

The task shows each rejection and each dead letter. When a message is still Pending and the task is In Progress, the engineer can name the rejection, name why it is poison, and press Reject message. A dead letter shows the message and its reason. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see which message was set aside and which rejections are still short of the third.

**Independent Test**: Complete one read. The page offers Reject message. After three rejections, the page shows the dead letter and does not offer delivery of that message.

**Acceptance Scenarios**:

1. **Given** a Pending message, **When** the engineer opens the task, **Then** the page offers Reject message.
2. **Given** one rejection, **When** the engineer returns to the task, **Then** the page shows that rejection and the message is still Pending.
3. **Given** a dead letter, **When** the engineer returns to the task, **Then** the page shows that message as a dead letter with its reason.

### Edge Cases

- A dead letter is not deleted. The original outbox message stays on the task.
- One request records one rejection or, on the third rejection, one dead letter.
- Delivery of a name still delivers the oldest message that is Pending and not a dead letter.
- Rejecting does not approve a change and does not advance the workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Rejecting a name and a reason MUST record one poison rejection of the oldest Pending message that is not already a dead letter. The first and second rejection MUST leave that message Pending. The third rejection of that message MUST make it a dead letter and keep the latest reason. A different message MUST start its own count.
- **FR-002**: The same rejection name MUST NOT count again. A blank name MUST be refused with `Name this rejection.` A blank reason MUST be refused with `Name why this message is poison.` When no Pending message remains, a new name MUST be refused with `There is no outbox message to reject.` A rolled-back rejection MUST leave no poison record and no dead letter.
- **FR-003**: A dead letter MUST NOT be delivered. Delivery MUST continue with the next Pending message. Rejection MUST NOT read a file, create a folder, approve a change, advance the workflow, or change the task status. The same name on another task MUST be able to reject that task's own oldest Pending message.
- **FR-004**: The task page MUST show the rejections and the dead letters. A Pending message on an In Progress task MUST offer Reject message. The task list MUST stay the list of tasks.

### Key Entities

- **Poison rejection**: One named reason that a Pending message could not be accepted. Three rejections of the same message make a dead letter.
- **Dead letter**: A message set aside with the reason from its third rejection. It stays on the task and is not delivered.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of rejections, 100% of third rejections set aside the oldest Pending message and leave the newer one available.
- **SC-002**: In a review of repeated names and rolled-back rejections, 100% leave the poison count unchanged.
- **SC-003**: An engineer can see the dead letter and its reason on the task in one view.

## Assumptions

- Specifications 001 through 028 are not rewritten. Delivery still accepts the oldest Pending message that is not a dead letter.
- Three rejections of the same message are enough to set it aside. The count is not configurable.
- One or two rejections do not stop a later delivery of that same message.
- The rules are covered by automated checks.
