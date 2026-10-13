# Feature Specification: Commit One File

**Feature Branch**: `014-commit-file`

**Created**: 2026-10-13

**Status**: Accepted

**Input**: User description: "Commit one file in the named project only after the engineer approves."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Commit one file after approval (Priority: P1)

On an In Progress task, the engineer names an existing project that is already a repository and one text file inside it that has a change. The request waits. Nothing is committed until the engineer approves that change. Approval commits that one file. Opening the task again does not make another commit.

**Why this priority**: A commit adds durable history. It waits for an approval that names this change.

**Independent Test**: On one In Progress task, ask to commit a changed `label.txt` in an existing repository `billing`. Nothing is committed and the task shows Awaiting approval. After the engineer approves, that file is in one new commit and a second opening does not add another.

**Acceptance Scenarios**:

1. **Given** an In Progress task and a changed text file `billing/label.txt` in an existing repository, **When** the engineer asks to commit it with the account "Record the label", **Then** nothing is committed, the task shows that file, its text, the assistant, consequential, and Awaiting approval, and the task stays In Progress.
2. **Given** that waiting commit, **When** the engineer approves it and the file still has the same text, **Then** one commit records that file and that account, and the task shows Carried out.
3. **Given** that stored commit, **When** the engineer opens the task again, **Then** the same record is shown and no second commit is made.
4. **Given** another changed file in the same repository, **When** the engineer approves a commit of `label.txt`, **Then** the commit contains `label.txt` and the other file stays uncommitted.
5. **Given** the same task, **When** the file name is blank, **Then** nothing is stored and the engineer is told `Name the file this change commits.`
6. **Given** a project that does not exist, **When** the engineer asks for a commit, **Then** nothing is stored and the engineer is told `The project must already exist.`
7. **Given** a project that is not a repository, **When** the engineer asks for a commit, **Then** nothing is stored and the engineer is told `The project must already be a repository.`
8. **Given** `billing` exists and the named file does not, **When** the engineer asks for a commit, **Then** nothing is stored and the engineer is told `The file must already exist.`
9. **Given** a path that would leave the project, **When** the engineer asks for it, **Then** nothing is stored and the engineer is told `The file must stay inside the named project.`
10. **Given** a folder at the named path, **When** the engineer asks to commit it, **Then** nothing is stored and the engineer is told `The path is a folder.`
11. **Given** a link at the named path, **When** the engineer asks to commit it, **Then** nothing is stored and the engineer is told `A link cannot be committed by this change.`
12. **Given** a file that is not text, **When** the engineer asks to commit it, **Then** the file stays uncommitted, nothing is stored, and the engineer is told `The file is not text.`
13. **Given** a text file with no change, **When** the engineer asks to commit it, **Then** nothing is stored and the engineer is told `That file has no change to commit.`
14. **Given** a waiting commit, **When** the assistant tries to approve it, **Then** nothing is committed and the engineer is told `The assistant cannot approve a change.`
15. **Given** a waiting commit, **When** the engineer declines it, **Then** nothing is committed.
16. **Given** a waiting commit whose file text has changed, **When** the engineer approves it, **Then** nothing is committed and the engineer is told `The file no longer matches the text this change was proposed against.`
17. **Given** a repository check that refuses the commit, **When** the engineer approves it, **Then** nothing is committed, the request stays Awaiting approval, and the engineer is told `The commit was refused.`

### Edge Cases

- A wrong task status is reported before a blank project. The messages match recording a change.
- An ordinary request and a stopped request also wait. Nothing is committed until the engineer approves.
- One request names one text file. It does not commit a folder, a link, or a second file.
- The commit uses the repository as it already is. It does not change repository settings, skip the repository's checks, amend an earlier commit, or push.
- The commit does not record a requirement result, verify a criterion, record a check, or complete the task.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: On an In Progress task, the engineer MUST be able to ask for one named text file in an existing repository to be committed, with an account of what changed and a class of ordinary or consequential.
- **FR-002**: The request MUST be stored as consequential and Awaiting approval. The task MUST show the file, the text it had, and the assistant. Nothing MUST be committed until the engineer approves that change.
- **FR-003**: The product MUST refuse a blank file, a missing project, a project that is not a repository, a missing file, a path outside the project, a folder, a link, a file that is not text, and a file with no change, using the messages in the scenarios. A refusal MUST leave the repository unchanged and MUST store nothing.
- **FR-004**: Approval MUST commit that one file only when it is still that text. The account is the commit message. The assistant MUST NOT approve. Decline MUST NOT commit. A file whose text changed MUST stay uncommitted, with the mismatch message, and the request MUST stay Awaiting approval. A repository check that refuses the commit MUST leave it uncommitted.
- **FR-005**: Opening the task MUST show the stored commit and MUST NOT make another commit.
- **FR-006**: Committing a file MUST NOT record a requirement result, verify a criterion, record a check, or complete the task.

### Key Entities

- **Committed file**: The project, the file path, the text the file had when the commit was requested, and, after approval, the commit that recorded it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can state, from the task record alone, which file was proposed for commit and whether it was carried out, in under 2 minutes.
- **SC-002**: In a review of commit requests before approval, 100% leave the repository without a new commit.
- **SC-003**: In a review of approved commits, 100% record that one file once, leave other changes uncommitted, and stay the same when the task is opened again.

## Assumptions

- Specifications 001 through 013 are not rewritten. A file write, a folder, a test run, and a delete keep their current rules.
- A commit adds durable history, so every commit waits for an approval that names this change. Choosing ordinary does not commit now.
- The engineer names one existing text file that already has a change. The product does not accept an arbitrary command.
- The commit does not push, open a pull request, change repository settings, skip checks, or amend an earlier commit.
- Opening a pull request stays out of this action. It waits for a later feature that names the approval.
