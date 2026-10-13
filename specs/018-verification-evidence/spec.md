# Feature Specification: Verification Evidence and Trace Gaps

**Feature Branch**: `018-verification-evidence`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Record the verification method and the test-run identifier on each criterion verification. List tasks that have no requirement, and criteria that have no verification."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record how a criterion was verified (Priority: P1)

On an In Progress task, the engineer marks one acceptance criterion Verified only with an observation, an explicit pass, a verification method, and a test-run identifier. The record also keeps the time and the workspace engineer. A later reading shows that method and that identifier. Opening the task again does not change them. Marking the criterion Unverified clears them from the current record.

**Why this priority**: A Verified criterion is the definition of completion for that condition. The observation and the pass already exist. The method and the test-run identifier are what a reader still cannot see.

**Independent Test**: Verify one criterion with method "inspection" and test-run identifier "local-1". The criterion shows Verified, that method, that identifier, the observation, the pass, the time, and the engineer. A blank method leaves the criterion Unverified.

**Acceptance Scenarios**:

1. **Given** an In Progress task whose criterion is Unverified, and no required check is failing, **When** the engineer records the observation "The export contains the goal", an explicit pass, the method "inspection", and the test-run identifier "local-1", **Then** the criterion is Verified and shows that observation, the pass, the method "inspection", the identifier "local-1", the workspace engineer, and the time.
2. **Given** that verified criterion, **When** the engineer opens the task again, **Then** the same method, identifier, observation, pass, engineer, and time are shown, and nothing new is stored.
3. **Given** that verified criterion, **When** the workspace is opened again with a different engineer, **Then** the stored method, identifier, observation, and engineer stay as they were.
4. **Given** the same task, **When** the method is blank or only spaces, **Then** nothing is stored, the criterion stays Unverified, and the engineer is told `A verification method is required.`
5. **Given** a method "inspection" and a blank test-run identifier, **When** the engineer verifies, **Then** nothing is stored, the criterion stays Unverified, and the engineer is told `A test-run identifier is required.`
6. **Given** a blank observation, a missing pass, a task that is not In Progress, or a required check that has not passed, **When** the method is also blank, **Then** the existing refusal is shown and the new messages are not used.
7. **Given** a verified criterion, **When** the engineer marks it Unverified, edits its text, or a linked requirement's statement or kind changes, **Then** the criterion is Unverified and the current record no longer shows the method or the test-run identifier.

---

### User Story 2 - See tasks and criteria the requirement list misses (Priority: P2)

The engineer opens the same gap analysis that already lists requirements missing a task, a criterion, a check, or a passing result. That analysis also lists every task that has no linked requirement, and every acceptance criterion that is Unverified. Linking a requirement removes that task from the first list. Verifying a criterion removes it from the second list.

**Why this priority**: The current gap list starts from a requirement. A task with no requirement, and an unverified criterion on a task that already has a requirement, never appear there.

**Independent Test**: Create one task with one unverified criterion and no requirement. The analysis lists that task and that criterion. Link a requirement to the task and the task leaves the list. Verify the criterion and the criterion leaves the list. The requirement's own missing phrases stay the phrases already defined.

**Acceptance Scenarios**:

1. **Given** a task with no linked requirement, **When** the engineer opens the gap analysis, **Then** that task appears with its title and status, and it does not appear as a requirement.
2. **Given** a parent task linked to a requirement and a subtask with no requirement of its own, **When** the engineer opens the gap analysis, **Then** the parent is absent from the task list and the subtask is present.
3. **Given** an Unverified acceptance criterion, **When** the engineer opens the gap analysis, **Then** that criterion appears with its text and the task it belongs to.
4. **Given** a task linked to a requirement whose criterion is still Unverified, **When** the engineer opens the gap analysis, **Then** the task is absent from the task list and the criterion is present.
5. **Given** that criterion, **When** the engineer verifies it, **Then** it leaves the criterion list. **When** the engineer marks it Unverified, **Then** it returns.
6. **Given** a requirement missing a task, **When** the engineer opens the gap analysis, **Then** that requirement still appears as missing a task, and the other existing missing phrases are unchanged.
7. **Given** a task created before any requirement existed, **When** the engineer opens the requirement list, **Then** that task is still not shown as a requirement.

