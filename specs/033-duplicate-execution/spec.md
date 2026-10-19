# Feature Specification: Idempotency and Duplicate Execution Control

**Feature Branch**: `033-duplicate-execution`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Implement Idempotency and Duplicate Execution Control."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One name performs one command (Priority: P1)

The engineer may name an execution when reading a file or creating a folder. The first accepted use of that name on a task performs that command once and records the name, the command, and the path. The same name afterward does not read a file, does not create a folder, and does not store a second file read or a second folder change, even when the later request names a different path. After the file or folder has been removed, the same name still does not put it back. A different name can perform another command. The task status stays as it was.

**Why this priority**: Submitting the same command twice must not take effect twice.

**Independent Test**: Name a read "once" for `note.txt`. One file read is stored. Remove `note.txt` and send "once" again for `other.txt`. The file read is still only `note.txt`, and `other.txt` is not read. Name a folder "notes" and send that name again. One folder change is stored, and a removed folder stays removed.

**Acceptance Scenarios**:

1. **Given** an In Progress task and a file `note.txt`, **When** the engineer reads it with the execution name "once", **Then** one file read names `note.txt` and the task lists that execution.
2. **Given** that execution, **When** the engineer sends "once" again for a different file after `note.txt` is removed, **Then** the file read is still only `note.txt`, the other file is not read, and `note.txt` stays removed.
3. **Given** an ordinary folder created with the execution name "notes", **When** the engineer sends "notes" again after that folder is removed, **Then** one folder change remains and the folder stays removed.
4. **Given** a consequential folder recorded with the execution name "hold", **When** the engineer sends "hold" again, **Then** one folder change remains and the folder is not created.
5. **Given** the name "once" was used, **When** the engineer uses a different name, **Then** that command is performed once.

---

### User Story 2 - A refusal does not use the name (Priority: P2)

A blank execution name is not saved. Each blank command keeps the existing rules, so an unnamed read can still be recorded again. A command that is refused does not use up the name. The same name afterward can still perform one command. The same name on another task is a different execution and can still perform that task's command. A name with surrounding spaces is the same name as the trimmed text. A rolled-back command leaves no execution and no effect.

**Why this priority**: A name must mean one accepted execution, not one attempt.

**Independent Test**: Read a missing file with the name "once". The name is not saved. Create the file and send "once". One file read is stored. Send "once" with surrounding spaces. The file is not read again.

**Acceptance Scenarios**:

1. **Given** a blank execution name, **When** the engineer reads an existing file twice, **Then** two file reads are stored and no named execution is recorded.
2. **Given** a read of a missing file named "once", **When** the file exists and the engineer sends "once", **Then** one file read is stored.
3. **Given** a read that is rolled back, **When** the engineer opens the task, **Then** no file read and no named execution are stored, and that name can still be used.
4. **Given** the name "once" was used on one task, **When** the engineer uses "once" on another task, **Then** that other task still performs its command.
5. **Given** the task is not In Progress, **When** the engineer names an execution, **Then** the engineer is told `The task must be In Progress.` and the name is not saved.

---

### User Story 3 - The task shows the named executions (Priority: P3)

The task shows each named execution, the command, and the path. Read a file and Create a folder each offer an execution name. Leaving the name blank does not record an execution. The task list stays the list of tasks. A workflow step does not record one of these executions, and a named workflow advance stays as it is.

**Why this priority**: The engineer needs to see which command the name already performed.

**Independent Test**: Read `note.txt` with the name "once" and open the task. The page shows "once" as Read a file `note.txt`. Submit that name again from the page. The file is not read again.

**Acceptance Scenarios**:

1. **Given** a named read, **When** the engineer opens the task, **Then** the page shows that name, Read a file, and the path.
2. **Given** no named execution, **When** the engineer opens the task, **Then** the page says `No named executions yet.`
3. **Given** the page's execution name, **When** the engineer submits a name that already ran, **Then** the following command is not performed.

### Edge Cases

- A second use of a name does not change the stored path.
- Creating a folder that is refused, including a blank folder name, does not save the execution name.
- One request performs one command or returns the earlier execution.
- Repeating a name does not approve a change and does not advance a workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an execution of Read a file or Create a folder. The first accepted use of that name on a task MUST perform that command once and MUST record the name, the command, and the path. The same name afterward MUST NOT read a file, create a folder, or store a second file read or folder change, even when the later request names a different path. A removed file or folder MUST stay removed.
- **FR-002**: A blank name MUST NOT be saved. Each blank command MUST keep the existing rules. A refused or rolled-back command MUST NOT use up the name. The same name on another task MUST still be able to perform that task's command. A different name on the same task MUST be able to perform another command. A task that is not In Progress MUST be refused with `The task must be In Progress.` and MUST NOT save the name.
- **FR-003**: The task page MUST show the named executions and MUST offer an execution name on Read a file and Create a folder. When none are recorded, it MUST say `No named executions yet.` The task list MUST stay the list of tasks. A workflow step MUST NOT record one of these executions, and the task status MUST stay unchanged.

### Key Entities

- **Named execution**: The trimmed name of one accepted Read a file or Create a folder on one task, together with the path that command stored.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of repeated execution names, 100% leave the original file read or folder change as the only one, and leave a removed file or folder removed.
- **SC-002**: In a review of refused commands, 100% leave that name available for one later accepted command.
- **SC-003**: An engineer can see the named execution on the task and submit it again without a second effect, in one view.

## Assumptions

- Specifications 001 through 032 are not rewritten. A named workflow advance stays as it is.
- Read a file and Create a folder are the commands this name controls. Other commands may still be used more than once.
- The execution name is chosen by the engineer. A blank name keeps today's command.
- The rules are covered by automated checks.
