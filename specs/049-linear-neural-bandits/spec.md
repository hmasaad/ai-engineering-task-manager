# Feature Specification: Contextual Bandits with Linear Models and Neural Contextual Bandits

**Feature Branch**: `049-linear-neural-bandits`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Contextual Bandits with Linear Models and Neural Contextual Bandits"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name an arm and a context with two marks (Priority: P1)

The engineer names an arm on an In Progress task. An arm is one choice a model can select. A task holds at most 2 arms. The engineer also names a context and gives it two marks. Each mark is 0 or 1. A mark of 1 means that part of the situation is present. A mark of 0 means it is absent. A task holds at most 2 contexts. The same arm name does not store the arm again. The same context name does not store the context again and does not change its marks. A blank name is refused. A mark other than 0 or 1 is refused. A third arm is refused. A third context is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A model can score an arm only after the arms and the marked contexts exist.

**Independent Test**: Name " ada " and then "ada" again. The task still has one arm. Name " rush " with marks 1 and 1, then name "rush" again with marks 0 and 0. Rush stays marks 1 and 1.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada ", **Then** ada is listed as an arm.
2. **Given** ada is already an arm, **When** the engineer names "ada" again, **Then** the task still has one arm.
3. **Given** two arms, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 arms.` and the third is not stored.
4. **Given** a blank arm name, **When** the engineer names an arm, **Then** the engineer is told `Name this arm.`
5. **Given** an In Progress task, **When** the engineer names " rush " with marks 1 and 1, **Then** rush is listed with marks 1 and 1.
6. **Given** rush already has marks 1 and 1, **When** the engineer names "rush" with marks 0 and 0, **Then** rush stays marks 1 and 1.
7. **Given** two contexts, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 contexts.` and the third is not stored.
8. **Given** a blank context name, **When** the engineer names a context, **Then** the engineer is told `Name this context.` A mark other than 0 or 1 is refused with `Name a mark of 0 or 1.`
9. **Given** a task that is not In Progress, **When** the engineer names "ada" or "rush", **Then** the engineer is told `The task must be In Progress.` and nothing is stored.
10. **Given** ada was named on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own arm.

---

### User Story 2 - Record a pull that changes the weights (Priority: P2)

The engineer records a pull. A pull has a name, a context, an arm, and a reward of 1 or 2. Each arm has three weights, and each weight starts at 0: the first mark, the second mark, and the pair. A pull adds its reward to the first weight when that context's first mark is 1. It adds its reward to the second weight when the second mark is 1. It adds its reward to the pair weight when both marks are 1. A mark of 0 adds nothing to that weight. A task holds at most 4 pulls. The same pull name does not store the pull again and does not change its context, arm, or reward. A new arm, a new context, or a new pull removes the stored choice. The same arm name, the same context name, and the same pull name do not remove it.

**Why this priority**: The linear score and the neural score are counted from these weights.

**Independent Test**: Quiet has marks 1 and 0. Record " one " for quiet, ada, and reward 2. Record "one" again with reward 1. The task still has one pull, and that pull stays reward 2.

**Acceptance Scenarios**:

1. **Given** arm ada and context quiet with marks 1 and 0, **When** the engineer records " one " for " quiet ", " ada ", and reward 2, **Then** the task lists one as quiet, ada, reward 2.
2. **Given** that pull, **When** the engineer records "one" again with reward 1, **Then** one stays reward 2.
3. **Given** a context that is not on this task, **When** the engineer records a pull in it, **Then** the engineer is told `That context is not on this task.`
4. **Given** an arm that is not on this task, **When** the engineer records a pull of it, **Then** the engineer is told `That arm is not on this task.`
5. **Given** four pulls, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 pulls.`
6. **Given** a blank pull name, **When** the engineer records a pull, **Then** the engineer is told `Name this pull.` A blank context is refused with `Name the context.` A blank arm is refused with `Name the arm.` A reward other than 1 or 2 is refused with `Name a reward of 1 or 2.`
7. **Given** a stored choice, **When** the engineer records a new pull, **Then** the choice is removed.
8. **Given** a pull that is rolled back, **When** the engineer opens the task, **Then** the other pulls and the stored choice are unchanged.

---

### User Story 3 - Choose an arm with a linear or neural model (Priority: P3)

The engineer chooses an arm in one context with one model. The linear score is the first weight times the first mark, plus the second weight times the second mark. The neural score is the linear score plus the pair weight when both marks are 1. When either mark is 0, the neural score is the linear score. The arm with the higher score is chosen. Equal scores choose the arm that was named first. The context, the model, and the chosen arm are stored with that choice. Opening the task later does not choose again. A new arm, a new context, or a new pull removes the choice. The task shows each arm, each context and its marks, each pull, and the choice. Name model arm and Name model context are offered while the task is In Progress. Record model pull and Choose with model are offered only while the task has an arm and a context. The task list stays the list of tasks.

**Why this priority**: The stored choice is what the engineer reads after the model has scored the arms.

**Independent Test**: Ada is named before grace. Quiet has marks 1 and 0. Rush has marks 1 and 1. Ada has two pulls in quiet with reward 2, so ada's first weight is 4 and the other two weights stay 0. Grace has one pull in rush with reward 2, so grace's three weights are 2. In rush the linear scores are 4 and 4, so the linear choice is ada. The neural scores are 4 and 6, so the neural choice is grace.

**Acceptance Scenarios**:

1. **Given** those pulls, **When** the engineer chooses with the linear model in rush, **Then** the choice is ada, because both linear scores are 4 and ada was named first.
2. **Given** those pulls, **When** the engineer chooses with the neural model in rush, **Then** the choice is grace, because grace's neural score is 6 and ada's neural score is 4.
3. **Given** those pulls, **When** the engineer chooses with the neural model in quiet, **Then** the choice is ada, because the second mark is 0 and the pair weight is not added.
4. **Given** no pulls, **When** the engineer chooses with the linear model, **Then** every score is 0 and the choice is the arm named first.
5. **Given** no arm, **When** the engineer chooses, **Then** the engineer is told `Name an arm first.`
6. **Given** a blank context, **When** the engineer chooses, **Then** the engineer is told `Name the context to choose.` A task with no context is refused with `Name a context first.` A context that is not on this task is refused with `That context is not on this task.`
7. **Given** a blank model, **When** the engineer chooses, **Then** the engineer is told `Name the model.` A model other than linear or neural is refused with `Name a linear or neural model.`
8. **Given** a choice that is rolled back, **When** the engineer opens the task, **Then** the previous choice is unchanged.

### Edge Cases

- A name, a context, or an arm with surrounding spaces is the same text as the trimmed value.
- A mark is accepted only when the trimmed text is 0 or 1.
- A reward is accepted only when the trimmed text is 1 or 2.
- A model is accepted only when the trimmed text is linear or neural.
- One request names one arm, names one context, records one pull, or chooses once.
- A task holds at most 2 arms, at most 2 contexts, and at most 4 pulls.
- The weights are counted from the pulls. A mark of 0 adds nothing. The pair weight changes only when both marks are 1.
- When two arms have the same score, the arm that was named first is chosen.
- Opening the task later does not change a stored choice. A choice changes only when the engineer chooses again, or when a new arm, a new context, or a new pull removes it.
- Naming an arm, naming a context, recording a pull, or choosing an arm does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an arm, and to name a context with two marks of 0 or 1, on an In Progress task. The first accepted use of a name MUST store that arm or that context. The same context name MUST NOT change its marks. A task MUST hold at most 2 arms and at most 2 contexts. A blank arm name MUST be refused with `Name this arm.` A third arm MUST be refused with `This task already has 2 arms.` A blank context name MUST be refused with `Name this context.` A mark other than 0 or 1 MUST be refused with `Name a mark of 0 or 1.` A third context MUST be refused with `This task already has 2 contexts.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: The engineer MUST be able to record a pull with a name, a context, an arm, and a reward of 1 or 2. The same pull name MUST NOT store the pull again and MUST NOT change its context, arm, or reward. A task MUST hold at most 4 pulls. Each arm MUST start with a first weight, a second weight, and a pair weight of 0. A pull MUST add its reward to a weight only when the matching mark is 1, and to the pair weight only when both marks are 1. A new arm, a new context, or a new pull MUST remove the stored choice. A context that is not on this task MUST be refused with `That context is not on this task.` An arm that is not on this task MUST be refused with `That arm is not on this task.` A blank pull name MUST be refused with `Name this pull.` A blank context MUST be refused with `Name the context.` A blank arm MUST be refused with `Name the arm.` A reward other than 1 or 2 MUST be refused with `Name a reward of 1 or 2.` A fifth pull MUST be refused with `This task already has 4 pulls.` A rolled-back pull MUST leave the other pulls and the stored choice as they were.
- **FR-003**: The engineer MUST be able to choose an arm in one context with the linear model or the neural model. The linear score MUST be the first weight times the first mark, plus the second weight times the second mark. The neural score MUST add the pair weight when both marks are 1, and MUST stay the linear score when either mark is 0. The higher score MUST be chosen. Equal scores MUST choose the arm named first. The context, the model, and the chosen arm MUST be stored. A task with no arm MUST be refused with `Name an arm first.` A blank context MUST be refused with `Name the context to choose.` A task with no context MUST be refused with `Name a context first.` A context that is not on this task MUST be refused with `That context is not on this task.` A blank model MUST be refused with `Name the model.` A model other than linear or neural MUST be refused with `Name a linear or neural model.` A rolled-back choice MUST restore the previous choice.
- **FR-004**: The task page MUST show each arm, each context and its marks, each pull, and the choice. It MUST offer Name model arm and Name model context while the task is In Progress, and Record model pull and Choose with model only while the task has an arm and a context. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Arm**: The trimmed name of one choice a model can select.
- **Context**: The trimmed name of one situation and its two marks, each 0 or 1.
- **Pull**: One named reward for one arm in one context. The reward is 1 or 2 and is added to the weights whose marks are 1.
- **Choice**: The stored context, the model name linear or neural, and the arm that model chose.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named arms and contexts, 100% keep the first accepted name and the first accepted marks. A repeated name adds nothing and changes no mark. A third arm and a third context are refused.
- **SC-002**: In a review of pulls, 100% add the reward only to the weights whose marks are 1, and 100% add to the pair weight only when both marks are 1.
- **SC-003**: In a review of choices, 100% of linear choices follow the linear score and 100% of neural choices follow the neural score. Equal scores choose the arm named first.
- **SC-004**: An engineer can see each arm, each context and its marks, each pull, and the choice on the task in one view.

## Assumptions

- Specifications 001 through 048 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, learned forecasts, bandit choices, policy scores, safe probes, and exploration draws stay as they are.
- A mark of 1 means that part of the situation is present. A mark of 0 means it is absent.
- A reward of 2 is a stronger result than a reward of 1. Both are added as whole numbers to the weights whose marks are present.
- A task holds at most 2 arms, 2 contexts, and 4 pulls. One choice is stored. The weights are counted from the pulls when the engineer chooses.
- The linear model uses the two marks separately. The neural model also uses the pair of marks when both are 1.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
