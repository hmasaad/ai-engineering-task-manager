# Feature Specification: Constrained and Multi-Objective Bayesian Optimization

**Feature Branch**: `050-bayesian-optimization`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Constrained and Multi-Objective Bayesian Optimization"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name a design and its two settings (Priority: P1)

The engineer names a design on an In Progress task. A design is one point that can be tried. Each design has two settings, and each setting is 1 or 2. A task holds at most 4 designs. The same design name does not store the design again and does not change its settings. A blank name is refused. A setting other than 1 or 2 is refused. A fifth design is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: An observation and a recommendation can name a design only after the designs exist.

**Independent Test**: Name " ada " with settings 1 and 1, then name "ada" again with settings 2 and 2. Ada stays settings 1 and 1.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada " with settings 1 and 1, **Then** ada is listed with settings 1 and 1.
2. **Given** ada already has settings 1 and 1, **When** the engineer names "ada" with settings 2 and 2, **Then** ada stays settings 1 and 1.
3. **Given** four designs, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 designs.` and the fifth is not stored.
4. **Given** a blank name, **When** the engineer names a design, **Then** the engineer is told `Name this design.`
5. **Given** the setting "3", **When** the engineer names "note", **Then** the engineer is told `Name a setting of 1 or 2.` and no design is stored.
6. **Given** a task that is not In Progress, **When** the engineer names "ada" with settings 1 and 1, **Then** the engineer is told `The task must be In Progress.` and no design is stored.
7. **Given** ada was named on one task, **When** the engineer names "ada" with settings 2 and 2 on another task, **Then** that other task has its own design.

---

### User Story 2 - Record two objectives and a constraint (Priority: P2)

The engineer records an observation of a design. An observation has a name, a design, two objective scores, and a constraint. Each objective score is 1 or 2. A higher score is a better result. The constraint is 1 or 2. A constraint of 1 means the design is feasible. A constraint of 2 means the design is violated. A task holds at most 4 observations. A design has at most one observation. The same observation name does not store the observation again and does not change its design, scores, or constraint. A new design or a new observation removes the stored recommendation. The same design name and the same observation name do not remove it.

**Why this priority**: The front and the next design are counted from these observations.

**Independent Test**: Record " one " for ada, objectives 2 and 1, and constraint 1. Record "one" again with constraint 2. The task still has one observation, and that observation stays constraint 1.

**Acceptance Scenarios**:

1. **Given** design ada, **When** the engineer records " one " for " ada ", objectives 2 and 1, and constraint 1, **Then** the task lists one as ada, objectives 2 and 1, constraint 1.
2. **Given** that observation, **When** the engineer records "one" again with constraint 2, **Then** one stays constraint 1.
3. **Given** a design that is not on this task, **When** the engineer records an observation of it, **Then** the engineer is told `That design is not on this task.`
4. **Given** ada already has an observation, **When** the engineer records another observation of ada, **Then** the engineer is told `That design already has an observation.`
5. **Given** four observations, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 observations.`
6. **Given** a blank observation name, **When** the engineer records an observation, **Then** the engineer is told `Name this observation.` A blank design is refused with `Name the design.` An objective other than 1 or 2 is refused with `Name an objective of 1 or 2.` A constraint other than 1 or 2 is refused with `Name a constraint of 1 or 2.`
7. **Given** a stored recommendation, **When** the engineer records a new observation, **Then** the recommendation is removed.
8. **Given** an observation that is rolled back, **When** the engineer opens the task, **Then** the other observations and the stored recommendation are unchanged.

---

### User Story 3 - Recommend the next feasible design (Priority: P3)

The engineer asks for a recommendation. The front holds every feasible observation that is not dominated. One feasible observation dominates another when both of its objectives are at least as high and one objective is higher. Violated observations stay off the front. The front is listed oldest observation first. The next design is an unobserved design. Its neighbor is the nearest feasible observation: the fewest setting differences, then the higher total of the two objectives, then the observation stored first. Its score is that total minus the number of differences. The highest score is recommended. Equal scores choose the design stored first. The front and the next design are stored with that recommendation. Opening the task later does not recommend again. A new design or a new observation removes the recommendation. The task shows each design, each observation, the front, and the next design. Name design is offered while the task is In Progress. Record observation is offered only while a design exists. Recommend a design is offered only while an observation exists. The task list stays the list of tasks.

**Why this priority**: The stored recommendation is what the engineer reads after the feasible observations have been compared.

**Independent Test**: Ada has settings 1 and 1, objectives 2 and 1, and constraint 1. Grace has settings 2 and 2, objectives 2 and 2, and constraint 2. Mina has settings 1 and 2 and no observation. Nora has settings 2 and 1 and no observation. The front is ada. The next design is mina, because mina and nora both score 2 and mina was stored first.

**Acceptance Scenarios**:

1. **Given** those four designs and two observations, **When** the engineer recommends a design, **Then** the front is ada and the next design is mina.
2. **Given** ada with objectives 1 and 1 and grace with objectives 2 and 2, both feasible, **When** the engineer recommends a design, **Then** the front is grace, because grace dominates ada.
3. **Given** ada with objectives 2 and 1 and grace with objectives 1 and 2, both feasible, **When** the engineer recommends a design, **Then** the front lists ada and then grace.
4. **Given** no design, **When** the engineer recommends, **Then** the engineer is told `Name a design first.`
5. **Given** designs but no feasible observation, **When** the engineer recommends, **Then** the engineer is told `Record a feasible observation first.`
6. **Given** every design already has an observation and at least one is feasible, **When** the engineer recommends, **Then** the engineer is told `No design is left to try.`
7. **Given** a recommendation that is rolled back, **When** the engineer opens the task, **Then** the previous recommendation is unchanged.

### Edge Cases

- A name or a design with surrounding spaces is the same text as the trimmed value.
- A setting, an objective, and a constraint are accepted only when the trimmed text is 1 or 2.
- One request names one design, records one observation, or recommends once.
- A task holds at most 4 designs and at most 4 observations. A design has at most one observation.
- A constraint of 2 keeps that observation off the front and out of the neighbor choice.
- When two designs have the same score, the design stored first is recommended.
- When two feasible observations are the same distance from a design and have the same objective total, the observation stored first is the neighbor.
- Opening the task later does not change a stored recommendation. A recommendation changes only when the engineer recommends again, or when a new design or a new observation removes it.
- Naming a design, recording an observation, or recommending a design does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a design with two settings of 1 or 2 on an In Progress task. The first accepted use of that name MUST store the design and its settings. The same name MUST NOT store the design again and MUST NOT change its settings. A task MUST hold at most 4 designs. A blank name MUST be refused with `Name this design.` A setting other than 1 or 2 MUST be refused with `Name a setting of 1 or 2.` A fifth design MUST be refused with `This task already has 4 designs.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: The engineer MUST be able to record an observation with a name, a design, two objective scores of 1 or 2, and a constraint of 1 or 2. A constraint of 1 means feasible. A constraint of 2 means violated. The same observation name MUST NOT store the observation again and MUST NOT change its fields. A design MUST have at most one observation. A task MUST hold at most 4 observations. A new design or a new observation MUST remove the stored recommendation. A design that is not on this task MUST be refused with `That design is not on this task.` A second observation of the same design MUST be refused with `That design already has an observation.` A blank observation name MUST be refused with `Name this observation.` A blank design MUST be refused with `Name the design.` An objective other than 1 or 2 MUST be refused with `Name an objective of 1 or 2.` A constraint other than 1 or 2 MUST be refused with `Name a constraint of 1 or 2.` A fifth observation MUST be refused with `This task already has 4 observations.` A rolled-back observation MUST leave the other observations and the stored recommendation as they were.
- **FR-003**: The engineer MUST be able to recommend a design. The stored front MUST list each feasible observation that is not dominated, oldest observation first. One feasible observation dominates another when both objectives are at least as high and one is higher. The next design MUST be the unobserved design with the highest score. That score MUST be the neighbor's objective total minus the number of setting differences. The neighbor MUST be the nearest feasible observation, with a higher objective total breaking a distance tie and the observation stored first breaking a total tie. Equal design scores MUST choose the design stored first. A task with no design MUST be refused with `Name a design first.` A task with no feasible observation MUST be refused with `Record a feasible observation first.` A task whose every design has an observation MUST be refused with `No design is left to try.` A rolled-back recommendation MUST restore the previous recommendation.
- **FR-004**: The task page MUST show each design, each observation, the front, and the next design. It MUST offer Name design while the task is In Progress, Record observation only while a design exists, and Recommend a design only while an observation exists. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Design**: The trimmed name of one point and its two settings, each 1 or 2.
- **Observation**: One named trial of one design, with two objective scores and a constraint of 1 or 2.
- **Recommendation**: The stored front of feasible undominated observations and the next unobserved design.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named designs, 100% keep the settings from the first accepted name. A repeated name adds no design and changes no setting. A fifth design is refused.
- **SC-002**: In a review of observations, 100% keep the scores and the constraint from the first accepted name. A second observation of the same design is refused.
- **SC-003**: In a review of recommendations, 100% of fronts omit violated and dominated observations, and 100% of next designs have the highest score. Equal scores choose the design stored first.
- **SC-004**: An engineer can see each design, each observation, the front, and the next design on the task in one view.

## Assumptions

- Specifications 001 through 049 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, learned forecasts, bandit choices, policy scores, safe probes, exploration draws, and model choices stay as they are.
- A higher objective score is better. A constraint of 1 is feasible. A constraint of 2 is violated.
- A task holds at most 4 designs and 4 observations. One recommendation is stored. The front and the next design are counted when the engineer recommends.
- The neighbor stands in for a model of nearby designs. The same designs and the same observations always recommend the same next design.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
