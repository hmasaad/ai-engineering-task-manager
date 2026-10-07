# Feature Specification: Manage Engineering Tasks

**Feature Branch**: `001-manage-engineering-tasks`

**Created**: 2026-10-06

**Status**: Accepted

**Input**: User description: "Build an AI Engineering Task Manager that allows engineers to create engineering tasks, define goals and acceptance criteria, break tasks into subtasks, track task status, record implementation decisions, and mark tasks as completed."

## Clarifications

### Session 2026-10-06

- Q: What must be recorded before an acceptance criterion counts as Verified? → A: The engineer records three separate facts: what was observed, that the criterion passed, and when. A note with no pass result does not count.
- Q: Who is allowed to supply the observation and the pass result that mark an acceptance criterion Verified? → A: Only the engineer. The record names that engineer, plus the observation, the pass, and the time.
- Q: Can a Completed task be reopened, and what happens to a Completed parent above it? → A: Yes, with a recorded reason. The task returns to In Progress and its verified criteria stay Verified. Every Completed ancestor also returns to In Progress, and each of those changes records the reopen as the cause.
- Q: Can a Cancelled task be restored to an active status? → A: No. Cancelled is final. The task, its reason, and its history stay. Continued work is a new task.
- Q: Can one implementation decision supersede more than one earlier decision on the same task? → A: Yes. A decision may name one or more earlier decisions on the same task. It cannot name itself or a decision that comes after it. Each named decision stays visible and unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture a task with a goal and acceptance criteria (Priority: P1)

An engineer creates an engineering task, names it, writes the goal, and adds one or more acceptance criteria. The task appears in the list, and opening it shows those details again.

**Why this priority**: Every later action needs a task whose outcome and checks are written down. Without this, status, subtasks, and decisions have nothing to attach to.

**Independent Test**: Create one task with a title, a goal, and two acceptance criteria, then open it from the list and confirm those fields are unchanged.

**Acceptance Scenarios**:

1. **Given** the workspace has no tasks, **When** the engineer creates a task titled "Add export" with the goal "An engineer can take a finished task record with them" and two acceptance criteria, **Then** the task appears on the list with status Draft, the goal is shown, and both criteria are Unverified.
2. **Given** the engineer is creating a task, **When** the title is empty or only spaces, **Then** the task is not created and the engineer is told a title is required.
3. **Given** a Draft task with a title, a goal, and one acceptance criterion, **When** the engineer marks the task Ready, **Then** the status becomes Ready.
4. **Given** a Draft task with a title and a goal but no acceptance criterion, **When** the engineer marks the task Ready, **Then** the status stays Draft and the engineer is told at least one acceptance criterion is required.
5. **Given** a Ready task with one acceptance criterion, **When** the engineer removes that criterion, **Then** the status returns to Draft and the history records the removal as the cause.

---

### User Story 2 - Track status through to completion (Priority: P2)

An engineer starts a Ready task, checks each acceptance criterion against what was observed, and marks the task completed only when every criterion is verified. The task keeps a history of each status change. A completed task can be reopened with a reason, and every Completed ancestor returns to In Progress with that same cause.

**Why this priority**: Completion is meaningful only when it is tied to the criteria from Story 1 and the status is always explicit.

**Independent Test**: On one Ready task with no subtasks, start it, verify each criterion with an observation, an explicit pass, and a time, mark it completed, and read back a history that shows Draft or Ready through In Progress to Completed.

**Acceptance Scenarios**:

