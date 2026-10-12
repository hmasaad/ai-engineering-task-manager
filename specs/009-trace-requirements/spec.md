# Feature Specification: Trace Requirements

**Feature Branch**: `009-trace-requirements`

**Created**: 2026-10-12

**Status**: Accepted

**Input**: User description: "Introduce requirements traceability and executable verification. Requirements have stable identifiers and a functional or non-functional kind. A requirement traces to engineering tasks, acceptance criteria, and named checks. A verification record stores the test result, the time, and a run identifier. A criterion cannot be marked Verified, and a task cannot be completed, while a required check linked to that work has not passed. The engineer can see requirements with no linked task, criterion, or passing check, and can see what a requirement change affects. The rules are covered by automated checks. Keep this local to one workspace, and do not rewrite the existing specifications or the constitution."

## Clarifications

### Session 2026-10-12

- Q: Can the engineer remove a named check from a requirement after it has been added? → A: The engineer can remove a named check. Earlier runs stay readable and that check no longer blocks. If no named check remains, completion is not blocked and the requirement appears on the gap list.
- Q: If the engineer saves a requirement without changing its statement or its kind, do linked Verified criteria become Unverified and does a Completed task return to In Progress? → A: Only a different statement or a different kind unverifies linked criteria and reopens a Completed task. An unchanged save leaves them as they are.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Give a requirement a stable identity and a trace (Priority: P1)

An engineer records a requirement as functional or non-functional. The product assigns an identifier the engineer can read, and that identifier stays the same when the wording changes. The engineer links the requirement to an engineering task and to an acceptance criterion on that task. Opening the requirement later shows the identifier, the kind, the statement, the task, and the criterion.

**Why this priority**: Later checks and gap reports need a requirement that stays identifiable. Without that identity, a task and a criterion cannot be traced back to a requirement.

**Independent Test**: Create one functional requirement and link it to one task and one acceptance criterion on that task. Read the requirement back. The identifier is unchanged, and a task that has no linked requirement still completes under the existing rules.

**Acceptance Scenarios**:

1. **Given** a workspace with no requirements, **When** the engineer records the functional requirement "The export contains the goal", **Then** the requirement is stored with that statement, the kind functional, and an identifier that starts with `REQ-` followed by a number, and a later reading shows the same identifier, kind, and statement.
2. **Given** a non-functional requirement "The export page opens promptly", **When** the engineer reads it back, **Then** the kind is non-functional and the identifier is different from every other requirement in the workspace.
3. **Given** an existing requirement, **When** the statement is blank or only spaces, **Then** nothing is stored and the engineer is told `A requirement statement is required.`
4. **Given** a statement, **When** the kind is missing or is neither functional nor non-functional, **Then** nothing is stored and the engineer is told `Choose functional or non-functional.`
5. **Given** requirement `REQ-1` and an In Progress task "Add export" whose acceptance criterion is "The export contains the goal", **When** the engineer links `REQ-1` to that task and that criterion, **Then** the requirement shows that task and that criterion, and the task shows `REQ-1`.
6. **Given** requirement `REQ-1` linked to a task, **When** the engineer names an acceptance criterion from a different task, **Then** the criterion is not linked and the engineer is told `The criterion must be on that task.`
7. **Given** an unknown requirement, **When** the engineer links a task, **Then** nothing is linked and the engineer is told `Requirement not found.`
8. **Given** a task with no linked requirement, and every existing completion condition already met, **When** the engineer completes the task, **Then** the task becomes Completed under the existing rules.

---

### User Story 2 - Record a run and hold verification until required checks pass (Priority: P2)

An engineer names the checks a requirement needs, then records one result for one of those checks. The record shows Passed or Failed, the time, the workspace engineer, and the run identifier the engineer supplies. The current result of a check is the latest record for that requirement and that check. A linked criterion cannot be marked Verified, and a linked task cannot be completed, while any of those required checks is not currently Passed. Earlier records stay.

**Why this priority**: An identifier is not yet evidence. The run record is what a later reader uses to see whether the required checks passed, and the hold is what stops a task from looking finished when they have not.

