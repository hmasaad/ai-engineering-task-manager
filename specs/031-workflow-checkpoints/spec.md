# Feature Specification: Workflow Snapshots and Checkpointing

**Feature Branch**: `031-workflow-checkpoints`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Workflow Snapshots and Checkpointing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A named checkpoint stores the workflow (Priority: P1)

The engineer names a checkpoint. The task stores each current step and its state. The same name again does not replace that snapshot. A blank name is refused with `Name this checkpoint.` No workflow is refused with `There is no workflow to checkpoint.` A running step is refused with `Recover the interrupted step first.` A checkpoint that is rolled back is not kept. Taking a checkpoint does not change the task status and does not read a file.

**Why this priority**: A later failure is only useful to undo when the engineer can name the point to return to.

**Independent Test**: Add "Read the note" and "Read the extra". Take the checkpoint `before the read`. Advance the note. Take `before the read` again. The stored snapshot still shows both steps as Pending.

**Acceptance Scenarios**:

1. **Given** two pending steps, **When** the engineer takes `before the read`, **Then** the checkpoint lists both steps as Pending.
2. **Given** that checkpoint, **When** a step later completes and the engineer takes `before the read` again, **Then** the snapshot is unchanged.
3. **Given** a blank name, **When** the engineer takes a checkpoint, **Then** nothing is stored and the engineer is told `Name this checkpoint.`
4. **Given** no steps, **When** the engineer takes a checkpoint, **Then** the engineer is told `There is no workflow to checkpoint.`
5. **Given** a running step, **When** the engineer takes a checkpoint, **Then** the engineer is told `Recover the interrupted step first.`
6. **Given** a checkpoint that is rolled back, **When** the engineer opens the task, **Then** there is no checkpoint.
7. **Given** the same name on another task, **When** the engineer takes it there, **Then** that task stores its own checkpoint.

---

### User Story 2 - Restore returns a failed step to the snapshot (Priority: P2)

The engineer restores a checkpoint. A completed step stays completed. A failed step that the snapshot recorded as Pending, and that has no stored effect, becomes Pending again. A failed step that has a stored effect stays failed, and the engineer is told `A stored effect cannot be restored over.` A checkpoint from another shape of workflow is refused with `The workflow has changed since this checkpoint.` A missing checkpoint is refused with `That checkpoint is not on this task.` Restore does not read a file again, does not remove a stored read, and does not change the task status.

**Why this priority**: The snapshot is the point the workflow can safely resume from.

**Independent Test**: Checkpoint after "Read the note" is completed and "Read the gap" is pending. Let the gap fail. Restore the checkpoint. The note stays completed and still read once. The gap is Pending.

**Acceptance Scenarios**:

1. **Given** a completed step and a later failed step with no stored effect, **When** the engineer restores the checkpoint taken while the later step was Pending, **Then** the completed step stays completed and the failed step becomes Pending.
2. **Given** a failed step with a stored effect, **When** the engineer restores a checkpoint that recorded it as Pending, **Then** the step stays failed and the engineer is told `A stored effect cannot be restored over.`
3. **Given** a checkpoint whose steps are no longer the current workflow, **When** the engineer restores it, **Then** the engineer is told `The workflow has changed since this checkpoint.`
4. **Given** a checkpoint that is not on the task, **When** the engineer restores it, **Then** the engineer is told `That checkpoint is not on this task.`

---

### User Story 3 - The task shows its checkpoints (Priority: P3)

The task shows each checkpoint and the step states it stored. Before any checkpoint, the page says `No checkpoints yet.` An In Progress task that has steps and is not interrupted offers Take checkpoint and Restore checkpoint. The task list stays the list of tasks.

**Why this priority**: The engineer needs the saved point on the task, beside the workflow.

**Independent Test**: Open a task with two pending steps. The page says `No checkpoints yet.` Take `before the read`. The page shows both steps as Pending.

**Acceptance Scenarios**:

1. **Given** no checkpoint, **When** the engineer opens the task, **Then** the page says `No checkpoints yet.`
2. **Given** a checkpoint, **When** the engineer opens the task, **Then** the page shows its name and each step state.
3. **Given** a failed step that the checkpoint can restore, **When** the engineer restores it from the page, **Then** that step is Pending and the completed step is unchanged.

### Edge Cases

- A checkpoint does not include a step added after it was taken. Restoring that checkpoint is refused because the workflow has changed.
- Restore does not delete a file read, a folder change, a span, or an outbox message.
- One request stores one checkpoint or restores one checkpoint.
- Reading the checkpoints does not move the clock.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Naming a checkpoint MUST store each current step and its state. The same name MUST NOT replace that snapshot. A blank name MUST be refused with `Name this checkpoint.` No steps MUST be refused with `There is no workflow to checkpoint.` A running step MUST be refused with `Recover the interrupted step first.` A rolled-back checkpoint MUST leave nothing stored. The same name on another task MUST store that task's own checkpoint.
- **FR-002**: Restore MUST leave a completed step completed. A failed step that the snapshot recorded as Pending, and that has no stored effect, MUST become Pending. A failed step with a stored effect MUST stay failed, and the engineer MUST be told `A stored effect cannot be restored over.` A changed workflow MUST be refused with `The workflow has changed since this checkpoint.` A checkpoint that is not on the task MUST be refused with `That checkpoint is not on this task.`
- **FR-003**: Taking or restoring a checkpoint MUST NOT read a file, remove a stored read, advance the workflow, or change the task status.
- **FR-004**: The task page MUST show the checkpoints. Before any exist, it MUST say `No checkpoints yet.` The task list MUST stay the list of tasks.

### Key Entities

- **Checkpoint**: A named snapshot of the current workflow. It keeps the step states from the moment it was taken.
- **Checkpoint step**: One step as it stood in that snapshot: its place and its state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of repeated checkpoint names, 100% keep the original step states.
- **SC-002**: In a review of restores after a failure, 100% leave the completed step and its stored read in place.
- **SC-003**: An engineer can see the checkpoint and restore it from the task in one view.

## Assumptions

- Specifications 001 through 030 are not rewritten. Advance, recovery, delivery, compensation, and tracing stay as they are.
- Restore rewinds only a failed step with no stored effect. It does not make a completed step run again.
- A checkpoint is not taken while a step is running.
- The rules are covered by automated checks.
