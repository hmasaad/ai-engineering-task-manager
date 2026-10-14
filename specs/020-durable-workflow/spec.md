# Feature Specification: Durable Workflow Orchestration

**Feature Branch**: `020-durable-workflow`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Implement durable workflow orchestration. Store an ordered run of steps with each task. Advance one step at a time. Resume from the stored step after the workspace is opened again. A failed or approval-waiting step stops the run and names that step."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Store the steps before the run (Priority: P1)

The engineer adds one step at a time to a task that is In Progress. A step has a title and one action: Read a file, or Create a folder. Read a file names the project and the file. Create a folder names the project, what changed, whether the folder is ordinary or consequential, and the folder. The steps stay in the order they were added. Opening the task again shows the same steps, each Pending. A blank title, an unknown action, or a missing field for that action is refused and stores nothing. A step can be removed only while every step is still Pending. After any step has left Pending, another step cannot be added and a step cannot be removed.

**Why this priority**: A later advance can resume only from steps that were stored first.

**Independent Test**: On an In Progress task, add "Read the note" and then "Create the folder". The task lists them in that order, both Pending. A blank title stores nothing. Removing "Read the note" leaves "Create the folder".

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer adds "Read the note" as Read a file for an existing project and a file, **Then** the task lists that step as Pending, and opening the task again shows the same step.
2. **Given** that step, **When** the engineer adds "Create the folder" as Create a folder, **Then** "Read the note" stays first and "Create the folder" is second.
3. **Given** an In Progress task, **When** the engineer adds a step with a blank title, **Then** nothing is stored and the engineer is told `Name the step.`
4. **Given** an In Progress task, **When** the engineer chooses an action other than Read a file or Create a folder, **Then** nothing is stored and the engineer is told `Choose a step action.`
5. **Given** two Pending steps, **When** the engineer removes the first, **Then** the task no longer lists it. Removing a step that is not on the task is refused with `That step is not on this task.`
6. **Given** a task that is not In Progress, **When** the engineer adds or removes a step, **Then** nothing is stored. A Draft task is told `The task must be In Progress.` A Ready task is told `Start the task first.` A Completed task is told `Reopen the task first.` A Cancelled task is told `A cancelled task cannot be changed. Continued work is a new task.`

---

### User Story 2 - Advance one stored step and resume (Priority: P2)

The engineer advances the workflow. That request performs only the first step that is not Completed. A step that succeeds becomes Completed. The following step stays Pending. Advancing again performs that next step. Opening the workspace again shows the same step states, and the next advance continues at the first step that is not Completed. A Completed step is not performed again. When every step is Completed, another advance is refused with `There is no step to run.` Reading the task does not perform a step. Adding, removing, and advancing do not change the task status.

**Why this priority**: The stored list is useful once one advance does one step and a later opening continues there.

**Independent Test**: Add "Read the note" for a file that exists, then "Create the folder" as an ordinary folder. The first advance reads the file and leaves the folder uncreated. After the workspace is opened again, the read is still Completed, and the next advance creates the folder without reading the file again.

**Acceptance Scenarios**:

1. **Given** "Read the note" then "Create the folder", and the file exists, **When** the engineer advances once, **Then** "Read the note" is Completed, "Create the folder" stays Pending, and the folder is not created.
2. **Given** that recorded read, **When** the workspace is opened again and the engineer advances, **Then** "Create the folder" becomes Completed, the folder is created, and the file is not read again.
3. **Given** every step is Completed, **When** the engineer advances, **Then** nothing is performed and the engineer is told `There is no step to run.`
4. **Given** a stored step, **When** the engineer opens the task without advancing, **Then** no step is performed and no status changes.
5. **Given** a step that has left Pending, **When** the engineer adds or removes a step, **Then** the stored steps stay and the engineer is told `A step can be added only before the workflow runs.` or `A step cannot be removed after the workflow runs.`

---

### User Story 3 - Stop and name the step (Priority: P3)

A step that the action refuses becomes Failed. The workflow stops, and the task reports `Stopped at {title}: {message}` using that action's existing message. Later steps stay Pending and are not performed. Advancing again retries that Failed step and does not perform a later step. A Create a folder step that waits for approval becomes Waiting. The task reports `Stopped at {title}: waiting for approval.` Advancing again while it is still waiting does not record a second change. Approving or declining that change does not advance the workflow. The next advance, after approval, marks the step Completed without performing it again and leaves the next step Pending. The next advance, after a decline, marks the step Failed and uses the decline reason after the colon.

**Why this priority**: A run that continues past a failure or an approval is not safe to resume.

