# Feature Specification: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

**Feature Branch**: `041-deadline-slos`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Deadline-Aware Scheduling and Service-Level Objectives (SLOs)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name an objective and its deadline (Priority: P1)

The engineer names an objective on an In Progress task and gives it a deadline. The deadline is a UTC time written as a year, month, day, the letter T, hours, minutes, seconds, and the letter Z, for example `2026-12-01T00:00:00Z`. The same objective name does not store the objective again and does not change its deadline. A blank name is refused. A deadline in any other form is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A deadline schedule can be checked only after an objective has a deadline.

**Independent Test**: Set " export " due `2026-12-01T00:00:00Z` and "rush" due `2026-10-01T00:00:00Z`. The task lists both deadlines. Set "export" due `2026-01-01T00:00:00Z` again. Export stays due `2026-12-01T00:00:00Z`.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer sets " export " due `2026-12-01T00:00:00Z`, **Then** export is listed with that deadline.
2. **Given** export is already due `2026-12-01T00:00:00Z`, **When** the engineer sets "export" due `2026-01-01T00:00:00Z`, **Then** export stays due `2026-12-01T00:00:00Z`.
3. **Given** a blank name, **When** the engineer sets an objective, **Then** the engineer is told `Name this objective.`
4. **Given** the name "export" and the deadline "tomorrow", **When** the engineer sets an objective, **Then** the engineer is told `Name a deadline.` and no objective is stored.
5. **Given** a task that is not In Progress, **When** the engineer sets "export" due `2026-12-01T00:00:00Z`, **Then** the engineer is told `The task must be In Progress.` and no objective is stored.
6. **Given** export was set on one task, **When** the engineer sets "export" due `2026-11-01T00:00:00Z` on another task, **Then** that other task has its own objective.

---

### User Story 2 - Serve the earliest deadline and record the objective (Priority: P2)

The engineer names a service. The service goes to the objective that has not been served and has the earliest deadline. The objective named first wins a tie. The service is recorded as met when it is recorded at or before that deadline, and as missed when it is recorded after that deadline. That result stays as recorded. The same service name does not serve again. A task with no objective is refused. A rolled-back service leaves the objectives as they were.

**Why this priority**: Serving the earliest deadline, and recording whether the objective was met, is the schedule.

**Independent Test**: Set rush due `2026-10-01T00:00:00Z` and export due `2026-12-01T00:00:00Z`. Serve "one". Rush is served and the service is missed, because that deadline has passed. Serve "one" again. The task still has that one service.

**Acceptance Scenarios**:

1. **Given** rush is due `2026-10-01T00:00:00Z` and export is due `2026-12-01T00:00:00Z`, **When** the engineer serves "one", **Then** rush is served and the service is missed.
2. **Given** export is still waiting and its deadline is `2026-12-01T00:00:00Z`, **When** the engineer serves "two", **Then** export is served and the service is met.
3. **Given** two waiting objectives share one deadline, **When** the engineer serves, **Then** the objective named first is served.
4. **Given** a service named "one", **When** the engineer serves "one" again, **Then** no other service is stored.
5. **Given** no objective has been set, **When** the engineer serves "one", **Then** the engineer is told `Name an objective first.`
6. **Given** a service that is rolled back, **When** the engineer opens the task, **Then** that objective is still waiting and that service name can still be used.

---

### User Story 3 - Keep a later deadline from jumping the queue (Priority: P3)

An objective that has been served is not chosen again. When every objective has been served, the engineer is told `Every objective has been served.` A blank service name is refused with `Name this service.` The task shows each waiting objective and its deadline, and each service as met or missed. Set objective is offered while the task is In Progress. Serve objective is offered only while an objective is waiting. The task list stays the list of tasks.

**Why this priority**: The page is where the engineer sees which deadline was kept and which was missed.

**Independent Test**: After rush has been served as missed and export has been served as met, serve "three". The engineer is told `Every objective has been served.` The page shows `one missed rush` and `two met export`.

**Acceptance Scenarios**:

1. **Given** rush and export have both been served, **When** the engineer serves "three", **Then** the engineer is told `Every objective has been served.`
2. **Given** a blank service name, **When** the engineer serves, **Then** the engineer is told `Name this service.`
3. **Given** objectives and services, **When** the engineer opens the task, **Then** the page shows each waiting objective with its deadline and each service as met or missed for that objective. Serve objective is offered only while an objective is waiting.
4. **Given** a service on one task, **When** the engineer opens another task, **Then** that other task does not list the first task's services.
5. **Given** an objective and a service, **When** the engineer opens the task, **Then** the task status is unchanged and the priority schedule is unchanged.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- A deadline is accepted only when the trimmed text is a real UTC time in the form `2026-12-01T00:00:00Z`.
- One request sets one objective or serves one objective.
- An objective that has been served is not waiting and is not chosen again.
- Opening the task later does not change a service that was already recorded as met or missed.
- Setting an objective or serving an objective does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an objective on an In Progress task and give it a deadline. The first accepted use of that name MUST store the objective with that deadline. The same name MUST NOT store the objective again and MUST NOT change its deadline. A blank name MUST be refused with `Name this objective.` A deadline that is not a real UTC time in the form `2026-12-01T00:00:00Z` MUST be refused with `Name a deadline.` A task that is not In Progress MUST be refused with `The task must be In Progress.`
- **FR-002**: The engineer MUST be able to name a service. The first accepted use of that name MUST serve the waiting objective with the earliest deadline. The objective named first MUST win a tie. The service MUST be recorded as met when its recorded time is at or before the deadline, and as missed when its recorded time is after the deadline. That result MUST stay as recorded. The same service name MUST NOT serve again. A blank name MUST be refused with `Name this service.` A task with no objective MUST be refused with `Name an objective first.` When every objective has been served, the service MUST be refused with `Every objective has been served.` A rolled-back service MUST leave the objectives and the services as they were. The same names on another task MUST apply only to that other task.
- **FR-003**: The task page MUST show each waiting objective and its deadline, and each service as met or missed for that objective. It MUST offer Set objective while the task is In Progress, and Serve objective only while an objective is waiting. The task list MUST stay the list of tasks.
- **FR-004**: Setting an objective or serving an objective MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, or change the task status.

### Key Entities

- **Objective**: The trimmed name of one service-level objective on the task, and the deadline the engineer gave it. It is waiting until a service records it.
- **Service**: The trimmed name of one service of an objective. It records which objective was served and whether that service met or missed the deadline.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly set objectives, 100% keep the deadline the engineer gave, and a repeated name adds no objective and changes no deadline.
- **SC-002**: In a review of services, 100% go to the waiting objective with the earliest deadline. Equal deadlines choose the objective named first. A service at or before the deadline is met, and a service after the deadline is missed.
- **SC-003**: In a review of services made after every objective has been served, 100% are refused and leave the schedule unchanged. In a review of rolled-back services, 100% leave that objective waiting.
- **SC-004**: An engineer can see each waiting deadline, and each met or missed service, on the task in one view.

## Assumptions

- Specifications 001 through 040 are not rewritten. Priority ranks, tenants, workers, and the workflow steps stay as they are.
- A deadline is a real UTC time written as `2026-12-01T00:00:00Z`. The earliest such time is served first.
- A service meets the objective when the service is recorded at or before the deadline. It misses the objective when the service is recorded after the deadline. The recorded result does not change later.
- One service serves one objective.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