**Independent Test**: Name one check on one requirement, record a Failed run, and try to verify the linked criterion and complete the linked task. Both are refused. Record a later Passed run for the same check and the same run rules then allow the existing verification and completion steps to proceed.

**Acceptance Scenarios**:

1. **Given** requirement `REQ-1`, **When** the engineer names the check "export shows the goal", **Then** that check is required for `REQ-1`, and a second attempt to name the same check is refused with `That check is already named on this requirement.`
2. **Given** requirement `REQ-1` with that required check, **When** the engineer records the run identifier "local-1", the result Passed, and the check "export shows the goal", **Then** the requirement shows that check as Passed, the run identifier "local-1", the workspace engineer, and the time.
3. **Given** the same requirement, **When** a later record for the same check uses run identifier "local-2" and the result Failed, **Then** both records remain, and the current result is Failed.
4. **Given** a required check whose current result is Failed, and a criterion linked to that requirement on an In Progress task, **When** the engineer records an observation and an explicit pass for that criterion, **Then** the criterion stays Unverified and the engineer is told `A required check has not passed.`
5. **Given** a required check whose current result is not Passed, and an In Progress task linked to that requirement whose criteria are otherwise Verified, **When** the engineer completes the task, **Then** the task stays In Progress and the refusal includes `A required check has not passed: REQ-1.`
6. **Given** the same task also has an Unverified criterion, an unfinished subtask, a change awaiting approval, and a carried-out change with no passing check, **When** completion is refused, **Then** the refusal names the unverified criteria, the unfinished subtasks, the awaiting approval, and the missing passing check, in that order, and then names the required check.
7. **Given** a criterion on an In Progress task that is not linked to any requirement, **When** the engineer records an observation and an explicit pass, **Then** that criterion becomes Verified under the existing rule.
8. **Given** a required check with no recorded run, **When** the engineer verifies a criterion linked to that requirement, **Then** the criterion stays Unverified and the engineer is told `A required check has not passed.`
9. **Given** a blank check name, a blank run identifier, a missing result, or a check name that the requirement does not list, **When** the engineer records the run, **Then** nothing is stored. The refusals are `Name the check this requirement uses.`, `A run identifier is required.`, `Choose Passed or Failed.`, and `Check not found.`
10. **Given** requirement `REQ-1` with the named check "export shows the goal" and a Failed run for that check, linked to an In Progress task whose criterion is otherwise ready to verify, **When** the engineer removes that check, **Then** the run stays readable, the criterion can be marked Verified, the task can be completed, and the requirement appears on the gap list as missing a check.
11. **Given** that same removed check, **When** the engineer names "export shows the goal" again, **Then** the new check has no current result, and the removed check's run does not become that result.

---

### User Story 3 - Find requirements that are not traced or not verified (Priority: P3)

An engineer opens one list of requirements that are missing a linked task, a linked acceptance criterion, a named check, or a current Passed result for a named check. A requirement that is fully traced and whose every named check is currently Passed does not appear. Existing tasks and criteria that were never linked to a requirement do not appear as requirements.

**Why this priority**: The hold in User Story 2 only protects work that is already linked. The list is how the engineer finds requirements that never reached a task or a passing check.

**Independent Test**: Create four requirements. Leave one unlinked, link one to a task only, name a check on one without recording a pass, and fully link and pass the fourth. Only the first three appear on the list.

**Acceptance Scenarios**:

1. **Given** a requirement with no linked task, **When** the engineer opens the gap list, **Then** that requirement appears as missing a task, and its identifier, kind, and statement are shown.
2. **Given** a requirement linked to a task and to no acceptance criterion, **When** the engineer opens the gap list, **Then** that requirement appears as missing an acceptance criterion.
3. **Given** a requirement linked to a task and a criterion, with no named check, **When** the engineer opens the gap list, **Then** that requirement appears as missing a check.
4. **Given** a named check whose current result is Failed or is missing, **When** the engineer opens the gap list, **Then** that requirement appears as missing a passing result for that check.
5. **Given** a requirement linked to a task and a criterion, with every named check currently Passed, **When** the engineer opens the gap list, **Then** that requirement does not appear.
6. **Given** tasks and acceptance criteria created before any requirement existed, **When** the engineer opens the gap list, **Then** those tasks and criteria are not listed as requirements.