**Independent Test**: Advance "Read the note" while the file is missing. The step is Failed, the sentence names "Read the note" and says the file must already exist, and a following folder step stays Pending. Create the file and advance once. The read becomes Completed and the folder step stays Pending.

**Acceptance Scenarios**:

1. **Given** "Read the note" names a file that does not exist, and a folder step follows it, **When** the engineer advances, **Then** "Read the note" is Failed, the folder is not created, and the task reports `Stopped at Read the note: The file must already exist.`
2. **Given** that failure, **When** the file is created and the engineer advances once, **Then** "Read the note" is Completed and the folder step stays Pending.
3. **Given** a consequential "Create the folder" step and a later read, **When** the engineer advances, **Then** the folder is not created, the step is Waiting, and the task reports `Stopped at Create the folder: waiting for approval.`
4. **Given** that waiting step, **When** the engineer advances again before deciding the change, **Then** the step stays Waiting and no second change is recorded.
5. **Given** the engineer approves that change, **When** the engineer advances, **Then** the step is Completed, the folder exists, the action is not performed again, and the later step stays Pending.
6. **Given** the engineer declines that change with reason `Not this folder`, **When** the engineer advances, **Then** the step is Failed and the task reports `Stopped at Create the folder: Not this folder`. The later step stays Pending.

### Edge Cases

- A task with no steps, or with every step Completed, refuses the advance with `There is no step to run.`
- The first unfinished step is the one that advances. A later Pending step is not reached in that request.
- A Waiting step is not performed again. The stored change is read instead.
- A Failed step that the action refused can be retried by the next advance. That advance still does not perform the following step.
- Two steps may share a title. The step is identified on its own, and the sentence uses the title of the step that stopped.
- An ordinary folder that the action accepts is Completed. A consequential folder waits.
- Marking Ready, starting, completing, and cancelling keep their current rules. This feature does not start or complete the task.
- Read a file and Create a folder keep their current field rules. A commit, a branch, a pull request, a test, a deletion, and a model proposal stay on their own commands and are not workflow steps.
- One request adds one step, removes one step, or advances once.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to add and remove one workflow step on an In Progress task while every step is Pending. The task MUST list each step's title, action, and state in the order the steps were added. Opening the task MUST NOT add, remove, or perform a step.
- **FR-002**: A blank title MUST be refused with `Name the step.` An action other than Read a file or Create a folder MUST be refused with `Choose a step action.` A missing field MUST be refused with the message that action already uses. A refusal MUST store nothing. A step that is not on the task MUST be refused with `That step is not on this task.`
- **FR-003**: One advance MUST perform only the first step that is not Completed, store that step's resulting state, and leave every later step Pending. A Completed step MUST NOT be performed again, including after the workspace is opened again. When no such step remains, the advance MUST be refused with `There is no step to run.`
- **FR-004**: A refused action MUST store the step as Failed and the task MUST report `Stopped at {title}: {message}` with that action's message. The next advance MUST retry that step only. A step that waits for approval MUST stay Waiting, report `Stopped at {title}: waiting for approval.`, and MUST NOT record a second change when advanced again. After approval, the next advance MUST mark that step Completed without performing it again. After a decline, the next advance MUST mark it Failed and place the decline reason after the colon.
- **FR-005**: Adding, removing, and advancing MUST NOT change the task status. A task that is not In Progress MUST keep the existing status refusal. After a step has left Pending, adding a step MUST be refused with `A step can be added only before the workflow runs.` and removing a step MUST be refused with `A step cannot be removed after the workflow runs.`

### Key Entities

- **Workflow step**: One stored action on one task, with a title, an action, the fields that action needs, and one state: Pending, Completed, Waiting, or Failed.
- **Workflow**: The ordered steps of one task. The first step that is not Completed is the step an advance considers.
- **Stop sentence**: The sentence that names the Failed or Waiting step. It is absent while the next step is Pending or every step is Completed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can name each step, its order, and its state from the task, in under 2 minutes, including after the workspace is opened again.
- **SC-002**: In a review of advances, 100% perform only the first step that is not Completed.
- **SC-003**: In a review of failed and waiting steps, 100% leave later steps unperformed and name the step that stopped the run.
- **SC-004**: In a review of completed steps, 100% are not performed again on a later advance.

## Assumptions

- Specifications 001 through 019 are not rewritten. Ready still means a goal and an acceptance criterion. A workflow step does not change that.
- The workflow actions in this feature are Read a file and Create a folder. Their existing messages and approval rules stay. Other actions stay on their own commands.
- A step is stored before it is performed. The file or folder is checked when the step runs, not when the step is added.
- The engineer name and the time still come from the workspace. A client-supplied name or time is ignored.
- The stop sentence is shown on the task while a step is Failed or Waiting.
- The rules are covered by automated checks.
