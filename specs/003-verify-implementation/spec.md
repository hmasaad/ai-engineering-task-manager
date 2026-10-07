# Feature Specification: Verify a Recorded Change

**Feature Branch**: `003-verify-implementation`

**Created**: 2026-10-07

**Status**: Accepted

**Input**: User description: "The next feature should let the engineer check a recorded implementation change: what was checked, the evidence, and whether it passed. A later reader must be able to inspect that check without the original conversation. Keep it human-driven. An assistant that verifies on its own stays out of scope. Priority, due dates, comments, and sharing stay out of scope."

## Clarifications

### Session 2026-10-07

- Q: When a carried-out change has been checked against more than one acceptance criterion, which results must be Passed before that change counts as passing? → A: Every criterion already checked must have a current Passed result.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check a carried-out change against a criterion (Priority: P1)

An engineer takes a change that is already carried out and records a check of it against one acceptance criterion of the same task. The check states the evidence of what was seen and whether that check passed or failed. Opening the task later shows that check with the change it serves.

**Why this priority**: A carried-out change is not yet something a later reader can trust. The check is the record that ties the change to a requirement and to evidence.

**Independent Test**: On one In Progress task, record an ordinary change, then record a passing check of that change against one acceptance criterion, and read the check back on the task. The task status and the change outcome stay as they were.

**Acceptance Scenarios**:

1. **Given** an In Progress task with the acceptance criterion "The export contains the goal" and a carried-out change "Rename the export label", **When** the engineer records the evidence "The detail page shows the goal in the export" and the result Passed for that change and that criterion, **Then** the task shows that check with the criterion wording, the evidence, Passed, the engineer, and the time, the change stays Carried out, and the task stays In Progress.
2. **Given** the same In Progress task and carried-out change, **When** the engineer records non-empty evidence and the result Failed, **Then** the check is stored as Failed, the change stays Carried out, and the task stays In Progress.
3. **Given** an In Progress task with a carried-out change and one acceptance criterion, **When** the evidence is empty or only spaces, **Then** no check is stored and the engineer is told an account of the evidence is required.
4. **Given** an In Progress task with a carried-out change and one acceptance criterion, **When** the result is missing or is neither Passed nor Failed, **Then** no check is stored and the engineer is told to choose Passed or Failed.
5. **Given** an In Progress task with a consequential change that is Awaiting approval, **When** the engineer tries to record a check of that change, **Then** no check is stored and the change stays Awaiting approval.
6. **Given** an In Progress task with a change that is Not carried out, **When** the engineer tries to record a check of that change, **Then** no check is stored and the change stays Not carried out.
7. **Given** a carried-out change on a task that is Completed, **When** the engineer tries to record a check, **Then** no check is stored and the engineer is told to reopen the task first.
8. **Given** an In Progress task with a carried-out change, **When** the engineer names an acceptance criterion from a different task, **Then** no check is stored.
9. **Given** an In Progress task, **When** the engineer names a carried-out change from a different task, **Then** no check is stored.

---

### User Story 2 - Finish the task only when each carried-out change has passed (Priority: P2)

An engineer can mark a task completed only when every carried-out change on that task has a passing check. A change has a passing check when every acceptance criterion it has been checked against has a current result of Passed. A change with no check, or with a current Failed result for any criterion it has been checked against, keeps the task In Progress. The engineer is told which changes are still short.

**Why this priority**: The check in Story 1 is useful only if completion cannot skip it. A task with carried-out work still waits until that work has a passing check.

**Independent Test**: On one In Progress task whose acceptance criteria are already Verified and that has no subtasks, record one ordinary change and attempt to complete the task before any check. Then record a passing check and complete the task.

**Acceptance Scenarios**:

1. **Given** an In Progress task whose acceptance criteria are all Verified, that has no unfinished subtasks, and that has one carried-out change with no check, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told that change by the account of what changed.
2. **Given** that same task where the change's current result is Failed, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told that change by the account of what changed.
3. **Given** that same task where the change has a current result of Passed against an acceptance criterion on that task, **When** the engineer marks the task completed, **Then** the status is Completed.
4. **Given** an In Progress task with two carried-out changes, only one of which has a current Passed result, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told only the change that lacks a current Passed result.
5. **Given** an In Progress task whose acceptance criteria are all Verified, that has no carried-out changes, and whose only implementation change is Not carried out, **When** the engineer marks the task completed, **Then** the status is Completed.
6. **Given** an In Progress task whose acceptance criteria are all Verified and that has no implementation changes, **When** the engineer marks the task completed, **Then** the status is Completed.
7. **Given** an In Progress task with a carried-out change that has no check and a consequential change that is Awaiting approval, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told both the waiting change and the carried-out change that lacks a passing check.
8. **Given** an In Progress task with a carried-out change that has no check and no unfinished subtasks, **When** the engineer cancels the task with a reason, **Then** the status is Cancelled.
9. **Given** an In Progress task that otherwise may be completed, and a carried-out change with a current Passed result against one acceptance criterion and a current Failed result against another acceptance criterion on that task, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told that change by the account of what changed.

