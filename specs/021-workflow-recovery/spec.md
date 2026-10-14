# Feature Specification: Workflow Recovery and Replay

**Feature Branch**: `021-workflow-recovery`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Implement workflow recovery and replay. Keep a replay of each step result. Recover a step that was interrupted. If the step's effect was already stored, recover from that record without performing the step again."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read the replay (Priority: P1)

Each advance records the step as it starts and the result it reaches. The engineer can read that replay in order: the step title, the state, the time, and the detail when there is one. A task that has not advanced has an empty replay. Opening the task again shows the same replay. Reading the replay does not perform a step, does not add a replay entry, and does not change a status.

**Why this priority**: Recovery is trustworthy only when the engineer can read what already happened.

**Independent Test**: Advance "Read the note" for a file that exists. The replay lists that step as running, then completed. Opening the workspace again shows the same two entries, and the file is not read again.

**Acceptance Scenarios**:

1. **Given** an In Progress task with no advance yet, **When** the engineer reads the replay, **Then** the replay has no entries.
2. **Given** "Read the note" for a file that exists, **When** the engineer advances once, **Then** the replay lists that step as running and then completed, in that order.
3. **Given** that replay, **When** the engineer reads it again after the workspace is opened again, **Then** the same entries are shown, in the same order, and the file is not read again.
4. **Given** a stored replay, **When** the engineer opens the task without advancing or recovering, **Then** no step is performed and the replay does not gain an entry.

---

### User Story 2 - Recover an interrupted step (Priority: P2)

An advance records a step as running before it records the result. If that result is never recorded, the step stays running. The task reports `Stopped at {title}: the step was interrupted.` Advancing again is refused with `Recover the interrupted step first.` and does not perform the step. Recover marks that step Failed, keeps the same sentence, and does not perform the following step. The next advance retries only the interrupted step. Recovering when no step is running is refused with `There is no step to recover.`

**Why this priority**: A step left running must not be started a second time, and the engineer needs one recovery that names it.

**Independent Test**: Leave "Read the note" running before the file is read. Advance is refused. Recover marks it Failed with `Stopped at Read the note: the step was interrupted.` The following folder step stays Pending, and the file is still unread.

**Acceptance Scenarios**:

1. **Given** "Read the note" is running and the file was not read, **When** the engineer looks at the task, **Then** the step is running and the task reports `Stopped at Read the note: the step was interrupted.`
2. **Given** that running step, **When** the engineer advances, **Then** the step stays running, nothing is performed, and the engineer is told `Recover the interrupted step first.`
3. **Given** that running step and a later folder step, **When** the engineer recovers, **Then** "Read the note" is Failed, the sentence stays `Stopped at Read the note: the step was interrupted.`, and the folder step stays Pending.
4. **Given** no step is running, **When** the engineer recovers, **Then** nothing changes and the engineer is told `There is no step to recover.`
5. **Given** the recovered failure, **When** the file exists and the engineer advances once, **Then** only that step is retried.

---

### User Story 3 - Recover from a stored effect (Priority: P3)

If the step's effect was stored while the step was still running, recovery uses that record. A stored file read becomes Completed and the file is not read again. A stored folder change becomes Completed or Waiting from that change, and a second change is not recorded. A change that is still waiting reports `Stopped at {title}: waiting for approval.` Recovery does not approve the change and does not perform the next step.

**Why this priority**: An effect that already happened must be kept, and recovery must not repeat it.

**Independent Test**: Leave "Read the note" running after the file read was stored. Recover marks the step Completed, the replay gains that completed result, and the file is not read again.

**Acceptance Scenarios**:

1. **Given** "Read the note" is running and the file read is already stored, **When** the engineer recovers, **Then** the step is Completed, the replay records that completed result, and the file is not read again.
2. **Given** "Create the folder" is running and its consequential change is already stored, **When** the engineer recovers, **Then** the step is Waiting, no second change is recorded, and the task reports `Stopped at Create the folder: waiting for approval.`
3. **Given** that waiting step, **When** the engineer recovers again, **Then** the engineer is told `There is no step to recover.` Approving the change does not advance the workflow.

### Edge Cases

- A replay entry for a failure keeps the action's message. The stop sentence stays the one that feature already uses.
- An advance that leaves a waiting step waiting does not add another replay entry.
- Recovery and replay do not change the task status.
- A task that is not In Progress keeps the existing status refusal for advance and recover. Reading the replay of an existing task is still allowed.
- One request reads the replay, recovers one running step, or advances once.
- Read a file and Create a folder stay the only workflow actions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every advance MUST record the step as running and then record the result it reaches. The engineer MUST be able to read those entries in order, with the step title, the state, the time, and the detail when there is one. A task with no advance MUST have an empty replay.
- **FR-002**: Reading the replay MUST NOT perform a step, add an entry, or change a status. Opening the workspace again MUST show the same entries in the same order.
- **FR-003**: A step that is running MUST make the task report `Stopped at {title}: the step was interrupted.` Advance MUST be refused with `Recover the interrupted step first.` and MUST NOT perform the step.
- **FR-004**: Recover MUST mark a running step with no stored effect as Failed and keep `Stopped at {title}: the step was interrupted.` Later steps MUST stay unperformed. When no step is running, recover MUST be refused with `There is no step to recover.`
- **FR-005**: When the running step's effect is already stored, recover MUST mark the step from that record and MUST NOT perform the action again. A stored file read becomes Completed. A stored folder change becomes Completed or Waiting. A waiting result uses `Stopped at {title}: waiting for approval.` Recovery MUST NOT approve a change.

### Key Entities

- **Replay entry**: One stored moment of one step: running, or the result the step reached, with the time and any detail.
- **Running step**: A step whose start is recorded and whose result is not.
- **Stored effect**: The file read or folder change already kept for that step before recovery.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can name each replay entry, in order, from the task, in under 2 minutes, including after the workspace is opened again.
- **SC-002**: In a review of replay readings, 100% perform no step and add no entry.
- **SC-003**: In a review of interrupted steps, 100% stay unperformed until recover, and the sentence names that step.
- **SC-004**: In a review of recoveries where the effect is already stored, 100% leave a single copy of that effect.

## Assumptions

- Specifications 001 through 020 are not rewritten. An advance still performs one step, and a completed step is still not performed again.
- A step can be running only because an advance recorded the start and did not record the result. The engineer recovers that step. The product does not guess a result that was not stored.
- The engineer name and the time still come from the workspace. A client-supplied name or time is ignored.
- The replay is shown on the task. The interruption sentence is shown while a step is running.
- The rules are covered by automated checks.
