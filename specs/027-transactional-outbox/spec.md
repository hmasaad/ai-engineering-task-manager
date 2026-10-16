# Feature Specification: Transactional Outbox and Inbox

**Feature Branch**: `027-transactional-outbox`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Transactional Outbox and Inbox Patterns."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A completed step stores one outbox message (Priority: P1)

When a workflow step becomes Completed, the same result stores one outbox message for that step. The message names the step and the file or folder that step stored. The message is Pending. A step that fails, or a step that is still waiting, stores no message. If that completion is rolled back, the message is not kept. Completing the step again does not store a second message.

**Why this priority**: A message that is stored apart from the step result can be lost, or it can be kept after the result was discarded.

**Independent Test**: Advance "Read the note" for a file that exists. The task shows one Pending outbox message for `note.txt`. A missing file leaves the step Failed and stores no message.

**Acceptance Scenarios**:

1. **Given** "Read the note" completes, **When** the engineer opens the task, **Then** one Pending outbox message names that step and `note.txt`.
2. **Given** "Read the note" fails because the file is missing, **When** the engineer opens the task, **Then** the outbox has no message.
3. **Given** a completion that is rolled back, **When** the engineer opens the task, **Then** the step is unchanged and the outbox has no message.
4. **Given** one completed step, **When** that completion is recorded again, **Then** the outbox still has one message.

---

### User Story 2 - A named delivery is accepted once (Priority: P2)

The engineer delivers the oldest Pending message by naming the delivery. That message becomes Delivered, and the inbox records the name. The same name again does not deliver another message. A different name delivers the next Pending message. A blank name is refused with `Name this delivery.` No Pending message is refused with `There is no outbox message to deliver.` Delivery does not read a file, does not create a folder, and does not change the task status.

**Why this priority**: The outbox is useful only when each delivery is accepted once.

**Independent Test**: Complete two reads. Deliver with the name `once`. The first message is Delivered and the second stays Pending. Deliver `once` again. The second message stays Pending. Deliver with `next`. The second message is Delivered. Each file was read only once.

**Acceptance Scenarios**:

1. **Given** two Pending messages, **When** the engineer delivers `once`, **Then** the older message is Delivered, the newer one stays Pending, and the inbox records `once`.
2. **Given** that delivery, **When** the engineer delivers `once` again, **Then** no other message is delivered and the inbox still has one `once`.
3. **Given** a blank name, **When** the engineer delivers, **Then** every message stays as it was and the engineer is told `Name this delivery.`
4. **Given** no Pending message, **When** the engineer delivers a new name, **Then** the engineer is told `There is no outbox message to deliver.`
5. **Given** the same name on another task, **When** the engineer delivers it there, **Then** that task can deliver its own oldest Pending message.

---

### User Story 3 - The task shows the outbox and the inbox (Priority: P3)

The task shows each outbox message and each inbox name. When a message is Pending and the task is In Progress, the engineer can enter a delivery name and press Deliver outbox. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see which message is waiting and which delivery was accepted.

**Independent Test**: Complete one read and open the task. The page shows the Pending message and Deliver outbox. After delivering `once`, the message is Delivered and the inbox shows `once`.

**Acceptance Scenarios**:

1. **Given** no completed step, **When** the engineer opens the task, **Then** the outbox says `No outbox messages yet.`
2. **Given** a Pending message, **When** the engineer opens the task, **Then** the page shows that message and Deliver outbox.
3. **Given** a delivery named `once`, **When** the engineer returns to the task, **Then** the message is Delivered and the inbox shows `once`.

### Edge Cases

- A waiting step stores no outbox message. Approving it does not by itself store one. The message is stored when the step becomes Completed.
- Delivery does not approve a change and does not advance the workflow.
- One request stores one completion or delivers one message.
- The same delivery name on another task is a separate inbox entry.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A step that becomes Completed MUST store one outbox message in that same result. The message MUST name the step and its stored file or folder and MUST start Pending. A failed step, a waiting step, and a rolled-back completion MUST NOT leave a message. A second completion of that step MUST NOT store another message.
- **FR-002**: Delivering a name MUST mark the oldest Pending message Delivered and record that name in the inbox. The same name MUST NOT deliver another message. A blank name MUST be refused with `Name this delivery.` When no message is Pending, a new name MUST be refused with `There is no outbox message to deliver.`
- **FR-003**: Delivery MUST NOT read a file, create a folder, approve a change, advance the workflow, or change the task status. The same name on another task MUST be able to deliver that task's own oldest Pending message.
- **FR-004**: The task page MUST show the outbox and the inbox. An empty outbox MUST say `No outbox messages yet.` A Pending message on an In Progress task MUST offer Deliver outbox.

### Key Entities

- **Outbox message**: One stored notice for one completed step. It is Pending until a delivery accepts it, then Delivered.
- **Inbox entry**: The delivery name that accepted one outbox message. A name is recorded once for a task.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of completed steps, 100% have one outbox message, and 100% of failed or rolled-back steps have none.
- **SC-002**: In a review of repeated deliveries of the same name, 100% leave every other message Pending.
- **SC-003**: An engineer can see the Pending message and the accepted delivery name on the task in one view.

## Assumptions

- Specifications 001 through 026 are not rewritten. Advance, recovery, exactly-once effects, and replay stay as they are.
- The outbox records a step that has already completed. Delivery does not perform that step.
- The rules are covered by automated checks.
