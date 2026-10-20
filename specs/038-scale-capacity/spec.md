# Feature Specification: Autoscaling and Queue-Based Capacity Planning

**Feature Branch**: `038-scale-capacity`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Autoscaling and Queue-Based Capacity Planning"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read how many workers the queue needs (Priority: P1)

The engineer names work that is waiting. Waiting work is not held by a worker yet. The engineer then names a capacity plan. That plan records how many items are waiting, how many jobs are already held, how many workers are active, and how many workers are needed. One worker is needed for every three items of waiting or held work. No work needs no workers. The same plan name does not record another plan. The task status stays as it was.

**Why this priority**: A later scale can be checked only after the queue says how many workers it needs.

**Independent Test**: Queue "one", "two", "three", and "four" with no workers. Plan "now". The plan says 4 waiting, 0 held, 2 needed, and 0 active. Plan "now" again. The task still has one plan.

**Acceptance Scenarios**:

1. **Given** no workers and no jobs, **When** the engineer queues "one", **Then** "one" is waiting and no worker holds it.
2. **Given** four waiting items and no workers, **When** the engineer plans "now", **Then** the plan says 4 waiting, 0 held, 2 workers needed, and 0 active.
3. **Given** that plan, **When** the engineer plans "now" again, **Then** no other plan is stored.
4. **Given** one worker who holds one job, **When** the engineer plans "later", **Then** the plan says 0 waiting, 1 held, 1 needed, and 1 active.
5. **Given** the name "one" was queued on one task, **When** the engineer queues "one" on another task, **Then** that other task has its own waiting work.

---

### User Story 2 - Add a worker only when the queue is past capacity (Priority: P2)

The engineer names a scale. If a worker has room for waiting work, that scale gives the oldest waiting item to the worker who holds the fewest jobs. The worker named first wins a tie. No worker is added. If every active worker is full, or there is no worker, and more work is still waiting, the scale adds one worker and that worker holds the oldest waiting item. The new worker is named by the scale. The same scale name does not change the queue again. A scale that is rolled back leaves the queue and the workers as they were.

**Why this priority**: Spare room must be used before another worker is added, and a full queue must be able to grow by one worker.

**Independent Test**: One worker, ada, is idle. Queue "one", "two", "three", and "four". Scale "fill". Ada holds "one" and no new worker is added. Repeat until ada holds three items. Scale "grace". Grace is added and holds "four". Scale "grace" again. The queue does not change.

**Acceptance Scenarios**:

1. **Given** ada holds nothing and work is waiting, **When** the engineer scales "fill", **Then** ada holds the oldest waiting item and grace is not added.
2. **Given** ada already holds three jobs and one item is still waiting, **When** the engineer scales "grace", **Then** grace is added and holds that item.
3. **Given** no workers and one waiting item, **When** the engineer scales "ada", **Then** ada is added and holds that item.
4. **Given** a scale named "grace", **When** the engineer scales "grace" again, **Then** no other worker is added and no other item is assigned.
5. **Given** a scale that is rolled back, **When** the engineer opens the task, **Then** the waiting item is still waiting and that scale name can still be used.
6. **Given** a worker named ada, **When** the engineer scales up with the name "ada", **Then** no worker is added and the engineer is told `That worker is already on this task.`

---

### User Story 3 - Release an idle worker the queue does not need (Priority: P3)

When the queue needs fewer workers than are active, a scale releases the newest active worker who holds nothing. A worker who holds a job is not released. When the queue already has the workers it needs, and no waiting work can be assigned, the engineer is told `The queue already has the workers it needs.` A blank scale name is refused with `Name this scale.` A blank plan name is refused with `Name this plan.` A blank queued name is refused with `Name this work.` A task that is not In Progress is refused with `The task must be In Progress.` The task shows the waiting work, the capacity, each plan, and each scale.

**Why this priority**: Extra idle workers should leave once the queue no longer needs them, and the page should show that reading.

**Independent Test**: Ada and grace are active and hold nothing. Scale "trim". Grace is released and ada stays. Queue nothing more. Scale "again". Ada is released. Scale "stop". The engineer is told `The queue already has the workers it needs.`

**Acceptance Scenarios**:

