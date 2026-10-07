# Feature Specification: Link a Decision to Its Evidence

**Feature Branch**: `004-link-decision-evidence`

**Created**: 2026-10-07

**Status**: Accepted

**Input**: User description: "The next feature should let the engineer record a decision that names the check it rests on, so a later reader can follow the requirement, the task, the change, the check, and the decision without the original conversation. Keep it human-driven. An assistant that decides on its own stays out of scope. Priority, due dates, comments, and sharing stay out of scope."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a decision that names its check (Priority: P1)

An engineer records a decision on a task and names the check that decision rests on. The decision states what was chosen and why. Opening the task later shows that decision together with the criterion that was checked, what changed, the evidence, and the result of that check.

**Why this priority**: A decision that does not name its evidence still needs the original conversation. The named check is what lets a later reader follow the requirement through the change to the decision.

**Independent Test**: On one task that is not Cancelled, record a carried-out change and a check of that change, then record a decision that names that check, and read the decision back on the task. The task status, the change outcome, the check, and the criterion's verification state stay as they were.

**Acceptance Scenarios**:

1. **Given** an In Progress task with the acceptance criterion "The export contains the goal", a carried-out change "Rename the export label", and a Passed check of that change against that criterion whose evidence is "The detail page shows the goal in the export", **When** the engineer records the statement "Keep the export label" and the rationale "The check shows the goal is visible" naming that check, **Then** the task shows that decision with the statement, the rationale, the time, the criterion wording, the account of what changed, the evidence, and Passed, the change stays Carried out, the check stays Passed, and the task stays In Progress.
2. **Given** the same task and a Failed check whose evidence is "The label was still old", **When** the engineer records a non-empty statement and rationale naming that Failed check, **Then** the decision shows that evidence and Failed, and the check stays Failed.
3. **Given** a task that is not Cancelled and a check on that task, **When** the statement or the rationale is empty or only spaces, **Then** no decision is stored and the engineer is told both a statement and a rationale are required.
4. **Given** a task that is not Cancelled, **When** the engineer uses this action to record a statement and a rationale but names no check, **Then** no decision is stored and the engineer is told to choose the check this decision rests on.
5. **Given** a task that is not Cancelled, **When** the engineer names a check that does not exist, **Then** no decision is stored and the engineer is told the check was not found.
6. **Given** a check on one task, **When** the engineer records a decision on a different task that names that check, **Then** no decision is stored and the engineer is told the decision must name a check on that task.
7. **Given** a Cancelled task that already has a check, **When** the engineer records a decision naming that check, **Then** no decision is stored and the engineer is told decisions cannot be added to a cancelled task.
8. **Given** a Completed task with a check recorded before it was completed, **When** the engineer records a decision naming that check, **Then** the decision is stored and the task stays Completed.

---

### User Story 2 - Keep the decision on the check it named (Priority: P2)

A later check of the same change and criterion does not rewrite a decision already recorded. The decision keeps the evidence and the result of the check it named. A later reader can still tell which evidence the decision used.

**Why this priority**: If a later check replaced the evidence a decision cited, the record would no longer show what the engineer actually relied on.

**Independent Test**: Record a decision naming a Failed check, then record a later Passed check of the same change and criterion, and read the decision again. It still shows the earlier evidence and Failed. The later check is also still listed.

**Acceptance Scenarios**:

1. **Given** a decision that names a Failed check of a carried-out change against one criterion, **When** the engineer records a later Passed check of that same change and criterion, **Then** the decision still shows the earlier evidence and Failed, the earlier check is unchanged, and the later check is listed after it.
2. **Given** a decision that names one check, **When** the engineer records another check of a different criterion on the same change, **Then** the decision still names the original check and shows that check's criterion wording, evidence, and result.
3. **Given** a stored decision that names a check, **When** the engineer tries to change its statement, its rationale, or which check it names, or tries to remove it, **Then** the stored decision is unchanged.
4. **Given** a check whose criterion wording is later edited on the task, **When** the engineer reads a decision that names that check, **Then** the decision still shows the criterion wording stored with the check.

---

### User Story 3 - Supersede a decision without losing the chain (Priority: P3)

An engineer can record a later decision that names a check and supersedes one or more earlier decisions on the same task. Every earlier decision stays readable, including a decision that does not name a check. The later decision identifies the ones it supersedes.

**Why this priority**: Work often revises an earlier choice. The revision has to stay attached to evidence, and the earlier choice has to remain so a later reader can see what changed.

