# Feature Specification: Read a Project File

**Feature Branch**: `007-read-project-file`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "On an In Progress task, the engineer names an existing project and one text file inside it. The product stores the text it read, the path, the project, and the assistant. It does not call a model and does not change the file. A later replay shows that stored text and does not read the file again."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read one text file (Priority: P1)

An engineer asks for one existing text file to be read for an In Progress task in a project folder that already exists. The product stores the text it read, the file's place inside that project, the project, and the assistant. The file is left as it was. No model is asked to produce or interpret the text. A later reader can see that stored text without the original conversation and without opening the project.

**Why this priority**: The assistant cannot yet see a file in the project. A stored read is the record a later model call can use. Without it, the only text on the task is text the engineer already typed.

**Independent Test**: On one In Progress task, name an existing project folder and one text file inside it. The task shows that file's text, its path, the project, and the assistant, and the file in the project is unchanged.

**Acceptance Scenarios**:

1. **Given** an In Progress task "Add export" and an existing project folder "billing" relative to the folder where the task manager was started, and "notes/label.txt" in that folder contains "Export", **When** the engineer asks for that file to be read, **Then** the task shows the path "notes/label.txt", the text "Export", the project path "billing", the assistant, and the time, the file still contains "Export", and the task stays In Progress.
2. **Given** the same In Progress task, **When** the project folder name is empty or only spaces, **Then** nothing is stored, no file is changed, and the engineer is told to name the project this change is for.
3. **Given** the same In Progress task and a project folder name that does not exist, **When** the engineer asks for a file to be read, **Then** nothing is stored, no file is changed, and the engineer is told the project must already exist.
4. **Given** an existing project folder, **When** the file name is empty or only spaces, **Then** nothing is stored, no file is changed, and the engineer is told to name the file this change reads.
5. **Given** an existing project folder, **When** the file name points outside that folder, **Then** nothing is stored, nothing outside the project is changed, and the engineer is told the file must stay inside the named project.
6. **Given** an existing project folder that has no file "notes/label.txt", **When** the engineer asks for that file to be read, **Then** nothing is stored and the engineer is told the file must already exist.
7. **Given** an existing project folder and a file that is not text, including a folder at that path, **When** the engineer asks for that file to be read, **Then** nothing is stored, the file is unchanged, and the engineer is told the file is not text.
8. **Given** an existing empty text file, **When** the engineer asks for that file to be read, **Then** the task shows that empty text, and the file stays empty.
9. **Given** a task that is Draft, **When** the engineer asks for a file to be read, **Then** nothing is stored and the engineer is told the task must be In Progress.
10. **Given** a task that is Ready, **When** the engineer asks for a file to be read, **Then** nothing is stored and the engineer is told to start the task first.
11. **Given** a task that is Completed, **When** the engineer asks for a file to be read, **Then** nothing is stored and the engineer is told to reopen the task first.
12. **Given** a task that is Cancelled, **When** the engineer asks for a file to be read, **Then** nothing is stored and the engineer is told that a cancelled task cannot be changed and continued work is a new task.
13. **Given** a task that is not In Progress and a blank project and a blank file name, **When** the engineer asks for a file to be read, **Then** the engineer is told the status problem, and nothing is stored.
14. **Given** an unknown task, **When** the engineer asks for a file to be read, **Then** the engineer is told the task was not found, and nothing is stored.
15. **Given** an In Progress task and a file whose text is "Export ", including the trailing space, **When** the engineer asks for that file to be read, **Then** the task shows "Export " and the file still contains "Export ".

---

### User Story 2 - Read the stored text again (Priority: P2)

The stored read is what a later reader and a later replay use. Opening the task shows the text that was read, the path, the project, and the assistant. Repeating that stored record does not read the file again. A later edit to the file does not change the stored text.

**Why this priority**: A read that is fetched again from the project can change after the conversation is gone. The record has to stay the text that was read.

**Independent Test**: Read one text file, change that file, then open the task and replay the stored read. The task still shows the original text, and the replay does not read the file again.

**Acceptance Scenarios**:

1. **Given** a stored read of "notes/label.txt" whose text was "Export", **When** a reader opens the task, **Then** the reader can see the path, the text "Export", the project, the assistant, and the time.
2. **Given** the same stored read, **When** that record is replayed after the file has been changed to "Newer", **Then** the task still shows "Export", the file is left as "Newer", and the file is not read again.
3. **Given** a stored read, **When** the file is later deleted, **Then** the task still shows the text that was read.
4. **Given** a stored read of "Export", **When** the engineer asks for the same file to be read again after it contains "Newer", **Then** the task shows both reads, oldest first, the first still "Export" and the second "Newer".
5. **Given** a stored read on a subtask, **When** a reader opens the parent task, **Then** the parent does not list that read, and the read stays on the subtask.