---

### User Story 4 - See what a requirement change affects (Priority: P4)

An engineer changes the statement or the kind of a requirement. The identifier stays. The requirement shows the tasks, acceptance criteria, and named checks it still traces to. Each linked criterion that was Verified becomes Unverified. If that criterion's task was Completed, the task returns to In Progress, and every Completed ancestor returns to In Progress. Verification records stay as they were.

**Why this priority**: A changed requirement can make an earlier pass refer to wording that no longer exists. The engineer needs the affected work listed, and the earlier Verified mark cannot remain attached to the old wording.

**Independent Test**: Link one requirement to one Verified criterion on a Completed task, record one Passed run, then change the requirement statement. The identifier is unchanged, the criterion is Unverified, the task is In Progress, the run is still readable, and the requirement lists that task, criterion, and check.

**Acceptance Scenarios**:

1. **Given** requirement `REQ-1` linked to a Verified criterion on a Completed task, with a Passed run for check "export shows the goal", **When** the engineer changes the statement to "The export contains the revised goal", **Then** the identifier remains `REQ-1`, the criterion is Unverified, the task is In Progress, the history records the requirement change as the cause, and the Passed run is still readable with its run identifier and time.
2. **Given** the same Completed task under a Completed parent, **When** the statement changes, **Then** the parent is also In Progress and the parent's own Verified criteria stay Verified.
3. **Given** a requirement linked to two criteria, only one of which is Verified, **When** the kind changes from functional to non-functional, **Then** only the Verified linked criterion becomes Unverified, and the requirement shows both criteria and the new kind.
4. **Given** a requirement with no links and one named check, **When** the statement changes, **Then** the identifier and the check stay, and no task status changes.
5. **Given** the engineer removes the link to one criterion, **When** the requirement is read again, **Then** that criterion is no longer listed, its Verified or Unverified state stays as it was, and earlier runs stay.
6. **Given** requirement `REQ-1` linked to a Verified criterion on a Completed task, **When** the engineer saves the same statement and the same kind, **Then** the criterion stays Verified, the task stays Completed, and no requirement-change history is added.

### Edge Cases