1. **Given** a Ready task, **When** the engineer starts work, **Then** the status is In Progress and the history records the previous status, the new status, the time, and that the engineer started work.
2. **Given** an In Progress task with two Unverified criteria, **When** the engineer records what was observed, an explicit pass, and the time for one criterion, **Then** that criterion is Verified, the record names the engineer as the provider, the other criterion stays Unverified, and the task stays In Progress.
3. **Given** an In Progress task with an Unverified criterion, **When** the engineer records what was observed but does not record that the criterion passed, **Then** the criterion stays Unverified.
4. **Given** an In Progress task whose every acceptance criterion is Verified and that has no subtasks, **When** the engineer marks the task completed, **Then** the status is Completed.
5. **Given** an In Progress task with an Unverified criterion, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told which criteria are still Unverified.
6. **Given** a Ready task, **When** the engineer marks the task completed, **Then** the status stays Ready and the engineer is told the task must be In Progress before it can be completed.
7. **Given** a Completed task, **When** the engineer reopens it with the reason "A missed case was found", **Then** the status is In Progress, verified criteria stay Verified, and the history records that reason.
8. **Given** a Completed parent whose subtask is also Completed, **When** the engineer reopens the subtask with the reason "A missed case was found", **Then** the subtask and the parent are both In Progress, both histories record that reopen, and verified criteria on both stay Verified.
9. **Given** a Completed task, **When** the engineer changes the text of a Verified criterion, **Then** that criterion becomes Unverified, the observation, pass result, time, and provider are cleared, the status becomes In Progress, and the history records the criterion edit as the cause.
10. **Given** a Completed parent whose subtask is also Completed, **When** the engineer changes the text of a Verified criterion on the subtask, **Then** the subtask and the parent are both In Progress, the edited criterion is Unverified, and both histories record the criterion edit as the cause.
11. **Given** an In Progress task with a Verified criterion, **When** the engineer marks that criterion Unverified, **Then** the criterion is Unverified, the observation, pass result, time, and provider are cleared, and the task stays In Progress.
12. **Given** an In Progress task with no unfinished subtasks, **When** the engineer cancels it with the reason "Superseded by another task", **Then** the status is Cancelled and the history records that reason.
13. **Given** an In Progress parent whose subtask is still Draft, **When** the engineer cancels the parent, **Then** the parent stays In Progress and the engineer is told the subtask must be finished or cancelled first.
14. **Given** a Cancelled task, **When** the engineer tries to restore it to Draft, Ready, In Progress, or Completed, **Then** the status stays Cancelled and the engineer is told that continued work is a new task.

---

### User Story 3 - Break a task into subtasks (Priority: P3)

An engineer splits a task into smaller tasks. Each subtask has its own goal, acceptance criteria, and status. A parent task cannot be completed while any subtask is still unfinished.

**Why this priority**: Large tasks become reviewable only after they are split into pieces that can be checked on their own. The parent record still shows whether the whole job is done.

**Independent Test**: Add two subtasks to one parent and confirm they appear in the order they were created. Then, with the parent's own criteria verified, attempt to complete the parent while one subtask is still Ready and confirm the parent does not complete.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer adds a subtask with its own title, **Then** the subtask is listed on that task, its status is Draft, and it names that task as its parent.
2. **Given** a parent whose first subtask is "Write the checklist" and whose second is "Record the result", **When** the engineer views the parent, **Then** the subtasks appear in that creation order.
3. **Given** an In Progress parent whose own criteria are all Verified and that has a subtask still in Ready, **When** the engineer marks the parent completed, **Then** the parent stays In Progress and the engineer is told which subtask is unfinished.
4. **Given** an In Progress parent whose own criteria are all Verified and whose only subtask is Completed, **When** the engineer marks the parent completed, **Then** the parent status becomes Completed.
5. **Given** a Completed parent, **When** the engineer adds a subtask, **Then** no subtask is created and the engineer is told to reopen the parent first.
6. **Given** task A is a subtask of task B, **When** the engineer tries to make B a subtask of A, **Then** the parent relationship is unchanged and the engineer is told a task cannot contain its own ancestor.

---

### User Story 4 - Record implementation decisions (Priority: P4)

An engineer writes down a decision made while doing a task, including why it was made. A later decision can supersede one or more earlier decisions on the same task. Every named decision stays readable.

**Why this priority**: The goal and the criteria say what "done" means. The decision record says how the work got there, so a later reader does not need the original conversation.

