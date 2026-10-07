# Feature Specification: Assist an Ordinary Change

**Feature Branch**: `005-assist-ordinary-change`

**Created**: 2026-10-07

**Status**: Accepted

**Input**: User description: "The next feature should let an assistant carry out one ordinary change for an In Progress task in a project the engineer names. The record shows what changed, which task it serves, and that the assistant did it, so a later reader can check it without the original conversation. Consequential actions still stop for a named human approval. The assistant does not verify criteria, choose Passed or Failed, or complete the task. Priority, due dates, comments, and sharing stay out of scope."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carry out one ordinary change (Priority: P1)

An engineer asks the assistant to carry out one ordinary change for an In Progress task in a named project. The assistant carries out that change and the task shows what changed, the project, the assistant, and that the change is Carried out. A later reader can see that record without the original conversation.

**Why this priority**: This is the first action an assistant may take on its own. Without the record, the work cannot be checked or trusted.

**Independent Test**: On one In Progress task, ask the assistant to carry out one ordinary change in a named project, then read the task. The change is Carried out, names the assistant and the project, and the task stays In Progress.

**Acceptance Scenarios**:

1. **Given** an In Progress task "Add export" and the project "billing", **When** the engineer asks the assistant to carry out an ordinary change and the assistant reports "Rename the export label", **Then** the task shows that account, the project "billing", the assistant, Carried out, and the time, and the task stays In Progress.
2. **Given** the same In Progress task, **When** the project name is empty or only spaces, **Then** nothing is carried out, nothing is stored, and the engineer is told to name the project this change is for.
3. **Given** the same In Progress task and a named project, **When** the account of what changed is empty or only spaces, **Then** nothing is carried out, nothing is stored, and the engineer is told an account of what changed is required.
4. **Given** the same In Progress task and a named project, **When** the class is missing or is neither ordinary nor consequential, **Then** nothing is carried out and the engineer is told to choose ordinary or consequential.
5. **Given** a task that is Draft, **When** the engineer asks the assistant to carry out an ordinary change, **Then** nothing is carried out and the engineer is told the task must be In Progress.
6. **Given** a task that is Ready, **When** the engineer asks the assistant to carry out an ordinary change, **Then** nothing is carried out and the engineer is told to start the task first.
7. **Given** a task that is Completed, **When** the engineer asks the assistant to carry out an ordinary change, **Then** nothing is carried out and the engineer is told to reopen the task first.
8. **Given** a task that is Cancelled, **When** the engineer asks the assistant to carry out an ordinary change, **Then** nothing is carried out and the engineer is told that a cancelled task cannot be changed and continued work is a new task.
9. **Given** an In Progress task, **When** the engineer records an ordinary change without asking the assistant, **Then** that change is still stored as the engineer's own change, as it is today.

---

### User Story 2 - Stop a consequential change for approval (Priority: P2)

The engineer asks the assistant to carry out a change and declares it consequential, or the assistant finds that carrying it out would be consequential. The assistant does not carry it out. The task shows the proposal as Awaiting approval. The engineer approves or declines it later, in a separate action.

**Why this priority**: An assistant that can change a project must still stop before a consequential effect. Silence is not approval.

**Independent Test**: On one In Progress task, ask the assistant for a consequential change in a named project. The project is unchanged, the task shows Awaiting approval, and the task stays In Progress until the engineer approves or declines.

**Acceptance Scenarios**:

1. **Given** an In Progress task and the project "billing", **When** the engineer asks the assistant to carry out a consequential change "Replace the stored export name", **Then** the change is not carried out, the task shows that account, the project, the assistant, and Awaiting approval, and the task stays In Progress.
2. **Given** an ordinary request for an In Progress task, **When** carrying it out would delete or overwrite durable data, change permissions, spend money, contact an external party, merge, deploy, or could not be undone by a later task, **Then** the assistant stops, the project is unchanged, and the task shows the proposal as Awaiting approval.
3. **Given** a change the assistant left Awaiting approval, **When** the engineer approves it with a non-empty account of the evidence reviewed, **Then** the change becomes Carried out and the approval names the engineer, not the assistant.
4. **Given** a change the assistant left Awaiting approval, **When** the assistant tries to approve it, **Then** the change stays Awaiting approval.
5. **Given** a change the assistant left Awaiting approval, **When** the engineer marks it not carried out with a reason, **Then** the change stays visible as Not carried out and cannot later be approved.

---

### User Story 3 - Leave a record that can be read again (Priority: P3)

The stored assistant record is the record a later reader and a later replay use. Reading the task shows the assistant, the project, what changed, and the outcome. Repeating the same stored record does not ask the assistant to carry the work out again.

**Why this priority**: The assistant's work is not repeatable unless the record, not a new request, is what gets replayed.

**Independent Test**: Carry out one ordinary assistant change, read it back, and replay that stored record. The second pass shows the same account, the same assistant, the same project, and the same outcome, and does not carry the change out again.

**Acceptance Scenarios**:

1. **Given** a stored ordinary assistant change, **When** a reader opens the task, **Then** the reader can see the account of what changed, the project, the assistant, Carried out, and the time.
2. **Given** the same stored change, **When** that record is replayed, **Then** the task shows the same account, project, assistant, and outcome, and the assistant is not asked to carry the work out again.
3. **Given** an assistant change on a subtask, **When** the reader opens the parent, **Then** the parent's changes do not include the subtask's assistant change.
4. **Given** an assistant change that is Carried out, **When** the engineer completes the task, **Then** completion still waits until that change has a passing check. The assistant does not record the check, choose Passed or Failed, record a decision, or mark the task completed.

---

### Edge Cases