- The same criterion may be linked to more than one requirement. Each linked requirement's required checks apply on their own.
- The same requirement may be linked to more than one task. Completion of one linked task does not complete or verify another.
- A requirement linked only to a subtask blocks that subtask. It does not by itself block the parent.
- Linking a pair that is already linked changes nothing and tells the engineer `That criterion is already linked to this requirement.` A task that is already linked changes nothing.
- Removing an acceptance criterion removes its link to requirements. The requirement, its task link, and its runs stay. If no criterion remains, the requirement appears on the gap list.
- A requirement is not deleted. Its runs are not edited or deleted.
- The engineer can remove a named check. The check's runs stay readable and no longer count toward the current result or the completion hold. If the requirement then has no named check, it appears on the gap list and does not block verification or completion. Naming that same check again starts a new check with no current result. Removing an unknown check is refused with `Check not found.`
- Two runs may use the same run identifier. The current result is the latest record for that requirement and check by time, and then by the order the records were stored.
- A run identifier that is blank or only spaces is refused with `A run identifier is required.` Nothing is stored.
- Saving the same statement and the same kind does not unverify a linked criterion, does not change task status, and does not add a requirement-change history entry. A statement that differs only by surrounding spaces is the same statement.
- Recording a run does not change task status, criterion Verified state, change outcome, or an existing check of a carried-out change.
- The assistant does not create a requirement, link one, name a check, record a run, verify a criterion, or complete a task.
- A cancelled task can still be shown on a requirement. New verification of a criterion and completion still follow the existing status rules.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to record a requirement with a non-empty statement and a kind of functional or non-functional. The product MUST assign an identifier that starts with `REQ-` and a number. That identifier MUST be unique in the workspace and MUST NOT change when the statement or the kind changes. A retired identifier MUST NOT be reused.
- **FR-002**: A blank statement MUST be refused with `A requirement statement is required.` A missing or unknown kind MUST be refused with `Choose functional or non-functional.` Nothing is stored in either case.
- **FR-003**: The engineer MUST be able to link a requirement to a task, and to an acceptance criterion on that same task. The requirement MUST show the task and the criterion. The task MUST show each requirement linked to it. A criterion from another task MUST be refused with `The criterion must be on that task.` An unknown requirement MUST be refused with `Requirement not found.`
- **FR-004**: The engineer MUST be able to name one or more checks on a requirement, and MUST be able to remove a named check. A check name MUST be non-empty and unique among the checks that are still named on that requirement. A blank name MUST be refused with `Name the check this requirement uses.` A duplicate name MUST be refused with `That check is already named on this requirement.` Removing a check MUST keep its runs readable, MUST drop it from the current-result rule, and MUST NOT delete those runs. If no named check remains, that requirement MUST NOT block verification or completion, and it MUST appear on the gap list as missing a check. The same name MAY be named again afterward; the new check starts with no current result, and the removed check's runs MUST NOT become that result. Removing an unknown check MUST be refused with `Check not found.`
- **FR-005**: The engineer MUST be able to record a verification of one named check. The record MUST keep the result Passed or Failed, the run identifier the engineer entered, the workspace engineer, and the time. A blank run identifier MUST be refused with `A run identifier is required.` A missing or unknown result MUST be refused with `Choose Passed or Failed.` An unknown check MUST be refused with `Check not found.` The record MUST NOT be edited or deleted afterward.
- **FR-006**: The current result of a named check MUST be the latest stored record for that requirement and that check. A check with no record has no current pass. An earlier record MUST remain readable.
- **FR-007**: Marking an acceptance criterion Verified MUST be refused with `A required check has not passed.` when any requirement linked to that criterion has a named check whose current result is not Passed. A criterion linked to no requirement MUST keep the existing verification rule.
- **FR-008**: Completing a task MUST be refused when any requirement linked to that task has a named check whose current result is not Passed. The refusal MUST include `A required check has not passed: {identifiers}.` Identifiers are listed from lowest number to highest, separated by a comma and a space. When older completion conditions also fail, their existing sentences stay first, in their existing order, and this sentence follows them. A task with no linked requirement MUST keep the existing completion rules, including tasks and criteria stored before this feature.
- **FR-009**: The engineer MUST be able to open one list of requirements that are missing a linked task, a linked acceptance criterion, a named check, or a current Passed result for a named check. The list MUST show the identifier, the kind, the statement, and which of those are missing. A requirement that is not missing any of them MUST NOT appear. Tasks and criteria that are not requirements MUST NOT appear on that list.
- **FR-010**: Changing a requirement's statement or kind MUST keep the identifier and MUST show the tasks, criteria, and named checks that requirement traces to. A change is a statement that differs after surrounding spaces are removed, or a different kind. Each linked criterion that was Verified MUST become Unverified. If that criterion's task is Completed, the task MUST return to In Progress, and every Completed ancestor MUST return to In Progress. The history MUST record the requirement change as the cause. Verification records MUST stay. Criteria that are not linked to that requirement MUST stay as they were. Saving the same statement and the same kind MUST leave Verified criteria, task status, and history unchanged. A blank replacement statement MUST be refused with `A requirement statement is required.` and MUST leave the requirement unchanged.
- **FR-011**: Removing a link MUST NOT delete the requirement or its verification records, and MUST NOT change the Verified state of the criterion that was unlinked.
- **FR-012**: A requirement linked only to a subtask MUST affect that subtask's completion and that subtask's criteria. It MUST NOT by itself block the parent.
- **FR-013**: Recording a requirement, a link, a check name, or a run MUST NOT change a task's status, a criterion's Verified state, a change outcome, or an existing check of a carried-out change, except for the effect FR-010 describes when the requirement statement or kind itself changes.
- **FR-014**: Each rule in this specification MUST be proven by an automated check before the feature is treated as done. One rule MUST be able to fail on its own. The path from a requirement through its linked task and acceptance criterion to a stored run MUST be able to fail as its own check.
- **FR-015**: The product MUST NOT run the named checks, MUST NOT read requirements out of specification documents, and MUST NOT add a task status beyond Draft, Ready, In Progress, Completed, and Cancelled.

