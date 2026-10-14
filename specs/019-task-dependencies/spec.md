# Feature Specification: Task Dependencies

**Feature Branch**: `019-task-dependencies`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Store prerequisite task IDs. Reject invalid references, self-dependencies, and cycles. Show a valid execution order. A task cannot be started while a prerequisite is incomplete or unverified, and the refusal names that prerequisite."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a prerequisite (Priority: P1)

The engineer names one existing task as a prerequisite of another task. The link is stored in the workspace. A task cannot depend on itself. A prerequisite that does not exist is refused. A link that would close a cycle, including A depends on B, B depends on C, and C depends on A, is refused and not stored. Naming the same prerequisite again does not add a second link. The engineer can remove a link. Opening the task again shows the same prerequisites.

**Why this priority**: Later ordering and the start hold need a stored link that cannot form a cycle.

**Independent Test**: Link task "Add export" to prerequisite "Write the label". The task lists that prerequisite. A self-link, an unknown task, and a cycle are refused and store nothing.

**Acceptance Scenarios**:

1. **Given** tasks "Add export" and "Write the label", **When** the engineer names "Write the label" as a prerequisite of "Add export", **Then** "Add export" lists "Write the label" and its status, and a later reading shows the same link.
2. **Given** that link, **When** the engineer names "Write the label" again, **Then** the task still lists it once.
3. **Given** task "Add export", **When** the engineer names "Add export" as its own prerequisite, **Then** nothing is stored and the engineer is told `A task cannot depend on itself.`
4. **Given** task "Add export", **When** the engineer names a task that does not exist, **Then** nothing is stored and the engineer is told `Prerequisite not found.`
5. **Given** "Add export" depends on "Write the label", and "Write the label" depends on "Choose the format", **When** the engineer names "Add export" as a prerequisite of "Choose the format", **Then** that link is not stored and the engineer is told `That dependency would form a cycle.` The two earlier links stay.
6. **Given** a stored prerequisite, **When** the engineer removes it, **Then** the task no longer lists it. Removing a task that is not a prerequisite is refused with `That prerequisite is not linked.`
7. **Given** a cancelled task, **When** the engineer adds or removes a prerequisite, **Then** nothing changes and the engineer is told `A cancelled task cannot be changed. Continued work is a new task.`

---

### User Story 2 - Show a valid execution order (Priority: P2)

The engineer can read one order of every task in the workspace. Each prerequisite appears before the task that names it. When more than one task could come next, the task with the lower id comes first. Reading the order does not add a link, start a task, or change a status.

**Why this priority**: A stored graph is useful once the engineer can see an order that respects it.

**Independent Test**: Let "Add export" depend on "Write the label", and "Write the label" depend on "Choose the format". The order shows "Choose the format", then "Write the label", then "Add export".

**Acceptance Scenarios**:

1. **Given** "Add export" depends on "Write the label", and "Write the label" depends on "Choose the format", **When** the engineer reads the execution order, **Then** "Choose the format" comes before "Write the label", and "Write the label" comes before "Add export".
2. **Given** two tasks that could both come next, **When** the engineer reads the order, **Then** the task with the lower id comes first.
3. **Given** a task with no prerequisite, **When** the engineer reads the order, **Then** that task is included.
4. **Given** a stored order, **When** the engineer reads it again, **Then** the same order is shown and no task status changes.

---

### User Story 3 - Hold the start while a prerequisite is unfinished (Priority: P3)

A task can still be marked Ready while a prerequisite is unfinished. It cannot be started until every prerequisite is Completed. The refusal names each unfinished prerequisite. If that prerequisite has an unverified acceptance criterion, the refusal names the criterion. Otherwise it says the prerequisite is incomplete and shows its status. A Completed prerequisite does not block. A task that is already In Progress stays In Progress when a prerequisite later leaves Completed.

**Why this priority**: The order is only a reading. The hold is what stops work from starting on an unfinished prerequisite.

**Independent Test**: Mark "Add export" Ready while "Write the label" is Draft. Starting "Add export" is refused and names "Write the label". Complete "Write the label", and "Add export" can be started.

**Acceptance Scenarios**:

1. **Given** "Add export" is Ready and its prerequisite "Write the label" is Draft, **When** the engineer starts "Add export", **Then** "Add export" stays Ready and the refusal is `Blocked by Write the label (Draft): incomplete.`
2. **Given** "Write the label" is In Progress and its criterion "The label is recorded" is Unverified, **When** the engineer starts "Add export", **Then** "Add export" stays Ready and the refusal is `Blocked by Write the label (In Progress): unverified The label is recorded.`
3. **Given** two unfinished prerequisites, **When** the engineer starts the task, **Then** the refusal names the prerequisite with the lower id first, then the other.
4. **Given** a task that is still Draft, **When** the engineer starts it, **Then** the refusal stays `The task must be Ready to start work.` even when a prerequisite is also unfinished.
5. **Given** every prerequisite is Completed, **When** the engineer starts the Ready task, **Then** the task becomes In Progress.
6. **Given** the task is already In Progress, **When** a prerequisite is reopened, **Then** the task stays In Progress. The task shows the blocked explanation. Starting is not asked again.
7. **Given** the only unfinished prerequisite is removed, **When** the engineer starts the Ready task, **Then** the task becomes In Progress.

### Edge Cases

- A prerequisite that is Cancelled is unfinished. The explanation says incomplete and shows Cancelled.
- A prerequisite that is In Progress with every criterion Verified, and that is not Completed, is incomplete.
- Several unverified criteria on one prerequisite are listed from the first criterion to the last, separated by a comma and a space.
- Adding or removing a prerequisite does not change either task's status.
- Marking a task Ready still requires a goal and an acceptance criterion. An unfinished prerequisite does not change that rule.
- A subtask link is not a prerequisite. A prerequisite is not a subtask.
- One request names one prerequisite. It does not start, complete, or cancel a task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name one existing task as a prerequisite of another task, and MUST be able to remove that link. The task MUST list each prerequisite's title and status. A repeated name MUST leave a single link. Opening the task MUST NOT add or remove a link.
- **FR-002**: A self-link MUST be refused with `A task cannot depend on itself.` An unknown prerequisite MUST be refused with `Prerequisite not found.` A link that would form a cycle MUST be refused with `That dependency would form a cycle.` A refusal MUST store nothing. Removing a task that is not a prerequisite MUST be refused with `That prerequisite is not linked.`
- **FR-003**: The engineer MUST be able to read one order of every task in the workspace. Each prerequisite MUST appear before the task that depends on it. When several tasks could come next, the lower id MUST come first. Reading the order MUST NOT change a status or a link.
- **FR-004**: Starting a task MUST be refused while any prerequisite is not Completed. The refusal MUST name each such prerequisite, the one with the lower id first. A prerequisite with an unverified criterion MUST use `Blocked by {title} ({status}): unverified {criteria}.` Otherwise it MUST use `Blocked by {title} ({status}): incomplete.` The task MUST stay in its current status.
- **FR-005**: The existing start refusal `The task must be Ready to start work.` MUST stay first when the task is not Ready. Marking Ready, completing, and cancelling MUST keep their current rules. A task that is already In Progress MUST stay In Progress when a prerequisite leaves Completed.

### Key Entities

- **Prerequisite link**: One task names one other task that must be Completed before this task can be started.
- **Execution order**: One reading of every task such that each prerequisite comes first.
- **Blocked explanation**: The sentence that names each prerequisite that is not Completed, and names unverified criteria when that prerequisite has them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can name the prerequisites of a task, and whether each is Completed, from that task's record, in under 2 minutes.
- **SC-002**: In a review of self-links, unknown tasks, and cycles, 100% store no new link.
- **SC-003**: In a review of execution orders, 100% place each prerequisite before the task that names it.
- **SC-004**: In a review of start attempts with an unfinished prerequisite, 100% leave the task unstarted and name that prerequisite.

## Assumptions

- Specifications 001 through 018 are not rewritten. The status Ready still means the task has a goal and an acceptance criterion. It does not mean the prerequisites are Completed.
- There is no Failed task status. A prerequisite blocks the start when its status is not Completed. Cancelled is one of those statuses.
- The blocked explanation is also shown on the task while any prerequisite is not Completed, including before the engineer starts the task.
- A subtask relationship and a prerequisite link are separate. Neither creates the other.
- The engineer name and the time still come from the workspace. A client-supplied name or time is ignored.
- The rules are covered by automated checks.
