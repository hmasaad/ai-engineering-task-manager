# Feature Specification: Apply an Ordinary File

**Feature Branch**: `006-apply-ordinary-file`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "Move to stage 6. The next class of action applies one ordinary change inside the project the engineer names and records the file that was written. A consequential change, a stopped change, and a change that would overwrite an existing file still wait for the engineer's approval and do not change the project until that approval. The assistant does not verify criteria, choose Passed or Failed, record a decision, or complete the task."

## Clarifications

### Session 2026-10-07

- Q: When the engineer names the project folder, which folder on the computer is that? → A: A folder path. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The folder must already exist.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Write one new file (Priority: P1)

An engineer asks the assistant to carry out one ordinary change for an In Progress task in a project folder that already exists. The assistant has already produced the file: its place inside that project, and the text the file should contain. The product writes that new file, and the task shows the file, the text written, the project, the assistant, and Carried out. A later reader can see that record without the original conversation.

**Why this priority**: Stage 6 is the first time the assistant's ordinary work changes a project. Without the written file and the record of that file, the earlier account is only a report.

**Independent Test**: On one In Progress task, point at an existing project folder and ask the assistant to add one new ordinary file. The file is in the project with the submitted text, the task shows that file and Carried out, and the task stays In Progress.

**Acceptance Scenarios**:

1. **Given** an In Progress task "Add export" and an existing project folder "billing" relative to the folder where the task manager was started, and that folder has no file "notes/label.txt", **When** the engineer asks the assistant to carry out an ordinary change with the account "Rename the export label", the file "notes/label.txt", and the text "Export", **Then** that folder's "notes/label.txt" contains "Export", the task shows that account, the project path "billing", the file "notes/label.txt", that the file was new, the text "Export", the assistant, Carried out, and the time, and the task stays In Progress.
2. **Given** the same In Progress task, **When** the project folder name is empty or only spaces, **Then** nothing is written, nothing is stored, and the engineer is told to name the project this change is for.
3. **Given** the same In Progress task and a project folder name that does not exist, **When** the engineer asks the assistant to write a new file, **Then** nothing is written, nothing is stored, and the engineer is told the project must already exist.
4. **Given** an existing project folder and a blank or whitespace account, **When** the engineer asks the assistant to write a file, **Then** nothing is written, nothing is stored, and the engineer is told an account of what changed is required.
5. **Given** an existing project folder and an account, **When** the class is missing or is neither ordinary nor consequential, **Then** nothing is written, nothing is stored, and the engineer is told to choose ordinary or consequential.
6. **Given** an existing project folder, an account, and the class ordinary, **When** the file name is empty or only spaces, **Then** nothing is written, nothing is stored, and the engineer is told to name the file this change writes.
7. **Given** an existing project folder, **When** the file name points outside that folder, **Then** nothing is written, nothing is stored, and the engineer is told the file must stay inside the named project.
8. **Given** an existing project folder that has no folder "notes", **When** the file name is "notes/label.txt", **Then** nothing is written, nothing is stored, and the engineer is told the folder for that file must already exist.
9. **Given** a task that is Draft, **When** the engineer asks the assistant to write a file, **Then** nothing is written and the engineer is told the task must be In Progress.
10. **Given** a task that is Ready, **When** the engineer asks the assistant to write a file, **Then** nothing is written and the engineer is told to start the task first.
11. **Given** a task that is Completed, **When** the engineer asks the assistant to write a file, **Then** nothing is written and the engineer is told to reopen the task first.
12. **Given** a task that is Cancelled, **When** the engineer asks the assistant to write a file, **Then** nothing is written and the engineer is told that a cancelled task cannot be changed and continued work is a new task.
13. **Given** a task that is not In Progress and a blank project, a blank account, and a blank file name, **When** the engineer asks the assistant to write a file, **Then** the engineer is told the status problem, and nothing is written.
14. **Given** an unknown task, **When** the engineer asks the assistant to write a file, **Then** the engineer is told the task was not found, and nothing is written.
15. **Given** an In Progress task and an existing folder for the file, **When** the new file's text is empty, **Then** the file is created empty, the task shows that empty text, and the account is still required.

---

### User Story 2 - Wait before changing a file that is already there (Priority: P2)

A request that would overwrite a file, a consequential request, or an ordinary request the assistant stops, does not change the project. The task shows the proposal as Awaiting approval, including the text already in the file when there was one, and the text the assistant proposed. The engineer approves or declines later. Approval writes the file. Decline does not. The assistant cannot approve or decline.

**Why this priority**: Writing a new file can be ordinary. Replacing durable text, or any consequential effect, stays outside that boundary until the engineer approves that file.

**Independent Test**: On one In Progress task, ask the assistant to replace an existing file, or to stop an ordinary new file. The file on disk is unchanged and the task shows Awaiting approval until the engineer approves or declines.

**Acceptance Scenarios**:

