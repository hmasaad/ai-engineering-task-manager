# Feature Specification: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

**Feature Branch**: `048-thompson-sampling`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name the arms and the contexts (Priority: P1)

The engineer names an arm on an In Progress task. An arm is one choice the engineer can draw. A task holds at most 2 arms. The engineer also names a context. A context is the situation in which a pull is counted. A task holds at most 2 contexts. The same arm name does not store the arm again. The same context name does not store the context again. A blank name is refused. A third arm is refused. A third context is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A draw can compare arms only after the arms and the situations exist.

**Independent Test**: Name " ada " and then "ada" again. The task still has one arm. Name "grace". Name " rush " and then "rush" again. The task still has one context.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada ", **Then** ada is listed as an arm.
2. **Given** ada is already an arm, **When** the engineer names "ada" again, **Then** the task still has one arm.
3. **Given** two arms, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 arms.` and the third is not stored.
4. **Given** a blank arm name, **When** the engineer names an arm, **Then** the engineer is told `Name this arm.`
5. **Given** an In Progress task, **When** the engineer names " rush ", **Then** rush is listed as a context.
6. **Given** two contexts, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 contexts.` and the third is not stored.
7. **Given** a blank context name, **When** the engineer names a context, **Then** the engineer is told `Name this context.`
8. **Given** a task that is not In Progress, **When** the engineer names "ada" or "rush", **Then** the engineer is told `The task must be In Progress.` and nothing is stored.
9. **Given** ada was named on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own arm.

---

### User Story 2 - Record a pull in one context (Priority: P2)

The engineer records a pull. A pull has a name, a context, an arm, and a reward of 1 or 2. A reward of 2 is a win. A reward of 1 is a loss. A task holds at most 4 pulls. The same pull name does not store the pull again and does not change its context, arm, or reward. A pull counts only in the context it names. A new arm, a new context, or a new pull removes the stored draw. The same arm name, the same context name, and the same pull name do not remove it.

**Why this priority**: The next sample can change only after a pull has been recorded in that context.

**Independent Test**: Record " one " for rush, ada, and reward 2. Record "one" again with reward 1. The task still has one pull, and that pull stays a win.

**Acceptance Scenarios**:

1. **Given** arm ada and context rush, **When** the engineer records " one " for " rush ", " ada ", and reward 2, **Then** the task lists one as rush, ada, reward 2.
2. **Given** that pull, **When** the engineer records "one" again with reward 1, **Then** one stays reward 2.
3. **Given** a context that is not on this task, **When** the engineer records a pull in it, **Then** the engineer is told `That context is not on this task.`
4. **Given** an arm that is not on this task, **When** the engineer records a pull of it, **Then** the engineer is told `That arm is not on this task.`
5. **Given** four pulls, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 pulls.`
6. **Given** a blank pull name, **When** the engineer records a pull, **Then** the engineer is told `Name this pull.` A blank context is refused with `Name the context.` A blank arm is refused with `Name the arm.` A reward other than 1 or 2 is refused with `Name a reward of 1 or 2.`
7. **Given** a stored draw, **When** the engineer records a new pull, **Then** the draw is removed.
8. **Given** a pull that is rolled back, **When** the engineer opens the task, **Then** the other pulls and the stored draw are unchanged.

---

### User Story 3 - Draw an arm from three samples (Priority: P3)

The engineer draws an arm in one context. Each arm starts with one imagined win and one imagined loss. Each reward of 2 in that context adds one win. Each reward of 1 in that context adds one loss. Pulls from another context do not count. The middle score is twice the wins, after the imagined win, minus the losses, after the imagined loss. The high score is the middle score plus an extra amount: 4 when the arm has no pulls in that context, 1 when it has one pull, and 0 when it has two or more. The low score is the middle score minus 1. The first draw uses the middle score. The next draw uses the high score. The next draw uses the low score. The draw after that uses the middle score again. The arm with the higher score is chosen. Equal scores choose the arm that was named first. The chosen arm and the sample name are stored with that draw. Opening the task later does not choose again. A new arm, a new context, or a new pull removes the draw, and the next draw starts again at the middle score. The task shows each arm, each context, each pull, and the draw. Name arm and Name context are offered while the task is In Progress. Record pull and Draw arm are offered only while the task has an arm and a context. The task list stays the list of tasks.

**Why this priority**: The stored draw is what the engineer reads after the samples have been taken.

**Independent Test**: Ada is named before grace. Rush is the context. One pull is rush, ada, reward 2. Another is rush, ada, reward 1. Grace has no pull in rush. The middle draw chooses ada. The high draw chooses grace.

**Acceptance Scenarios**:

1. **Given** those two pulls, **When** the engineer draws in rush, **Then** the draw is ada on the middle sample, because ada's middle score is 2 and grace's middle score is 1.
2. **Given** that middle draw, **When** the engineer draws in rush again, **Then** the draw is grace on the high sample, because grace's high score is 5 and ada's high score is 2.
3. **Given** that high draw, **When** the engineer draws in rush again, **Then** the draw is ada on the low sample, because ada's low score is 1 and grace's low score is 0.
4. **Given** ada has two wins in rush and grace has no pull there, **When** the engineer draws the high sample, **Then** both high scores are 5 and the draw stays ada, the arm named first.
5. **Given** grace has a win in quiet and ada has one win and one loss in rush, **When** the engineer draws the middle sample in rush, **Then** the quiet pull does not count and the draw is ada.
6. **Given** no arm, **When** the engineer draws, **Then** the engineer is told `Name an arm first.`
7. **Given** a blank context, **When** the engineer draws, **Then** the engineer is told `Name the context to draw.` A task with no context is refused with `Name a context first.` A context that is not on this task is refused with `That context is not on this task.`
8. **Given** a draw that is rolled back, **When** the engineer opens the task, **Then** the previous draw is unchanged.

### Edge Cases

- A name, a context, or an arm with surrounding spaces is the same text as the trimmed value.
- A reward is accepted only when the trimmed text is 1 or 2.
- One request names one arm, names one context, records one pull, or draws once.
- A task holds at most 2 arms, at most 2 contexts, and at most 4 pulls.
- Pulls in one context do not change the scores in another context.
- When two arms have the same score, the arm that was named first is chosen.
- Opening the task later does not change a stored draw. A draw changes only when the engineer draws again, or when a new arm, a new context, or a new pull removes it.
- After a draw is removed, the next draw uses the middle score.
- Naming an arm, naming a context, recording a pull, or drawing an arm does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an arm and a context on an In Progress task. The first accepted use of a name MUST store that arm or that context. The same name MUST NOT store it again. A task MUST hold at most 2 arms and at most 2 contexts. A blank arm name MUST be refused with `Name this arm.` A third arm MUST be refused with `This task already has 2 arms.` A blank context name MUST be refused with `Name this context.` A third context MUST be refused with `This task already has 2 contexts.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: The engineer MUST be able to record a pull with a name, a context, an arm, and a reward of 1 or 2. A reward of 2 is a win. A reward of 1 is a loss. The same pull name MUST NOT store the pull again and MUST NOT change its context, arm, or reward. A task MUST hold at most 4 pulls. A new arm, a new context, or a new pull MUST remove the stored draw. A context that is not on this task MUST be refused with `That context is not on this task.` An arm that is not on this task MUST be refused with `That arm is not on this task.` A blank pull name MUST be refused with `Name this pull.` A blank context MUST be refused with `Name the context.` A blank arm MUST be refused with `Name the arm.` A reward other than 1 or 2 MUST be refused with `Name a reward of 1 or 2.` A fifth pull MUST be refused with `This task already has 4 pulls.` A rolled-back pull MUST leave the other pulls and the stored draw as they were.
- **FR-003**: The engineer MUST be able to draw an arm in one context. Each arm MUST start with one imagined win and one imagined loss. Wins and losses MUST come only from pulls in that context. The middle score MUST be twice the wins, after the imagined win, minus the losses, after the imagined loss. The high score MUST add 4 when the arm has no pulls in that context, 1 when it has one pull, and 0 when it has two or more. The low score MUST be the middle score minus 1. Draws MUST use the middle score, then the high score, then the low score, and then repeat. The higher score MUST be chosen. Equal scores MUST choose the arm named first. The chosen arm and the sample name MUST be stored. A task with no arm MUST be refused with `Name an arm first.` A blank context MUST be refused with `Name the context to draw.` A task with no context MUST be refused with `Name a context first.` A context that is not on this task MUST be refused with `That context is not on this task.` A rolled-back draw MUST restore the previous draw. After the draw is removed, the next draw MUST use the middle score.
- **FR-004**: The task page MUST show each arm, each context, each pull, and the draw. It MUST offer Name arm and Name context while the task is In Progress, and Record pull and Draw arm only while the task has an arm and a context. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Arm**: The trimmed name of one choice the engineer can draw.
- **Context**: The trimmed name of one situation. Pulls and scores belong to one context.
- **Pull**: One named result for one arm in one context, with a reward of 1 or 2.
- **Draw**: The stored arm and the sample name, middle, high, or low, for one context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named arms and contexts, 100% keep the first accepted name. A repeated name adds nothing. A third arm and a third context are refused.
- **SC-002**: In a review of pulls, 100% keep the reward from the first accepted name. A pull in one context leaves the scores of another context unchanged.
- **SC-003**: In a review of draws, 100% follow the middle, high, and low order, and 100% choose the higher score for that sample. Equal scores choose the arm named first.
- **SC-004**: An engineer can see each arm, each context, each pull, and the draw on the task in one view.

## Assumptions

- Specifications 001 through 047 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, learned forecasts, bandit choices, policy scores, and safe probes stay as they are.
- A reward of 2 is a win. A reward of 1 is a loss. An arm with no pulls in a context still has one imagined win and one imagined loss.
- A task holds at most 2 arms, 2 contexts, and 4 pulls. One draw is stored. The sample order is middle, then high, then low, and then it repeats.
- The three samples stand in for a random draw. The same stored pulls and the same draw count always choose the same arm.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
