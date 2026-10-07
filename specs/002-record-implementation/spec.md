# Feature Specification: Record Task Implementation

**Feature Branch**: `002-record-implementation`

**Created**: 2026-10-06

**Status**: Accepted

**Input**: User description: "The next feature should let the engineer attach the change that carries out a task: what was changed, which task it serves, and a record a later reader can check without the original conversation. Keep it human-driven. Consequential actions still need a named approval. Priority, due dates, comments, and sharing stay out of scope."

## Clarifications

### Session 2026-10-07

- Q: If a consequential change is still waiting for approval, can the engineer complete or cancel that task? → A: No. The task cannot be completed or cancelled until every waiting change is approved or marked not carried out. Approval and decline stay available only while the task is In Progress.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Attach what changed to an in-progress task (Priority: P1)

An engineer who has started a task records the change that carries it out. The record says what changed and which task it serves. A later reader opens that task and sees the record without the original conversation.

**Why this priority**: The goal and the acceptance criteria say what "done" means. They do not say what was actually changed. Without this record, a later reader cannot check the work from the task alone.

**Independent Test**: On one In Progress task, record one ordinary change that describes what changed. Open the task and confirm the description, the task it serves, the engineer, and the time are visible, and the task status is still In Progress.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer records an ordinary change with a non-empty account of what changed, **Then** the change appears on that task as Carried out, names that task, names the engineer, and records the time, and the task status stays In Progress.
2. **Given** the engineer is recording a change, **When** the account of what changed is empty or only spaces, **Then** nothing is saved and the engineer is told an account of what changed is required.
3. **Given** the engineer is recording a change, **When** the engineer does not state whether the change is ordinary or consequential, **Then** nothing is saved and the engineer is told to choose ordinary or consequential.
4. **Given** a Draft task, **When** the engineer records a change, **Then** nothing is saved and the engineer is told the task must be In Progress.
5. **Given** a Ready task, **When** the engineer records a change, **Then** nothing is saved and the engineer is told to start the task first.
6. **Given** a Completed task, **When** the engineer records a change, **Then** nothing is saved and the engineer is told to reopen the task first.
7. **Given** a Cancelled task, **When** the engineer records a change, **Then** nothing is saved and the engineer is told that continued work is a new task.
8. **Given** an In Progress task on which the engineer has recorded two ordinary changes, first "Rename the export label" and then "Write the export steps", **When** a reader opens the task, **Then** the two changes appear in that order, each still naming that task.
9. **Given** an In Progress task, **When** the engineer records an ordinary change, **Then** the task is not marked Completed, no acceptance criterion changes verification state, and no implementation decision is created.
10. **Given** a change recorded on one task, **When** a reader opens a different task, **Then** that change is not listed there.

---

### User Story 2 - Approve a consequential change by name (Priority: P2)

Some changes must not count as carried out just because they were written down. The engineer marks a change consequential when it removes or overwrites something already kept, changes who is allowed to do something, spends money, contacts someone outside the workspace, merges or publishes work, or cannot be undone by a later change on the same task. Saving that change leaves it waiting. A later, separate action approves that specific change and states the evidence the engineer reviewed. Until that approval exists, the change is not carried out, and the task cannot be completed or cancelled.

**Why this priority**: An ordinary record is enough for the common case. Consequential work needs a second explicit act so silence, or the act of describing the change, is never treated as approval.

**Independent Test**: On one In Progress task, record a consequential change and confirm it is awaiting approval and the task is still In Progress. Then approve that change with a non-empty account of the evidence reviewed, and confirm the change is carried out and the approval names the change, the evidence, the engineer, and the time.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer records a consequential change with a non-empty account of what changed, **Then** the change is Awaiting approval, it is not carried out, no approval is stored, and the task status stays In Progress.
2. **Given** a change that is Awaiting approval, **When** the engineer approves it in a separate action that names that change and includes a non-empty account of the evidence reviewed, **Then** the change is Carried out, the approval names the engineer, the evidence, and the time, and the task status stays In Progress.
3. **Given** a change that is Awaiting approval, **When** the engineer tries to approve it with an empty or whitespace-only account of the evidence reviewed, **Then** the change stays Awaiting approval and no approval is stored.
4. **Given** an ordinary change that is already Carried out, **When** the engineer tries to approve it, **Then** the change stays Carried out and the engineer is told that an ordinary change does not wait for approval.
5. **Given** a consequential change that was only saved, **When** no later approval action is taken, **Then** the change stays Awaiting approval.
6. **Given** a consequential change that is already Carried out, **When** the engineer tries to approve it again, **Then** the original approval stays unchanged and the engineer is told the change is already carried out.
7. **Given** a change recorded on one task, **When** the engineer tries to approve a change that is not on that task, **Then** nothing is approved and the engineer is told the approval must name a change on that task.
8. **Given** an In Progress task whose acceptance criteria are all Verified, **When** the engineer records a consequential change or approves one, **Then** the task stays In Progress.
9. **Given** an In Progress task whose acceptance criteria are all Verified, that has no unfinished subtasks, and that has one change Awaiting approval, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told that change is still Awaiting approval, by the account of what changed.
10. **Given** an In Progress task that has no unfinished subtasks and one change Awaiting approval, **When** the engineer cancels the task with a reason, **Then** the status stays In Progress and the engineer is told that change is still Awaiting approval, by the account of what changed.
11. **Given** an In Progress task whose acceptance criteria are all Verified, that has no unfinished subtasks, and whose only change was Awaiting approval and has since been approved, **When** the engineer marks the task completed, **Then** the status is Completed.

