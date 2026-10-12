# Feature Specification: Record One Check by the Assistant

**Feature Branch**: `010-record-assistant-check`

**Created**: 2026-10-12

**Status**: Draft

**Input**: User description: "one check by the assistant"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record one check of a carried-out change (Priority: P1)

On an In Progress task, the engineer submits one check the assistant has already produced. The check names one carried-out change on that task, one acceptance criterion of that same task, the evidence of what was seen, and an explicit result of Passed or Failed. The task shows that check with the criterion wording, the evidence, the result, the assistant, and the time. The product does not call a model, does not open a project file, and does not change the task status or the change outcome.

**Why this priority**: The assistant can already carry out one ordinary change, but a later reader still cannot see a check the assistant recorded. The check is the record that ties that change to a criterion and to evidence.

**Independent Test**: On one In Progress task, record one ordinary change, then submit one Passed check of that change against one acceptance criterion as the assistant. Read the task. The check shows the assistant, the evidence, and Passed. The change stays Carried out, the criterion stays Unverified, and the task stays In Progress.

**Acceptance Scenarios**:

1. **Given** an In Progress task "Add export" with the acceptance criterion "The export contains the goal" and a carried-out change "Rename the export label", **When** the engineer submits the assistant's evidence "The detail page shows the goal in the export" and the result Passed for that change and that criterion, **Then** the task shows that check with the criterion wording, that evidence, Passed, the assistant configured for the workspace, and the time, the change stays Carried out, the criterion stays Unverified, and the task stays In Progress.
2. **Given** the same task and carried-out change, **When** the engineer submits non-empty evidence and the result Failed, **Then** the check is stored as Failed, names the assistant, and the change and the task stay as they were.
3. **Given** the same task, **When** the evidence is empty or only spaces, **Then** no check is stored and the engineer is told `An account of the evidence is required.`
4. **Given** the same task and non-empty evidence, **When** the result is missing or is neither Passed nor Failed, **Then** no check is stored and the engineer is told `Choose Passed or Failed.`
5. **Given** a task that is Draft, **When** the engineer submits an assistant check, **Then** no check is stored and the engineer is told `The task must be In Progress.`
6. **Given** a task that is Ready, **When** the engineer submits an assistant check, **Then** no check is stored and the engineer is told `Start the task first.`
7. **Given** a task that is Completed, **When** the engineer submits an assistant check, **Then** no check is stored and the engineer is told `Reopen the task first.`
8. **Given** a task that is Cancelled, **When** the engineer submits an assistant check, **Then** no check is stored and the engineer is told `A cancelled task cannot be changed. Continued work is a new task.`
9. **Given** an In Progress task, **When** the engineer records a check without asking the assistant, **Then** that check is stored as it is today, names the workspace engineer, and does not name the assistant.

---

### User Story 2 - Let that check count, and stop the assistant there (Priority: P2)

A check the assistant recorded is a check. A carried-out change has a passing check under the existing rule when this check is the current Passed result for every criterion that change has been checked against. The engineer can then complete the task under the existing rules. The assistant still cannot mark a criterion Verified, record a decision, approve or decline a change, complete the task, or cancel the task.

**Why this priority**: A stored check that does not count leaves the assistant's work unable to satisfy the completion rule that already exists. Completing the task stays a separate action for the engineer.

**Independent Test**: On one In Progress task whose criteria are Verified and that has no subtasks, submit a Failed assistant check of its one carried-out change and try to complete the task. Then submit a later Passed assistant check of that same pair and have the engineer complete the task. The first attempt stays In Progress. The second becomes Completed. The assistant does not complete it.

**Acceptance Scenarios**:

1. **Given** an In Progress task that otherwise may be completed and one carried-out change whose current assistant check is Failed, **When** the engineer marks the task completed, **Then** the status stays In Progress and the engineer is told that change by the account of what changed, in the existing completion sentence.
2. **Given** that same task after a later assistant check of that same change and criterion is Passed, and no other completion rule fails, **When** the engineer marks the task completed, **Then** the status is Completed.
3. **Given** a Passed assistant check, **When** the task is read, **Then** the acceptance criterion it names stays Unverified until the engineer verifies it in a separate action.
4. **Given** a Passed assistant check, **When** the engineer records a decision, **Then** that decision is still the engineer's action. The assistant check does not itself add a decision.
5. **Given** a change the assistant left Awaiting approval, **When** an assistant check of that change is submitted, **Then** no check is stored, the change stays Awaiting approval, and the engineer is told `The change must be carried out before it can be checked.`
6. **Given** a change that is Not carried out, **When** an assistant check of that change is submitted, **Then** no check is stored and the engineer is told `A change that was not carried out cannot be checked.`

