# Feature Specification: Instruction Page

**Feature Branch**: `023-instruction-page`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Create a webpage so the engineer can manage the instructions there. The page takes the task, what we want to achieve, and which file the model may change, and the model can start working on that task."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set the model on the page (Priority: P1)

The engineer opens Instructions and sees the model name and the text that model returns. Saving a name and text makes that the model for later work. Opening the workspace again shows the same name and text. A blank name is refused with `Choose the model this change uses.` A blank text is refused with `Name the text the model returns.` Nothing is saved in either case.

**Why this priority**: Work cannot start until the engineer can name the model without leaving the page.

**Independent Test**: Save the model name "Guide" and the text "Export". Open the workspace again. Instructions still shows "Guide" and "Export".

**Acceptance Scenarios**:

1. **Given** no model has been saved, **When** the engineer opens Instructions, **Then** the model name and the model text are empty.
2. **Given** the engineer saves the name "Guide" and the text "Export", **When** the workspace is opened again, **Then** Instructions shows that name and that text.
3. **Given** a saved model, **When** the engineer saves a blank name, **Then** the saved model stays and the engineer is told `Choose the model this change uses.`
4. **Given** a saved model, **When** the engineer saves a blank text, **Then** the saved model stays and the engineer is told `Name the text the model returns.`

---

### User Story 2 - Start work from one instruction (Priority: P2)

The engineer writes the task title, the goal, one acceptance criterion, the project, the file to read, the file to change, whether the change is ordinary or consequential, and what changed. Starting work creates that task, marks it Ready, starts it, reads the named file, and asks the saved model once for the file to change. The engineer then sees that task. A new ordinary file is written with the model's text. A file that already exists waits for approval and is not replaced yet. A missing field, a missing project, or a missing file stores nothing.

**Why this priority**: One page is useful once starting work performs the read and the one model change.

**Independent Test**: With the model text "Export", start work for a new ordinary file in an existing project. The task is In Progress, the file contains "Export", and the task shows one file read and that model text.

**Acceptance Scenarios**:

1. **Given** a saved model that returns "Export", an existing project, and an existing file to read, **When** the engineer starts work for a new ordinary file, **Then** the task is In Progress, that file contains "Export", one file read is stored, and the model was asked once.
2. **Given** the file to change already exists, **When** the engineer starts work, **Then** the task is In Progress, the file is unchanged, and the change is waiting for approval.
3. **Given** no model has been saved, **When** the engineer starts work, **Then** nothing is stored and the engineer is told `Choose the model this change uses.`
4. **Given** a blank title, goal, criterion, project, file to read, file to change, class, or account, **When** the engineer starts work, **Then** nothing is stored and the existing message for that field is shown.
5. **Given** a project or a file to read that does not exist, **When** the engineer starts work, **Then** nothing is stored and the existing message for that problem is shown.

---

### User Story 3 - Find the page from the task list (Priority: P3)

The task list links to Instructions. Instructions links back to all tasks. The engineer can open the page, save the model, and start work from the browser.

**Why this priority**: The instructions are reachable with the tasks the engineer already uses.

**Independent Test**: Open the task list. Follow Instructions. The page shows the model fields and the task fields, including the file to read and the file to change.

**Acceptance Scenarios**:

1. **Given** the task list, **When** the engineer opens Instructions, **Then** the page shows the model name, the model text, the title, the goal, the acceptance criterion, the project, the file to read, the file to change, ordinary or consequential, and what changed.
2. **Given** that page, **When** the engineer starts work successfully, **Then** the task is shown.

### Edge Cases

- The model text is kept as the engineer entered it, including a trailing line break. Only a blank text is refused.
- A name with surrounding spaces is the trimmed name. The text itself is stored as entered when it is not blank.
- Starting work asks the model once. Approval of a waiting change does not ask the model again.
- The model changes one file. Read a file and the existing model proposal stay available on the task afterward.
- One request saves the model or starts one piece of work.
- Starting work does not complete the task and does not approve a waiting change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Instructions MUST show the saved model name and the text that model returns. Saving MUST keep that name and text for the next time the workspace is opened. A blank name MUST be refused with `Choose the model this change uses.` A blank text MUST be refused with `Name the text the model returns.`
- **FR-002**: Starting work MUST create one In Progress task from the title, goal, and acceptance criterion, read the named file once, and ask the saved model once for the file to change.
- **FR-003**: A new ordinary file MUST contain the model text. A file that already exists MUST stay unchanged and wait for approval. Starting work MUST NOT approve that change.
- **FR-004**: A missing model, a blank field, a missing project, or a missing file to read MUST store nothing and MUST use the message already used for that problem, except the blank model text message in FR-001.
- **FR-005**: The task list MUST link to Instructions. After work starts, the engineer MUST see that task.

### Key Entities

- **Saved model**: The name and the text returned for one file, kept with the workspace.
- **Instruction**: The title, goal, acceptance criterion, project, file to read, file to change, class, and account of what changed for one start.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer can save a model and see it again after the workspace is opened, in under 2 minutes.
- **SC-002**: In a review of successful starts, 100% leave one In Progress task, one file read, and one model result.
- **SC-003**: In a review of refused starts, 100% leave no task and no file.
- **SC-004**: An engineer can open Instructions from the task list and start work without a second page for the model.

## Assumptions

- Specifications 001 through 022 are not rewritten. The model still proposes one file from one stored file read. A replacement still waits for approval.
- The page is available while the task manager is running. The engineer name and the time still come from the workspace.
- The file to read must already exist. The file to change may be new or already present.
- The rules are covered by automated checks.
