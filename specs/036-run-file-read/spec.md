# Feature Specification: Run One File Read

**Feature Branch**: `036-run-file-read`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Implement one named run of the next ordinary file-read step. The same name leaves the workflow where it is. A run that rolls back leaves the step pending. A folder, an approval, a delivery, a commit, and a pull request stay for the engineer."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the next file read (Priority: P1)

The engineer names a run. That run performs the next workflow step only when the step reads a file. The file read is stored the same way an advance of that step stores it. The step is completed. Every later step stays pending. The same name again does not perform another step. A different name performs the next file read, and only that one. The task status stays as it was.

**Why this priority**: The engineer can name one ordinary read and leave every other action for a separate decision.

**Independent Test**: Store "Read the note" and then "Read the extra". Run "once". Only the note is read, and the extra step stays pending. Run "once" again. The extra file is still unread. Run "next". Only the extra file is read.

**Acceptance Scenarios**:

1. **Given** the next step reads a file, **When** the engineer runs it with "once", **Then** that file is read, the step is completed, and the run names "once".
2. **Given** a later step, **When** that run finishes, **Then** the later step stays pending.
3. **Given** that run, **When** the engineer runs "once" again, **Then** no other step is performed.
4. **Given** a second file-read step, **When** the engineer runs "next", **Then** only that second file is read.
5. **Given** the same name on another task, **When** the engineer runs "once" there, **Then** that other task reads its own next file.

---

### User Story 2 - A run that does not finish leaves the step pending (Priority: P2)

A blank name is refused with `Name this run.` No file-read step is refused with `There is no file to read.` A next step that is not a file read is refused with `The next step is not a file read.` An interrupted step is refused with `Recover the interrupted step first.` None of those refusals stores the name. A run that is rolled back leaves the step pending, stores no file read, and stores no run. The same name can then be used. A file that cannot be read marks that step failed, stores the name, and does not read a later step. The same name does not try the failed step again.

**Why this priority**: A crash or a refusal must not look like the file was read, and must not perform a folder or an approval.

**Independent Test**: Roll back a run named "once". The step stays pending and the file has no stored read. Use "once" again. The file is read. Put a folder step first and run "once". The engineer is told `The next step is not a file read.` and the folder is not created.

**Acceptance Scenarios**:

1. **Given** a blank name, **When** the engineer runs, **Then** the step stays pending and the engineer is told `Name this run.`
2. **Given** no file-read step, **When** the engineer runs, **Then** the engineer is told `There is no file to read.`
3. **Given** a folder step is next, **When** the engineer runs, **Then** the engineer is told `The next step is not a file read.` and the folder is not created.
4. **Given** a run that is rolled back, **When** the engineer opens the task, **Then** the step stays pending and no run is stored.
5. **Given** a task that is not In Progress, **When** the engineer runs, **Then** the engineer is told `The task must be In Progress.` and no run is stored.

---

### User Story 3 - The task shows the run (Priority: P3)

The task shows each run. When the task is In Progress and the next step reads a file, the engineer can enter a run name and press Run file read. After that read, a following folder step does not offer Run file read. The task list stays the list of tasks.

**Why this priority**: The engineer needs to see which read the name performed.

**Independent Test**: Open a task whose next step reads a file. The page offers Run file read. Press it with "once". The page shows that run, the file is read, and a following folder step is still pending.

**Acceptance Scenarios**:

1. **Given** the next step reads a file, **When** the engineer opens the task, **Then** the page offers Run file read.
2. **Given** a run named "once", **When** the engineer opens the task, **Then** the page shows that name and the step it read.
3. **Given** the next step is a folder, **When** the engineer returns to the task, **Then** Run file read is not offered.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- One request runs one step.
- A run does not deliver a message, approve a change, create a folder, commit a file, or open a pull request.
- A file that cannot be read fails that step and does not continue.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a run. The first accepted use of that name MUST perform the next step only when that step reads a file. The file read MUST be stored the same way an advance of that step stores it. The step MUST be completed. Later steps MUST stay pending. The same name MUST NOT perform another step. A different name MUST be able to perform the next file read.
- **FR-002**: A blank name MUST be refused with `Name this run.` No file-read step MUST be refused with `There is no file to read.` A next step that is not a file read MUST be refused with `The next step is not a file read.` An interrupted step MUST be refused with `Recover the interrupted step first.` A task that is not In Progress MUST be refused with `The task must be In Progress.` Those refusals MUST NOT store the name. A rolled-back run MUST leave the step pending and MUST leave no run and no file read. The same name on another task MUST be able to read that task's next file.
- **FR-003**: A file that cannot be read MUST fail that step, MUST store the name, and MUST NOT perform a later step. The same name MUST NOT try that step again.
- **FR-004**: A run MUST NOT create a folder, approve a change, deliver a message, commit a file, open a pull request, or change the task status. The task page MUST show the run and MUST offer Run file read while the task is In Progress and the next step reads a file. The task list MUST stay the list of tasks.

### Key Entities

- **File run**: The trimmed name that performed one file-read step. The step and the stored file read remain.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of runs, 100% read only the next file and leave every later step pending.
- **SC-002**: In a review of rolled-back runs, 100% leave the step pending and leave no stored file read.
- **SC-003**: An engineer can see the run and start it from the task in one view.

## Assumptions

- Specifications 001 through 035 are not rewritten. Advance workflow still performs whatever step is next, including a folder. A run does not take the place of that advance.
- A run stores the same file read an advance of that read stores. It does not deliver the message that completion stores.
- A folder, an approval, a delivery, a commit, and a pull request stay for the engineer to name.
- The rules are covered by automated checks.