**Independent Test**: On one task, save a decision that does not name a check, then save a decision that names a check and supersedes the first. Both remain visible, and only the second shows a check.

**Acceptance Scenarios**:

1. **Given** a task with a decision that has a statement and a rationale and does not name a check, **When** the engineer records a later decision that names a check on that task and names the earlier decision as superseded, **Then** both decisions remain visible, the later decision identifies the earlier one, and the later decision shows that check's evidence and result.
2. **Given** a task with two earlier decisions, **When** the engineer records a later decision that names a check on that task and names both as superseded, **Then** all three remain visible and the later decision identifies both.
3. **Given** a decision on one task and a check on that same task, **When** the engineer records a decision naming that check and also naming a decision from a different task as superseded, **Then** the new decision is not saved and the engineer is told a decision can only supersede earlier decisions on the same task.
4. **Given** a task that is not Cancelled, **When** the engineer records a decision with a statement and a rationale and does not name a check, using the existing decision action, **Then** that decision is saved without a check, as it is today.
5. **Given** a parent task and a subtask that has its own check, **When** the engineer records a decision on the subtask naming that check, **Then** the decision appears on the subtask and does not appear on the parent.

---

### Edge Cases

- A statement or rationale that is only spaces is refused, and no partial decision is stored. The check it would have named is left unchanged.
- If the statement or rationale is blank and the check is also missing, the engineer is told both a statement and a rationale are required, and nothing is stored.
- The product does not treat a Passed check, a Failed check, or a Verified criterion as a decision. The engineer writes the statement and the rationale and names the check.
- A decision may name a Passed check or a Failed check. The product does not require the named check to be the current result of that change and criterion.
- A Cancelled task rejects the new decision. Checks and decisions already stored stay visible. Continued work is a new task.
- A decision that names a check on another task is refused, and nothing is stored.
- Two decisions on the same task may name the same check. Each stays visible.
- Recording this decision does not verify or unverify an acceptance criterion, does not approve a change, does not record a new check, and does not start, complete, cancel, or reopen the task.
- Completing or cancelling a task is not refused only because a change has no decision, or because a decision does not name a check. Existing completion and cancellation rules still apply.
- A decision on a subtask's check does not appear on the parent, and it does not satisfy the parent. The parent lists only its own decisions.
- Removing an acceptance criterion does not remove a check or a decision that names that check. The decision still shows the criterion wording stored with the check.
- Reopening a Completed task leaves decisions and the checks they name in place.
- A later decision follows the existing supersede rules: it may name one or more earlier decisions on the same task, and it cannot name itself, a decision recorded after it, or a decision on another task.
- Two decisions recorded in the same order on the same kind of task, naming the same check, produce the same statements and the same order.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to record a decision on a task that is not Cancelled by providing a non-empty statement, a non-empty rationale, and naming exactly one change check on that same task.
- **FR-002**: The product MUST refuse a decision of this kind whose statement or rationale is empty or only spaces, and MUST leave stored records unchanged. The refusal MUST tell the engineer that both a statement and a rationale are required.
- **FR-003**: The product MUST refuse a decision of this kind that names no check. The refusal MUST tell the engineer to choose the check this decision rests on, and MUST leave stored records unchanged.
- **FR-004**: Each decision of this kind MUST name exactly one check on its task. Reading it MUST show the statement, the rationale, the time it was recorded, the criterion wording stored on that check, the account of what changed, the evidence, and the result of that check. The task the decision serves is the task that check serves.
- **FR-005**: The product MUST refuse a decision that names a check that does not exist, and MUST tell the engineer the check was not found. The product MUST refuse a decision that names a check on a different task, and MUST tell the engineer the decision must name a check on that task. A refusal MUST leave existing decisions and checks unchanged.
- **FR-006**: The product MUST refuse a decision on a Cancelled task and MUST tell the engineer that decisions cannot be added to a cancelled task. A decision naming a check MAY be recorded on a Draft, Ready, In Progress, or Completed task when that check is on that task.
- **FR-007**: The product MUST NOT infer a decision from a check, from Passed or Failed, or from a Verified criterion. The engineer writes the statement and the rationale and names the check.
- **FR-008**: Recording a decision that names a check MUST NOT change the task status, the outcome of the implementation change, the evidence or result of any check, the Verified or Unverified state of any acceptance criterion, or any earlier decision.
- **FR-009**: A saved decision MUST NOT be edited or removed, and MUST remain named to the same check. A later check of the same change and criterion MUST NOT change the evidence or result shown for a decision that named an earlier check.
- **FR-010**: Decisions on a task MUST be listed oldest first. A decision that names a check and a decision that does not name a check appear in that one list. For a decision that names a check, the engineer MUST be able to read the statement, the rationale, the time, the criterion wording, the account of what changed, the evidence, and the result.
- **FR-011**: A later decision that names a check MAY name one or more earlier decisions on the same task as the ones it supersedes, including an earlier decision that does not name a check. It MUST NOT name itself, a decision recorded after it, or a decision on another task. Each named decision MUST remain visible and unchanged. The existing refusal for a decision on another task still applies.
- **FR-012**: The engineer MUST still be able to record a decision with only a non-empty statement and a non-empty rationale, without naming a check, under the existing decision rules.
- **FR-013**: Only the engineer of the workspace may record a decision that names a check. The decision belongs to that engineer's task record.
- **FR-014**: From the same task with the same check, repeating the same sequence of decisions MUST produce the same statements, the same named checks, and the same order of records.
- **FR-015**: The product MUST NOT refuse to complete or cancel a task solely because a carried-out change has no decision, or because a decision does not name a check.
- **FR-016**: A decision that names a check on a subtask MUST NOT appear as a decision of the parent task and MUST NOT satisfy the parent. Each task lists only its own decisions.

