# Feature Specification: Open One Pull Request

**Feature Branch**: `015-open-pull-request`

**Created**: 2026-10-13

**Status**: Accepted

**Input**: User description: "Open one pull request for a named branch only after the engineer approves."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open one pull request after approval (Priority: P1)

On an In Progress task, the engineer names an existing project that already has a remote and one local branch other than the base branch. The request waits. Nothing is published and no pull request is opened until the engineer approves that change. Approval publishes that one branch and opens one pull request. Opening the task again does not open another.

**Why this priority**: Opening a pull request contacts another party and publishes the branch. It waits for an approval that names this change.

**Independent Test**: On one In Progress task, ask to open a pull request for branch `feature` in an existing project `billing`. Nothing is published and the task shows Awaiting approval. After the engineer approves, that branch is published, one pull request is open, and a second opening does not open another.

**Acceptance Scenarios**:

1. **Given** an In Progress task, a project `billing` with a remote and a base branch, and a local branch `feature`, **When** the engineer asks to open a pull request with the account "Open the label pull request", **Then** nothing is published, the task shows `feature`, the base branch, the assistant, consequential, and Awaiting approval, and the task stays In Progress.
2. **Given** that waiting request, **When** the engineer approves it and the branch is still that branch, **Then** only `feature` is published and one pull request is opened into the base branch. The task shows Carried out and the pull request.
3. **Given** that stored pull request, **When** the engineer opens the task again, **Then** the same record is shown and no second pull request is opened.
4. **Given** another local branch, **When** the engineer approves a pull request for `feature`, **Then** the other branch stays unpublished.
5. **Given** the same task, **When** the branch name is blank, **Then** nothing is stored and the engineer is told `Name the branch this change proposes.`
6. **Given** a project that does not exist, **When** the engineer asks for a pull request, **Then** nothing is stored and the engineer is told `The project must already exist.`
7. **Given** a project that is not a repository, **When** the engineer asks for a pull request, **Then** nothing is stored and the engineer is told `The project must already be a repository.`
8. **Given** a repository with no remote, **When** the engineer asks for a pull request, **Then** nothing is stored and the engineer is told `The project must already have a remote.`
9. **Given** a remote with no base branch, **When** the engineer asks for a pull request, **Then** nothing is stored and the engineer is told `The repository must already have a base branch.`
10. **Given** a branch name that is not one local branch, **When** the engineer asks for it, **Then** nothing is stored and the engineer is told `The branch must already exist.`
11. **Given** the base branch itself, **When** the engineer asks to propose it, **Then** nothing is stored and the engineer is told `Choose a branch other than the base branch.`
12. **Given** a waiting pull request, **When** the assistant tries to approve it, **Then** nothing is published and the engineer is told `The assistant cannot approve a change.`
13. **Given** a waiting pull request, **When** the engineer declines it, **Then** nothing is published.
14. **Given** a waiting pull request whose branch is no longer the named branch, **When** the engineer approves it, **Then** nothing is published and the engineer is told `The pull request no longer matches the branch this change was proposed against.`
15. **Given** a repository check that refuses the publish, **When** the engineer approves it, **Then** nothing is published, no pull request is opened, the request stays Awaiting approval, and the engineer is told `The pull request was refused.`

### Edge Cases

- A wrong task status is reported before a blank project. The messages match recording a change.
- An ordinary request and a stopped request also wait. Nothing is published until the engineer approves.
- One request names one branch. It does not publish another branch, force the remote, change repository settings, merge, or skip the repository's checks.
- The pull request does not record a requirement result, verify a criterion, record a check, or complete the task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On an In Progress task, the engineer MUST be able to ask for one named local branch in an existing project to be proposed, with an account of what changed and a class of ordinary or consequential.
- **FR-002**: The request MUST be stored as consequential and Awaiting approval. The task MUST show the branch, the base branch, and the assistant. Nothing MUST be published until the engineer approves that change.
- **FR-003**: The product MUST refuse a blank branch, a missing project, a project that is not a repository, a missing remote, a missing base branch, a missing branch, and a request to propose the base branch, using the messages in the scenarios. A refusal MUST leave the remote unchanged and MUST store nothing.
- **FR-004**: Approval MUST publish that one branch without force and open one pull request into the base branch, using the account as the title. The assistant MUST NOT approve. Decline MUST NOT publish. A branch that no longer matches MUST stay unpublished, with the mismatch message, and the request MUST stay Awaiting approval. A repository check that refuses the publish MUST leave the branch unpublished and MUST NOT open a pull request.
- **FR-005**: Opening the task MUST show the stored pull request and MUST NOT open another.
- **FR-006**: Opening a pull request MUST NOT record a requirement result, verify a criterion, record a check, or complete the task.

### Key Entities

- **Pull request**: The project, the branch, the base branch, and, after approval, the pull request that was opened.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state, from the task record alone, which branch was proposed and whether a pull request was opened, in under 2 minutes.
- **SC-002**: In a review of pull-request requests before approval, 100% leave the remote unpublished.
- **SC-003**: In a review of approved pull requests, 100% publish that one branch once, leave other branches unpublished, and stay the same when the task is opened again.

## Assumptions

- Specifications 001 through 014 are not rewritten. A file write, a folder, a test run, a delete, and a commit keep their current rules.
- Opening a pull request contacts another party and publishes a branch, so every request waits for an approval that names this change. Choosing ordinary does not publish now.
- The project already has one remote and a base branch. The engineer names one other local branch. The product does not accept an arbitrary command.
- Approval publishes that branch as it is and opens one pull request. It does not force the remote, publish another branch, change repository settings, merge, or skip checks.
- A pull request that is already open is left as it is when a later check refuses a second one.