---

### User Story 3 - Record a later check without erasing the earlier one (Priority: P3)

An engineer who already checked a change can record another check. The earlier check stays visible and unchanged. The current result is the latest check for that change and that criterion.

**Why this priority**: A failed check has to remain in the record when a later check passes, and a later failure has to be able to supersede a pass. Neither case should rewrite history.

**Independent Test**: On one carried-out change, record a Failed check against one criterion, then a Passed check against the same criterion, and confirm both appear in that order with Passed as the current result.

**Acceptance Scenarios**:

1. **Given** a carried-out change whose only check against a criterion is Failed, **When** the engineer records a later check of the same change and the same criterion with result Passed, **Then** both checks remain in that order, the earlier evidence and Failed result are unchanged, and the current result for that pair is Passed.
2. **Given** a carried-out change whose current result against a criterion is Passed, and a task that otherwise may be completed, **When** the engineer records a later check of that same pair with result Failed, **Then** the current result is Failed and marking the task completed leaves it In Progress.
3. **Given** a carried-out change with a Passed check against one criterion, **When** the engineer records a Passed check of the same change against a different criterion on that task, **Then** both checks remain and the change still counts as having a passing check.
4. **Given** a stored check, **When** the engineer tries to change its evidence or result, or to remove it, **Then** the stored check is unchanged.

---

### Edge Cases

- A check whose evidence is only spaces is refused, and no partial check is stored.
- The product does not treat persuasive evidence wording as a pass. The engineer must choose Passed or Failed.
- A check on a Draft or Ready task is refused. A change cannot be recorded in those statuses, and a check is refused with the same demand that the task be In Progress or started.
- A check on a Cancelled task is refused. Existing checks stay visible. Continued work is a new task.
- A check that names a change or a criterion on another task is refused, and nothing is stored.
- Recording a check does not verify or unverify an acceptance criterion, does not approve a change, and does not start, complete, cancel, or reopen the task.
- A Not carried out change does not need a check before completion or cancellation.
- A change that is Awaiting approval still blocks completion and cancellation, and it cannot be checked until it is carried out.
- Completing a parent considers only that parent's carried-out changes. A subtask's missing check is not copied onto the parent. The subtask itself cannot be completed until its own carried-out changes have a current passing check.
- Reopening a Completed task leaves existing checks in place.
- Editing the wording of an acceptance criterion does not rewrite checks already stored. Each check keeps the wording it recorded.
- A current Failed result for any criterion a change has been checked against means that change lacks a passing check, even when another criterion of that change has a current Passed result. A later Passed result for the failed criterion can make that pair Passed. The earlier Failed check stays in the record.
- Two checks recorded in the same order on the same kind of task produce the same results and the same order.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to record a check of one carried-out implementation change on a task that is In Progress by naming one acceptance criterion of that same task, providing a non-empty account of the evidence of what was seen, and choosing an explicit result of Passed or Failed.
- **FR-002**: The product MUST refuse a check whose evidence is empty or only spaces, or whose result is missing or neither Passed nor Failed, and MUST leave stored records unchanged.
- **FR-003**: Each check MUST serve exactly one implementation change and exactly one acceptance criterion. The record MUST name that change, that criterion, the wording of the criterion at the time of the check, the evidence, the result, the engineer, and the time. The task the check serves is the task that change serves.
- **FR-004**: The product MUST refuse a check when the task is Draft, Ready, Completed, or Cancelled. The refusal MUST tell the engineer to start the task, to reopen it, or that continued work is a new task, matching that status.
- **FR-005**: The product MUST refuse a check of a change that is Awaiting approval or Not carried out, a check that names a change on a different task, and a check that names an acceptance criterion on a different task. A refusal MUST leave the change and any existing checks unchanged.
- **FR-006**: The product MUST NOT infer Passed or Failed from the wording of the evidence. The engineer chooses the result.
- **FR-007**: Recording a check MUST NOT change the task status, the outcome of the implementation change, the Verified or Unverified state of any acceptance criterion, or the task's implementation decisions.
- **FR-008**: Checks on a change MUST be listed oldest first. The engineer MUST be able to read, for each check, the criterion wording, the evidence, the result, the engineer, and the time. The current result of one change and one criterion is the latest check of that pair. A change has a passing check only when it has been checked against at least one acceptance criterion on its task and every criterion it has been checked against has a current result of Passed.
- **FR-009**: A saved check MUST NOT be edited or removed, and MUST NOT be moved to another change or another criterion.
- **FR-010**: While a task is In Progress, the engineer MUST be able to record a later check of a carried-out change that already has one. The later check MAY name the same criterion or another acceptance criterion on that task. Earlier checks MUST stay unchanged.
- **FR-011**: Only the engineer of the workspace may record a check. Every stored check MUST name that engineer and MUST NOT name a different person.
- **FR-012**: From the same In Progress task with the same carried-out change and no checks, repeating the same sequence of checks MUST produce the same results and the same order of records.
- **FR-013**: The product MUST refuse to mark a task Completed while any carried-out change on that task lacks a passing check. The task MUST stay In Progress, and the engineer MUST be told each such change by the account of what changed. A change that is Not carried out MUST NOT by itself block completion. A task with no carried-out changes MUST NOT be blocked by this rule. A change that is Awaiting approval MUST continue to block completion under the existing rule.
- **FR-014**: The product MUST NOT refuse to cancel a task solely because a carried-out change lacks a passing check.
- **FR-015**: A passing check of a subtask's change MUST NOT satisfy a parent task. Completing a task considers only the carried-out changes on that task.