1. **Given** an In Progress task and an existing file "notes/label.txt" whose text is "Old", **When** the engineer asks the assistant for an ordinary change that would write "Export" into that file, **Then** the file still contains "Old", and the task shows the account, the project, the file, the text "Old", the proposed text "Export", the assistant, and Awaiting approval.
2. **Given** an In Progress task and no such file, **When** the engineer asks the assistant for a consequential change that would create "notes/label.txt" with the text "Export", **Then** the file is not created and the task shows Awaiting approval, the file, that the file was new, and the proposed text "Export".
3. **Given** an ordinary request for a new file, **When** the engineer asks the assistant to stop before carrying it out, **Then** the file is not created and the task shows Awaiting approval.
4. **Given** a waiting proposal whose file was new, **When** the engineer approves it and names the evidence reviewed, **Then** the file is created with the proposed text, the task shows Carried out, and the approval names the engineer and the time.
5. **Given** a waiting proposal to replace "Old" with "Export", **When** the engineer approves it and the file still contains "Old", **Then** the file contains "Export", the task shows the text that was replaced and the text written, Carried out, and the approval names the engineer.
6. **Given** a waiting proposal to replace "Old" with "Export", **When** the file now contains something other than "Old" and the engineer approves it, **Then** the file is left as it is, the proposal stays Awaiting approval, and the engineer is told the file no longer matches the text this change was proposed against.
7. **Given** a waiting proposal for a new file, **When** that file has appeared before approval, **Then** approval does not overwrite it, the proposal stays Awaiting approval, and the engineer is told the file no longer matches the text this change was proposed against.
8. **Given** a waiting proposal, **When** the engineer marks it not carried out and gives a reason, **Then** the project is unchanged, the task shows Not carried out and the reason, and a later approval is refused.
9. **Given** a waiting proposal, **When** the assistant tries to approve or decline it, **Then** nothing is written, no approval or decline is stored, and the engineer is told the assistant cannot approve a change or cannot decline a change.
10. **Given** an ordinary new file that is already Carried out, **When** the engineer tries to approve it, **Then** the file is not written again.

---

### User Story 3 - Read the written file without asking again (Priority: P3)

The stored record is what a later reader and a later replay use. Reading the task shows the file, whether it was new, the text it had, the text written or proposed, the assistant, and the outcome. Repeating that stored record does not write the file again and does not ask the assistant to produce the text again.

**Why this priority**: A written file that cannot be reconstructed from the task record cannot be checked after the conversation is gone.

**Independent Test**: Write one ordinary new file, read the task, and replay that stored record. The second pass shows the same file, text, assistant, and outcome, and the file is not written again.

**Acceptance Scenarios**:

1. **Given** a stored ordinary file change, **When** a reader opens the task, **Then** the reader can see the account, the project, the file, whether the file was new, the text it had, the text written, the assistant, Carried out, and the time.
2. **Given** the same stored change, **When** that record is replayed, **Then** the task shows the same file, text, assistant, and outcome, and the file in the project is not modified again.
3. **Given** an assistant file change on a subtask, **When** a reader opens the parent task, **Then** the parent does not list that change, and the file record stays on the subtask.
4. **Given** an assistant change stored before this feature, with an account and a project but no file, **When** a reader opens the task, **Then** that earlier change is still shown and no file is written for it.
5. **Given** an engineer recording a change with no file, **When** the change is saved, **Then** the named project is not modified.
6. **Given** an assistant file change that is Carried out, **When** the engineer completes the task, **Then** completion still waits until that change has a passing check. The assistant does not record the check, choose Passed or Failed, record a decision, or mark the task completed.

---

### Edge Cases

