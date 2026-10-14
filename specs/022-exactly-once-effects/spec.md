# Feature Specification: Idempotency and Exactly-Once Effects

**Feature Branch**: `022-exactly-once-effects`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Implement idempotency and exactly-once effects. Each workflow step stores its effect once. Repeating that step does not store a second file read or a second folder change. The same named advance performs one step and, when repeated, does not perform another."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One effect for one step (Priority: P1)

A Read a file step stores one file read. A Create a folder step stores one folder change. After that effect is stored, another advance or another finish of that step does not store a second copy and does not perform the action again. The step stays on the result that effect already has: Completed, Waiting, or Failed. A later step stays unperformed. A Failed step that stored no effect can still be retried by a later advance, and that retry stores one effect.

**Why this priority**: A step that already took effect must not take effect again.

**Independent Test**: Advance a consequential "Create the folder", then decline it. The step is Failed and one change is stored. Advance again. The change is still the only one, the step stays Failed with `Stopped at Create the folder: Not this folder`, and the following step stays Pending.

**Acceptance Scenarios**:

1. **Given** "Read the note" is running and that file read is already stored, **When** the advance finishes, **Then** the step is Completed, the replay records that completed result, and the file is not read again.
2. **Given** a consequential "Create the folder" was declined, **When** the engineer advances again, **Then** no second change is recorded, the step stays Failed, the task still reports `Stopped at Create the folder: Not this folder`, and the following step stays Pending.
3. **Given** "Read the note" failed because the file was missing and no file read is stored, **When** the file exists and the engineer advances, **Then** the step is Completed and one file read is stored.

---

### User Story 2 - The same advance name performs one step (Priority: P2)

The engineer may name an advance. The first use of that name on a task performs one step. The same name afterward does not perform a step, does not store another effect, and does not add a replay entry, including after the workspace is opened again. A different name performs the next unfinished step that is still allowed to run. A blank name is not saved. Each blank advance follows the existing advance rules, so an unnamed advance can still move to the next step.

**Why this priority**: Submitting the same advance twice must not run two steps.

**Independent Test**: Name an advance "once" for "Read the note", then a folder step. The read is Completed and the folder stays Pending. Sending "once" again leaves the folder Pending and does not read the file again. A new name then creates the folder.

**Acceptance Scenarios**:

1. **Given** "Read the note" and then "Create the folder", and the file exists, **When** the engineer advances with the name "once", **Then** the read is Completed, one file read is stored, and the folder step stays Pending.
2. **Given** that named advance, **When** the engineer sends "once" again, **Then** the folder step stays Pending, the file is not read again, and the replay does not gain an entry.
3. **Given** that same task, **When** the engineer advances with a different name, **Then** the folder step runs and the file is not read again.
4. **Given** a blank name, **When** the engineer advances twice on a task whose first step can complete, **Then** the second advance can perform the next step.
5. **Given** the name "once" was used on one task, **When** the engineer uses "once" on another task, **Then** that other task still performs its step.

---

### User Story 3 - The page supplies the advance name (Priority: P3)

The task page fills in an advance name each time the task is shown. The engineer can replace it before advancing. Submitting the shown name performs one step. Showing the task again supplies a new name, so the next advance can perform the next step. Submitting the earlier name again does not.

**Why this priority**: The page is how the engineer repeats an advance without running a second step.

**Independent Test**: Open an In Progress task that has a pending read and a later folder step. The advance form shows a name. Submit it. The read is Completed, the folder stays Pending, and the form shows a different name.

**Acceptance Scenarios**:

1. **Given** an In Progress task with a step left to run, **When** the engineer opens the task, **Then** the advance form shows an advance name.
2. **Given** that name, **When** the engineer advances, **Then** one step is performed and the task, shown again, supplies a different name.
3. **Given** the earlier name, **When** the engineer submits it again, **Then** the following step stays unperformed.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- While the named step is still running, the same name is refused with `Recover the interrupted step first.` and nothing is performed.
- A name is not saved when the advance is refused because the task is not In Progress, because there is no step to run, or because a step must be recovered first.
- A repeated name does not change the task status.
- Recover still recovers one running step. A second recover is still `There is no step to recover.`
- Read a file and Create a folder stay the only workflow actions. The engineer's own Read a file and Create a folder commands may still be used more than once.
- One request advances once or recovers once.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A workflow step MUST store at most one file read or one folder change. After that effect is stored, finishing or advancing that step MUST NOT perform the action again and MUST NOT store a second copy. The following step MUST stay unperformed.
- **FR-002**: A Failed step that has no stored effect MAY be retried by a later advance. That retry MUST store one effect. A Failed step that already has its folder change MUST stay Failed with the same stop sentence and MUST NOT record another change.
- **FR-003**: The engineer MUST be able to name an advance. The first accepted use of that name on a task MUST perform one step. The same name afterward MUST NOT perform a step, store another effect, or add a replay entry. A different name MUST be able to perform the next step that is still allowed to run.
- **FR-004**: A blank name MUST NOT be saved. Each blank advance MUST keep the existing advance rules. The same name on another task MUST still be able to perform that task's step. A refused advance that stores nothing MUST NOT use up the name.
- **FR-005**: The task page MUST show an advance name and MUST supply a different name each time the task is shown. Submitting a name that already advanced MUST leave the following step unperformed.

### Key Entities

- **Step effect**: The one file read or folder change stored for a workflow step.
- **Advance name**: The trimmed name of one advance on one task. It remembers the step that advance was for.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of steps whose effect is already stored, 100% still have exactly one file read or one folder change after another advance.
- **SC-002**: In a review of repeated advance names, 100% leave the following step unperformed and add no replay entry.
- **SC-003**: An engineer can submit the same advance name twice and see that only one step ran, in under 2 minutes.
- **SC-004**: In a review of tasks opened again, 100% show a new advance name, and the previous name still does not run another step.

## Assumptions

- Specifications 001 through 021 are not rewritten. An unnamed advance still performs the first unfinished step that those specifications allow, including a retry of a failure that stored no effect.
- The advance name is chosen by the engineer or supplied by the task page. A client-supplied engineer name or time is ignored.
- The same stop sentences stay in use, including `Stopped at {title}: Not this folder`, `Recover the interrupted step first.`, and `There is no step to recover.`
- The rules are covered by automated checks.