---

### User Story 3 - Leave the project and the other records alone (Priority: P3)

A read does not write a file, does not call a model, and does not become an implementation change. Earlier assistant changes stay as they were. Completing the task still follows the existing rules. The assistant does not check a criterion, record a decision, or complete the task.

**Why this priority**: Seeing a file must not be treated as carrying out a change, and it must not weaken the approval and check rules already in place.

**Independent Test**: Read one file on a task that also has a carried-out file change. The read is shown separately, the project file is unchanged, and completing the task still waits for a passing check of that carried-out change.

**Acceptance Scenarios**:

1. **Given** an In Progress task and an existing text file, **When** the engineer asks for that file to be read, **Then** no implementation change is added, and the task does not show a class, Carried out, or Awaiting approval for that read.
2. **Given** a carried-out assistant file change that still needs a passing check, **When** a read of another file is stored and the engineer completes the task, **Then** completion still waits until that carried-out change has a passing check.
3. **Given** a waiting proposal to replace a file, **When** the engineer asks for that file to be read, **Then** the proposal stays Awaiting approval, the file is unchanged, and the read shows the text the file has now.
4. **Given** an assistant change stored before this feature, **When** a reader opens the task, **Then** that earlier change is still shown, and no file is written or read for it.
5. **Given** an engineer recording a change with no file, **When** the change is saved, **Then** no project file is read into the task and the named project is not modified.
6. **Given** a stored read, **When** the engineer completes or cancels the task, **Then** the read stays visible. The assistant does not record the check, choose Passed or Failed, record a decision, or mark the task completed or cancelled.

---

### Edge Cases

- A project folder path or a file name that is only spaces is refused, and no partial read is stored.
- An absolute project path is used as given. A relative project path is resolved from the folder where the task manager was started. A path that does not exist, or that names a file rather than a folder, is refused with `The project must already exist.`
- If the project folder is blank and the file name is also blank, the engineer is told to name the project this change is for.
- A wrong task status is reported before a blank project or a blank file name. An unknown task is reported as `Task not found.`
- A file name that uses a parent step, such as one that climbs out of the project folder, is refused with `The file must stay inside the named project.`, and nothing outside the project is stored or changed.
- A link is followed. If the file would land outside the resolved project folder, the request is refused with `The file must stay inside the named project.` and nothing is stored. A link that stays inside the project is allowed, and the stored text is the text that link reaches. The stored path is the path the engineer named.
- A missing file, including a file whose folder inside the project does not exist, is refused with `The file must already exist.` The product does not create that folder.
- A file that cannot be read as text, and a folder at the named path, are refused with `The file is not text.` Nothing is stored, and the file is unchanged. An empty file is text.
- The text stored is the file's text as it was read, including spaces at either end. The product does not trim that text, summarize it, or ask a model for it.
- The project path shown is the path the engineer typed, after surrounding spaces are removed. The file path shown is its place inside that project.
- One request reads one file. A second file is a second request. Two reads of the same file are two records, oldest first.
- Opening the task does not read the file again and does not change it.
- The product does not write, replace, or delete the file. It does not create the project folder.
- A read is not an implementation change. It does not wait for approval, and it does not add a new reason to refuse completion or cancellation.
- The assistant does not verify an acceptance criterion, record a check, record a decision, complete a task, or cancel a task.
- Two requests recorded in the same order, against the same file text, produce the same stored text and the same order. Replaying a stored read does not read the file again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to ask for one existing text file to be read for a task that is In Progress by naming an existing project folder and naming one file inside that folder. The project name is a folder path. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The task record shows that path, the file's place inside the project, the text read, the assistant, and the time. The task status MUST stay In Progress.
- **FR-002**: The product MUST NOT call a model to choose the file, produce the text, or interpret it. The stored text MUST be the text read from that file. The product MUST NOT write, replace, or delete the file, and MUST NOT create the project folder or a folder inside it.
- **FR-003**: The product MUST refuse a blank project folder with `Name the project this change is for.` It MUST refuse a missing project folder with `The project must already exist.` It MUST refuse a blank file name with `Name the file this change reads.` It MUST refuse a file outside the project with `The file must stay inside the named project.` It MUST refuse a missing file with `The file must already exist.` It MUST refuse a file that cannot be read as text with `The file is not text.` A refusal MUST leave the project and the task unchanged, and MUST store no read.
- **FR-004**: The product MUST refuse the request when the task is Draft, Ready, Completed, or Cancelled, with the same messages used when the engineer records a change. A wrong status is reported before a blank project or a blank file name. An unknown task is reported as `Task not found.`
- **FR-005**: A stored read MUST NOT be edited or removed. Opening the task and replaying that stored record MUST show the same text, path, project, and assistant, and MUST NOT read the file again. A later change to the file, including deletion, MUST NOT change the stored text.
- **FR-006**: A read MUST name exactly one task, one project, one file, and the assistant. A second read of the same file MUST be a separate record. Reads on a task MUST stay listed oldest first. A read on a subtask MUST NOT appear as a read of the parent.
- **FR-007**: A read MUST NOT be stored as an implementation change. It MUST NOT show a class, Carried out, or Awaiting approval. It MUST NOT verify a criterion, record a check, record a decision, or change the task status. Completing or cancelling the task MUST NOT gain a new refusal because of the read. A carried-out change MUST still need a passing check before completion. The assistant MUST NOT record that check, record a decision, or complete or cancel the task.
- **FR-008**: An engineer recording a change without a file MUST NOT read a project file into the task and MUST NOT modify the named project. An earlier assistant change MUST remain readable. This feature MUST NOT write a file for it and MUST NOT invent a read for it.
- **FR-009**: One request MUST read at most one file, and that file MUST stay inside the project named for that request. The product MUST follow links. It MUST refuse, with `The file must stay inside the named project.`, when the resolved file would land outside the resolved project folder, and it MUST store nothing for that request. A link that stays inside the project is allowed.

