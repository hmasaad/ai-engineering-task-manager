# Feature Specification: Priority Scheduling, Aging, and Starvation Prevention

**Feature Branch**: `040-priority-aging`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Priority Scheduling, Aging, and Starvation Prevention"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rank waiting work (Priority: P1)

The engineer names a piece of work on an In Progress task and gives it a rank of 1, 2, or 3. Rank 3 is served ahead of rank 2, and rank 2 is served ahead of rank 1, until aging changes the score. The work starts at age 0. The same work name does not rank the work again and does not change its rank or its age. A blank name is refused. A rank other than 1, 2, or 3 is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A priority schedule can be checked only after named work has a rank.

**Independent Test**: Rank " quiet " at 1 and "rush" at 3. The task lists quiet at rank 1, age 0, and rush at rank 3, age 0. Rank "quiet" at 3 again. Quiet stays at rank 1, age 0.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer ranks " quiet " at 1, **Then** quiet is listed at rank 1 and age 0.
2. **Given** quiet is already ranked at 1, **When** the engineer ranks "quiet" at 3, **Then** quiet stays at rank 1 and age 0.
3. **Given** a blank name, **When** the engineer ranks work, **Then** the engineer is told `Name this work.`
4. **Given** the name "quiet" and the rank "4", **When** the engineer ranks work, **Then** the engineer is told `Name a rank from 1 to 3.` and no work is stored.
5. **Given** a task that is not In Progress, **When** the engineer ranks "quiet" at 1, **Then** the engineer is told `The task must be In Progress.` and no work is stored.
6. **Given** quiet was ranked on one task, **When** the engineer ranks "quiet" at 2 on another task, **Then** that other task has its own work at rank 2 and age 0.

---

### User Story 2 - Serve the highest score and age the rest (Priority: P2)

The engineer names a serve. The score of waiting work is its rank plus its age. The serve goes to the waiting work with the highest score. The work ranked first wins a tie. That work leaves the waiting list. Every other piece of work that is still waiting ages by 1. The same serve name does not serve again and does not age anyone. A schedule with no waiting work is refused. A rolled-back serve leaves the ranks, the ages, and the serves as they were.

**Why this priority**: Serving the highest score, and aging what was passed over, is the schedule.

**Independent Test**: Rank quiet at 1 and rush at 3. Serve "one". Rush is served and quiet is at age 1. Serve "one" again. Quiet stays at age 1 and the task still has one serve.

**Acceptance Scenarios**:

1. **Given** quiet is rank 1 age 0 and rush is rank 3 age 0, **When** the engineer serves "one", **Then** rush is served and quiet is at rank 1 and age 1.
2. **Given** quiet is rank 1 age 1 and a new piece of work named again is rank 3 age 0, **When** the engineer serves "two", **Then** again is served and quiet is at age 2.
3. **Given** two pieces of waiting work have the same score, **When** the engineer serves, **Then** the work ranked first is served.
4. **Given** a serve named "one", **When** the engineer serves "one" again, **Then** no other serve is stored and no waiting work ages.
5. **Given** no work is waiting, **When** the engineer serves "one", **Then** the engineer is told `Rank work before serving.`
6. **Given** a serve that is rolled back, **When** the engineer opens the task, **Then** the work is still waiting at age 0 and that serve name can still be used.

---

### User Story 3 - Keep low rank from waiting forever (Priority: P3)

A piece of rank-1 work that has aged by 2 has the same score as a new piece of rank-3 work. The earlier work is served. The task shows each waiting piece as its rank and age, and each serve as the work it served. Rank work is offered while the task is In Progress. Serve next is offered only while work is waiting. The task list stays the list of tasks.

**Why this priority**: Aging is what stops a stream of new high-rank work from leaving low-rank work unserved, and the page is where the engineer sees that.

**Independent Test**: Rank quiet at 1, then rush at 3. Serve "one" and "two" so that rush and a later rank-3 piece are served and quiet is at age 2. Rank late at 3. Serve "three". Quiet is served ahead of late. The page shows `three served quiet`.

**Acceptance Scenarios**:

1. **Given** quiet is rank 1 age 2 and late is rank 3 age 0, **When** the engineer serves "three", **Then** quiet is served and late stays waiting at rank 3 and age 1.
2. **Given** a blank serve name, **When** the engineer serves, **Then** the engineer is told `Name this serve.`
3. **Given** ranked work and serves, **When** the engineer opens the task, **Then** the page shows each waiting piece as rank and age and each serve as served to that work. Serve next is offered only while work is waiting.
4. **Given** a serve on one task, **When** the engineer opens another task, **Then** that other task does not list the first task's serves.
5. **Given** ranked work and a serve, **When** the engineer opens the task, **Then** the task status is unchanged and the tenant schedule is unchanged.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- A rank is accepted only when the trimmed text is 1, 2, or 3.
- One request ranks one piece of work or serves one piece of work.
- Work that has been served is not waiting, is not chosen again, and does not age.
- Aging by 1 applies only to other work that is still waiting, and only when a new serve is stored.
- Ranking work or serving work does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name work on an In Progress task and give it a rank of 1, 2, or 3. The first accepted use of that name MUST store the work at that rank and at age 0. The same name MUST NOT store the work again and MUST NOT change its rank or its age. A blank name MUST be refused with `Name this work.` A rank other than 1, 2, or 3 MUST be refused with `Name a rank from 1 to 3.` A task that is not In Progress MUST be refused with `The task must be In Progress.`
- **FR-002**: The engineer MUST be able to name a serve. The score of waiting work MUST be its rank plus its age. The first accepted use of that serve name MUST serve the waiting work with the highest score. The work ranked first MUST win a tie. Served work MUST leave the waiting list. Every other piece of work that is still waiting MUST age by 1. The same serve name MUST NOT serve again and MUST NOT age any work. A blank name MUST be refused with `Name this serve.` A schedule with no waiting work MUST be refused with `Rank work before serving.` A rolled-back serve MUST leave the work, the ages, and the serves as they were. The same names on another task MUST apply only to that other task.
- **FR-003**: Rank-1 work that has aged by 2 MUST have the same score as rank-3 work at age 0, and the work ranked first MUST be served. The task page MUST show each waiting piece with its rank and age, and each serve with the work it served. It MUST offer Rank work while the task is In Progress, and Serve next only while work is waiting. The task list MUST stay the list of tasks.
- **FR-004**: Ranking work or serving work MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, or change the task status.

### Key Entities

- **Ranked work**: The trimmed name of one piece of waiting work on the task, its rank of 1, 2, or 3, and its age. Age starts at 0 and rises by 1 each time other work is served while this work is still waiting.
- **Serve**: The trimmed name of one service. It records which ranked work was served.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly ranked work, 100% start at the given rank and age 0, and a repeated name adds no work and changes no rank.
- **SC-002**: In a review of serves, 100% go to waiting work with the highest score, where the score is rank plus age. Equal scores choose the work ranked first, and every other waiting piece ages by 1.
- **SC-003**: In a review where rank-1 work has aged by 2 and new rank-3 work is waiting, 100% of the next serves choose the earlier work. In a review of rolled-back serves, 100% leave that work waiting at the age it had before.
- **SC-004**: An engineer can see each waiting rank and age, and each serve, on the task in one view.

## Assumptions

- Specifications 001 through 039 are not rewritten. Tenants, workers, the waiting queue, and the workflow steps stay as they are.
- A rank is 1, 2, or 3. Rank 3 is the highest rank. The score is rank plus age.
- One serve chooses one piece of waiting work and ages every other piece that is still waiting by 1.
- Equal scores choose the work ranked first.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
