# Feature Specification: Delete One File

**Feature Branch**: `013-delete-file`

**Created**: 2026-10-13

**Status**: Accepted

**Input**: User description: "Delete one file in the named project only after the engineer approves."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete one file after approval (Priority: P1)

On an In Progress task, the engineer names an existing project and one text file inside it. The request waits. The file stays until the engineer approves that change. Approval removes that one file. Opening the task again does not remove anything else.

**Why this priority**: Creating a folder and running a test can proceed when the engineer asks. Deleting a file removes durable data, so it waits for an approval that names this change.

**Independent Test**: On one In Progress task, ask to delete `label.txt` in an existing project `billing`. The file remains and the task shows Awaiting approval. After the engineer approves, `label.txt` is gone and a second opening does not delete another file.

**Acceptance Scenarios**:

1. **Given** an In Progress task and an existing text file `billing/label.txt`, **When** the engineer asks to delete it with the account "Remove the old label", **Then** the file remains, the task shows that file, the assistant, consequential, and Awaiting approval, and the task stays In Progress.
2. **Given** that waiting delete, **When** the engineer approves it and the file still has the same text, **Then** `label.txt` is removed and the task shows Carried out.
3. **Given** that stored delete, **When** the engineer opens the task again, **Then** the same record is shown and no other file is removed.
4. **Given** the same task, **When** the file name is blank, **Then** nothing is stored and the engineer is told `Name the file this change deletes.`
5. **Given** a project that does not exist, **When** the engineer asks for a delete, **Then** nothing is stored and the engineer is told `The project must already exist.`
6. **Given** `billing` exists and the named file does not, **When** the engineer asks for a delete, **Then** nothing is stored and the engineer is told `The file must already exist.`
7. **Given** a path that would leave the project, **When** the engineer asks for it, **Then** nothing is stored and the engineer is told `The file must stay inside the named project.`
8. **Given** a folder at the named path, **When** the engineer asks to delete it, **Then** nothing is stored and the engineer is told `The path is a folder.`
9. **Given** a link at the named path, **When** the engineer asks to delete it, **Then** the link and its target stay, nothing is stored, and the engineer is told `A link cannot be deleted by this change.`
10. **Given** a file that is not text, **When** the engineer asks to delete it, **Then** the file stays, nothing is stored, and the engineer is told `The file is not text.`
11. **Given** a waiting delete, **When** the assistant tries to approve it, **Then** the file stays and the engineer is told `The assistant cannot approve a change.`
12. **Given** a waiting delete, **When** the engineer declines it, **Then** the file stays.
13. **Given** a waiting delete whose file text has changed, **When** the engineer approves it, **Then** the file stays and the engineer is told `The file no longer matches the text this change was proposed against.`

### Edge Cases

- A wrong task status is reported before a blank project. The messages match recording a change.
- An ordinary request and a stopped request also wait. The file is not removed until the engineer approves.
- One request names one text file. It does not remove a folder, a link, or a second file.
- The delete does not record a requirement result, verify a criterion, record a check, or complete the task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On an In Progress task, the engineer MUST be able to ask for one named text file in an existing project to be deleted, with an account of what changed and a class of ordinary or consequential.
- **FR-002**: The request MUST be stored as consequential and Awaiting approval. The task MUST show the file, the text it had, and the assistant. The file MUST remain until the engineer approves that change.
- **FR-003**: The product MUST refuse a blank file, a missing project, a missing file, a path outside the project, a folder, a link, and a file that is not text, using the messages in the scenarios. A refusal MUST leave the project unchanged and MUST store nothing.
- **FR-004**: Approval MUST remove the file only when it is still that text file inside the project. The assistant MUST NOT approve. Decline MUST NOT remove the file. A file whose text changed MUST stay, with the mismatch message, and the request MUST stay Awaiting approval.
- **FR-005**: Opening the task MUST show the stored delete and MUST NOT remove another file.
- **FR-006**: Deleting a file MUST NOT record a requirement result, verify a criterion, record a check, or complete the task.

### Key Entities

- **Deleted file**: The project, the file path, and the text the file had when the delete was requested. The file is removed only when the engineer approves and that text is unchanged.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state, from the task record alone, which file was proposed for deletion and whether it was carried out, in under 2 minutes.
- **SC-002**: In a review of delete requests before approval, 100% leave the file in place.
- **SC-003**: In a review of approved deletes, 100% remove that one file once and leave the record readable after the task is opened again.

## Assumptions

- Specifications 001 through 012 are not rewritten. A file write, a folder, and a test run keep their current rules.
- Deleting a file removes durable data, so every delete waits for an approval that names this change. Choosing ordinary does not remove the file now.
- The engineer names one existing text file. The product does not accept an arbitrary command, and it does not remove a folder or a link.
- Committing and opening a pull request stay out of this action. Each waits for a later feature that names the approval.