**Independent Test**: On one task, save two decisions, then save a third that supersedes both, and confirm all three remain visible and the third names the first two.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer records a decision with a statement and a rationale, **Then** the decision appears on that task with the time it was recorded.
2. **Given** a task that already has a decision, **When** the engineer records a later decision that names the earlier one as superseded, **Then** both decisions remain visible and the later decision identifies the earlier one.
3. **Given** a task with two earlier decisions, **When** the engineer records a later decision that names both as superseded, **Then** all three remain visible and the later decision identifies both.
4. **Given** the engineer is recording a decision, **When** the statement or the rationale is empty, **Then** the decision is not saved and the engineer is told both a statement and a rationale are required.
5. **Given** a decision on one task and a decision on another task, **When** the engineer records a decision that names the other task's decision as superseded, **Then** the new decision is not saved and the engineer is told a decision can only supersede earlier decisions on the same task.
6. **Given** a Cancelled task, **When** the engineer records a decision, **Then** no decision is saved and the engineer is told decisions cannot be added to a cancelled task.

---

### Edge Cases

- A goal, acceptance criterion, observation, decision statement, rationale, cancellation reason, or reopen reason that is empty or only spaces is refused, and the task is left unchanged.
- Two tasks may use the same title. They stay separate records, ordered by when they were created.
- Marking a task Ready is refused until it has a non-empty title, a non-empty goal, and at least one non-empty acceptance criterion.
- While a task is Draft or Ready, the engineer may change the goal and add or remove criteria. If a Ready task loses its goal or its last criterion, the status returns to Draft and the history records that cause.
- Clearing the goal, or removing the last acceptance criterion, is refused while the task is In Progress or Completed.
- Editing the text of a Verified criterion returns that criterion to Unverified and clears its observation, pass result, time, and provider. On a Completed task, the status also returns to In Progress. Every Completed ancestor returns to In Progress as well, and each history records that criterion edit as the cause. Verified criteria on those ancestors stay Verified.
- Verifying a criterion is refused unless the task is In Progress and the engineer records a non-empty observation, an explicit pass, and the time. An observation without a pass result leaves the criterion Unverified. Draft, Ready, Completed, and Cancelled tasks cannot gain a new verification until the task is In Progress.
- A task with no subtasks can be completed once it is In Progress and every criterion is Verified.
- A subtask in Draft, Ready, or In Progress blocks completion of its parent. A Completed or Cancelled subtask does not. The same rule applies at every level, so an unfinished grandchild blocks its parent and, through that parent, the top-level task.
- Cancelling a task is refused while any of its subtasks is Draft, Ready, or In Progress. The engineer finishes or cancels those subtasks first, confirms the cancellation, and supplies a reason.
- A Cancelled task rejects changes to its goal, its criteria, its subtasks, and its decisions. It cannot return to Draft, Ready, In Progress, or Completed. Continued work is a new task, and the cancelled task keeps its reason and history.
- A task cannot be its own parent, cannot have more than one parent, and cannot be placed under one of its descendants.
- Starting work, completing, reopening, cancelling, and verifying a criterion happen only when the engineer takes that action.
- There is no action that removes a saved decision. Superseding it leaves each earlier decision in place. A decision cannot name itself, a decision recorded after it, or a decision on another task.
- Repeating the same engineer actions from an empty workspace produces the same statuses, verification states, and ordering.
- Status history and decisions are shown oldest first. Top-level tasks and the subtasks of a parent are shown in creation order, oldest first.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to create a task by providing a title. The new task's status MUST be Draft.
- **FR-002**: The product MUST refuse to create a task whose title is empty or only spaces, and MUST tell the engineer that a title is required.
- **FR-003**: The engineer MUST be able to set and edit the goal of a task that is not Cancelled, subject to FR-014.
- **FR-004**: The engineer MUST be able to add, edit, and remove acceptance criteria on a task that is not Cancelled, subject to FR-014. Each new criterion MUST start as Unverified.
- **FR-005**: Each acceptance criterion MUST be exactly one of Unverified or Verified.
- **FR-006**: A task MUST be in exactly one status at a time: Draft, Ready, In Progress, Completed, or Cancelled.
- **FR-007**: The only status transitions MUST be:
  - Draft → Ready, when the engineer marks it Ready and FR-008 holds
  - Draft → Cancelled, when the engineer confirms cancellation and FR-018 holds
  - Ready → Draft, when the goal becomes empty or the last criterion is removed
  - Ready → In Progress, when the engineer starts work
  - Ready → Cancelled, when the engineer confirms cancellation and FR-018 holds
  - In Progress → Completed, when the engineer marks it completed and FR-009 holds
  - In Progress → Cancelled, when the engineer confirms cancellation and FR-018 holds
  - Completed → In Progress, when the engineer reopens it with a reason, when the text of a Verified criterion on it is edited, or when a descendant leaves Completed for either of those causes
