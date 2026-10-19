# Feature Specification: Replay a Dead Letter

**Feature Branch**: `035-replay-dead-letter`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Replay one dead letter. Return it to delivery. Keep the dead-letter record. The same replay name does not return it twice. A rolled-back replay leaves it Dead."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Return the oldest dead letter to delivery (Priority: P1)

The engineer names a replay. That returns the oldest dead letter that has not been replayed. The message is shown as Pending again, so a later delivery can accept it. The dead letter remains, including its reason. The stored message is not given a new state. The same name again does not return another message. A different name returns the next dead letter that has not been replayed. Replay does not add a delivery attempt and does not clear the attempt count. A replayed message can be delivered even when an earlier next time has not arrived. The task status stays as it was.

**Why this priority**: A message set aside is useful only when the engineer can put it back into delivery.

**Independent Test**: Set "Read the note" aside with three rejections. Replay it with "once". The message is shown as Pending, the dead letter still names the reason, and delivering "ship" marks it Delivered. The file was read only once. Replay "once" again. Nothing else is returned.

**Acceptance Scenarios**:

1. **Given** one dead letter, **When** the engineer replays it with "once", **Then** the message is shown as Pending, the dead letter remains, and the replay names "once".
2. **Given** that replay, **When** the engineer delivers a new name, **Then** the message is Delivered.
3. **Given** that replay, **When** the engineer replays "once" again, **Then** no second replay is recorded.
4. **Given** two dead letters, **When** the engineer replays once, **Then** only the older message is shown as Pending.
5. **Given** a message whose attempt count is 3, **When** the engineer replays it, **Then** the count stays 3 and a delivery can accept the message before the old next time.

---

### User Story 2 - A replay that does not finish leaves the message Dead (Priority: P2)

A blank name is refused with `Name this replay.` No dead letter left to replay is refused with `There is no dead letter to replay.` A replay that is rolled back leaves the message Dead, leaves no replay, and delivery still skips it. The same name on another task can replay that task's dead letter. Replay does not read a file, create a folder, approve a change, or advance the workflow.

**Why this priority**: A crash must not look like the message was returned.

**Independent Test**: Roll back a replay named "once". The message stays Dead and delivery is refused with `There is no outbox message to deliver.` Use "once" again. The message is shown as Pending.

**Acceptance Scenarios**:

1. **Given** a blank name, **When** the engineer replays, **Then** the message stays Dead and the engineer is told `Name this replay.`
2. **Given** no dead letter, **When** the engineer replays, **Then** the engineer is told `There is no dead letter to replay.`
3. **Given** a replay that is rolled back, **When** the engineer opens the task, **Then** the message stays Dead, no replay is stored, and a delivery does not accept it.
4. **Given** the name "once" was used on one task, **When** the engineer uses "once" on another task, **Then** that other task returns its own dead letter.
5. **Given** a task that is not In Progress, **When** the engineer replays, **Then** the engineer is told `The task must be In Progress.` and no replay is stored.

---

### User Story 3 - The task shows the replay (Priority: P3)

The task shows each replay. When the task is In Progress and a dead letter has not been replayed, the engineer can enter a replay name and press Replay dead letter. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see which dead letter was returned.

**Independent Test**: Open a task with one dead letter. The page offers Replay dead letter. Press it with "once". The page shows that replay and the message as Pending.

**Acceptance Scenarios**:

1. **Given** one dead letter that has not been replayed, **When** the engineer opens the task, **Then** the page offers Replay dead letter.
2. **Given** a replay named "once", **When** the engineer opens the task, **Then** the page shows that name and the message as Pending.
3. **Given** that replay was the only dead letter, **When** the engineer returns to the task, **Then** Replay dead letter is not offered again.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- One request replays one dead letter.
- The dead letter is not deleted.
- Replay does not start another round of attempts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a replay. The first accepted use of that name MUST return the oldest dead letter that has not been replayed. The message MUST be shown as Pending. The dead letter, including its reason, MUST remain. The same name MUST NOT return another message. A different name MUST be able to return the next dead letter.
- **FR-002**: After a replay, a delivery MUST be able to accept that message, including when an earlier next time has not arrived. Replay MUST NOT add an attempt and MUST NOT clear the attempt count.
- **FR-003**: A blank name MUST be refused with `Name this replay.` No remaining dead letter MUST be refused with `There is no dead letter to replay.` A rolled-back replay MUST leave the message Dead and MUST leave no replay. A task that is not In Progress MUST be refused with `The task must be In Progress.` The same name on another task MUST be able to return that task's dead letter.
- **FR-004**: Replay MUST NOT read a file, create a folder, approve a change, advance the workflow, or change the task status. The task page MUST show the replay and MUST offer Replay dead letter while the task is In Progress and a dead letter has not been replayed. The task list MUST stay the list of tasks.

### Key Entities

- **Dead-letter replay**: The trimmed name that returned one dead letter to delivery. The dead letter itself remains.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of replays, 100% show the returned message as Pending and keep the dead letter.
- **SC-002**: In a review of rolled-back replays, 100% leave the message Dead and leave delivery unable to accept it.
- **SC-003**: An engineer can see the replay and return the message from the task in one view.

## Assumptions

- Specifications 001 through 034 are not rewritten. A dead letter is still created the way those specifications say. The outbox message is not given a new stored state.
- Replay does not delete the dead letter and does not start a new round of attempts.
- The rules are covered by automated checks.
