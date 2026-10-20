# Feature Specification: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

**Feature Branch**: `045-contextual-bandits`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Contextual Bandits and Reinforcement Learning for Workflow Scheduling."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name the actions and the contexts (Priority: P1)

The engineer names an action on an In Progress task. An action is one way the work can be done. A task holds at most 2 actions. The engineer also names a context. A context is the situation the work is in. A task holds at most 4 contexts. The same action name does not store the action again. The same context name does not store the context again. A blank name is refused. A third action is refused. A fifth context is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A choice can be learned only after the actions and the situations exist.

**Independent Test**: Name " ada " and then "ada" again. The task still has one action. Name "grace". Name " rush " and then "rush" again. The task still has one context.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada ", **Then** ada is listed as an action.
2. **Given** ada is already an action, **When** the engineer names "ada" again, **Then** the task still has one action.
3. **Given** two actions, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 actions.` and the third is not stored.
4. **Given** a blank action name, **When** the engineer names an action, **Then** the engineer is told `Name this action.`
5. **Given** an In Progress task, **When** the engineer names " rush ", **Then** rush is listed as a context.
6. **Given** four contexts, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 contexts.`
7. **Given** a blank context name, **When** the engineer names a context, **Then** the engineer is told `Name this context.`
8. **Given** a task that is not In Progress, **When** the engineer names "ada" or "rush", **Then** the engineer is told `The task must be In Progress.` and nothing is stored.
9. **Given** ada was named on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own action.

---

### User Story 2 - Record a reward for an action in a context (Priority: P2)

The engineer records a trial. A trial has a name, a context, an action, and a reward of 1 or 2. A reward of 1 is a weak result. A reward of 2 is a strong result. A task holds at most 4 trials. The same trial name does not store the trial again and does not change its context, action, or reward. Each new trial updates the total reward of that action in that context. The task lists each pair that has a trial, oldest pair first, with the total reward and the number of trials. A new action, a new context, or a new trial removes the stored choice. The same action name, the same context name, and the same trial name do not remove it.

**Why this priority**: The next choice can improve only after a reward has been recorded.

**Independent Test**: Record " one " for rush and ada with reward 1. Record "one" again with reward 2. The task still has one trial, and it stays reward 1. The pair shows a total of 1 from 1 trial.

**Acceptance Scenarios**:

1. **Given** ada and rush, **When** the engineer records " one " for rush and ada with reward 1, **Then** the task lists one as rush, ada, reward 1, and the pair shows a total of 1 from 1 trial.
2. **Given** that trial, **When** the engineer records "one" again with reward 2, **Then** the trial stays reward 1.
3. **Given** a stored choice, **When** the engineer records a new trial, **Then** the choice is removed and the totals use the new reward.
4. **Given** four trials, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 trials.`
5. **Given** a reward of "3", **When** the engineer records "note", **Then** the engineer is told `Name a reward of 1 or 2.` and no trial is stored.
6. **Given** a context that is not on this task, **When** the engineer records a trial, **Then** the engineer is told `That context is not on this task.` An unknown action is refused with `That action is not on this task.`
7. **Given** a blank trial name, **When** the engineer records a trial, **Then** the engineer is told `Name this trial.` A blank context is refused with `Name the context.` A blank action is refused with `Name the action.`
8. **Given** a trial that is rolled back, **When** the engineer opens the task, **Then** the other trials and the stored choice are unchanged.

---

### User Story 3 - Choose the action for a context (Priority: P3)

The engineer asks for a choice in one context. If an action has no trial in that context, the choice is the earliest-named of those untried actions. When every action has at least one trial in that context, the choice is the action with the higher average reward. An equal average chooses the action that was named first. The choice is stored with that request. Trials in another context do not change it. The task shows each action, each context, each trial, each learned total, and the choice. Name action and Name context are offered while the task is In Progress. Record trial and Choose action are offered only while an action and a context exist. The task list stays the list of tasks.

**Why this priority**: The stored choice is the schedule the engineer reads after the rewards have been learned.

**Independent Test**: Ada is named before grace. Both are untried in rush, so the choice is ada. A trial gives ada reward 1. The next choice is grace. A trial gives grace reward 1. The averages are equal, so the choice is ada. A trial gives grace reward 2. Grace now has a total of 3 from 2 trials, and ada has a total of 1 from 1 trial, so the choice is grace.

**Acceptance Scenarios**:

1. **Given** ada and grace, named in that order, and the context rush, **When** the engineer chooses for rush before any trial, **Then** the choice is ada.
2. **Given** ada has one trial of reward 1 in rush and grace has none, **When** the engineer chooses for rush, **Then** the choice is grace.
3. **Given** ada and grace each have one trial of reward 1 in rush, **When** the engineer chooses for rush, **Then** the choice is ada.
4. **Given** ada has a total of 1 from 1 trial and grace has a total of 3 from 2 trials, **When** the engineer chooses for rush, **Then** the choice is grace.
5. **Given** rush has those trials and quiet has none, **When** the engineer chooses for quiet, **Then** the choice is ada.
6. **Given** no action, **When** the engineer chooses, **Then** the engineer is told `Name an action first.` A task with no context is refused with `Name a context first.` A blank context is refused with `Name the context to choose.` A context that is not on this task is refused with `That context is not on this task.`
7. **Given** a choice that is rolled back, **When** the engineer opens the task, **Then** the previous choice is unchanged.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- A reward is accepted only when the trimmed text is 1 or 2.
- One request names one action, names one context, records one trial, or chooses once.
- A task holds at most 2 actions, 4 contexts, and 4 trials.
- An equal average reward chooses the action named first.
- Opening the task later does not change a stored choice. A choice changes only when the engineer chooses again, or when a new action, a new context, or a new trial removes it.
- Naming an action, naming a context, recording a trial, or choosing does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an action and a context on an In Progress task. The first accepted use of a name MUST store it. The same name MUST NOT store it again. A task MUST hold at most 2 actions and at most 4 contexts. A blank action name MUST be refused with `Name this action.` A blank context name MUST be refused with `Name this context.` A third action MUST be refused with `This task already has 2 actions.` A fifth context MUST be refused with `This task already has 4 contexts.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: The engineer MUST be able to record a trial with a name, a context, an action, and a reward of 1 or 2. The same trial name MUST NOT store the trial again and MUST NOT change its context, action, or reward. A task MUST hold at most 4 trials. Each pair that has a trial MUST show its total reward and its number of trials, oldest pair first. A new action, a new context, or a new trial MUST remove the stored choice. A blank trial name MUST be refused with `Name this trial.` A blank context MUST be refused with `Name the context.` A blank action MUST be refused with `Name the action.` A reward other than 1 or 2 MUST be refused with `Name a reward of 1 or 2.` A context that is not on this task MUST be refused with `That context is not on this task.` An action that is not on this task MUST be refused with `That action is not on this task.` A fifth trial MUST be refused with `This task already has 4 trials.` A rolled-back trial MUST leave the other trials and the stored choice as they were.
- **FR-003**: The engineer MUST be able to choose an action for one context. An action with no trial in that context MUST be chosen before any action that already has a trial, and the earliest-named untried action MUST win. When every action has a trial in that context, the choice MUST be the action with the higher average reward. An equal average MUST choose the action named first. Trials in another context MUST NOT change the choice. The choice MUST be stored with the request. A task with no action MUST be refused with `Name an action first.` A task with no context MUST be refused with `Name a context first.` A blank context MUST be refused with `Name the context to choose.` A context that is not on this task MUST be refused with `That context is not on this task.` A rolled-back choice MUST restore the previous choice.
- **FR-004**: The task page MUST show each action, each context, each trial, each learned total, and the choice. It MUST offer Name action and Name context while the task is In Progress, and Record trial and Choose action only while an action and a context exist. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Action**: The trimmed name of one way the work can be done.
- **Context**: The trimmed name of one situation.
- **Trial**: One named reward of 1 or 2 for one action in one context.
- **Learned value**: The total reward and the number of trials for one action in one context.
- **Choice**: The stored action selected for one context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named actions and contexts, 100% keep the name the engineer gave. A repeated name adds nothing. A third action and a fifth context are refused.
- **SC-002**: In a review of trials, 100% keep the reward the engineer gave. A repeated name adds nothing. Each pair shows the total of its rewards and the number of trials.
- **SC-003**: In a review of choices, 100% try an untried action before using averages. Equal averages choose the action named first. A higher average replaces that action on the next choice.
- **SC-004**: An engineer can see each action, each context, each trial, each learned total, and the choice on the task in one view.

## Assumptions

- Specifications 001 through 044 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, and learned forecasts stay as they are.
- A reward of 1 is a weak result. A reward of 2 is a strong result.
- A task holds at most 2 actions, 4 contexts, and 4 trials. The choice uses those trials and stores one action for one context.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
