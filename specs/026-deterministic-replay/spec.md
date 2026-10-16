# Feature Specification: Workflow Replay and Deterministic Execution

**Feature Branch**: `026-deterministic-replay`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Workflow Replay and Deterministic Execution."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Replay a finished workflow from its record (Priority: P1)

The engineer replays the current workflow version. Each completed step is matched to the effect already stored for it: a file that was read, or a folder change that was recorded. The report lists those steps in workflow order and names the stored effect. Replaying does not read a file, does not create a folder, does not call a model, and does not add a replay entry. Doing it again returns the same report.

**Why this priority**: A workflow can be trusted only when the same stored record produces the same result without doing the work again.

**Independent Test**: Advance "Read the note" and "Read the extra" until both are completed. Replay execution. The report lists both files. Replay again. The report is the same, and each file was read only once.

**Acceptance Scenarios**:

1. **Given** the current version has two completed reads, **When** the engineer replays execution, **Then** the report lists both steps as completed and names each stored file.
2. **Given** that report, **When** the engineer replays execution again, **Then** the report is the same, no file is read again, and the replay of step events does not gain an entry.
3. **Given** a completed step whose stored effect is gone, **When** the engineer replays execution, **Then** the report stops at that step with `Stopped at {title}: the stored effect is missing.` and the file is not read again.

---

### User Story 2 - Stop at the first step that has not finished (Priority: P2)

Replay walks the current version in order and stops at the first step that is not completed. A pending step stops with `Stopped at {title}: the step has not run.` A waiting step stops with `Stopped at {title}: waiting for approval.` A failed step stops with `Stopped at {title}: {detail}`. Steps after that one are not included. The stopped step is not performed, and a waiting change is not approved. A second replay returns the same report.

**Why this priority**: Deterministic replay must not continue past work that has not been stored.

**Independent Test**: Complete "Read the note" and leave "Read the other" pending. Replay execution. The report matches the note and stops at the other file. That other file is not read. Replay again and the report is unchanged.

**Acceptance Scenarios**:

1. **Given** one completed step and one pending step, **When** the engineer replays execution, **Then** only the completed step is matched and the report says `Stopped at {title}: the step has not run.`
2. **Given** a waiting folder step, **When** the engineer replays execution, **Then** the report says `Stopped at {title}: waiting for approval.` and the change is not approved.
3. **Given** a failed step, **When** the engineer replays execution, **Then** the report keeps that step's stored detail and does not retry the step.

---

### User Story 3 - Show the report on the task (Priority: P3)

The task shows the execution report for the current version: each matched step and, when the replay stops, the stop sentence. The engineer can ask for the report again with Replay execution. A workflow with no steps is refused with `There is no step to replay.` A running step is refused with `Recover the interrupted step first.` and nothing is performed. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see the deterministic result on the task, not only through a separate command.

**Independent Test**: Open a task whose first step has completed and whose second step is pending. The page shows the matched file and `Stopped at Read the other: the step has not run.` Replay execution leaves that report unchanged.

**Acceptance Scenarios**:

1. **Given** a completed step and a pending step, **When** the engineer opens the task, **Then** the page shows the matched step and the stop sentence.
2. **Given** that page, **When** the engineer uses Replay execution, **Then** the same report is shown and the task stays In Progress.
3. **Given** no workflow steps, **When** the engineer replays execution, **Then** the engineer is told `There is no step to replay.`
4. **Given** a running step, **When** the engineer replays execution, **Then** the engineer is told `Recover the interrupted step first.` and the step is not performed.

### Edge Cases

- Replay uses the current version. A pending step left on a superseded version is not part of the report.
- Replay does not change the task status, the step states, or the recorded replay of events.
- One request produces one report. A repeated request returns that same report.
- Read a file and Create a folder stay the only workflow actions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Replaying execution MUST walk the current version in order and match each completed step to its stored effect. The report MUST name the step and that effect. A missing stored effect MUST stop the report with `Stopped at {title}: the stored effect is missing.`
- **FR-002**: Replay MUST stop at the first step that is not completed. Pending uses `Stopped at {title}: the step has not run.` Waiting uses `Stopped at {title}: waiting for approval.` Failed uses `Stopped at {title}: {detail}`. Later steps MUST NOT be included. The stopped step MUST NOT be performed, and a waiting change MUST NOT be approved.
- **FR-003**: A second replay of the same stored workflow MUST return the same report. Replay MUST NOT read a file, create a folder, call a model, add a replay entry, or change the task status.
- **FR-004**: The task page MUST show the report. Replay execution MUST show it again. No steps MUST be refused with `There is no step to replay.` A running step MUST be refused with `Recover the interrupted step first.`

### Key Entities

- **Execution report**: The matched completed steps, in order, and the sentence where the replay stopped. It is derived from the stored workflow and its stored effects.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of repeated replays of the same workflow, 100% return the same report.
- **SC-002**: In a review of those replays, 100% leave the stored file reads, folder changes, and replay entries unchanged.
- **SC-003**: An engineer can see the matched steps and the stop sentence on the task in one view.

## Assumptions

- Specifications 001 through 025 are not rewritten. The existing replay of step events stays as it is. Recovery and exactly-once effects stay as they are.
- The stored file read or folder change is the effect. Replay does not look outside that record.
- The rules are covered by automated checks.
