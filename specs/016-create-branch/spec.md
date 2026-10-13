# Feature Specification: Create One Branch

**Feature Branch**: `016-create-branch`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Create one local branch and check it out only after the engineer approves."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create one branch after approval (Priority: P1)

On an In Progress task, the engineer names an existing project that is already a repository and one new branch. The request waits. Nothing is created and the current branch stays until the engineer approves that change. Approval creates that branch from the current commit and checks it out. Opening the task again does not create another branch and does not check out again.

**Why this priority**: Creating a branch and checking it out changes where the next commit will land. It waits for an approval that names this change.

**Independent Test**: On one In Progress task, ask to create branch `feature` in an existing repository `billing`. Nothing is created and the task shows Awaiting approval. After the engineer approves, `feature` is the current branch, and a second opening does not create another branch or change the current branch.

**Acceptance Scenarios**:

1. **Given** an In Progress task and a repository `billing` with a current commit, **When** the engineer asks to create branch `feature` with the account "Create the feature branch", **Then** no branch is created, the current branch stays, the task shows `feature`, the commit it starts from, the assistant, consequential, and Awaiting approval, and the task stays In Progress.
2. **Given** that waiting request, **When** the engineer approves it and the current commit is still that commit and `feature` is still absent, **Then** `feature` is created from that commit and becomes the current branch. The task shows Carried out.
3. **Given** that stored branch, **When** the engineer opens the task again, **Then** the same record is shown, no second branch is created, and the current branch is not changed.
4. **Given** another local branch and work that is not yet committed, **When** the engineer approves a new branch `feature`, **Then** `feature` is the current branch, the other branch remains, the uncommitted work remains uncommitted, and no new commit is added.
5. **Given** the same task, **When** the branch name is blank, **Then** nothing is stored and the engineer is told `Name the branch this change creates.`
6. **Given** a project that does not exist, **When** the engineer asks for a branch, **Then** nothing is stored and the engineer is told `The project must already exist.`
7. **Given** a project that is not a repository, **When** the engineer asks for a branch, **Then** nothing is stored and the engineer is told `The project must already be a repository.`
8. **Given** a repository with no commit, **When** the engineer asks for a branch, **Then** nothing is stored and the engineer is told `The repository must already have a commit.`
9. **Given** a branch name that is not one branch name, **When** the engineer asks for it, **Then** nothing is stored and the engineer is told `Name the branch this change creates.`
10. **Given** a branch that already exists, **When** the engineer asks to create it, **Then** nothing is stored and the engineer is told `The branch already exists.`
11. **Given** a waiting branch, **When** the assistant tries to approve it, **Then** nothing is created and the engineer is told `The assistant cannot approve a change.`
12. **Given** a waiting branch, **When** the engineer declines it, **Then** nothing is created and the current branch stays.
13. **Given** a waiting branch whose current commit has changed, or whose name is no longer absent, **When** the engineer approves it, **Then** nothing is created, the current branch stays, the request stays Awaiting approval, and the engineer is told `The branch no longer matches the commit this change was proposed against.`
14. **Given** a repository check that refuses the branch, **When** the engineer approves it, **Then** nothing is created, the current branch stays, the request stays Awaiting approval, and the engineer is told `The branch was refused.`

### Edge Cases

- A wrong task status is reported before a blank project. The messages match recording a change.
- An ordinary request and a stopped request also wait. Nothing is created until the engineer approves.
- One request names one new branch. It does not commit, publish, open a pull request, merge, change repository settings, or remove another branch.
- Creating a branch does not record a requirement result, verify a criterion, record a check, or complete the task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On an In Progress task, the engineer MUST be able to ask for one new branch in an existing repository, with an account of what changed and a class of ordinary or consequential.
- **FR-002**: The request MUST be stored as consequential and Awaiting approval. The task MUST show the branch, the commit it starts from, and the assistant. Nothing MUST be created until the engineer approves that change.
- **FR-003**: The product MUST refuse a blank or illegal branch name, a missing project, a project that is not a repository, a repository with no commit, and a branch that already exists, using the messages in the scenarios. A refusal MUST leave the repository unchanged and MUST store nothing.
- **FR-004**: Approval MUST create that one branch from the stored commit and check it out. Uncommitted work MUST stay uncommitted. The assistant MUST NOT approve. Decline MUST NOT create the branch. A commit that changed, or a name that is no longer absent, MUST leave the current branch in place, with the mismatch message, and the request MUST stay Awaiting approval. A repository check that refuses the branch MUST leave the repository unchanged.
- **FR-005**: Opening the task MUST show the stored branch and MUST NOT create another branch or check out again.
- **FR-006**: Creating a branch MUST NOT record a requirement result, verify a criterion, record a check, or complete the task.

### Key Entities

- **Created branch**: The project, the branch name, the commit it starts from, and, after approval, that the branch was checked out.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state, from the task record alone, which branch was proposed and whether it was checked out, in under 2 minutes.
- **SC-002**: In a review of branch requests before approval, 100% leave the current branch unchanged and create no branch.
- **SC-003**: In a review of approved branches, 100% create that one branch once, leave other branches in place, add no commit, and stay the same when the task is opened again.

## Assumptions

- Specifications 001 through 015 are not rewritten. A file write, a folder, a test run, a delete, a commit, and a pull request keep their current rules.
- Creating a branch and checking it out changes where later work is committed, so every request waits for an approval that names this change. Choosing ordinary does not create the branch now.
- The engineer names one new branch. The repository already has a current commit. The product does not accept an arbitrary command.
- Approval creates that branch from the current commit and checks it out. It does not commit, publish, open a pull request, merge, remove another branch, or change repository settings.
- Work that is not yet committed stays uncommitted when the new branch becomes current.