---

### User Story 3 - Read the same check again (Priority: P3)

The stored check is what a later reader and a later replay use. Opening the task shows the assistant, the evidence, and the result, and does not store another check. A later check of the same change and criterion stays after the earlier one. The current result is the latest check of that pair. An assistant check on a subtask stays on that subtask.

**Why this priority**: The check is not trustworthy if opening the task or replaying the record asks the assistant to judge the work again.

**Independent Test**: Submit one assistant check, open the task, and replay that stored record. The second pass shows the same evidence, result, and assistant, and does not add a check.

**Acceptance Scenarios**:

1. **Given** a stored assistant check, **When** a reader opens the task, **Then** the reader can see the criterion wording, the evidence, Passed or Failed, the assistant, and the time, and no further check is stored.
2. **Given** the same stored check, **When** that record is replayed, **Then** the task shows the same evidence, result, and assistant, and no further check is stored.
3. **Given** an assistant check whose result is Failed, **When** a later check of the same change and the same criterion is Passed, **Then** both checks remain in that order, the earlier evidence and Failed result are unchanged, and the current result of that pair is Passed.
4. **Given** an assistant check on a subtask, **When** a reader opens the parent, **Then** the parent's changes do not include that check.
5. **Given** a check the engineer recorded before this feature, **When** a reader opens the task, **Then** that check is unchanged and does not name an assistant.

---

### Edge Cases

- An unknown task is refused with `Task not found.` and nothing is stored.
- A wrong task status is reported before a missing change, a missing criterion, blank evidence, or a bad result. Nothing is stored.
- The refusal order after a known In Progress task is: unknown change `Implementation change not found.`, a change on another task `The check must name a change on that task.`, a change Awaiting approval `The change must be carried out before it can be checked.`, a change Not carried out `A change that was not carried out cannot be checked.`, no criterion chosen `Choose an acceptance criterion.`, an unknown criterion `Acceptance criterion not found.`, a criterion on another task `The check must name a criterion on that task.`, blank evidence `An account of the evidence is required.`, then a missing or unknown result `Choose Passed or Failed.`
- When the evidence is blank and the result is also invalid, the engineer is told that an account of the evidence is required.
- The product does not treat the evidence wording or the assistant's confidence as a pass. The submitted result is Passed or Failed.
- The product does not call a model and does not open or write a project file in order to record the check.
- A name supplied with the request is not the assistant that is stored. The stored assistant is the assistant configured for the workspace. The time is the workspace time.
- One request stores one check. A second check is a second request.
- The check may name a carried-out change the engineer recorded or a carried-out change the assistant recorded. Both follow the same check rules.
- Recording the check does not verify or unverify a criterion, does not approve or decline a change, does not add a decision, and does not start, complete, cancel, or reopen the task.
- The assistant is not given an action that marks a criterion Verified, records a decision, approves or declines a change, completes a task, or cancels a task. Approval and decline still use the existing messages that the assistant cannot approve a change and cannot decline a change.
- A check on a subtask does not satisfy the parent. Completing the parent still considers only the parent's own carried-out changes.
- An assistant check does not record a requirement run, does not name a requirement check, and does not by itself satisfy or clear a required check on a requirement. Those rules stay as they are.
- A saved check is not edited or removed. A later check does not rewrite an earlier one.
- Two requests recorded in the same order, with the same change, criterion, evidence, and result, produce the same results and the same order.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On a task that is In Progress, the engineer MUST be able to submit one check produced by the assistant. The check MUST name one carried-out change on that task, one acceptance criterion of that same task, a non-empty account of the evidence, and an explicit result of Passed or Failed.
- **FR-002**: The stored check MUST show the wording of that criterion at that time, the evidence, Passed or Failed, the assistant configured for the workspace, and the time. It MUST also name the workspace engineer, as every check does. The change MUST stay Carried out. The criterion MUST stay Verified or Unverified as it was. The task status MUST stay In Progress.
- **FR-003**: The product MUST refuse the request, and MUST store nothing, in this order: unknown task `Task not found.`; Draft `The task must be In Progress.`; Ready `Start the task first.`; Completed `Reopen the task first.`; Cancelled `A cancelled task cannot be changed. Continued work is a new task.`; unknown change `Implementation change not found.`; a change on another task `The check must name a change on that task.`; Awaiting approval `The change must be carried out before it can be checked.`; Not carried out `A change that was not carried out cannot be checked.`; no criterion chosen `Choose an acceptance criterion.`; unknown criterion `Acceptance criterion not found.`; a criterion on another task `The check must name a criterion on that task.`; blank evidence `An account of the evidence is required.`; missing or unknown result `Choose Passed or Failed.`
- **FR-004**: The product MUST NOT infer Passed or Failed from the evidence. The product MUST NOT call a model and MUST NOT open or write a project file to record the check. A client-supplied assistant name, engineer name, or time MUST NOT replace the workspace assistant, the workspace engineer, or the workspace time.
- **FR-005**: A check recorded by the assistant MUST count as a check under the existing passing-check rule. The current result of a change and a criterion MUST remain the latest check of that pair, whether an earlier or later check was recorded by the engineer or by the assistant. Completion MUST keep its existing sentences. No new completion sentence is added.
- **FR-006**: The assistant MUST NOT mark a criterion Verified, record a decision, approve or decline a change, complete a task, or cancel a task. Those actions remain the engineer's. An assistant check MUST NOT itself add a decision or a requirement run.
- **FR-007**: The engineer MUST still be able to record a check without the assistant. That check MUST NOT name an assistant. Checks stored before this feature MUST stay readable and MUST NOT gain an assistant.
- **FR-008**: Checks on a change MUST stay listed oldest first. An assistant check on a subtask MUST NOT appear on the parent and MUST NOT satisfy the parent's completion.
- **FR-009**: A stored assistant check MUST NOT be edited or removed. Opening the task and replaying that record MUST show the same evidence, result, and assistant, and MUST NOT store another check.
- **FR-010**: One request MUST store at most one check.

