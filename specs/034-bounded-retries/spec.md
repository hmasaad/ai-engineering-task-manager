# Feature Specification: Bounded Delivery Retries

**Feature Branch**: `034-bounded-retries`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Start bounded retries. A pending outbox message records how many deliveries were attempted and the next time a delivery is allowed. A delivery before that time does not deliver and does not add an attempt. The attempt that reaches the bound writes the existing dead letter. The outbox message stays Pending."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An unsuccessful delivery waits one minute (Priority: P1)

The engineer names an unsuccessful delivery of the oldest Pending message. That records one attempt and a next time one minute later. The message stays Pending and is not delivered. The same name again does not record another attempt. Before that next time, Deliver outbox does not deliver the message, does not add an attempt, and tells the engineer `This delivery is not due yet.` That early delivery name is not saved. When the next time has arrived, Deliver outbox delivers the message as it does today. A blank attempt name is refused with `Name this attempt.` No Pending message is refused with `There is no outbox message to retry.` The task status stays as it was.

**Why this priority**: A delivery that failed must not be tried again immediately, and it must not be counted twice.

**Independent Test**: Complete "Read the note". Record the unsuccessful delivery "once". The message stays Pending, the attempt count is 1, and a delivery is refused with `This delivery is not due yet.` After one minute, deliver "ship". The message is Delivered and the attempt count is still 1.

**Acceptance Scenarios**:

1. **Given** one Pending message, **When** the engineer records the unsuccessful delivery "once", **Then** the attempt count is 1, the next time is one minute later, and the message stays Pending.
2. **Given** that attempt, **When** the engineer records "once" again, **Then** the attempt count stays 1.
3. **Given** that attempt, **When** the engineer delivers before the next time, **Then** the message stays Pending, the attempt count stays 1, and the engineer is told `This delivery is not due yet.`
4. **Given** the next time has arrived, **When** the engineer delivers "ship", **Then** the message is Delivered and the attempt count stays 1.
5. **Given** a blank attempt name, **When** the engineer records an unsuccessful delivery, **Then** nothing is recorded and the engineer is told `Name this attempt.`
6. **Given** no Pending message, **When** the engineer records an unsuccessful delivery, **Then** the engineer is told `There is no outbox message to retry.`

---

### User Story 2 - The third attempt writes the dead letter (Priority: P2)

Three is the bound. The third unsuccessful delivery of the same message writes one dead letter in that same result, with the reason `The delivery was attempted too many times.` The attempt count stays 3. The message is shown as Dead and is not delivered. A delivery after that does not deliver it. If that third attempt is rolled back, the attempt count stays 2 and no dead letter is kept. The same name can then be used. Recording an attempt does not read a file, create a folder, approve a change, or advance the workflow.

**Why this priority**: A message that keeps failing must leave the line of Pending messages, and a crash must not leave it half recorded.

**Independent Test**: Record three unsuccessful deliveries, each after the previous next time. The message is shown as Dead, the attempt count is 3, and the file was read only once. Roll back a third attempt on another message. The count stays 2 and there is no dead letter.

**Acceptance Scenarios**:

1. **Given** two recorded attempts and a next time that has arrived, **When** the engineer records a third unsuccessful delivery, **Then** the attempt count is 3, one dead letter names `The delivery was attempted too many times.`, and the message is shown as Dead.
2. **Given** that dead letter, **When** the engineer delivers a new name, **Then** the message is not Delivered.
3. **Given** a third attempt that is rolled back, **When** the engineer opens the task, **Then** the attempt count is 2, no dead letter is stored, and that attempt name can still be used.
4. **Given** the name "once" was used on one task, **When** the engineer uses "once" on another task, **Then** that other task records its own attempt.

---

### User Story 3 - The task shows the attempts (Priority: P3)

The task shows the attempt count and the next time. When the task is In Progress and a message is Pending, the engineer can enter an attempt name and press Delivery did not succeed. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see why a delivery is waiting.

**Independent Test**: Record one unsuccessful delivery and open the task. The page shows attempt count 1 and the next time. Press Delivery did not succeed with a new name before that time. The count stays 1.

**Acceptance Scenarios**:

1. **Given** one unsuccessful delivery, **When** the engineer opens the task, **Then** the page shows the attempt count 1 and the next time.
2. **Given** a Pending message, **When** the engineer opens the task, **Then** the page offers Delivery did not succeed.
3. **Given** that page, **When** the engineer submits an attempt before the next time, **Then** the attempt count stays 1.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- An unsuccessful delivery before the next time does not save its name.
- A task that is not In Progress keeps the existing status refusal, and the name is not saved.
- One request records one attempt or delivers one message.
- Replaying a dead letter is not part of this feature.
- A poison rejection stays as it is. It is not an unsuccessful delivery.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an unsuccessful delivery of the oldest Pending message. The first accepted use of that name MUST record one attempt and a next time one minute later. The message MUST stay Pending. The same name MUST NOT record another attempt. A blank name MUST be refused with `Name this attempt.` No Pending message MUST be refused with `There is no outbox message to retry.`
- **FR-002**: Before the next time, a delivery and another unsuccessful delivery MUST NOT deliver the message and MUST NOT add an attempt. The engineer MUST be told `This delivery is not due yet.` The name of that early request MUST NOT be saved. When the next time has arrived, Deliver outbox MUST deliver the message as it does today and MUST NOT add an attempt.
- **FR-003**: The third unsuccessful delivery of a message MUST write one dead letter with the reason `The delivery was attempted too many times.` The attempt count MUST stay 3. The message MUST be shown as Dead and MUST NOT be Delivered. A rolled-back third attempt MUST leave the count at 2 and MUST leave no dead letter. The same name on another task MUST record that task's own attempt.
- **FR-004**: Recording an attempt MUST NOT read a file, create a folder, approve a change, advance the workflow, or change the task status. The task page MUST show the attempt count and the next time, and MUST offer Delivery did not succeed while the task is In Progress and a message is Pending. The task list MUST stay the list of tasks.

### Key Entities

- **Delivery attempt**: The trimmed name of one unsuccessful delivery, the message it counted, and the next time a delivery of that message is allowed.
- **Attempt count**: How many unsuccessful deliveries are recorded for one message. It stops at three.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of deliveries before the next time, 100% leave the message Pending and leave the attempt count unchanged.
- **SC-002**: In a review of third attempts, 100% leave one dead letter and an attempt count of 3. In a review of rolled-back third attempts, 100% leave no dead letter and a count of 2.
- **SC-003**: An engineer can see the attempt count and the next time on the task in one view.

## Assumptions

- Specifications 001 through 033 are not rewritten. A delivery that is due still marks the message Delivered. Poison rejections stay as they are.
- The bound is three unsuccessful deliveries. The wait is one minute on the workspace clock.
- The outbox message is not given a new stored state. Dead is the existing way to show a message that has a dead letter.
- Replaying a dead letter is a later feature.
- The rules are covered by automated checks.
