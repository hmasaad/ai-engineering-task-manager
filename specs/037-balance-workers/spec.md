# Feature Specification: Work Stealing, Backpressure, and Load Balancing

**Feature Branch**: `037-balance-workers`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Work Stealing, Backpressure, and Load Balancing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Place a job on the least busy worker (Priority: P1)

The engineer names workers on an In Progress task, then names a job. That job is held by the worker who already holds the fewest pending jobs. When two workers hold the same number, the worker named first gets the job. The same worker name does not add a second worker. The same job name does not place a second job. The task status stays as it was.

**Why this priority**: Work has to land on a named worker before a full queue or a steal can be judged.

**Independent Test**: Name "ada", then "grace". Place "one", "two", and "three". Ada holds "one" and "three". Grace holds "two". Place "one" again. The jobs stay as they are.

**Acceptance Scenarios**:

1. **Given** no workers, **When** the engineer names "ada", **Then** the task shows ada with no jobs.
2. **Given** ada and grace, and no jobs, **When** the engineer places "one", **Then** ada holds "one" and grace stays idle.
3. **Given** ada holds one job and grace holds none, **When** the engineer places "two", **Then** grace holds "two".
4. **Given** ada and grace each hold one job, **When** the engineer places "three", **Then** ada holds that job, because ada was named first.
5. **Given** those jobs, **When** the engineer places "one" again, **Then** no other job is added.
6. **Given** the name "ada" on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own ada.

---

### User Story 2 - A full queue refuses more work (Priority: P2)

Three is the bound. A job is refused when the worker who would take it already holds three pending jobs. The engineer is told `Every worker is full.` The refused name is not saved. A blank job name is refused with `Name this job.` No worker is refused with `Name a worker first.` A blank worker name is refused with `Name this worker.` A task that is not In Progress is refused with `The task must be In Progress.` None of those refusals stores the name. A placement that is rolled back leaves the workers as they were, and the same name can then be used.

**Why this priority**: A worker who is already at the bound must not silently take more work.

**Independent Test**: Name one worker and place "one", "two", and "three". Place "four". The engineer is told `Every worker is full.` and the worker still holds only those three jobs. Roll back a placement named "once". That name is not stored, and "once" can be placed afterward.

**Acceptance Scenarios**:

1. **Given** one worker who holds three jobs, **When** the engineer places another job, **Then** the worker still holds three jobs and the engineer is told `Every worker is full.`
2. **Given** two workers who each hold three jobs, **When** the engineer places another job, **Then** no job is added and the engineer is told `Every worker is full.`
3. **Given** no worker, **When** the engineer places "one", **Then** nothing is stored and the engineer is told `Name a worker first.`
4. **Given** a blank job name, **When** the engineer places it, **Then** nothing is stored and the engineer is told `Name this job.`
5. **Given** a placement that is rolled back, **When** the engineer opens the task, **Then** that job is absent and that name can still be used.
6. **Given** a task that is not In Progress, **When** the engineer names a worker or places a job, **Then** the engineer is told `The task must be In Progress.` and nothing is stored.

---

### User Story 3 - An idle worker takes the oldest job (Priority: P3)

The engineer names a steal and an idle worker. That worker takes the oldest pending job from the other worker who holds the most pending jobs. When two workers hold the same number, the one named first loses the job. The same steal name does not move another job. A worker who already holds a job is refused with `That worker is not idle.` A worker who is not on the task is refused with `That worker is not on this task.` No job to take is refused with `There is no work to steal.` A blank steal name is refused with `Name this steal.` A missing idle worker name is refused with `Name the idle worker.` A steal that is rolled back leaves the job where it was. The task shows each worker, the jobs that worker holds, and each steal.

**Why this priority**: An idle worker should take waiting work from the busiest worker, and the task should show that move.

**Independent Test**: Ada holds "one" and "three". Grace holds "two". Name idle worker "lin" and steal "take". Lin holds "one". Ada holds "three". Steal "take" again. The jobs stay as they are. Roll back a steal named "next". The job stays on its original worker.

**Acceptance Scenarios**:

1. **Given** ada holds two jobs and grace holds one, **When** idle worker lin steals "take", **Then** lin holds ada's oldest job and ada holds the other.
2. **Given** that steal, **When** the engineer steals "take" again, **Then** no other job moves.
3. **Given** two workers each hold one job, **When** an idle worker steals, **Then** the job comes from the worker named first.
4. **Given** a worker who holds a job, **When** that worker is named as the idle worker, **Then** no job moves and the engineer is told `That worker is not idle.`
5. **Given** a steal that is rolled back, **When** the engineer opens the task, **Then** the job is still on the original worker and that steal name can still be used.
6. **Given** workers and a steal, **When** the engineer opens the task, **Then** the page shows each worker, the jobs held, and the steal, and offers Steal work only while an idle worker can take a job.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- One request adds one worker, places one job, or steals one job.
- A worker with no jobs is idle. A worker becomes idle only by being named with no jobs, or by having every pending job stolen.
- The bound is three pending jobs on the worker who would otherwise take the next job.
- A repeated name does not add a worker, place a job, or steal a job.
- Naming a worker, placing a job, or stealing a job does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a worker on an In Progress task. The first accepted use of that name MUST show that worker with no jobs. The same name MUST NOT add a second worker. A blank name MUST be refused with `Name this worker.`
- **FR-002**: The engineer MUST be able to name a job. The first accepted use of that name MUST give the job to the worker who holds the fewest pending jobs. When the counts are equal, the worker named first MUST get the job. The same name MUST NOT place a second job. A blank name MUST be refused with `Name this job.` No worker MUST be refused with `Name a worker first.`
- **FR-003**: When the worker who would take the job already holds three pending jobs, the placement MUST be refused with `Every worker is full.` The name MUST NOT be saved. A rolled-back placement MUST leave the workers unchanged, and that name MUST still be usable.
- **FR-004**: The engineer MUST be able to name a steal and an idle worker. The first accepted use of that steal name MUST move the oldest pending job from the other worker who holds the most pending jobs onto the idle worker. When those counts are equal, the job MUST come from the worker named first. The same steal name MUST NOT move another job.
- **FR-005**: A steal MUST be refused with `Name this steal.` when the steal name is blank, with `Name the idle worker.` when the idle worker is blank, with `That worker is not on this task.` when the named worker is absent, with `That worker is not idle.` when that worker holds a job, and with `There is no work to steal.` when no other worker holds a job. Those refusals MUST NOT store the steal name. A rolled-back steal MUST leave the job on its original worker.
- **FR-006**: A task that is not In Progress MUST be refused with `The task must be In Progress.` That refusal MUST NOT store the name. The same names on another task MUST apply only to that other task.
- **FR-007**: Naming a worker, placing a job, or stealing a job MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, or change the task status. The task page MUST show each worker, the jobs that worker holds from oldest to newest, and each steal. It MUST offer Add worker while the task is In Progress, Place job while a worker can take a job, and Steal work while an idle worker can take a job. The task list MUST stay the list of tasks.

### Key Entities

- **Worker**: The trimmed name of one worker on one task. A worker holds zero or more pending jobs.
- **Job**: The trimmed name of one piece of pending work. It is held by exactly one worker. Stealing changes which worker holds it. It is not completed by this feature.
- **Steal**: The trimmed name of one move. It names the job, the worker who lost it, and the idle worker who took it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of placements onto workers with equal counts, 100% give the job to the worker named first. In a review of placements onto workers with different counts, 100% give the job to the worker who holds fewer jobs.
- **SC-002**: In a review of placements when every worker already holds three jobs, 100% leave the jobs unchanged and tell the engineer `Every worker is full.` In a review of rolled-back placements, 100% leave no job under that name.
- **SC-003**: In a review of steals, 100% move one oldest job from the busiest other worker onto the named idle worker. In a review of rolled-back steals, 100% leave that job on the original worker.
- **SC-004**: An engineer can see each worker, the jobs held, and each steal on the task in one view.

## Assumptions

- Specifications 001 through 036 are not rewritten. Workflow steps, deliveries, and file reads stay as they are.
- The bound is three pending jobs on a worker. The count is pending jobs, not steals.
- Jobs stay pending. This feature does not finish a job. An idle worker is one who holds none.
- The engineer names the idle worker for a steal. The product does not choose which idle worker steals.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
