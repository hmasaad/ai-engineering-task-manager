# Feature Specification: Safe Exploration, Causal Inference, and Counterfactual Evaluation

**Feature Branch**: `047-safe-exploration`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Safe Exploration, Causal Inference, and Counterfactual Evaluation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name an action and its risk (Priority: P1)

The engineer names an action on an In Progress task and gives it a risk of 1 or 2. A risk of 1 means the action is safe to explore. A risk of 2 means the action is not safe to explore. A task holds at most 2 actions. The same action name does not store the action again and does not change its risk. A blank name is refused. A risk other than 1 or 2 is refused. A third action is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A probe can be allowed or refused only after each action has a risk.

**Independent Test**: Name " ada " with risk 1 and "grace" with risk 2. Name "ada" again with risk 2. Ada stays at risk 1.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada " with risk 1, **Then** ada is listed at risk 1.
2. **Given** ada is already risk 1, **When** the engineer names "ada" with risk 2, **Then** ada stays at risk 1.
3. **Given** two actions, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 actions.` and the third is not stored.
4. **Given** a blank name, **When** the engineer names an action, **Then** the engineer is told `Name this action.`
5. **Given** the risk "3", **When** the engineer names "note", **Then** the engineer is told `Name a risk of 1 or 2.` and no action is stored.
6. **Given** a task that is not In Progress, **When** the engineer names "ada" with risk 1, **Then** the engineer is told `The task must be In Progress.` and no action is stored.
7. **Given** ada was named on one task, **When** the engineer names "ada" with risk 2 on another task, **Then** that other task has its own action.

---

### User Story 2 - Explore only a safe action (Priority: P2)

The engineer records a probe. A probe is one exploration of an action in a state, with a reward of 1 or 2. A reward of 1 is a weak result. A reward of 2 is a strong result. A probe is allowed only when that action's risk is 1. A task holds at most 4 probes. The same probe name does not store the probe again and does not change its state, action, or reward. A new action or a new probe removes the stored effect. The same action name and the same probe name do not remove it.

**Why this priority**: The comparison can use only the probes that were safe to record.

**Independent Test**: Ada has risk 1 and grace has risk 2. Record " one " for state " rush ", action ada, and reward 1. Record "two" for grace. The engineer is told `That action is not safe to explore.` and the task still has one probe.

**Acceptance Scenarios**:

1. **Given** ada at risk 1, **When** the engineer records " one " for state " rush ", action " ada ", and reward 1, **Then** the task lists one as rush, ada, reward 1.
2. **Given** that probe, **When** the engineer records "one" again with reward 2, **Then** one stays reward 1.
3. **Given** grace at risk 2, **When** the engineer records a probe of grace, **Then** the engineer is told `That action is not safe to explore.` and no probe is stored.
4. **Given** an action that is not on this task, **When** the engineer records a probe of it, **Then** the engineer is told `That action is not on this task.`
5. **Given** four probes, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 probes.`
6. **Given** a blank probe name, **When** the engineer records a probe, **Then** the engineer is told `Name this probe.` A blank state is refused with `Name the state.` A blank action is refused with `Name the action.` A reward other than 1 or 2 is refused with `Name a reward of 1 or 2.`
7. **Given** a stored effect, **When** the engineer records a new probe, **Then** the effect is removed.
8. **Given** a probe that is rolled back, **When** the engineer opens the task, **Then** the other probes and the stored effect are unchanged.

---

### User Story 3 - Compare two actions in the same state (Priority: P3)

The engineer compares one action with the action it replaces, in one state. The effect is the reward of the named action minus the reward of the action it replaces. Each reward is the reward of the earliest probe of that action in that state. The state stays the same, so the effect is the change that comes from the action. The effect is stored with that comparison. An action cannot replace itself. The comparison needs a probe of each action in that state. The task shows each action, its risk, each probe, and the effect. Name action is offered while the task is In Progress. Record probe is offered only while a safe action exists. Compare actions is offered only while two probes exist. The task list stays the list of tasks.

**Why this priority**: The stored effect is what the engineer reads after the safe probes are compared.

**Independent Test**: Ada and grace are both risk 1. One probe is rush, ada, reward 1. Another is rush, grace, reward 2. The effect of grace instead of ada in rush is 1. The effect of ada instead of grace in rush is -1.

**Acceptance Scenarios**:

1. **Given** those two probes, **When** the engineer compares grace instead of ada in rush, **Then** the effect is 1.
2. **Given** those two probes, **When** the engineer compares ada instead of grace in rush, **Then** the effect is -1.
3. **Given** two probes with the same reward, **When** the engineer compares them, **Then** the effect is 0.
4. **Given** an action compared with itself, **When** the engineer compares it, **Then** the engineer is told `An action cannot replace itself.`
5. **Given** a state that does not have a probe of both actions, **When** the engineer compares them, **Then** the engineer is told `That comparison needs both actions in this state.`
6. **Given** no probe, **When** the engineer compares actions, **Then** the engineer is told `Name a probe first.` A blank state is refused with `Name the state to compare.` A blank action is refused with `Name the action.` A blank replaced action is refused with `Name the action it replaces.`
7. **Given** a comparison that is rolled back, **When** the engineer opens the task, **Then** the previous effect is unchanged.

### Edge Cases

- A name, a state, or an action with surrounding spaces is the same text as the trimmed value.
- A risk is accepted only when the trimmed text is 1 or 2.
- A reward is accepted only when the trimmed text is 1 or 2.
- One request names one action, records one probe, or compares once.
- A task holds at most 2 actions and at most 4 probes.
- When an action has more than one probe in a state, the earliest probe is the one that counts.
- Opening the task later does not change a stored effect. An effect changes only when the engineer compares again, or when a new action or a new probe removes it.
- Naming an action, recording a probe, or comparing actions does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an action on an In Progress task and give it a risk of 1 or 2. The first accepted use of that name MUST store the action at that risk. The same name MUST NOT store the action again and MUST NOT change its risk. A task MUST hold at most 2 actions. A blank name MUST be refused with `Name this action.` A risk other than 1 or 2 MUST be refused with `Name a risk of 1 or 2.` A third action MUST be refused with `This task already has 2 actions.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: The engineer MUST be able to record a probe of a risk-1 action with a name, a state, an action, and a reward of 1 or 2. The same probe name MUST NOT store the probe again and MUST NOT change its state, action, or reward. A task MUST hold at most 4 probes. A new action or a new probe MUST remove the stored effect. A risk-2 action MUST be refused with `That action is not safe to explore.` An action that is not on this task MUST be refused with `That action is not on this task.` A blank probe name MUST be refused with `Name this probe.` A blank state MUST be refused with `Name the state.` A blank action MUST be refused with `Name the action.` A reward other than 1 or 2 MUST be refused with `Name a reward of 1 or 2.` A fifth probe MUST be refused with `This task already has 4 probes.` A rolled-back probe MUST leave the other probes and the stored effect as they were.
- **FR-003**: The engineer MUST be able to compare one action with the action it replaces in one state. The stored effect MUST be the reward of the earliest probe of the named action in that state minus the reward of the earliest probe of the replaced action in that state. An action compared with itself MUST be refused with `An action cannot replace itself.` A comparison that lacks a probe of either action in that state MUST be refused with `That comparison needs both actions in this state.` A task with no probe MUST be refused with `Name a probe first.` A blank state MUST be refused with `Name the state to compare.` A blank action MUST be refused with `Name the action.` A blank replaced action MUST be refused with `Name the action it replaces.` A rolled-back comparison MUST restore the previous effect.
- **FR-004**: The task page MUST show each action, its risk, each probe, and the effect. It MUST offer Name action while the task is In Progress, Record probe only while a safe action exists, and Compare actions only while two probes exist. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Action**: The trimmed name of one action and its risk of 1 or 2.
- **Probe**: One named exploration of a safe action in one state, with a reward of 1 or 2.
- **Effect**: The stored change in reward when one action replaces another in the same state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named actions, 100% keep the risk the engineer gave. A repeated name adds no action and changes no risk. A third action is refused.
- **SC-002**: In a review of probes, 100% are for a risk-1 action. A risk-2 action is refused and stores nothing. A repeated name adds nothing.
- **SC-003**: In a review of comparisons, 100% equal the earliest reward of the named action minus the earliest reward of the replaced action in that same state.
- **SC-004**: An engineer can see each action, its risk, each probe, and the effect on the task in one view.

## Assumptions

- Specifications 001 through 046 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, learned forecasts, bandit choices, and policy scores stay as they are.
- A risk of 1 is safe to explore. A risk of 2 is not safe to explore.
- A reward of 1 is a weak result. A reward of 2 is a strong result.
- A task holds at most 2 actions and at most 4 probes. The comparison uses the earliest probe of each action in one state and stores one effect.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