- A project name or an account of what changed that is only spaces is refused, and no partial change is stored.
- If the project name is blank and the account of what changed is also blank, the engineer is told to name the project this change is for, and nothing is stored.
- The product does not treat the assistant's confidence as approval. A consequential change stays Awaiting approval until the engineer approves it in a separate action.
- The assistant does not verify an acceptance criterion, record a check, record a decision, complete a task, or cancel a task.
- One request carries out at most one change. A second change is a second request.
- The assistant works only in the project the engineer named for that request. It does not change any other project.
- A Draft, Ready, Completed, or Cancelled task is refused with the same demand used when the engineer records a change: start the task, reopen it, or start a new task.
- The engineer can still record, approve, and decline changes without the assistant. Those records name the engineer.
- An assistant change on a subtask is not copied onto the parent.
- Two requests recorded in the same order, with the same stored account, project, and class, produce the same outcomes and the same order.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to ask the assistant to carry out one change for a task that is In Progress by naming the project, stating whether the change is ordinary or consequential, and providing the account of what changed once the assistant has done or proposed the work.
- **FR-002**: For an ordinary change, the assistant MUST carry out that one change in the named project. The task MUST show the account of what changed, the project, the assistant, Carried out, and the time. The task status MUST stay In Progress.
- **FR-003**: The product MUST refuse the request when the project name is empty or only spaces, and MUST tell the engineer to name the project this change is for. It MUST refuse an empty account of what changed, and MUST tell the engineer an account of what changed is required. It MUST refuse a missing class or a class other than ordinary or consequential, and MUST tell the engineer to choose ordinary or consequential. A refusal MUST leave the project and the task unchanged.
- **FR-004**: The product MUST refuse the request when the task is Draft, Ready, Completed, or Cancelled, with the same messages used when the engineer records a change. A wrong status is reported before a blank project or a blank account.
- **FR-005**: A consequential request MUST NOT be carried out. The task MUST show the account, the project, the assistant, and Awaiting approval. The project MUST be unchanged.
- **FR-006**: If carrying out an ordinary request would delete or overwrite durable data, change permissions, spend money, contact an external party, merge, deploy, or could not be undone by a later task, the assistant MUST stop. The project MUST be unchanged, and the task MUST show the proposal as Awaiting approval.
- **FR-007**: The engineer MUST approve or decline a waiting assistant change in a separate action, using the existing approval rules. The approval MUST name the engineer. The assistant MUST NOT approve or decline its own change.
- **FR-008**: The assistant MUST NOT verify an acceptance criterion, record a check, choose Passed or Failed, record a decision, complete a task, or cancel a task. Completion of a task that has a carried-out assistant change still waits for a passing check of that change.
- **FR-009**: The engineer MUST still be able to record an ordinary or consequential change without the assistant. That change names the engineer, not the assistant.
- **FR-010**: Each assistant change MUST name exactly one task, one project, and the assistant. Changes on a task MUST stay listed oldest first, together with the engineer's own changes. An assistant change on a subtask MUST NOT appear as a change of the parent.
- **FR-011**: A stored assistant change MUST NOT be edited or removed. Replaying that stored record MUST produce the same account, project, assistant, and outcome, and MUST NOT ask the assistant to carry the work out again.
- **FR-012**: One request MUST carry out or propose at most one change. The assistant MUST work only in the project named for that request.

### Key Entities *(include if feature involves data)*

- **Assistant Change**: A change on one task that the assistant carried out or proposed. It has the account of what changed, the project, the assistant, the class ordinary or consequential, the outcome Carried out or Awaiting approval or Not carried out, and the time. The task it serves is the task the engineer named.
- **Assistant Request**: The engineer's ask that the assistant carry out one change. It names the task, the project, and whether the change is ordinary or consequential. The stored change is the record used when that request is read again.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, what the assistant changed or proposed, which project it was for, and whether it was carried out, in under 2 minutes.
- **SC-002**: In a review of ordinary assistant changes, 100% name exactly one task, one non-empty project, the assistant, a non-empty account of what changed, Carried out, and a time.
- **SC-003**: In a review of consequential assistant requests, 100% leave the named project unchanged and show Awaiting approval until the engineer approves or declines them.
- **SC-004**: Across a sample of 20 ordinary assistant changes, 100% leave the task status In Progress and leave every acceptance criterion's Verified or Unverified state unchanged.
- **SC-005**: Two passes of the same stored assistant record produce the same account, project, assistant, outcome, and order, and the second pass does not carry the work out again.
- **SC-006**: At least 95% of engineers ask the assistant for one ordinary change and find the assistant, the project, and what changed on the task on the first attempt without assistance.
- **SC-007**: In a review of approval actions on assistant changes, 100% of approvals name the engineer. No assistant approval is stored.

## Assumptions

- The task, the implementation record, the check, and the decision are already in place. This feature adds one assistant action: carry out or propose one change on an In Progress task. It does not add people, sharing, or a second approver.
- The engineer names the project for that request. The project is the coding work the assistant may touch. The assistant does not leave that project.
- The engineer says whether the request is ordinary or consequential before the assistant acts. The product does not infer the class from the wording. If the work would nevertheless be consequential, the assistant stops and leaves the proposal Awaiting approval.
- The assistant has a name, distinct from the engineer. Ordinary changes and proposals show that name. Approval and decline still show the engineer.
- The account of what changed is stored when the assistant finishes or stops. A later replay uses that stored account and does not ask the assistant to do the work again.
- The engineer can still record changes, checks, and decisions. The assistant does not take those actions.
- Priority, due dates, estimates, comments, notifications, sharing, and links to code review or release tools stay out of scope.
- These rules follow the project constitution: this is the first class of action an assistant may carry out, the record is on the task, and a consequential action still waits for a named human approval.
