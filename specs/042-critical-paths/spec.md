# Feature Specification: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

**Feature Branch**: `042-critical-paths`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name a schedule step and its length (Priority: P1)

The engineer names a step on an In Progress task and gives it a length of 1 or 2. A length of 1 is one day. A length of 2 is two days. The same step name does not store the step again and does not change its length. A blank name is refused. A length other than 1 or 2 is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A critical path can be checked only after the steps and their lengths exist.

**Independent Test**: Name " design " with length 1 and "build" with length 2. The task lists both lengths. Name "design" with length 2 again. Design stays at length 1.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " design " with length 1, **Then** design is listed at length 1.
2. **Given** design is already length 1, **When** the engineer names "design" with length 2, **Then** design stays at length 1.
3. **Given** a blank name, **When** the engineer names a step, **Then** the engineer is told `Name this step.`
4. **Given** the name "design" and the length "3", **When** the engineer names a step, **Then** the engineer is told `Name a length of 1 or 2.` and no step is stored.
5. **Given** a task that is not In Progress, **When** the engineer names "design" with length 1, **Then** the engineer is told `The task must be In Progress.` and no step is stored.
6. **Given** design was named on one task, **When** the engineer names "design" with length 2 on another task, **Then** that other task has its own step.

---

### User Story 2 - Record which step follows another (Priority: P2)

The engineer names a step and the step it follows. That link is stored once. The same link does not store another link. A step cannot follow itself. A step that already follows one step cannot follow a second step. A link that would make a cycle is refused. A name that is not a step on this task is refused. A rolled-back link leaves the steps as they were.

**Why this priority**: The critical path is the chain made by these links.

**Independent Test**: Name design and build. Record that build follows design. Record that again. The task still has one link. Record that design follows build. The engineer is told `Those steps would form a cycle.`

**Acceptance Scenarios**:

1. **Given** design and build, **When** the engineer records that build follows design, **Then** build is listed as following design.
2. **Given** build already follows design, **When** the engineer records that again, **Then** no other link is stored.
3. **Given** build already follows design, **When** the engineer records that build follows note, **Then** the engineer is told `That step already follows another step.`
4. **Given** a step named "build", **When** the engineer records that build follows build, **Then** the engineer is told `A step cannot follow itself.`
5. **Given** build follows design and review follows build, **When** the engineer records that design follows review, **Then** the engineer is told `Those steps would form a cycle.`
6. **Given** a link that is rolled back, **When** the engineer opens the task, **Then** build follows nothing and that link can still be recorded.

---

### User Story 3 - Show the critical path and propagate the deadline (Priority: P3)

The critical path is the chain with the greatest total length. The chain whose first step was named first wins a tie. The engineer gives the schedule one deadline, written as a real UTC time such as `2026-12-03T00:00:00Z`. The last step of every chain finishes at that deadline. Each earlier step finishes earlier by the days of the steps after it. A later deadline replaces the stored deadline, and every latest time follows the new deadline. The task shows each step, what it follows, its latest time, the critical path, and the deadline. Name step is offered while the task is In Progress. Add dependency is offered only while two steps exist. Set deadline is offered only while a step exists. The task list stays the list of tasks.

**Why this priority**: The critical path and the propagated deadline are what the engineer uses to see which chain sets the schedule.

**Independent Test**: Design has length 1 and build has length 2. Build follows design. The deadline is `2026-12-03T00:00:00Z`. The critical path is design, build. Design's latest time is `2026-12-01T00:00:00Z`. Build's latest time is `2026-12-03T00:00:00Z`.

**Acceptance Scenarios**:

1. **Given** design of length 1 and build of length 2, and build follows design, **When** the engineer opens the task, **Then** the critical path is design, build.
2. **Given** two chains with the same total length, **When** the engineer opens the task, **Then** the critical path is the chain whose first step was named first.
3. **Given** that chain and the deadline `2026-12-03T00:00:00Z`, **When** the engineer sets the deadline, **Then** build's latest time is `2026-12-03T00:00:00Z` and design's latest time is `2026-12-01T00:00:00Z`.
4. **Given** a deadline of `2026-12-03T00:00:00Z`, **When** the engineer sets `2026-12-04T00:00:00Z`, **Then** the stored deadline is `2026-12-04T00:00:00Z` and build's latest time is that deadline.
5. **Given** no step has been named, **When** the engineer sets a deadline, **Then** the engineer is told `Name a step first.`
6. **Given** a blank service of the link form, **When** the engineer records a dependency, **Then** the engineer is told `Name the step that follows.` A deadline that is not a real UTC time is refused with `Name a deadline.`

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- A length is accepted only when the trimmed text is 1 or 2.
- A deadline is accepted only when the trimmed text is a real UTC time in the form `2026-12-03T00:00:00Z`.
- One request names one step, records one dependency, or sets one deadline.
- A step follows at most one other step.
- Opening the task later does not change the stored deadline. Latest times are the deadline minus the days of the steps that come after.
- Naming a step, recording a dependency, or setting a deadline does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a step on an In Progress task and give it a length of 1 or 2. The first accepted use of that name MUST store the step at that length. The same name MUST NOT store the step again and MUST NOT change its length. A blank name MUST be refused with `Name this step.` A length other than 1 or 2 MUST be refused with `Name a length of 1 or 2.` A task that is not In Progress MUST be refused with `The task must be In Progress.`
- **FR-002**: The engineer MUST be able to record that one step follows another step on the same task. The same link MUST NOT be stored again. A step MUST NOT follow itself, and the refusal is `A step cannot follow itself.` A step that already follows a step MUST NOT follow a different step, and the refusal is `That step already follows another step.` A link that would make a cycle MUST be refused with `Those steps would form a cycle.` A name that is not a step on this task MUST be refused with `That step is not on this task.` A blank follower MUST be refused with `Name the step that follows.` A blank predecessor MUST be refused with `Name the step it follows.` A rolled-back link MUST leave the steps as they were. The same names on another task MUST apply only to that other task.
- **FR-003**: The critical path MUST be the chain with the greatest total length. The chain whose first step was named first MUST win a tie. The engineer MUST be able to set one deadline for the schedule. The last step of every chain MUST finish at that deadline. Each earlier step MUST finish earlier by one day for each day of length in the steps after it. A new deadline MUST replace the stored deadline. A deadline that is not a real UTC time in the form `2026-12-03T00:00:00Z` MUST be refused with `Name a deadline.` A schedule with no step MUST be refused with `Name a step first.`
- **FR-004**: The task page MUST show each step, its length, the step it follows, its latest time, the critical path, and the deadline. It MUST offer Name step while the task is In Progress, Add dependency only while two steps exist, and Set deadline only while a step exists. Naming a step, recording a dependency, or setting a deadline MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Schedule step**: The trimmed name of one step on the task, and its length of 1 or 2 days.
- **Dependency**: The record that one step follows one earlier step.
- **Schedule deadline**: The one UTC time by which the last step of every chain must finish. Latest times are counted back from it by the lengths of the later steps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named steps, 100% keep the length the engineer gave, and a repeated name adds no step and changes no length.
- **SC-002**: In a review of dependencies, 100% record one earlier step for the follower. A repeated link adds nothing. A cycle, a self-link, and a second predecessor are refused and leave the links unchanged.
- **SC-003**: In a review of schedules, 100% name the chain with the greatest total length as the critical path. Equal lengths choose the chain whose first step was named first. Each latest time is the deadline minus the days of the steps after it.
- **SC-004**: An engineer can see each step, its dependency, its latest time, the critical path, and the deadline on the task in one view.

## Assumptions

- Specifications 001 through 041 are not rewritten. Workflow actions, objectives, priority ranks, tenants, and workers stay as they are.
- A length of 1 is one day. A length of 2 is two days.
- A step follows at most one other step. The critical path is one chain.
- One deadline applies to every chain. The last step of each chain finishes at that deadline.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
