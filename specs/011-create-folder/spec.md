# Feature Specification: Create One Folder

**Feature Branch**: `011-create-folder`

**Created**: 2026-10-13

**Status**: Accepted

**Input**: User description: "The assistant can create one folder inside a project that already exists."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create one folder (Priority: P1)

On an In Progress task, the engineer names an existing project and one new folder inside it. An ordinary request creates that folder. The project folder itself must already exist, and so must the folder that holds the new one. The task shows the folder, the assistant, and Carried out.

**Independent Test**: On one In Progress task, ask for an ordinary folder `notes` inside an existing project `billing`. The folder exists on disk and the task stays In Progress.

**Acceptance Scenarios**:

1. **Given** an In Progress task and an existing project `billing`, **When** the engineer asks for an ordinary folder `notes` with the account "Add the notes folder", **Then** `billing/notes` exists, the task shows that folder, the assistant, and Carried out, and the task stays In Progress.
2. **Given** the same task, **When** the folder name is blank, **Then** nothing is created and the engineer is told `Name the folder this change creates.`
3. **Given** a project that does not exist, **When** the engineer asks for a folder, **Then** nothing is created and the engineer is told `The project must already exist.`
4. **Given** `billing` exists and `billing/notes` does not, **When** the engineer asks for `notes/export`, **Then** nothing is created and the engineer is told `The folder that holds this one must already exist.`
5. **Given** `billing/notes` already exists, **When** the engineer asks for `notes`, **Then** nothing is stored and the engineer is told `The folder already exists.`
6. **Given** a file at `billing/label.txt`, **When** the engineer asks for a folder `label.txt`, **Then** nothing is stored and the engineer is told `A file is already at that path.`
7. **Given** a folder name that would leave the project, **When** the engineer asks for it, **Then** nothing is created and the engineer is told `The folder must stay inside the named project.`
8. **Given** a consequential request or an ordinary request that is stopped, **When** the engineer asks for `notes`, **Then** the folder is not created and the task shows Awaiting approval. Approval by the engineer creates it. The assistant cannot approve.

### Edge Cases

- A wrong task status is reported before a blank project. The messages match recording a change.
- One request creates one folder. It does not create the project and it does not create missing parents.
- Opening the task does not create the folder again.
- A file write still refuses a missing destination folder. This feature does not change that rule.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On an In Progress task, the engineer MUST be able to ask the assistant to create one folder in a named existing project, with an account of what changed and a class of ordinary or consequential.
- **FR-002**: An ordinary request that is not stopped MUST create that one folder when it is absent, its parent exists, and it stays inside the project. The task MUST show the folder, the assistant, and Carried out.
- **FR-003**: The product MUST refuse a blank folder, a missing project, a missing parent, an existing folder, a file at that path, and a path outside the project, using the messages in the scenarios. A refusal MUST leave the project unchanged and MUST store nothing, except a consequential or stopped request, which stores Awaiting approval and does not create the folder.
- **FR-004**: Approval of a waiting folder MUST create it when the path still matches. The assistant MUST NOT approve. Decline MUST NOT create the folder.
- **FR-005**: Creating a folder MUST NOT verify a criterion, record a check, or complete the task.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state, from the task record alone, which folder was created and whether it was carried out, in under 2 minutes.
- **SC-002**: In a review of ordinary new folders, 100% exist on disk once and name the assistant.
- **SC-003**: In a review of refused folder requests, 100% leave the project unchanged.

## Assumptions

- Specifications 001 through 010 are not rewritten. A file write still requires the destination folder to exist already.
- Creating a folder does not delete or overwrite durable data. A request that would replace an existing folder or file is refused and stores nothing.
- Running a test, deleting a file, committing, and opening a pull request stay out of this action. Delete, commit, and a pull request are consequential and wait for a later feature that names the approval.