### Key Entities *(include if feature involves data)*

- **Linked Decision**: An implementation decision on one task that names exactly one change check on that task. It has a statement, a rationale, the time it was recorded, and the check it rests on. Reading it also shows the criterion wording, the account of what changed, the evidence, and the result stored with that check. It may name earlier decisions on the same task that it supersedes.
- **Decision Chain**: The readable path from one linked decision back to its task, the acceptance criterion wording stored on the named check, the account of what changed, and that check's evidence and result. The chain stays on the named check even when a later check of the same change and criterion has a different result.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, the criterion wording, what changed, the evidence, the check result, the decision statement, and the rationale, in under 2 minutes.
- **SC-002**: In a review of decisions that name a check, 100% name exactly one check on that decision's task and show a non-empty statement, a non-empty rationale, a time, that check's criterion wording, the account of what changed, the evidence, and the result.
- **SC-003**: Across a sample of 20 decisions that name a check, 100% leave the task status, the change outcome, the named check's evidence and result, and each acceptance criterion's Verified or Unverified state unchanged.
- **SC-004**: Two passes of the same written sequence (record a decision naming a Failed check, then record a Passed check of that same change and criterion), each starting from the same kind of task with that one Failed check and no decision naming it, produce the same decision text and leave that decision showing the earlier evidence and Failed.
- **SC-005**: At least 95% of engineers record a decision naming one check and find the criterion, the change, the evidence, and the decision together on the task on the first attempt without assistance.
- **SC-006**: In a review of later checks recorded after a decision named an earlier check of the same change and criterion, 100% of those decisions still show the evidence and result of the check they named.
- **SC-007**: In a review of completion attempts, 100% are unchanged by the mere absence of a decision on a carried-out change. A decision with only a statement and a rationale can still be saved.

## Assumptions

- The task record, the implementation record, and the check record are already in place: one engineer, one workspace, decisions with a statement and a rationale, and change checks that store a criterion wording, evidence, and Passed or Failed. This feature lets a decision name one of those checks. It does not add people, sharing, or a second author.
- A decision of this kind names one stored check, not "whatever the latest result is." A later check does not move the decision onto the new result. A new choice is a new decision, which may supersede the earlier one.
- The engineer may name a Passed check or a Failed check. A failure is evidence a decision can rest on.
- The existing decision that has only a statement and a rationale stays available. This feature does not require every decision to name a check. Choices made before any check still have a place to be written down.
- Recording the decision does not mark an acceptance criterion Verified, does not record a check, and does not change whether a change is Carried out, Awaiting approval, or Not carried out.
- Completing and cancelling a task keep their current rules. A missing decision is not a new reason to refuse either action.
- The same engineer who owns the workspace records the decision. An assistant that writes the decision is out of scope.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools stay out of scope.
- An autonomous developer that carries out work, checks it, or records decisions on its own stays out of scope.
- These rules follow the project constitution: the decision is stored on the task, and a later reader can follow it to the requirement, the change, and the evidence without the original conversation.
