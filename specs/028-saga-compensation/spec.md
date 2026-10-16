# Feature Specification: Saga Pattern and Compensation

**Feature Branch**: `028-saga-compensation`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Saga Pattern & Compensation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A failed workflow can be compensated in reverse (Priority: P1)

The current workflow is a saga. It is Open while no step has failed. It is Failed when a step has failed. The engineer compensates one completed step at a time, starting with the latest. The engineer names why. A file read is compensated immediately. The stored file read stays. A created folder is not removed yet. Compensating does not run the step again, does not advance the workflow, and does not change the task status.

**Why this priority**: A saga is only safe when the steps that already finished can be withdrawn in reverse after a later step fails.

**Independent Test**: Complete "Read the extra", then complete "Read the note", then fail "Read the gap". Compensate with `Withdraw the note`. The note is compensated and the extra is not. Both files stay read once.

**Acceptance Scenarios**:

1. **Given** no step has failed, **When** the engineer compensates, **Then** nothing is compensated and the engineer is told `The workflow has not failed.`
2. **Given** a failed step and two completed reads, **When** the engineer compensates with a reason, **Then** only the latest completed step is compensated and its file read remains.
3. **Given** a blank reason, **When** the engineer compensates, **Then** nothing is compensated and the engineer is told `Name why this step is compensated.`
4. **Given** a failure and no completed step, **When** the engineer compensates, **Then** the engineer is told `There is no step to compensate.`
5. **Given** a running step, **When** the engineer compensates, **Then** the engineer is told `Recover the interrupted step first.`

---

### User Story 2 - Removing a folder waits for approval (Priority: P2)

Compensating a completed folder step records the compensation as waiting. The folder stays. The engineer approves it by naming the evidence reviewed, and an empty folder is removed. The original folder change stays in the record. A folder that contains something stays, and the engineer is told `The folder must be empty to compensate.` The engineer can mark the compensation not carried out, and the folder stays. While a compensation is waiting, another step is not compensated.

**Why this priority**: Removing a folder deletes something that was stored, so it waits for the engineer.

**Independent Test**: Create an empty folder, then fail the next step. Compensate that folder. The folder is still there. Approve it with `The folder is empty`. The folder is gone, and the original change remains.

**Acceptance Scenarios**:

1. **Given** a completed folder step and a later failure, **When** the engineer compensates, **Then** the compensation is waiting and the folder remains.
2. **Given** that waiting compensation and an empty folder, **When** the engineer approves it with the evidence reviewed, **Then** the folder is removed and the compensation is compensated.
3. **Given** a folder that contains a file, **When** the engineer approves the compensation, **Then** the folder remains and the engineer is told `The folder must be empty to compensate.`
4. **Given** a waiting compensation, **When** the evidence is blank, **Then** the folder remains and the engineer is told `An account of the evidence reviewed is required.`
5. **Given** a waiting compensation, **When** the engineer marks it not carried out with a reason, **Then** the folder remains.
6. **Given** a waiting compensation, **When** the engineer compensates again, **Then** the engineer is told `Finish the waiting compensation first.`

---

### User Story 3 - The task shows the saga (Priority: P3)

The task shows the saga as Open, Failed, Waiting, or Compensated. A failed saga offers Compensate. A waiting compensation offers Approve compensation and Mark compensation not carried out. After every completed step has been settled, the saga is Compensated. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see which step was withdrawn and whether a folder removal is still waiting.

**Independent Test**: Fail a workflow after one completed read. The page shows Saga Failed and Compensate. After compensating, the page shows that step and Saga Compensated.

**Acceptance Scenarios**:

1. **Given** a workflow whose step has failed, **When** the engineer opens the task, **Then** the page shows Saga Failed and Compensate.
2. **Given** a waiting folder compensation, **When** the engineer opens the task, **Then** the page shows Saga Waiting and Approve compensation.
3. **Given** every completed step has been compensated or marked not carried out, **When** the engineer opens the task, **Then** the page shows Saga Compensated.

### Edge Cases

- Compensation does not delete a stored file read or the original folder change.
- A second request does not compensate a step that already has a compensation.
- One request compensates one step, approves one waiting compensation, or marks one not carried out.
- The task status stays unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The current workflow MUST be a saga: Open when no step has failed, and Failed when a step has failed. Compensation MUST be refused with `The workflow has not failed.` until then, with `Recover the interrupted step first.` while a step is running, and with `There is no step to compensate.` when no completed step remains.
- **FR-002**: One compensation MUST withdraw the latest completed step that has not been compensated. The engineer MUST name why. A blank reason MUST be refused with `Name why this step is compensated.` A file read MUST be compensated immediately and its stored read MUST remain.
- **FR-003**: A completed folder MUST wait. The folder MUST remain until the engineer approves the evidence reviewed. Approval of an empty folder MUST remove the folder and keep the original change. A folder that contains something MUST stay, and the engineer MUST be told `The folder must be empty to compensate.` Blank evidence MUST be refused with `An account of the evidence reviewed is required.` Marking it not carried out MUST leave the folder. Another compensation MUST be refused with `Finish the waiting compensation first.`
- **FR-004**: The task page MUST show the saga and its compensations. The task status MUST stay unchanged. Compensation MUST NOT advance the workflow or run a step again.

### Key Entities

- **Saga**: The current workflow, named Open, Failed, Waiting, or Compensated.
- **Compensation**: The reason a completed step was withdrawn, and whether that withdrawal is waiting, compensated, or not carried out.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of compensations after a failure, 100% withdraw the latest completed step first.
- **SC-002**: In a review of folder compensations, 100% leave the folder in place until an approval names the evidence reviewed.
- **SC-003**: An engineer can see the saga and the compensated step on the task in one view.

## Assumptions

- Specifications 001 through 027 are not rewritten. Advance, recovery, replay, and delivery stay as they are.
- A file read has no disk change to undo. A created folder is removed only after approval, and only when it is empty.
- The rules are covered by automated checks.