---

### User Story 3 - Leave a consequential change uncarried (Priority: P3)

The engineer can close a consequential change that should not be carried out. The proposal stays on the task with a reason. It cannot be approved afterward. The task status does not change.

**Why this priority**: A change left waiting forever looks unfinished, and deleting it would hide the proposal. The reader needs to see that it was considered and not carried out.

**Independent Test**: Record one consequential change, mark it not carried out with a reason, and confirm it remains visible, cannot be approved, and the task status is unchanged.

**Acceptance Scenarios**:

1. **Given** a change that is Awaiting approval, **When** the engineer marks it not carried out with a non-empty reason, **Then** the change stays visible as Not carried out, the reason, the engineer, and the time are recorded, and the task status stays In Progress.
2. **Given** a change that is Not carried out, **When** the engineer tries to approve it, **Then** it stays Not carried out and the engineer is told it cannot be carried out.
3. **Given** an ordinary change that is Carried out, **When** the engineer tries to mark it not carried out, **Then** it stays Carried out and the engineer is told a carried-out change stays in the record.
4. **Given** a consequential change that is already Carried out, **When** the engineer tries to mark it not carried out, **Then** it stays Carried out and the original approval stays unchanged.
5. **Given** a change that is Awaiting approval, **When** the reason for not carrying it out is empty or only spaces, **Then** the change stays Awaiting approval and the engineer is told a reason is required.

---

### Edge Cases

- An account of what changed, an account of the evidence reviewed, or a reason for not carrying out a change that is empty or only spaces is refused, and the stored records are left unchanged.
- The engineer must choose ordinary or consequential when recording a change. The product does not infer that choice from the wording of what changed.
- Two changes may describe similar work. They stay separate records, ordered by when they were recorded, oldest first.
- Recording, approving, or declining a change does not start, complete, cancel, or reopen the task, and does not verify or unverify a criterion.
- A saved implementation record cannot be edited or removed. A saved approval cannot be edited or removed. A later change is a new record.
- A change serves exactly one task. It cannot be moved onto another task, and it is not listed on any other task.
- Approving a change and marking it not carried out are explicit engineer actions. Saving the change is not approval. Silence is not approval. Both actions are refused unless the task is In Progress, and the change outcome stays unchanged.
- Only a change that is Awaiting approval can be approved or marked not carried out.
- Completing or cancelling a task is refused while any change on that task is Awaiting approval. The task stays In Progress, and the engineer is told each waiting change by the account of what changed. A change that is Carried out or Not carried out does not block completion or cancellation.
- An implementation decision already stored on the task is not an implementation record. Recording a decision does not attach a change. Attaching a change does not create a decision.
- A reader who did not perform the work can name, for each change on the task, what changed, whether it was ordinary or consequential, whether it was carried out, and, when consequential and carried out, what evidence was reviewed.
- Repeating the same engineer actions against the same in-progress task with no implementation records produces the same outcomes and the same order of records.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools are not part of this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to record an implementation change on a task that is In Progress by providing a non-empty account of what changed and an explicit class of ordinary or consequential.
- **FR-002**: The product MUST refuse a change whose account of what changed is empty or only spaces, or whose class is missing, and MUST leave stored records unchanged.
- **FR-003**: Each implementation change MUST serve exactly one task. The record MUST name that task, the engineer, and the time it was recorded.
- **FR-004**: The product MUST refuse to record a change on a task that is Draft, Ready, Completed, or Cancelled. The refusal MUST tell the engineer to start the task, to reopen it, or that continued work is a new task, matching that status.
- **FR-005**: An ordinary change MUST be Carried out when it is saved. It MUST NOT wait for approval.
- **FR-006**: A consequential change MUST be Awaiting approval when it is saved. It MUST NOT be Carried out until a later approval action succeeds. Saving the change MUST NOT count as approval.
- **FR-007**: A change is consequential only when the engineer declares it so. The product MUST NOT infer the class from the text of what changed. The engineer uses this meaning: the change removes or overwrites something already kept, changes who is allowed to do something, spends money, contacts someone outside the workspace, merges or publishes work, or cannot be undone by a later change on the same task.
- **FR-008**: The engineer MUST be able to approve one Awaiting approval change on an In Progress task in a separate action that names that change and includes a non-empty account of the evidence reviewed. On success the change MUST become Carried out, and the approval MUST name the change, the evidence, the engineer, and the time.
- **FR-009**: The product MUST refuse an approval whose evidence account is empty or only spaces, an approval of a change that is not Awaiting approval, an approval when the task is not In Progress, and an approval that names a change on a different task. A refused approval MUST leave the change and any existing approval unchanged.
- **FR-010**: The engineer MUST be able to mark one Awaiting approval change on an In Progress task as Not carried out by providing a non-empty reason. The record MUST keep the change visible with that reason, the engineer, and the time. The change MUST NOT become Carried out afterward.
- **FR-011**: The product MUST refuse marking a change Not carried out when the task is not In Progress or the change is not Awaiting approval, and MUST refuse a Not carried out reason that is empty or only spaces. A refusal MUST leave the change outcome unchanged.
- **FR-012**: Recording, approving, or declining a change MUST NOT change the task status, the verification state of any acceptance criterion, or the task's implementation decisions.
- **FR-013**: Implementation changes on a task MUST be listed oldest first. The engineer MUST be able to read, for each change, what changed, the class, the outcome (Carried out, Awaiting approval, or Not carried out), the engineer, and the time. A carried-out consequential change MUST also show the evidence reviewed and the approval time. A change that is Not carried out MUST also show the reason.
- **FR-014**: A saved implementation change and a saved approval MUST NOT be edited or removed. A change MUST NOT be moved to another task.
- **FR-015**: Only the engineer of the workspace may record, approve, or decline a change. Every stored record MUST name that engineer and MUST NOT name a different person.
- **FR-016**: From the same In Progress task with no implementation records, repeating the same sequence of record, approve, and decline actions MUST produce the same outcomes and the same order of records.
- **FR-017**: The product MUST refuse to mark a task Completed or Cancelled while any implementation change on that task is Awaiting approval. The task MUST stay In Progress, and the engineer MUST be told each waiting change by the account of what changed. A change that is Carried out or Not carried out MUST NOT by itself block completion or cancellation.