### Key Entities *(include if feature involves data)*

- **Change Check**: The record that a carried-out implementation change was checked against one acceptance criterion. It names the change, the criterion, the wording of that criterion at the time of the check, the evidence of what was seen, a result of Passed or Failed, the engineer, and the time. The current result for a change and a criterion is the latest check of that pair.
- **Passing Check**: A carried-out change has a passing check when every acceptance criterion it has been checked against has a current result of Passed, and it has been checked against at least one. A current Failed result for any of those criteria, or no check at all, is not a passing check.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, what was checked, the evidence, and whether a carried-out change passed, in under 2 minutes.
- **SC-002**: In a review of stored change checks, 100% name exactly one change, exactly one acceptance criterion on that change's task, the criterion wording, a non-empty account of the evidence, a result of Passed or Failed, the engineer, and the time.
- **SC-003**: In a review of completion attempts made while a carried-out change on that task lacks a passing check, 100% leave the task In Progress and name each such change by the account of what changed.
- **SC-004**: Across a sample of 20 check actions, 100% leave the task status, the change outcome, and each acceptance criterion's Verified or Unverified state unchanged.
- **SC-005**: Two passes of the same written sequence (record a Failed check of a carried-out change against one criterion, then a Passed check of that same pair), each starting from the same kind of In Progress task with that one carried-out change and no checks, produce the same results and the same order of records.
- **SC-006**: At least 95% of engineers record a passing check of an ordinary carried-out change and find it again on the task on the first attempt without assistance.
- **SC-007**: In a review of completion of tasks that have at least one carried-out change, 100% of those changes have been checked, and 100% of the criteria each change was checked against have a current Passed result.

## Assumptions

- The task record and the implementation record are already in place: one engineer, one workspace, the statuses Draft, Ready, In Progress, Completed, and Cancelled, acceptance criteria that are Verified only by a separate action, and implementation changes that are Carried out, Awaiting approval, or Not carried out. This feature attaches checks to carried-out changes. It does not add people, sharing, or a second checker.
- What was checked is an acceptance criterion of the same task. The engineer names that criterion. The check keeps the criterion's wording as it stood at the time. A passing result that does not name an acceptance criterion is not a check this feature will store.
- The engineer writes the evidence in their own words and explicitly chooses Passed or Failed. This feature does not read files, run a test, or collect a review link.
- The same engineer who carried out the change records the check. Recording the change, or approving a consequential change, is not the check.
- A task with no carried-out changes is still completed under the existing rules: every acceptance criterion Verified, every direct subtask Completed or Cancelled, and no change Awaiting approval.
- Cancelling a task does not require a passing check. Cancellation abandons the task. The checks already stored stay visible.
- A later check does not delete an earlier one. The current result of a change and a criterion is the latest check of that pair. A change has a passing check only when every criterion it has been checked against has a current result of Passed.
- This feature does not mark an acceptance criterion Verified, and it does not create implementation decisions. Verifying a criterion remains a separate explicit action.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools stay out of scope.
- An assistant that records a check is out of scope. The engineer performs every action in this feature. An autonomous developer that carries out or checks work on its own stays out of scope.
- These rules follow the project constitution: the check is stored on the change a later reader can open, the check names the requirement it closes, and completion of a task that has carried-out work waits until that work has a passing check.