1. **Given** ada and grace hold nothing and no work is waiting, **When** the engineer scales "trim", **Then** grace is released and ada stays active.
2. **Given** two workers who both hold a job and the queue needs only one, **When** the engineer scales, **Then** both stay active and the engineer is told `Every extra worker holds a job.`
3. **Given** the queue already matches its workers and nothing is waiting, **When** the engineer scales "stop", **Then** the engineer is told `The queue already has the workers it needs.`
4. **Given** a scale that releases a worker and is rolled back, **When** the engineer opens the task, **Then** that worker is still active.
5. **Given** a plan and a scale, **When** the engineer opens the task, **Then** the page shows the waiting work, the workers needed, the active workers, the plan, and the scale. Scale workers is offered only while a scale can change the queue.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- One request queues one item, records one plan, or scales once.
- One worker is needed for every three waiting or held items. Zero items need zero workers.
- Waiting work is assigned oldest first. Equal job counts choose the worker named first.
- A released worker no longer receives jobs and cannot steal.
- The same queued name on a job that is already held is refused with `That work is already on this task.`
- Queuing, planning, or scaling does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, or change the task status.
- Placing a job while every active worker is full is still refused with `Every worker is full.`
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name waiting work on an In Progress task. The first accepted use of that name MUST leave the work waiting, held by no worker. The same name MUST NOT queue a second item. A blank name MUST be refused with `Name this work.` A name already held as a job MUST be refused with `That work is already on this task.`
- **FR-002**: The engineer MUST be able to name a capacity plan. The first accepted use of that name MUST record the waiting count, the held count, the active worker count, and the workers needed. Workers needed MUST be one for every three waiting or held items, and zero when nothing is waiting or held. The same name MUST NOT record another plan. A blank name MUST be refused with `Name this plan.`
- **FR-003**: The engineer MUST be able to name a scale. When an active worker has room and work is waiting, the first accepted use of that name MUST assign the oldest waiting item to the worker who holds the fewest jobs. The worker named first MUST win a tie. No worker is added. When no active worker has room and work is waiting, the scale MUST add one worker named by the scale, and that worker MUST hold the oldest waiting item.
- **FR-004**: When the active workers are more than the workers needed, a scale MUST release the newest active worker who holds nothing. A worker who holds a job MUST NOT be released. If every extra worker holds a job, the scale MUST be refused with `Every extra worker holds a job.` When the queue already has the workers it needs and no waiting work can be assigned, the scale MUST be refused with `The queue already has the workers it needs.` A scale name that is already an active or released worker MUST be refused with `That worker is already on this task.` when the scale would add a worker.
- **FR-005**: The same scale name MUST NOT scale again. A blank scale name MUST be refused with `Name this scale.` A rolled-back scale MUST leave the waiting work, the jobs, and the workers as they were. A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-006**: Queuing, planning, or scaling MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, or change the task status. A placement onto a full active worker MUST still be refused with `Every worker is full.` The task page MUST show the waiting work, the workers needed, the active workers, each plan, and each scale. It MUST offer Queue work and Plan capacity while the task is In Progress, and Scale workers only while a scale can change the queue. The task list MUST stay the list of tasks.

### Key Entities

- **Waiting work**: The trimmed name of work that is not held by a worker yet.
- **Capacity plan**: The trimmed name of one reading. It records waiting, held, active workers, and workers needed at that time.
- **Scale**: The trimmed name of one change. It assigns one waiting item, adds one worker, or releases one idle worker.
- **Released worker**: An active worker who was released. The worker stays on the record and no longer holds new work.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of capacity plans, 100% set workers needed to one worker for every three waiting or held items, and to zero when that total is zero.
- **SC-002**: In a review of scales made while a worker has room, 100% assign one oldest waiting item and add no worker. In a review of scales made while every active worker is full and work is waiting, 100% add one worker who holds the oldest waiting item.
- **SC-003**: In a review of scales made with more active workers than needed, 100% release only the newest idle worker. In a review of rolled-back scales, 100% leave the queue and the workers unchanged.
- **SC-004**: An engineer can see the waiting work, the workers needed, the active workers, each plan, and each scale on the task in one view.

## Assumptions

- Specifications 001 through 037 are not rewritten. A direct placement still refuses when every active worker holds three jobs. Stealing and load balancing stay as they are for active workers.
- One worker holds at most three jobs. The capacity reading uses that same bound.
- A released worker is kept on the task. The name is not given to a new worker.
- One scale changes one thing: one assignment, one added worker, or one release.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
