# Feature Specification: Multi-Fidelity Bayesian Optimization and Successive Halving

**Feature Branch**: `051-fidelity-halving`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Multi-Fidelity Bayesian Optimization and Successive Halving."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name a candidate (Priority: P1)

The engineer names a candidate on an In Progress task. A candidate is one design that can be measured. A task holds at most 4 candidates. The same candidate name does not store the candidate again. A blank name is refused. A fifth candidate is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A measurement and a halving can name a candidate only after the candidates exist.

**Independent Test**: Name " ada ", then name "ada" again. The task still has one candidate, ada.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada ", **Then** ada is listed.
2. **Given** ada is already named, **When** the engineer names "ada" again, **Then** the task still has one candidate.
3. **Given** four candidates, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 candidates.` and the fifth is not stored.
4. **Given** a blank name, **When** the engineer names a candidate, **Then** the engineer is told `Name this candidate.`
5. **Given** a task that is not In Progress, **When** the engineer names "ada", **Then** the engineer is told `The task must be In Progress.` and no candidate is stored.
6. **Given** ada was named on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own candidate.

---

### User Story 2 - Record a cheap or expensive measurement (Priority: P2)

The engineer records a measurement of a candidate. A measurement has a name, a candidate, a fidelity, and a score. The fidelity is 1 or 2. Fidelity 1 is the cheap measurement. Fidelity 2 is the expensive measurement. The score is 1 or 2. A higher score is a better result. A candidate has at most one measurement at each fidelity. A task holds at most 6 measurements. The same measurement name does not store the measurement again and does not change its candidate, fidelity, or score. An expensive measurement is accepted only after the field has been halved, and only for a candidate who was kept. A new candidate or a new cheap measurement removes the kept names and the winner. A new expensive measurement removes the winner and leaves the kept names. The same candidate name and the same measurement name do not remove them.

**Why this priority**: The kept half and the winner are counted from these measurements.

**Independent Test**: Record " one " for ada at fidelity 1 with score 2. Record "one" again at fidelity 1 with score 1. The task still has one measurement, and that measurement stays score 2.

**Acceptance Scenarios**:

1. **Given** candidate ada, **When** the engineer records " one " for " ada " at fidelity 1 with score 2, **Then** the task lists one as ada, fidelity 1, score 2.
2. **Given** that measurement, **When** the engineer records "one" again with score 1, **Then** one stays score 2.
3. **Given** a candidate that is not on this task, **When** the engineer records a measurement of it, **Then** the engineer is told `That candidate is not on this task.`
4. **Given** ada already has a fidelity 1 measurement, **When** the engineer records another fidelity 1 measurement of ada, **Then** the engineer is told `That candidate already has this fidelity.`
5. **Given** six measurements, **When** the engineer records a seventh, **Then** the engineer is told `This task already has 6 measurements.`
6. **Given** a blank measurement name, **When** the engineer records a measurement, **Then** the engineer is told `Name this measurement.` A blank candidate is refused with `Name the candidate.` A fidelity other than 1 or 2 is refused with `Name a fidelity of 1 or 2.` A score other than 1 or 2 is refused with `Name a score of 1 or 2.`
7. **Given** no kept names, **When** the engineer records fidelity 2, **Then** the engineer is told `Halve the field before an expensive measurement.`
8. **Given** a kept set that does not include ada, **When** the engineer records fidelity 2 for ada, **Then** the engineer is told `That candidate was not kept.`
9. **Given** a stored halving, **When** the engineer names a new candidate, **Then** the kept names and the winner are removed.
10. **Given** a stored winner, **When** the engineer records an expensive measurement for a candidate who was not kept, **Then** the engineer is told `That candidate was not kept.` and the winner stays.
11. **Given** a measurement that is rolled back, **When** the engineer opens the task, **Then** the other measurements, the kept names, and the winner are unchanged.

---

### User Story 3 - Halve the field and name the winner (Priority: P3)

The engineer halves the field. Every candidate must already have a cheap measurement, and the task must have at least two candidates. The kept names are the better half of the cheap scores. The number kept is half the number of candidates, dropping the remainder. A higher cheap score is kept first. Equal cheap scores keep the candidate stored first. The winner is named only when every kept candidate has an expensive measurement. The winner is the kept candidate with the higher expensive score. Equal expensive scores choose the candidate stored first. The kept names and the winner are stored with that halving. Opening the task later does not halve again. The task shows each candidate, each measurement, the kept names, and the winner. Name candidate is offered while the task is In Progress. Record fidelity is offered only while a candidate exists. Halve the field is offered only while two cheap measurements exist. The task list stays the list of tasks.

**Why this priority**: The stored kept names and the winner are what the engineer reads after the cheap scores have been compared.

**Independent Test**: Ada, grace, mina, and nora are named in that order. Cheap scores are ada 1, grace 2, mina 2, and nora 1. The kept names are grace and mina. Grace then scores 1 at fidelity 2 and mina scores 2. The winner is mina.

**Acceptance Scenarios**:

1. **Given** those four cheap measurements, **When** the engineer halves the field, **Then** the kept names are grace and mina and there is no winner yet.
2. **Given** grace scores 1 and mina scores 2 at fidelity 2, **When** the engineer halves the field again, **Then** the kept names stay grace and mina and the winner is mina.
3. **Given** grace and mina both score 2 at fidelity 2, **When** the engineer halves the field, **Then** the winner is grace, because grace was stored first.
4. **Given** two candidates and ada’s cheap score is higher than grace’s, **When** the engineer halves the field, **Then** the kept name is ada.
5. **Given** three candidates, **When** the engineer halves the field, **Then** one name is kept.
6. **Given** no candidate, **When** the engineer halves the field, **Then** the engineer is told `Name a candidate first.`
7. **Given** one candidate, **When** the engineer halves the field, **Then** the engineer is told `Name another candidate first.`
8. **Given** a candidate with no cheap measurement, **When** the engineer halves the field, **Then** the engineer is told `Record a cheap measurement for every candidate first.`
9. **Given** a halving that is rolled back, **When** the engineer opens the task, **Then** the previous kept names and winner are unchanged.

### Edge Cases

- A name or a candidate with surrounding spaces is the same text as the trimmed value.
- A fidelity and a score are accepted only when the trimmed text is 1 or 2.
- One request names one candidate, records one measurement, or halves the field once.
- A task holds at most 4 candidates and at most 6 measurements. A candidate has at most one measurement at each fidelity.
- When six measurements already exist, another measurement is refused with `This task already has 6 measurements.` even when that candidate already has that fidelity.
- An expensive score never changes who was kept. It can change only the winner.
- A candidate who was not kept is not measured at fidelity 2.
- When two cheap scores are equal, the candidate stored first is kept.
- When two expensive scores are equal, the candidate stored first is the winner.
- Opening the task later does not change a stored halving. A halving changes only when the engineer halves again, or when a new candidate or a new measurement removes the part that command is allowed to remove.
- Naming a candidate, recording a measurement, or halving the field does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a candidate on an In Progress task. The first accepted use of that name MUST store the candidate. The same name MUST NOT store the candidate again. A task MUST hold at most 4 candidates. A blank name MUST be refused with `Name this candidate.` A fifth candidate MUST be refused with `This task already has 4 candidates.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task. A new candidate MUST remove the kept names and the winner. The same candidate name MUST NOT remove them.
- **FR-002**: The engineer MUST be able to record a measurement with a name, a candidate, a fidelity of 1 or 2, and a score of 1 or 2. Fidelity 1 is cheap. Fidelity 2 is expensive. The same measurement name MUST NOT store the measurement again and MUST NOT change its fields. A candidate MUST have at most one measurement at each fidelity. A task MUST hold at most 6 measurements. A candidate that is not on this task MUST be refused with `That candidate is not on this task.` A second measurement of the same candidate at the same fidelity MUST be refused with `That candidate already has this fidelity.` A blank measurement name MUST be refused with `Name this measurement.` A blank candidate MUST be refused with `Name the candidate.` A fidelity other than 1 or 2 MUST be refused with `Name a fidelity of 1 or 2.` A score other than 1 or 2 MUST be refused with `Name a score of 1 or 2.` A seventh measurement MUST be refused with `This task already has 6 measurements.` Fidelity 2 before a halving MUST be refused with `Halve the field before an expensive measurement.` Fidelity 2 for a candidate who was not kept MUST be refused with `That candidate was not kept.` A new cheap measurement MUST remove the kept names and the winner. A new expensive measurement MUST remove the winner and MUST leave the kept names. A rolled-back measurement MUST leave the other measurements, the kept names, and the winner as they were.
- **FR-003**: The engineer MUST be able to halve the field. Every candidate MUST already have a cheap measurement, and the task MUST have at least two candidates. The stored kept names MUST be the better half of the cheap scores. The number kept MUST be half the number of candidates, dropping the remainder. A higher cheap score MUST be kept first. Equal cheap scores MUST keep the candidate stored first. The winner MUST be stored only when every kept candidate has an expensive measurement, and MUST be the kept candidate with the higher expensive score. Equal expensive scores MUST choose the candidate stored first. A task with no candidate MUST be refused with `Name a candidate first.` A task with one candidate MUST be refused with `Name another candidate first.` A candidate with no cheap measurement MUST be refused with `Record a cheap measurement for every candidate first.` A rolled-back halving MUST restore the previous kept names and winner.
- **FR-004**: The task page MUST show each candidate, each measurement, the kept names, and the winner. It MUST offer Name candidate while the task is In Progress, Record fidelity only while a candidate exists, and Halve the field only while two cheap measurements exist. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Candidate**: The trimmed name of one design that can be measured.
- **Measurement**: One named trial of one candidate, at fidelity 1 or 2, with a score of 1 or 2.
- **Halving**: The stored kept names from the cheap scores, and the winner from the expensive scores when every kept candidate has one.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named candidates, 100% keep the first accepted name. A repeated name adds no candidate. A fifth candidate is refused.
- **SC-002**: In a review of measurements, 100% keep the fidelity and the score from the first accepted name. A second measurement of the same candidate at the same fidelity is refused. An expensive measurement of a candidate who was not kept is refused.
- **SC-003**: In a review of halvings, 100% of kept sets are the better half of the cheap scores, and 100% of winners have the highest expensive score among the kept names. Equal scores choose the candidate stored first.
- **SC-004**: An engineer can see each candidate, each measurement, the kept names, and the winner on the task in one view.

## Assumptions

- Specifications 001 through 050 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, learned forecasts, bandit choices, policy scores, safe probes, exploration draws, model choices, and search recommendations stay as they are.
- A higher score is better. Fidelity 1 is the cheap measurement. Fidelity 2 is the expensive measurement.
- A task holds at most 4 candidates and 6 measurements. One halving is stored. The kept names and the winner are counted when the engineer halves the field.
- The cheap score stands in for a low-fidelity model. The expensive score stands in for the trusted result. The same candidates and the same measurements always keep the same names and name the same winner.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