### Key Entities *(include if feature involves data)*

- **Assistant Check**: A check of one carried-out change against one acceptance criterion, recorded by the assistant. It has the criterion wording at that time, the evidence, Passed or Failed, the workspace assistant, the workspace engineer, and the time. It is not edited after it is stored.
- **Passing Check**: The existing rule. A carried-out change has a passing check when it has been checked against at least one acceptance criterion that still exists on its task and every such criterion's current result is Passed. An assistant check is one of those checks. A current Failed result, or no check, is not a passing check.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not perform the work can state, from the task record alone, what the assistant checked, the evidence, whether it passed, and which change and criterion it names, in under 2 minutes.
- **SC-002**: In a review of assistant checks, 100% name exactly one carried-out change, exactly one acceptance criterion on that change's task, the criterion wording, a non-empty account of the evidence, Passed or Failed, the workspace assistant, and a time.
- **SC-003**: In a review of completion attempts while an assistant check is the current Failed result for a carried-out change, 100% leave the task In Progress and name that change by the account of what changed. After a later current Passed result, and with every other existing completion rule satisfied, the engineer can complete the task.
- **SC-004**: Across a sample of 20 assistant checks, 100% leave the task status, the change outcome, and each criterion's Verified or Unverified state unchanged, and 100% make no model call and open no project file.
- **SC-005**: Two passes of the same stored assistant check show the same evidence, result, assistant, and order, and the second pass does not store another check.
- **SC-006**: At least 95% of engineers submit one assistant check and find the assistant, the evidence, and the result on the task on the first attempt without assistance.
- **SC-007**: In a review of checks the engineer records without the assistant, 100% do not name an assistant. No assistant check adds a decision, verifies a criterion, or completes a task.

## Assumptions

- The task, the implementation change, and the engineer's check are already in place. This feature adds one action: the assistant records one check of one carried-out change against one acceptance criterion. It does not add a task status, a new result, or a second kind of passing check.
- Specification 003 says an assistant that records a check is out of scope, and specification 005 says the assistant does not record a check. This feature is that next class. Those specifications are not rewritten. A check the engineer records directly still names only the workspace engineer.
- The engineer submits the evidence and the result the assistant already produced. The product does not judge the work, does not call a model, and does not read a project file.
- The check may name any carried-out change on that In Progress task, including a change the engineer recorded.
- Recording a check does not delete or overwrite durable data. A later check of the same change and criterion can replace the current result, and the earlier check stays. Because of that, this action does not wait for a separate approval. The written boundary is that the assistant may record the check, and the assistant still may not mark a criterion Verified, record a decision, approve or decline a change, complete the task, or cancel the task.
- A requirement and its named checks and runs stay as they are. An assistant check is not a requirement run.
- Creating a folder, deleting a file, running a test, committing, and opening a pull request stay out of this action.
- Priority, due dates, estimates, comments, notifications, and sharing stay out of scope.
- These rules follow the project constitution: the check is stored on the task, a later reader can see what the assistant checked without the conversation, replay uses that stored check, and the actions that still need the engineer are named above.
