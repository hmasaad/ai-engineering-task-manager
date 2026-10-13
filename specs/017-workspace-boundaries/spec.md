# Feature Specification: Workspace Boundaries and Capability-Based Permissions

**Feature Branch**: `017-workspace-boundaries`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Workspace Boundaries and Capability-Based Permissions"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Keep one workspace separate, and keep it after a restart (Priority: P1)

The engineer starts the task manager with one workspace. Tasks, statuses, and evidence written there stay in that workspace. A second workspace opened at the same time does not show them and cannot change them. Closing the task manager and starting it again with the same workspace shows the same tasks, statuses, and evidence.

**Why this priority**: Two projects must not share task records by accident. A restart must not drop the record the engineer is relying on.

**Independent Test**: Create a task, a status, and a piece of evidence in workspace A. Open workspace B and confirm it has none of those records. Create a different task in B and confirm A is unchanged. Close A and open it again. The original task, status, and evidence are still there.

**Acceptance Scenarios**:

1. **Given** workspace A and workspace B, **When** the engineer records a task, a status, and evidence in A, **Then** B lists none of those records.
2. **Given** those two workspaces, **When** the engineer records a different task in B, **Then** A still shows only its own task.
3. **Given** a closed workspace A, **When** the engineer starts again with that same workspace, **Then** the task title, status, and evidence are unchanged.
4. **Given** a fresh start that names a workspace that does not exist yet, **When** the engineer creates a task there, **Then** that task is stored in the named workspace and not in any other workspace.

### User Story 2 - Task records do not touch the repository (Priority: P2)

Managing task records does not create, delete, or modify files in the named project, and it does not run a repository command. Creating a task, editing a goal, adding a criterion, changing status, recording a decision, recording a check, and recording a requirement are task records.

**Why this priority**: The task manager may be pointed at another repository. Keeping the task record must not change that repository.

**Independent Test**: In a repository that already has one commit and one changed file, record a task through to In Progress, verify a criterion, record an ordinary change that names no file, record a decision, and record a requirement. The repository files, the current commit, and the current branch are unchanged, and no repository command ran.

**Acceptance Scenarios**:

1. **Given** an existing repository and an In Progress task, **When** the engineer records only task records, **Then** the repository files, the current commit, and the current branch stay as they were.
2. **Given** an ordinary change whose account names a project but names no file, folder, test, or branch, **When** the engineer records it, **Then** the project is unchanged.
3. **Given** the same task, **When** the engineer opens it again, **Then** the stored records are shown and the repository is still unchanged.

### User Story 3 - One capability authorizes one named target (Priority: P3)

A repository capability is one requested command. It names one project and one target. The capabilities are: read one file, write one file, create one folder, run one test, delete one file, commit one file, create one branch, and open one pull request. Completing one capability does not authorize another. An approval names that one change. A prior approval, silence, or a different change does not approve it. The assistant cannot approve.

**Why this priority**: Pointing the task manager at a repository must not become permission to do every repository action.

**Independent Test**: Approve a request to create branch `feature`. That approval checks out `feature` and does not commit a file, delete a file, or open a pull request. A separate waiting commit stays waiting until its own approval.

**Acceptance Scenarios**:

1. **Given** a waiting branch request and a waiting commit on the same task, **When** the engineer approves only the branch, **Then** the branch is created and the commit stays Awaiting approval.
2. **Given** an approved file read, **When** the engineer has not asked to write, delete, commit, or open a pull request, **Then** the file is unchanged and no commit or pull request exists.
3. **Given** a waiting delete, commit, branch, or pull request, **When** the assistant tries to approve it, **Then** nothing is carried out and the engineer is told `The assistant cannot approve a change.`
4. **Given** a consequential request, **When** nobody has approved that change, **Then** it stays Awaiting approval. Choosing ordinary does not carry it out now.
5. **Given** an ordinary new file or a new folder that the existing rules already carry out, **When** the engineer asks for that one target, **Then** only that target is created. No other file, folder, test, branch, or pull request is touched.

### Edge Cases

- A task record is refused, or a capability is refused, without changing the other workspace and without changing the repository.
- The workspace file is created at the workspace the engineer named. It is not created inside the project unless the engineer named a workspace there.
- Specifications 001 through 016 keep their current rules for each capability. This feature does not add a second approval for a capability that already waits, and it does not remove an approval those specifications require.
- One request still names one target. It does not grant a standing permission for later requests.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The task manager MUST read and write task records only in the workspace named when it starts. Another workspace MUST NOT show or change those records.
- **FR-002**: Starting again with the same workspace MUST preserve tasks, statuses, and evidence already stored there.
- **FR-003**: Task records MUST NOT create, delete, or modify files in a project, and MUST NOT run a repository command.
- **FR-004**: Each repository capability MUST name one project and one target. Carrying out one capability MUST NOT carry out a different capability or a different target.
- **FR-005**: A capability that deletes, commits, creates a branch, opens a pull request, replaces a file, or otherwise waits under specifications 001 through 016 MUST remain waiting until an approval names that change. The assistant MUST NOT approve it.
- **FR-006**: This feature MUST NOT add a task status, a requirement result, or a second permission screen.

### Key Entities

- **Workspace**: The named store for tasks, statuses, and evidence. One start uses one workspace.
- **Capability**: One requested repository command, the project it names, the one target it names, and whether an approval has carried it out.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of two workspaces used together, 100% of records written in one are absent from the other.
- **SC-002**: After a restart with the same workspace, a reader can find the same task title, status, and evidence in under 2 minutes.
- **SC-003**: In a review of task-record commands, 100% leave the named project unchanged.
- **SC-004**: In a review of approved capabilities, 100% carry out only the named target. Every other waiting capability on that task stays waiting.

## Assumptions

- Specifications 001 through 016 are not rewritten. Their commands, messages, and approval rules stay as they are.
- There is one engineer and one assistant name. This feature does not add sign-in, roles, or a screen where capabilities are granted in advance.
- The capability is the stored command. A consequential capability is exercised only by the approval that names that change. An earlier approval does not cover a later change.
- The workspace is the file the engineer named at the start. Relative project names still resolve from the folder where the task manager was started. An absolute project path is used as given.
- Ordinary new files and new folders that specifications 006 and 011 already carry out on request still do so. They remain one target per request.
