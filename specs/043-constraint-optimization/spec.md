# Feature Specification: Constraint Programming and Optimization for Workflow Scheduling

**Feature Branch**: `043-constraint-optimization`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Constraint Programming and Optimization for Workflow Scheduling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name an activity and its length (Priority: P1)

The engineer names an activity on an In Progress task and gives it a length of 1 or 2. A length of 1 is one day. A length of 2 is two days. A task holds at most 4 activities. The same activity name does not store the activity again and does not change its length. A blank name is refused. A length other than 1 or 2 is refused. A fifth activity is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A schedule can be optimized only after the activities and their lengths exist.

**Independent Test**: Name " design " with length 1 and "build" with length 2. Name "design" with length 2 again. Design stays at length 1.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " design " with length 1, **Then** design is listed at length 1.
2. **Given** design is already length 1, **When** the engineer names "design" with length 2, **Then** design stays at length 1.
3. **Given** four activities, **When** the engineer names a fifth, **Then** the engineer is told `This schedule already has 4 activities.` and the fifth is not stored.
4. **Given** a blank name, **When** the engineer names an activity, **Then** the engineer is told `Name this activity.`
5. **Given** the length "3", **When** the engineer names "note", **Then** the engineer is told `Name a length of 1 or 2.` and no activity is stored.
6. **Given** a task that is not In Progress, **When** the engineer names "design" with length 1, **Then** the engineer is told `The task must be In Progress.` and no activity is stored.
7. **Given** design was named on one task, **When** the engineer names "design" with length 2 on another task, **Then** that other task has its own activity.

---

### User Story 2 - Record a precedence constraint (Priority: P2)

The engineer records that one activity cannot start until an earlier activity has finished. The same pair is stored once. An activity can wait for more than one earlier activity. An activity cannot wait for itself. A constraint that would make a cycle is refused. A name that is not an activity on this task is refused. A new constraint removes the stored plan, because that plan was built for the previous constraints.

**Why this priority**: Precedence is the constraint the optimizer has to obey.

**Independent Test**: Record that test starts after build. Record that again. The task still has one constraint. Record that build starts after test. The engineer is told `Those activities would form a cycle.`

**Acceptance Scenarios**:

1. **Given** build and test, **When** the engineer records that test starts after build, **Then** the task lists test after build.
2. **Given** that constraint, **When** the engineer records it again, **Then** no other constraint is stored.
3. **Given** test after build, **When** the engineer records that build starts after test, **Then** the engineer is told `Those activities would form a cycle.`
4. **Given** an activity named "test", **When** the engineer records that test starts after test, **Then** the engineer is told `An activity cannot follow itself.`
5. **Given** a stored plan, **When** the engineer records a new constraint, **Then** the plan is removed and can be optimized again.
6. **Given** a constraint that is rolled back, **When** the engineer opens the task, **Then** the activities are unchanged and that constraint can still be recorded.

---

### User Story 3 - Optimize the schedule under a capacity (Priority: P3)

The engineer sets a capacity of 1 or 2. Capacity is how many activities may run on the same day. The engineer then optimizes the schedule. Each activity receives a start day. Day 0 is the first day. An activity occupies its length of days from its start. The optimizer chooses starts that obey every precedence constraint and the capacity, and that finish on the earliest possible day. When two schedules finish on the same day, the optimizer chooses the one that starts the earliest-named activity sooner, then the next activity, and so on. The plan is stored with that optimization. A new activity, a new constraint, or a different capacity removes the stored plan. The same capacity does not remove the plan. The task shows each activity, its start, each constraint, the capacity, and the finish day. Name activity is offered while the task is In Progress. Add constraint is offered only while two activities exist. Set capacity is offered only while an activity exists. Optimize schedule is offered only while an activity and a capacity exist. The task list stays the list of tasks.

**Why this priority**: The stored plan is the schedule the engineer reads.

**Independent Test**: Design has length 1, build has length 2, and test has length 1. Test starts after build. The capacity is 2. Optimization starts design on day 0, build on day 0, and test on day 2. The finish day is 3. With capacity 1, design starts on day 0, build on day 1, and test on day 3. The finish day is 4.

**Acceptance Scenarios**:

1. **Given** those three activities, the constraint, and capacity 2, **When** the engineer optimizes, **Then** design starts on day 0, build starts on day 0, test starts on day 2, and the finish day is 3.
2. **Given** the same activities and constraint with capacity 1, **When** the engineer optimizes, **Then** design starts on day 0, build starts on day 1, test starts on day 3, and the finish day is 4.
3. **Given** ada and grace, each of length 1, named in that order, and capacity 1, **When** the engineer optimizes, **Then** ada starts on day 0 and grace starts on day 1.
4. **Given** a stored plan for capacity 2, **When** the engineer sets capacity 1, **Then** the plan is removed. Setting capacity 1 again leaves a later plan in place.
5. **Given** no activity, **When** the engineer sets a capacity or optimizes, **Then** the engineer is told `Name an activity first.`
6. **Given** activities and no capacity, **When** the engineer optimizes, **Then** the engineer is told `Name a capacity first.` A capacity other than 1 or 2 is refused with `Name a capacity of 1 or 2.`
7. **Given** an optimization that is rolled back, **When** the engineer opens the task, **Then** the previous plan and capacity are unchanged.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- A length is accepted only when the trimmed text is 1 or 2.
- A capacity is accepted only when the trimmed text is 1 or 2.
- One request names one activity, records one constraint, sets one capacity, or optimizes once.
- A task holds at most 4 activities, so the optimizer can check every legal start.
- Opening the task later does not change a stored plan. A plan changes only when the engineer optimizes again, or when a new activity, a new constraint, or a different capacity removes it.
- Naming an activity, recording a constraint, setting a capacity, or optimizing does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an activity on an In Progress task and give it a length of 1 or 2. The first accepted use of that name MUST store the activity at that length. The same name MUST NOT store the activity again and MUST NOT change its length. A task MUST hold at most 4 activities. A blank name MUST be refused with `Name this activity.` A length other than 1 or 2 MUST be refused with `Name a length of 1 or 2.` A fifth activity MUST be refused with `This schedule already has 4 activities.` A task that is not In Progress MUST be refused with `The task must be In Progress.`
- **FR-002**: The engineer MUST be able to record that one activity starts after an earlier activity on the same task has finished. The same pair MUST NOT be stored again. An activity MAY wait for more than one earlier activity. An activity MUST NOT wait for itself, and the refusal is `An activity cannot follow itself.` A constraint that would make a cycle MUST be refused with `Those activities would form a cycle.` A name that is not an activity on this task MUST be refused with `That activity is not on this task.` A blank activity MUST be refused with `Name the activity.` A blank earlier activity MUST be refused with `Name the earlier activity.` A new activity or a new constraint MUST remove the stored plan. A rolled-back constraint MUST leave the activities as they were. The same names on another task MUST apply only to that other task.
- **FR-003**: The engineer MUST be able to set a capacity of 1 or 2 and then optimize the schedule. The stored starts MUST obey every precedence constraint and the capacity, and MUST finish on the earliest possible day. Equal finish days MUST choose the schedule that starts the earliest-named activity sooner, then the next, and so on. A different capacity MUST remove the stored plan. The same capacity MUST leave the stored plan in place. A capacity other than 1 or 2 MUST be refused with `Name a capacity of 1 or 2.` A schedule with no activity MUST be refused with `Name an activity first.` An optimization with no capacity MUST be refused with `Name a capacity first.` A rolled-back optimization MUST restore the previous plan and capacity.
- **FR-004**: The task page MUST show each activity, its length, its start day, each constraint, the capacity, and the finish day. It MUST offer Name activity while the task is In Progress, Add constraint only while two activities exist, Set capacity only while an activity exists, and Optimize schedule only while an activity and a capacity exist. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Activity**: The trimmed name of one activity on the task, and its length of 1 or 2 days.
- **Precedence constraint**: The record that one activity cannot start until an earlier activity has finished.
- **Capacity**: How many activities may run on the same day, either 1 or 2.
- **Plan**: The stored start day of each activity and the finish day, produced by one optimization.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named activities, 100% keep the length the engineer gave. A repeated name adds no activity and changes no length. A fifth activity is refused.
- **SC-002**: In a review of constraints, 100% record one earlier activity for the later activity. A repeated pair adds nothing. A cycle and a self-link are refused and leave the constraints unchanged.
- **SC-003**: In a review of optimizations, 100% finish on the earliest day that obeys the constraints and the capacity. Equal finish days choose the schedule that starts earlier-named activities sooner.
- **SC-004**: An engineer can see each activity, its start, each constraint, the capacity, and the finish day on the task in one view.

## Assumptions

- Specifications 001 through 042 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, and workers stay as they are.
- A length of 1 is one day. A length of 2 is two days. Day 0 is the first day.
- Capacity 1 means one activity runs on a day. Capacity 2 means two activities may run on a day.
- A task holds at most 4 activities. The optimizer checks the legal start days and stores one plan.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