- **FR-008**: Draft → Ready MUST be refused unless the title, the goal, and at least one acceptance criterion are each non-empty.
- **FR-009**: In Progress → Completed MUST be refused unless every acceptance criterion is Verified and every direct subtask is Completed or Cancelled. The refusal MUST name the unmet criteria and the unfinished subtasks.
- **FR-010**: Only the engineer MUST be able to mark a criterion Verified, and only while its task is In Progress, by recording three separate facts: a non-empty observation of what was seen, an explicit pass result, and the time of that action. The record MUST name that engineer as the provider. An assistant MUST NOT draft, confirm, or mark a criterion Verified. An observation with no pass result MUST leave the criterion Unverified. While a criterion is Unverified, the observation, pass result, time, and provider MUST be absent.
- **FR-011**: Changing the text of a Verified criterion MUST set that criterion back to Unverified and MUST clear its observation, pass result, time, and provider. If the task was Completed, its status MUST become In Progress and the history MUST name the criterion edit as the cause. Every Completed ancestor MUST also become In Progress, each history MUST name that criterion edit as the cause, and verified criteria on those ancestors MUST stay Verified.
- **FR-012**: The engineer MUST be able to return a Verified criterion to Unverified by an explicit action while the task is In Progress. That action MUST clear the observation, pass result, time, and provider.
- **FR-013**: While a task is Draft or Ready, removing the goal or the last acceptance criterion MUST be allowed. If the task was Ready and no longer satisfies FR-008, its status MUST become Draft and the history MUST record that cause.
- **FR-014**: Clearing the goal, or removing the last acceptance criterion, MUST be refused while the task is In Progress or Completed.
- **FR-015**: Every status change MUST keep the previous status, the new status, the time, and the cause. The engineer MUST be able to read that history oldest first.
- **FR-016**: The engineer MUST be able to add a subtask to a task that is Draft, Ready, or In Progress. The subtask MUST itself be a task with exactly one parent. A Completed or Cancelled task MUST refuse new subtasks.
- **FR-017**: The product MUST refuse a parent link that gives a task more than one parent, makes a task its own parent, or places a task under one of its descendants.
- **FR-018**: The engineer MUST be able to cancel a Draft, Ready, or In Progress task only by confirming that cancellation and providing a non-empty reason, and only when every direct subtask is already Completed or Cancelled. A Completed task MUST be reopened before it can be cancelled.
- **FR-019**: A Cancelled task MUST refuse edits to its goal and criteria, new subtasks, new decisions, new verifications, and any return to Draft, Ready, In Progress, or Completed. Continued work MUST be a new task. The cancelled task MUST keep its reason and history.
- **FR-020**: The engineer MUST be able to record an implementation decision on a task that is not Cancelled. The decision MUST include a non-empty statement, a non-empty rationale, and the time it was recorded, and it MUST belong to exactly one task.
- **FR-021**: A decision MAY name one or more earlier decisions on the same task as the ones it supersedes. It MUST NOT name itself, a decision recorded after it, or a decision on another task. Each named decision MUST remain visible and unchanged.
- **FR-022**: Decisions MUST NOT be removed. The engineer MUST be able to read a task's decisions oldest first.
- **FR-023**: The engineer MUST be able to reopen a Completed task only by an explicit action that includes a non-empty reason. That task MUST become In Progress, its history MUST record the reason, and its verified criteria MUST stay Verified until their text changes or the engineer marks them Unverified. Every Completed ancestor MUST also become In Progress, and each of those histories MUST record the same reopen as the cause. Verified criteria on those ancestors MUST stay Verified.
- **FR-024**: The engineer MUST be able to list tasks that have no parent, oldest first, and open any task to see its goal, acceptance criteria and verification state, current status, status history, subtasks, and decisions.
- **FR-025**: Subtasks of a parent MUST be listed oldest first. The same status, criterion, and decision rules MUST apply to a subtask as to any other task.
- **FR-026**: Completion, cancellation, reopening, starting work, and criterion verification MUST occur only as explicit engineer actions. The product MUST NOT infer them from the presence of a goal, a decision, or a criterion.
- **FR-027**: From an empty workspace, repeating the same sequence of engineer actions MUST produce the same statuses, the same verification states, and the same ordering of tasks, subtasks, history, and decisions.

