# Feature Specification: Run One Test

**Feature Branch**: `012-run-one-test`

**Created**: 2026-10-13

**Status**: Accepted

**Input**: User description: "Run one test in the named project and store the result."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run one test (Priority: P1)

On an In Progress task, the engineer names an existing project and one test that already exists inside it. An ordinary request runs that test and stores whether it passed, the text the run produced, the assistant, and Carried out. Opening the task again shows that stored result and does not run the test again.

**Why this priority**: The assistant can already record a result the engineer typed. It still cannot run a test and keep the outcome.

**Independent Test**: On one In Progress task, ask for an ordinary run of `tests/test_label.py::test_label` in an existing project `billing`. The task shows that test, Passed or Failed, and Carried out, and a second opening does not run it again.

**Acceptance Scenarios**:

1. **Given** an In Progress task and an existing project `billing` that contains `tests/test_label.py::test_label`, **When** the engineer asks for an ordinary run with the account "Run the label test", **Then** that test runs once, the task shows the test, Passed or Failed, the text the run produced, the assistant, and Carried out, and the task stays In Progress.
2. **Given** that stored result, **When** the engineer opens the task again, **Then** the same result is shown and the test does not run again.
3. **Given** the same task, **When** the test name is blank, **Then** nothing runs and the engineer is told `Name the test this change runs.`
4. **Given** the same task, **When** the engineer names a file but not one test in that file, **Then** nothing runs and the engineer is told `Name one test in a file.`
5. **Given** a project that does not exist, **When** the engineer asks for a run, **Then** nothing runs and the engineer is told `The project must already exist.`
6. **Given** `billing` exists and the named test file does not, **When** the engineer asks for a run, **Then** nothing is stored and the engineer is told `The test must already exist.`
7. **Given** a test that would leave the project, **When** the engineer asks for it, **Then** nothing runs and the engineer is told `The test must stay inside the named project.`
8. **Given** a test that fails, **When** the ordinary run finishes, **Then** the task shows Failed and Carried out, and the task stays In Progress.
9. **Given** a consequential request or an ordinary request that is stopped, **When** the engineer asks for the test, **Then** the test does not run and the task shows Awaiting approval. Approval by the engineer runs it once. The assistant cannot approve. Declining does not run it.
10. **Given** a waiting run whose test file is no longer the file that was named, **When** the engineer approves it, **Then** the test does not run and the engineer is told `The test no longer matches the path this change was proposed against.`
11. **Given** a run that does not finish, **When** the product stops it, **Then** the stored result is Failed and the record says `The test did not finish.`
12. **Given** a test that cannot be started, **When** the engineer asks for an ordinary run, **Then** nothing is stored and the engineer is told `The test could not be run.`

### Edge Cases

- A wrong task status is reported before a blank project. The messages match recording a change.
- One request runs one test. It does not accept an arbitrary command, and it does not run a folder of tests.
- The run does not record a requirement result, verify a criterion, record a check, or complete the task.
- A later requirement result is still recorded only when the engineer records it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On an In Progress task, the engineer MUST be able to ask for one named test in an existing project, with an account of what changed and a class of ordinary or consequential.
- **FR-002**: An ordinary request that is not stopped MUST run that one test when the test file exists and stays inside the project. The task MUST show the test, Passed or Failed, the text the run produced, the assistant, and Carried out.
- **FR-003**: The product MUST refuse a blank test, a name that is not one test in a file, a missing project, a missing test, a path outside the project, and a test that cannot be started, using the messages in the scenarios. A refusal MUST leave the project unrun by this command and MUST store nothing, except a consequential or stopped request, which stores Awaiting approval and does not run the test.
- **FR-004**: Approval of a waiting run MUST run the test once when the path still matches. The assistant MUST NOT approve. Decline MUST NOT run the test. A run that does not finish MUST be stored as Failed with the unfinished message.
- **FR-005**: Opening the task MUST show the stored result and MUST NOT run the test again.
- **FR-006**: Running a test MUST NOT record a requirement result, verify a criterion, record a check, or complete the task.

### Key Entities

- **Test run**: The project, the one test that was named, whether it passed or failed, and the text the run produced. A waiting run has no result until the engineer approves it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state, from the task record alone, which test ran, whether it passed, and whether the change was carried out, in under 2 minutes.
- **SC-002**: In a review of ordinary runs, 100% name the assistant and show a stored Passed or Failed result that does not change when the task is opened again.
- **SC-003**: In a review of refused or waiting runs, 100% leave the test unrun until the engineer approves a waiting run.

## Assumptions

- Specifications 001 through 011 are not rewritten. A requirement result is still recorded only by the engineer. This run does not become that result.
- The engineer names one test that already exists in the project. The product does not accept an arbitrary command and does not invent extra arguments.
- An ordinary request that is not stopped may run now, because the engineer named that one test. A consequential request, a stopped request, and any name that is not one existing test inside the project do not run until the rules above allow it. Approval must name the change.
- The test itself may write files. That effect is part of the named test, not a separate delete, commit, or pull request.
- Deleting a file, committing, and opening a pull request stay out of this action. Each waits for a later feature that names the approval.