### Key Entities *(include if feature involves data)*

- **Implementation Change**: The account of what was changed to carry out one task. It has the task it serves, the account of what changed, a class of ordinary or consequential, an outcome of Carried out, Awaiting approval, or Not carried out, the engineer who recorded it, and the time it was recorded. When the outcome is Not carried out, it also has the reason and the time of that decision.
- **Approval**: The explicit later act that carries out one consequential change. It names that change, the evidence the engineer reviewed, the engineer, and the time. An ordinary change has no approval. A change that is Awaiting approval or Not carried out has no approval.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, what changed and which task an ordinary change serves, in under 2 minutes.
- **SC-002**: In a review of carried-out implementation changes, 100% name exactly one task, a non-empty account of what changed, the engineer, and the time recorded.
- **SC-003**: In a review of consequential changes, 100% of those without a separate approval that names the change and the evidence reviewed are not carried out, and 100% of those that are carried out have that approval stored with the engineer and the approval time.
- **SC-004**: Across a sample of 20 record, approve, and decline actions, 100% leave the task status unchanged.
- **SC-005**: Two passes of the same written sequence (record an ordinary change, record a consequential change, approve it, record another consequential change, and mark that one not carried out), each starting from the same kind of In Progress task with no implementation records, produce the same outcomes and the same order of records.
- **SC-006**: At least 95% of engineers record an ordinary change and find it again on the task on the first attempt without assistance.
- **SC-007**: In a review of completion and cancellation attempts made while a change on that task is Awaiting approval, 100% leave the task In Progress and name each waiting change by the account of what changed.

## Assumptions

- The existing task record is already in place: one engineer, one workspace, and the statuses Draft, Ready, In Progress, Completed, and Cancelled. This feature attaches changes to those tasks. It does not add people, sharing, or a second approver.
- The same engineer both records a consequential change and, in a later explicit action, approves it. Saving the change is not that approval.
- The engineer writes what changed, the evidence reviewed, and any reason in their own words. This feature does not collect a file list, a review link, or a transcript of the conversation.
- The engineer declares whether a change is ordinary or consequential. The product does not classify the wording.
- Marking a change Not carried out keeps it visible. It is not a way to delete the proposal.
- This feature does not check the change against the task's acceptance criteria. Verifying a criterion remains a separate explicit action.
- This feature does not start or reopen a task, and it does not create implementation decisions. Completing or cancelling a task is refused while any change on that task is Awaiting approval. Approval and marking a change not carried out are refused unless the task is In Progress.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools stay out of scope.
- An assistant that records, approves, or declines implementation changes is out of scope. The engineer performs every action in this feature.
- These rules follow the project constitution: the change is stored on the task a later reader can open, consequential work waits for an explicit approval that names the action and the evidence reviewed, and no task status is inferred from the record.