### Key Entities *(include if feature involves data)*

- **Requirement**: One functional or non-functional statement in the workspace. It has a stable identifier, a kind, and a statement. It is not deleted. The identifier survives a change of statement or kind.
- **Requirement Link**: The connection from one requirement to one task, or from one requirement to one acceptance criterion on a linked task. Removing the link does not remove the requirement or its runs.
- **Required Check**: A named check the engineer says the requirement needs. The name is unique among the checks still named on that requirement. The engineer can remove it. Removal keeps its runs readable and takes it out of the current-result rule. The same name can be added again as a new check with no current result.
- **Verification Run**: One stored result for one required check. It has Passed or Failed, the run identifier, the engineer, and the time. Later runs do not erase earlier ones. The latest run is the current result.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who did not write the requirement can state, from the stored record alone, its identifier, kind, statement, linked tasks, linked criteria, and the current result and run identifier of each named check, in under 2 minutes.
- **SC-002**: In a review of requirements whose statement or kind changed, 100% keep the same identifier.
- **SC-003**: In a review of attempts to verify a linked criterion or complete a linked task while a required check is not Passed, 100% leave the criterion Unverified or the task uncompleted, and 100% of tasks with no linked requirement still follow the existing completion rules.
- **SC-004**: In a review of the gap list, 100% of requirements that are missing a task, a criterion, a named check, or a current pass appear, and 100% of fully traced requirements with every named check Passed do not appear.
- **SC-005**: In a review of requirement changes that touch a Verified criterion, 100% return that criterion to Unverified, return a Completed task to In Progress, and keep the earlier run readable.
- **SC-006**: At least 95% of engineers can record a requirement, link it to a criterion, and find it again on the first attempt without assistance.
- **SC-007**: Every rule in this specification has an automated check, and a failing path from requirement to stored run is visible as its own check.

## Assumptions

- One local workspace holds the requirements. They are not shared across workspaces, and they are not read from specification documents.
- The engineer declares functional or non-functional. The product does not infer the kind.
- "Marked verified" uses the existing criterion state Verified and the existing task status Completed. This feature does not add a Verified task status.
- A named check is a label the engineer enters for a test or other check that was run outside this product. The product stores the result the engineer records. It does not run that check.
- A linked requirement with no named check does not block verification or completion. It appears on the gap list as missing a check. The block applies only when a check that is still named has a current result that is not Passed. Removing a named check takes that check out of the block and keeps its runs.
- "No linked implementation" on the gap list means no linked task. A missing acceptance criterion is reported separately. An implementation change of the kind already stored on a task is not, by itself, the implementation link for this feature.
- Tasks, criteria, and checks stored before this feature stay valid. They are not turned into requirements. Their verification and completion rules stay as they are until a requirement is linked.
- The current result is the latest record by time, then by the order stored. The same run identifier may appear on more than one record.
- Changing a requirement statement or kind is the requirement change that unverifies linked criteria. The statement differs only when the trimmed wording differs. An unchanged statement and kind, a new link, a check name, or a run is not that change.
- The additional Completed to In Progress cause is the requirement change in FR-010. The earlier specifications are not rewritten to list it.
- Only the workspace engineer records a run. A name or a time supplied by the request is ignored. The assistant does not perform this feature's actions.
- Existing sentences for unverified criteria, unfinished subtasks, awaiting approval, and a missing passing check stay in that order. The new sentence is added after them only when it applies.
- Running tests, creating folders, deleting files, committing, and opening a pull request stay out of this feature.
