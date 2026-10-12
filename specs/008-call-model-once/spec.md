# Feature Specification: Call the Model Once

**Feature Branch**: `008-call-model-once`

**Created**: 2026-10-12

**Status**: Accepted

**Input**: User description: "On an In Progress task, one model call takes the task plus one stored file read and returns the text for one file. Store the model name and the returned text. A later replay uses that stored text and does not call the model again. Writing follows the ordinary-file rules: a new file can be ordinary, and a replacement waits for approval. The assistant does not check a criterion, record a decision, or complete the task."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask the model for one new file (Priority: P1)

An engineer asks the model to propose one new file for an In Progress task. The request names an existing project, one file inside it, one stored file read on that task, whether the change is ordinary or consequential, and the account of what changed. The product calls the configured model once. The call's input is the task and that stored read. The returned text is the file text. For an ordinary request that is not stopped, and a file that does not already exist, the product writes that file and the task shows the model name, the returned text, the file, the project, the assistant, and Carried out.

**Why this priority**: A stored file read is useful only when a later model call can turn it into one file. The call has to be recorded so a later reader does not need the conversation or a second call.

**Independent Test**: On one In Progress task with one stored file read, ask for one new ordinary file. The model is called once, the new file contains the returned text, and the task shows the model name, that text, and Carried out.

**Acceptance Scenarios**:

1. **Given** an In Progress task "Add export" with a stored read of "notes/label.txt" whose text is "Export", an existing project folder "billing", and no file "notes/proposed.txt", **When** the engineer asks for an ordinary change with the account "Propose the export label" and the file "notes/proposed.txt", **Then** the configured model is called once, "notes/proposed.txt" contains the text the model returned, and the task shows that account, the project "billing", the file, that the file was new, the returned text, the model name, the assistant, Carried out, and the time, and the task stays In Progress.
2. **Given** the same task, **When** the project is blank, **Then** the model is not called, nothing is stored, and the engineer is told to name the project this change is for.
3. **Given** the same task and a project folder that does not exist, **When** the engineer asks for the file, **Then** the model is not called and the engineer is told the project must already exist.
4. **Given** an existing project and a blank account, **When** the engineer asks for the file, **Then** the model is not called and the engineer is told an account of what changed is required.
5. **Given** an existing project and an account, **When** the class is missing or is neither ordinary nor consequential, **Then** the model is not called and the engineer is told to choose ordinary or consequential.
6. **Given** an existing project, an account, and a class, **When** the file name is blank, **Then** the model is not called and the engineer is told to name the file this change writes.
7. **Given** an existing project and an account, **When** no file read is chosen, **Then** the model is not called and the engineer is told to choose the file read this change uses.
8. **Given** an unknown file read, **When** the engineer asks for the file, **Then** the model is not called and the engineer is told the file read was not found.
9. **Given** a file read stored on another task, **When** the engineer names that read, **Then** the model is not called and the engineer is told the change must name a file read on that task.
10. **Given** a file name outside the project, a missing destination folder, or an existing file that is not text, **When** the engineer asks for the file, **Then** the model is not called and the refusal is the same one used when the engineer asks the assistant to write a file.
11. **Given** no model is configured, **When** the other parts of the request are valid, **Then** nothing is stored and the engineer is told to choose the model this change uses.
12. **Given** a configured model that fails to return text, **When** the engineer asks for the file, **Then** nothing is stored, no file is written, and the engineer is told the model did not return file text.
13. **Given** a task that is Draft, Ready, Completed, or Cancelled, **When** the engineer asks for the file, **Then** the model is not called and the engineer is told the same status problem as when recording a change.

---

### User Story 2 - Wait before replacing a file (Priority: P2)

A request that would replace a file, a consequential request, or a stopped request still calls the model once and stores the returned text, and does not change the project until the engineer approves. Approval writes the stored text and does not call the model again. The assistant cannot approve or decline.

**Why this priority**: The model may propose text for a file that already exists. That replacement stays consequential until the engineer approves it.

**Independent Test**: Ask for an ordinary change that names an existing file. The model is called once, the file is unchanged, and the task shows Awaiting approval until the engineer approves. Approval writes the stored text and does not call the model again.

**Acceptance Scenarios**:

1. **Given** an existing file "notes/label.txt" whose text is "Old" and a model that returns "Export", **When** the engineer asks for an ordinary change for that file, **Then** the file still contains "Old", the model was called once, and the task shows class consequential, the returned text "Export", and Awaiting approval.
2. **Given** a consequential request for a new file, **When** the model returns "Export", **Then** the file is not created and the task shows Awaiting approval and the returned text.
3. **Given** an ordinary request for a new file, **When** the engineer asks to stop before carrying it out, **Then** the model is called once, the file is not created, and the task shows Awaiting approval.
4. **Given** a waiting proposal, **When** the engineer approves it and the file still matches, **Then** the file contains the stored model text, the approval names the engineer, and the model is not called again.
5. **Given** a waiting proposal, **When** the assistant tries to approve or decline it, **Then** nothing is written and no further model call is made.

---

### User Story 3 - Replay the stored model text (Priority: P3)

The stored model name and returned text are what a later reader and a later replay use. Opening the task does not call the model again. A later change to the project file does not change the stored text. The assistant does not check a criterion, record a decision, or complete the task.

**Why this priority**: A model call that is repeated can return different text. The record has to stay the text that was returned.

**Independent Test**: Record one model file, then open the task and replay that record. The model is not called again, and the task still shows the same model name and returned text.

**Acceptance Scenarios**:

1. **Given** a stored model file, **When** a reader opens the task, **Then** the reader can see the model name, the returned text, the file, the project, the assistant, and the outcome, and the model is not called again.
2. **Given** the same stored change, **When** that record is replayed, **Then** the task shows the same model name and returned text, and the model is not called again.
3. **Given** a model file on a subtask, **When** a reader opens the parent, **Then** the parent does not list that change.
4. **Given** an assistant file change that did not call the model, **When** a reader opens the task, **Then** that change is unchanged and no model is called for it.
5. **Given** a carried-out model file, **When** the engineer completes the task, **Then** completion still waits until that change has a passing check. The assistant does not record the check, record a decision, or complete the task.

---

### Edge Cases

- A wrong task status is reported before a blank project, a blank account, a blank file name, or a missing file read. The model is not called.
- The file read must already be stored on that task. The product does not read the project file again to build the model input.
- The model input includes the task title, the goal, the acceptance criteria, the stored file path, the stored file text, the project, and the file to write. That input and the returned text are stored. A later edit to the task or the project file does not change them.
- The model name is the name of the configured model. A name supplied with the request is not the name stored.
- One request calls the model at most once and writes or proposes one file. A second file is a second request.
- An empty text returned by the model is a real empty file text.
- The ordinary, consequential, stopped, and replacement rules are the same as for a file the engineer submits. The returned text takes the place of the submitted file text.
- Approval and decline do not call the model. A mismatch or a path outside the project leaves the proposal waiting and does not call the model.
- The assistant does not verify a criterion, record a check, record a decision, complete a task, or cancel a task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to ask for one model file on an In Progress task by naming an existing project, one file inside it, one stored file read on that task, ordinary or consequential, whether to stop, and the account of what changed. The product MUST call the configured model once. The call input MUST be that task and that stored read. The returned text MUST be the file text.
- **FR-002**: For an ordinary change that is not stopped, when the file does not already exist and its folder does, the product MUST write that file with the returned text. The task MUST show the account, the project, the file, that the file was new, the returned text, the model name, the assistant, Carried out, and the time. The task status MUST stay In Progress.
- **FR-003**: The product MUST NOT call the model when the task is missing or not In Progress, the project is blank or missing, the account is blank, the class is missing or invalid, the file name is blank, the file read is missing, unknown, or on another task, the file is outside the project, the destination folder is missing, or the existing file is not text. Those refusals MUST use the existing messages, plus `Choose the file read this change uses.`, `File read not found.`, and `The change must name a file read on that task.`
- **FR-004**: When no model is configured, the product MUST refuse with `Choose the model this change uses.` and MUST store nothing. When the model does not return text, the product MUST refuse with `The model did not return file text.`, MUST store nothing, and MUST NOT write a file.
- **FR-005**: A consequential request, a stopped request, and a request that names an existing file MUST call the model once, MUST store the returned text, and MUST NOT change the project until the engineer approves. Approval MUST write the stored text and MUST NOT call the model again. The assistant MUST NOT approve or decline.
- **FR-006**: A stored model call MUST NOT be edited or removed. Opening the task and replaying that record MUST show the same model name and returned text and MUST NOT call the model again.
- **FR-007**: A model file MUST name exactly one task, one project, one file, one stored file read, and the model. A model file on a subtask MUST NOT appear on the parent. An earlier change that did not call the model MUST stay readable and MUST NOT cause a model call.
- **FR-008**: Recording a model file MUST NOT verify a criterion, record a check, record a decision, or change the task status. Completing the task MUST still wait until a carried-out change has a passing check. The assistant MUST NOT record that check, record a decision, or complete or cancel the task.

### Key Entities *(include if feature involves data)*

- **Model Call**: One call to the configured model for one assistant file change. It has the model name, the input that was sent, the returned text, and the stored file read that input used. It is not edited after it is stored.
- **Configured Model**: The model named for this task manager. The request does not choose a different model. A missing model is refused.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, which model was called, what text it returned, which file that text was for, and whether the file was written, in under 2 minutes.
- **SC-002**: In a review of ordinary new model files, 100% call the model once, leave that file containing the returned text, and name the model, the assistant, and Carried out.
- **SC-003**: In a review of refused requests that never reach the model, 100% make no model call and store nothing.
- **SC-004**: In a review of replacements, consequential requests, and stopped requests, 100% call the model once and leave the project file unchanged until the engineer approves.
- **SC-005**: Two passes of the same stored model record show the same model name and returned text, and the second pass does not call the model.
- **SC-006**: At least 95% of engineers ask for one new model file and find the model name and the returned text on the task on the first attempt without assistance.
- **SC-007**: In a review of approvals of model files, 100% write the stored text, name the engineer, and make no further model call.

## Assumptions

- The task, the file read, and the ordinary file write are already in place. This feature adds one model call whose returned text is the file text for that write.
- The model is configured for the task manager before the request. This feature does not choose a model vendor, and a name sent with the request is ignored.
- The engineer still names the project, the file, the class, the account, and which stored file read to send. The product does not choose a different file or a different read.
- The model is called only after those parts are valid and the file can be written or proposed. A failed call stores nothing.
- Replay uses the stored model name and returned text. It does not call the model again and does not rebuild the input.
- Creating a folder, deleting a file, running tests, committing, and opening a pull request stay out of this action.
- The assistant does not check, decide, complete, or cancel. Approval still names the engineer.
- These rules follow the project constitution: the model call is recorded with its input and output, replay uses that record, and a replacement still waits for a named human approval.
