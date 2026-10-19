# Feature Specification: Deterministic Replay and Side-Effect Isolation

**Feature Branch**: `032-side-effect-isolation`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Implement Deterministic Replay and Side-Effect Isolation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A completed step seals its effect (Priority: P1)

When a workflow step becomes Completed, the same result seals the file or folder that step stored. A failed step seals nothing. A waiting step seals nothing. If that completion is rolled back, the seal is not kept. Completing the step again does not seal a second effect. Sealing does not change the task status.

**Why this priority**: Replay can stay away from the project only when the effect was sealed with the step.

**Independent Test**: Advance "Read the note" for a file that exists. The task has one sealed effect for `note.txt`. A missing file leaves the step Failed and seals nothing.

**Acceptance Scenarios**:

1. **Given** "Read the note" completes, **When** the engineer opens the task, **Then** one sealed effect names that step and `note.txt`.
2. **Given** "Read the note" fails because the file is missing, **When** the engineer opens the task, **Then** no effect is sealed.
3. **Given** a completion that is rolled back, **When** the engineer opens the task, **Then** the step is unchanged and no effect is sealed.
4. **Given** one completed step, **When** that completion is recorded again, **Then** the step still has one sealed effect.

---

### User Story 2 - Replay uses the seal and leaves the project alone (Priority: P2)

The engineer replays the sealed effects. Each completed step is matched to its seal. The report lists those steps in workflow order. Replay does not read a file, does not create a folder, and does not call a model. After the file or folder has been removed, the report still names the sealed effect and the project stays as it was. A second replay returns the same report and does not move the clock. A pending step stops with `Stopped at {title}: the step has not run.` A waiting step stops with `Stopped at {title}: waiting for approval.` A failed step stops with `Stopped at {title}: {detail}`. A completed step with no seal stops with `Stopped at {title}: the isolated effect is missing.` A running step is refused with `Recover the interrupted step first.` No steps is refused with `There is no isolated effect to replay.` An unknown task is refused with `Task not found.`

**Why this priority**: A replay that opens the project again is not isolated from the side effect.

**Independent Test**: Complete "Read the note", then remove `note.txt`. Replay the sealed effects. The report names `note.txt`. The file is still gone. Replay again. The report is the same, and the file was not read again.

**Acceptance Scenarios**:

1. **Given** a completed read whose file is then removed, **When** the engineer replays the sealed effects, **Then** the report names that file and the file stays removed.
2. **Given** a completed folder whose folder is then removed, **When** the engineer replays the sealed effects, **Then** the report names that folder and the folder stays removed.
3. **Given** one completed step and one pending step, **When** the engineer replays, **Then** the report stops with `Stopped at {title}: the step has not run.` and the pending file is not read.
4. **Given** a replay, **When** the engineer replays again, **Then** the report is the same and the clock does not move.
5. **Given** a running step, **When** the engineer replays, **Then** the engineer is told `Recover the interrupted step first.`

---

### User Story 3 - The task shows the sealed replay (Priority: P3)

The task shows the sealed effects and where the replay stopped. When the workflow has steps and is not interrupted, the engineer can press Replay isolated effects. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see that the replay used the seal rather than the project.

**Independent Test**: Complete one read and open the task. The page shows the sealed file. Press Replay isolated effects. The file was not read again.

**Acceptance Scenarios**:

1. **Given** a completed read, **When** the engineer opens the task, **Then** the page shows that sealed effect.
2. **Given** a pending step after it, **When** the engineer opens the task, **Then** the page shows where the replay stopped.
3. **Given** Replay isolated effects, **When** the engineer presses it, **Then** the report is unchanged and the file was read only once.

### Edge Cases

- A waiting step stores no seal. The seal is stored when the step becomes Completed.
- Replay does not approve a change and does not advance the workflow.
- One request seals one completion or reads the sealed report.
- Removing the project file after the seal does not change the report.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A step that becomes Completed MUST seal its file or folder in that same result. A failed step, a waiting step, and a rolled-back completion MUST NOT leave a seal. A second completion of that step MUST NOT seal another effect.
- **FR-002**: Replaying the sealed effects MUST match each completed step to its seal and stop at the first step that is not completed. It MUST NOT read a file, create a folder, approve a change, or change the task status. A removed file or folder MUST stay removed. A second replay MUST return the same report and MUST NOT move the clock.
- **FR-003**: No steps MUST be refused with `There is no isolated effect to replay.` A running step MUST be refused with `Recover the interrupted step first.` A completed step with no seal MUST stop with `Stopped at {title}: the isolated effect is missing.` A pending step MUST stop with `Stopped at {title}: the step has not run.` A waiting step MUST stop with `Stopped at {title}: waiting for approval.` A failed step MUST stop with `Stopped at {title}: {detail}`. An unknown task MUST be refused with `Task not found.`
- **FR-004**: The task page MUST show the sealed replay. When the workflow has steps and is not interrupted, it MUST offer Replay isolated effects. The task list MUST stay the list of tasks.

### Key Entities

- **Sealed effect**: The file or folder stored with one completed step. Replay uses this seal and does not touch the project.
- **Isolated replay**: The ordered report of sealed effects, ending at the first step that has not completed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of completed steps, 100% have one sealed effect stored with that completion.
- **SC-002**: In a review of replays after the project file is removed, 100% name the sealed effect and leave the project unchanged.
- **SC-003**: An engineer can see the sealed effect and replay it from the task in one view.

## Assumptions

- Specifications 001 through 031 are not rewritten. The existing execution replay stays as it is.
- The seal names the file or folder the step stored. It does not copy the file contents again.
- A waiting step is sealed only when it later becomes Completed.
- The rules are covered by automated checks.