### Edge Cases

- A method or a test-run identifier that differs only by surrounding spaces is stored without those spaces.
- Both a blank method and a blank test-run identifier produce the method message. Nothing is stored.
- The test-run identifier is the text the engineer entered. It is not checked against a test that was run or against a requirement's run.
- One verification names one criterion. It does not record a requirement run, record a check of a change, or complete the task.
- A cancelled task with no requirement still appears. An Unverified criterion on a cancelled task still appears.
- Opening the gap analysis does not verify a criterion, link a requirement, or change a task status.
- A criterion that is already Verified under the earlier rule, and that has no method stored, stays Verified. A new verification requires both the method and the test-run identifier.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Verifying an acceptance criterion MUST store a non-empty verification method and a non-empty test-run identifier with the observation, the explicit pass, the time, and the workspace engineer. A blank method MUST be refused with `A verification method is required.` A blank test-run identifier MUST be refused with `A test-run identifier is required.` A refusal MUST leave the criterion Unverified when it was Unverified.
- **FR-002**: The existing verification refusals MUST stay first: unknown task, a cancelled task, an unknown criterion, a task that is not In Progress, a blank observation, a missing pass, and a required check that has not passed. The method is checked after those, and the test-run identifier is checked after the method.
- **FR-003**: While the criterion is Verified, a reader MUST be able to see the method and the test-run identifier with the observation, the pass, the engineer, and the time. Opening the task MUST NOT change them. A later start MUST NOT rewrite them.
- **FR-004**: Marking the criterion Unverified, editing its text, or changing a linked requirement's statement or kind MUST clear the method and the test-run identifier from the current record, together with the existing verification.
- **FR-005**: The gap analysis MUST list every task that has no linked requirement, including a subtask, with its title and status. Linking a requirement to that task MUST remove it from that list. The existing requirement list MUST stay a list of requirements.
- **FR-006**: The gap analysis MUST list every Unverified acceptance criterion with its text and the task it belongs to. Verifying that criterion MUST remove it. Marking it Unverified MUST return it. A task that has a requirement MUST NOT appear in the task list only because a criterion is Unverified.
- **FR-007**: The phrases already used for a requirement missing a task, a criterion, a check, or a passing result MUST stay unchanged. Completion and the rule that blocks Verified while a required check has not passed MUST stay unchanged.

### Key Entities

- **Criterion evidence**: The verification method and the test-run identifier stored for the current verification of one acceptance criterion. They are present only while that criterion is Verified.
- **Trace gaps**: The tasks that have no linked requirement, and the acceptance criteria that are Unverified, shown beside the existing requirement gaps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state the method, the pass, the time, and the test-run identifier of a verified criterion from that criterion's record, in under 2 minutes.
- **SC-002**: In a review of verification attempts that omit the method or the test-run identifier, 100% leave an Unverified criterion Unverified.
- **SC-003**: In a review of the gap analysis, 100% of tasks with no linked requirement appear on the task list, 100% of Unverified criteria appear on the criterion list, and 100% of linked tasks and Verified criteria are absent from those lists.
- **SC-004**: A requirement that already has a missing phrase still shows that same phrase after this feature.

## Assumptions

- Specifications 001 through 017 are not rewritten. A requirement keeps its identifier, its kind, its checks, and its runs. A criterion becomes Verified only with an observation, an explicit pass, the time, and the workspace engineer, and now also a method and a test-run identifier.
- The verification method is the text the engineer names, such as inspection or test. The product does not choose it.
- The test-run identifier is the text the engineer enters. It does not have to match a stored test run or a requirement run. Two criteria may use the same identifier.
- The engineer name and the time still come from the workspace. A name or a time sent by the client is ignored. The method and the test-run identifier are the ones the engineer entered.
- Criteria already Verified before this feature stay Verified and do not gain a method or a test-run identifier. Every verification made after this feature requires both.
- The requirement gap phrases stay `Missing a task`, `Missing an acceptance criterion`, `Missing a check`, and `Missing a passing result for {check name}`.
- The rules are covered by automated checks.