### Key Entities *(include if feature involves data)*

- **File Read**: One stored observation of one text file for one task. It has the file's place inside the named project, the text read at that time, the project, the assistant, and the time. It is not an implementation change. A later read of the same file is a new file read.
- **Project Folder**: The existing folder the engineer names for that request, given as a path. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The product does not create it. The file stays inside it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, which file was read, the text that was read, which project it was in, and which assistant it is attributed to, in under 2 minutes.
- **SC-002**: In a review of successful reads, 100% leave the file's text unchanged, name exactly one file, one project, and the assistant, and show the text that was in the file.
- **SC-003**: In a review of refused reads, 100% store nothing and leave every named file unchanged.
- **SC-004**: Two passes of the same stored read produce the same text, path, project, assistant, and order, and the second pass does not read the file again.
- **SC-005**: In a review of reads whose file was changed after the read, 100% still show the original stored text.
- **SC-006**: At least 95% of engineers ask for one existing text file to be read and find that text, the path, the project, and the assistant on the task on the first attempt without assistance.
- **SC-007**: In a review of tasks that have both a read and a carried-out change, 100% still require a passing check of that change before completion, and no read is stored as a change awaiting approval.

## Assumptions

- The task, the implementation record, the check, the decision, and the written or proposed file are already in place. This feature adds one read of one existing text file. It does not add a model call, a file write, people, sharing, or a second approver.
- The engineer names the project and the file. The product reads that file. It does not choose a different file, and it does not ask a model to produce the text.
- The project name is a folder path, using the same rule as the previous feature. An absolute path is used as given. A relative path is resolved from the folder where the task manager was started. The folder must already exist. The task shows the path the engineer typed, after surrounding spaces are removed.
- The file must already exist inside that project. A missing folder inside the project is refused as a missing file. The same boundary as the previous feature applies: links are followed, a file that would land outside the resolved project folder is refused, and a link that stays inside is allowed.
- Text has the same meaning as in the previous feature. An empty file is text. A folder at the named path is not text. A file the product cannot read as characters is not text. The stored text keeps the file's spaces; it is not trimmed.
- The assistant has a name, distinct from the engineer. The read shows that name. A name supplied with the request is not the name stored.
- A read is a record of its own. It is not an ordinary or consequential implementation change, it does not need an account of what changed, and it does not wait for approval because it does not change the project.
- Creating a missing folder, writing or deleting a file, changing permissions, spending money, contacting an external party, merging, and deploying stay out of this action.
- The engineer can still record changes, checks, and decisions. Those actions do not read a project file. The assistant does not take those actions.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools stay out of scope.
- These rules follow the project constitution: this is the next class of autonomous action, the read is on the task, replay uses the stored text, and this class does not change the project.