### Key Entities *(include if feature involves data)*

- **Task**: A unit of engineering work. It has a title, a goal, one status, a creation time, an optional parent task, zero or more subtasks, zero or more acceptance criteria, zero or more decisions, and a status history.
- **Acceptance Criterion**: A checkable condition on one task. It has text and a verification state of Unverified or Verified. When Verified, it names the engineer who provided the evidence and has three separate facts: the observation, an explicit pass result, and the verification time. When Unverified, the provider and those three facts are absent.
- **Status Change**: One recorded transition on a task. It has the previous status, the new status, the time, and the cause (the engineer action or the edit that produced it).
- **Implementation Decision**: A choice recorded against one task. It has a statement, a rationale, the time it was recorded, and zero or more references to earlier decisions on the same task that it supersedes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer can create a task, enter a goal, add one acceptance criterion, and see that task on the list in under 3 minutes.
- **SC-002**: In a review of tasks marked Completed, 100% have every acceptance criterion Verified with the engineer named as provider, an observation, an explicit pass, and a time, and 100% have no subtask still in Draft, Ready, or In Progress.
- **SC-003**: A reader who did not perform the work can name the current status of a task and the cause of its latest status change from the task record alone, for 100% of a sample of 20 tasks.
- **SC-004**: An engineer can add a subtask to a parent and see that subtask listed on the parent in under 2 minutes.
- **SC-005**: 100% of saved decisions show a statement, a rationale, a time, and exactly one task. When a decision supersedes one or more earlier decisions, each of those earlier decisions remains readable.
- **SC-006**: Two passes of the same written sequence (create, mark ready, start, verify, complete, reopen, and record a decision), each starting from an empty workspace, produce the same statuses and the same order of tasks, criteria, and decisions.
- **SC-007**: At least 95% of engineers complete the primary path — create a task, define a goal and one acceptance criterion, start it, verify the criterion, and mark it completed — on the first attempt without assistance.

## Assumptions

- One engineer works in one workspace. Sign-in, sharing, permissions, and assigning work to other people are out of this feature.
- The engineer performs every action in this feature. Only that engineer may verify a criterion, and the verification record names them. An assistant that creates, splits, verifies, or completes tasks is out of scope. The records are still complete enough for a later reader to reconstruct the goal, the checks, the status, and the decisions without the original conversation.
- Abandoned or mistaken work ends as Cancelled, with a recorded reason. Cancelled is final and cannot be restored. Continued work is a new task. Deleting tasks or decisions is out of scope so the history stays intact.
- Subtasks may themselves have subtasks. A task has at most one parent. A cycle is refused.
- A subtask follows the same goal, criterion, status, and decision rules as a top-level task.
- Duplicate titles are allowed. Creation time distinguishes tasks that share a title.
- Priority, due dates, estimates, comments, notifications, and links to code review or release tools are out of scope.
- Times shown on status changes, verifications, and decisions are the times the engineer performed those actions.
- These rules follow the project constitution: one explicit status, a trace from the goal through the work to the evidence, and no completion until the acceptance criteria are checked.