- A project folder path, an account, or a file name that is only spaces is refused, and no partial file or record is stored.
- An absolute project path is used as given. A relative project path is resolved from the folder where the task manager was started. A path that does not exist is refused.
- If the project folder is blank and the file name is also blank, the engineer is told to name the project this change is for.
- A file name that uses a parent step, such as one that climbs out of the project folder, is refused, and nothing outside the project is written.
- The product creates the named file only. It does not create the project folder, and it does not create a missing folder inside the project.
- An empty file text is a real new file. The account of what changed is still required.
- One request writes or proposes one file. A second file is a second request.
- The product does not treat the assistant's confidence as approval. A consequential change, a stopped change, and a replacement of an existing file stay Awaiting approval until the engineer approves that change in a separate action.
- Approval writes the proposed text only when the file still matches the text recorded with the proposal. A file that appeared or changed after the proposal is left alone.
- The assistant does not verify an acceptance criterion, record a check, record a decision, complete a task, or cancel a task.
- Two requests recorded in the same order, with the same stored file and text, produce the same outcomes and the same order, and the second pass does not write the file again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to ask the assistant to carry out one file change for a task that is In Progress by naming an existing project folder, naming one file inside that folder, stating whether the change is ordinary or consequential, stating whether to stop before writing, providing the account of what changed, and providing the text the file should contain. The project name is a folder path. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The task record shows that path.
- **FR-002**: For an ordinary change that is not stopped, when the file does not already exist and its folder does, the product MUST write that file with the submitted text. The task MUST show the account, the project, the file, that the file was new, the text written, the assistant, Carried out, and the time. The task status MUST stay In Progress.
- **FR-003**: The product MUST refuse a blank project folder with `Name the project this change is for.` It MUST refuse a missing project folder with `The project must already exist.` It MUST refuse a blank account with `An account of what changed is required.` It MUST refuse a missing or unknown class with `Choose ordinary or consequential.` It MUST refuse a blank file name with `Name the file this change writes.` It MUST refuse a file outside the project with `The file must stay inside the named project.` It MUST refuse a missing destination folder with `The folder for that file must already exist.` A refusal MUST leave the project and the task unchanged.
- **FR-004**: The product MUST refuse the request when the task is Draft, Ready, Completed, or Cancelled, with the same messages used when the engineer records a change. A wrong status is reported before a blank project, a missing folder, a blank account, or a blank file name. An unknown task is reported as `Task not found.`
- **FR-005**: A consequential request, an ordinary request that is stopped, and an ordinary request that names a file that already exists MUST NOT change the project. The task MUST show the account, the project, the file, the text the file already had or that the file was new, the proposed text, the assistant, and Awaiting approval. The task status MUST stay In Progress.
- **FR-006**: The engineer MUST be able to approve a waiting file proposal by naming the evidence reviewed. Approval MUST write the proposed text only when the file still matches the recorded text, or when the file is still absent for a proposal that said the file was new. The approval MUST name the engineer and the time, and the outcome MUST become Carried out. If the file no longer matches, the product MUST leave the file and the proposal unchanged and tell the engineer `The file no longer matches the text this change was proposed against.`
- **FR-007**: The engineer MUST be able to mark a waiting file proposal not carried out by giving a reason. The project MUST stay unchanged. The assistant MUST NOT be able to approve or decline. Those attempts MUST be told `The assistant cannot approve a change.` and `The assistant cannot decline a change.` and MUST store nothing further.
- **FR-008**: A stored file change MUST NOT be edited or removed. Replaying that stored record MUST show the same file, text, assistant, and outcome, and MUST NOT write the file again or ask the assistant to produce the text again.
- **FR-009**: An assistant file change MUST name exactly one task, one project, one file, and the assistant. A change on a subtask MUST NOT appear as a change of the parent. An earlier assistant change that has no file MUST remain readable and MUST NOT cause a file to be written.
- **FR-010**: Recording a file change MUST NOT verify a criterion, record a check, record a decision, or change the task status. Completing the task MUST still wait until a carried-out change has a passing check. The assistant MUST NOT record that check, record a decision, or complete or cancel the task.
- **FR-011**: An engineer recording a change without a file MUST NOT modify the named project.
- **FR-012**: One request MUST write or propose at most one file, and that file MUST stay inside the project named for that request.

### Key Entities *(include if feature involves data)*

- **Applied File**: The one file an assistant change writes or proposes. It has its place inside the named project, whether it was new, the text it had when the request was recorded, and the text written or proposed. The assistant change it belongs to is the change from the previous stage.
- **Project Folder**: The existing folder the engineer names for that request, given as a path. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The product does not create it. The file stays inside it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, which file was written or proposed, what text it had, what text was written or proposed, which project it was in, and whether it was carried out, in under 2 minutes.
- **SC-002**: In a review of ordinary new-file changes, 100% leave that file in the named project with the submitted text, and the task names exactly one file, the assistant, Carried out, and a time.
- **SC-003**: In a review of consequential requests, stopped requests, and requests that name an existing file, 100% leave that file unchanged until the engineer approves the proposal.
- **SC-004**: In a review of approvals where the file changed after the proposal, 100% leave the file untouched and leave the proposal Awaiting approval.
- **SC-005**: Two passes of the same stored file record produce the same file, text, assistant, outcome, and order, and the second pass does not modify the file.
- **SC-006**: At least 95% of engineers ask the assistant to add one new file and find that file both in the project and on the task on the first attempt without assistance.
- **SC-007**: In a review of approval actions on file proposals, 100% of approvals name the engineer. No assistant approval is stored, and no assistant approval writes a file.

## Assumptions

- The assistant record from the previous stage is already in place. This feature adds the file that record writes or proposes. It does not add people, sharing, or a second approver.
- The text of the file is the text the assistant has already produced. The product does not ask the assistant to produce it again, and it does not invent the text.
- The engineer names an existing project folder by a path and says whether the request is ordinary or consequential. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The product does not infer the class from the file text. Replacing an existing file is treated as consequential even when the engineer said ordinary: the file is left unchanged until the engineer approves that proposal.
- Creating a missing folder, deleting a file, changing permissions, spending money, contacting an external party, merging, and deploying stay out of this action. Those requests are not given a special new form; a consequential choice or a stop still waits, and this feature does not carry them out on its own.
- The assistant has a name, distinct from the engineer. The written file and the proposal show that name. Approval and decline still show the engineer.
- An earlier assistant change that recorded only an account and a project stays valid. This feature does not go back and write a file for it.
- The engineer can still record changes, checks, and decisions. Those actions do not write a project file. The assistant does not take those actions.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools stay out of scope.
- These rules follow the project constitution: this is the next class of autonomous action, the written file and its text are on the task, replay uses the stored record, and a consequential action or an overwrite still waits for a named human approval.
