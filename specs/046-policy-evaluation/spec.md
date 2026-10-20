# Feature Specification: Offline Reinforcement Learning and Policy Evaluation

**Feature Branch**: `046-policy-evaluation`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Offline Reinforcement Learning and Policy Evaluation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a logged step (Priority: P1)

The engineer records a logged step on an In Progress task. A logged step is one past decision. It has a name, a state, an action, and a reward of 1 or 2. A reward of 1 is a weak result. A reward of 2 is a strong result. A task holds at most 4 logged steps. The same step name does not store the step again and does not change its state, action, or reward. A blank name is refused. A blank state is refused. A blank action is refused. A reward other than 1 or 2 is refused. A fifth step is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A policy can be scored only after the past decisions are on the task.

**Independent Test**: Record " one " for state " rush ", action " ada ", and reward 1. Record "one" again with reward 2. The task still has one logged step, and it stays reward 1.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer records " one " for state " rush ", action " ada ", and reward 1, **Then** the task lists one as rush, ada, reward 1.
2. **Given** that step, **When** the engineer records "one" again with reward 2, **Then** one stays reward 1.
3. **Given** four logged steps, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 logged steps.` and the fifth is not stored.
4. **Given** a blank name, **When** the engineer records a step, **Then** the engineer is told `Name this step.`
5. **Given** a blank state, **When** the engineer records "note" with reward 1, **Then** the engineer is told `Name the state.` and no step is stored.
6. **Given** a blank action, **When** the engineer records "note" for state "rush" with reward 1, **Then** the engineer is told `Name the action.` and no step is stored.
7. **Given** the reward "3", **When** the engineer records "note", **Then** the engineer is told `Name a reward of 1 or 2.` and no step is stored.
8. **Given** a task that is not In Progress, **When** the engineer records "one", **Then** the engineer is told `The task must be In Progress.` and no step is stored.
9. **Given** a step named "one" on one task, **When** the engineer records "one" on another task, **Then** that other task has its own step.

---

### User Story 2 - Name the action a policy takes in a state (Priority: P2)

The engineer names a policy rule. A rule says which action the policy takes in one state. The state must already appear in a logged step. One state has one rule. Naming the same state and the same action again does not store another rule. Naming the same state with a different action replaces the action. A new logged step or a changed rule removes the stored score. The same step name and the same rule do not remove it.

**Why this priority**: The score needs a stated policy before it can count the logged steps that agree with it.

**Independent Test**: A logged step is rush, ada, reward 1. Name the rule rush takes ada. Name that rule again. The task still has one rule. Name rush takes grace. The stored action becomes grace and the score is removed.

**Acceptance Scenarios**:

1. **Given** a logged step for rush, **When** the engineer names " rush " takes " ada ", **Then** the task lists rush: ada.
2. **Given** that rule, **When** the engineer names it again, **Then** no other rule is stored.
3. **Given** a stored score, **When** the engineer names rush takes grace, **Then** the rule becomes grace and the score is removed.
4. **Given** no logged step, **When** the engineer names a rule, **Then** the engineer is told `Name a logged step first.`
5. **Given** no logged step for state "quiet", **When** the engineer names a rule for quiet, **Then** the engineer is told `That state is not in the log.`
6. **Given** a blank state, **When** the engineer names a rule, **Then** the engineer is told `Name the state for this rule.` A blank action is refused with `Name the action for this rule.`
7. **Given** a rule that is rolled back, **When** the engineer opens the task, **Then** the logged steps and the stored score are unchanged.

---

### User Story 3 - Score the policy on the log (Priority: P3)

The engineer evaluates the policy. The score counts a logged step only when that step's state has a rule and that step's action is the action the rule names. The score stores the total of those rewards and the number of those steps. A logged step whose state has no rule is left out. The score is stored with that evaluation. The task shows each logged step, each rule, and the score. Record logged step is offered while the task is In Progress. Name policy rule is offered only while a logged step exists. Evaluate policy is offered only while a rule exists. The task list stays the list of tasks.

**Why this priority**: The stored score is what the engineer reads after the policy has been checked against the log.

**Independent Test**: One step is rush, ada, reward 1. Two is rush, grace, reward 2. Three is quiet, ada, reward 2. The policy says rush takes grace and quiet takes ada. The score is a total of 4 from 2 steps.

**Acceptance Scenarios**:

1. **Given** those three steps and those two rules, **When** the engineer evaluates the policy, **Then** the score is a total of 4 from 2 steps.
2. **Given** only the rule rush takes ada, **When** the engineer evaluates the policy, **Then** the score is a total of 1 from 1 step.
3. **Given** a rule whose action matches no logged step, **When** the engineer evaluates the policy, **Then** the engineer is told `No logged step matches this policy.` and no score is stored.
4. **Given** no logged step, **When** the engineer evaluates the policy, **Then** the engineer is told `Name a logged step first.`
5. **Given** logged steps and no rule, **When** the engineer evaluates the policy, **Then** the engineer is told `Name a policy rule first.`
6. **Given** a stored score, **When** the engineer records a new logged step, **Then** the score is removed and can be evaluated again.
7. **Given** an evaluation that is rolled back, **When** the engineer opens the task, **Then** the previous score is unchanged.

### Edge Cases

- A name, a state, or an action with surrounding spaces is the same text as the trimmed value.
- A reward is accepted only when the trimmed text is 1 or 2.
- One request records one logged step, names one rule, or evaluates once.
- A task holds at most 4 logged steps. One state has one rule, and that state must appear in the log.
- Opening the task later does not change a stored score. A score changes only when the engineer evaluates again, or when a new logged step or a changed rule removes it.
- Recording a logged step, naming a rule, or evaluating a policy does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to record a logged step on an In Progress task with a name, a state, an action, and a reward of 1 or 2. The first accepted use of that name MUST store the step. The same name MUST NOT store the step again and MUST NOT change its state, action, or reward. A task MUST hold at most 4 logged steps. A blank name MUST be refused with `Name this step.` A blank state MUST be refused with `Name the state.` A blank action MUST be refused with `Name the action.` A reward other than 1 or 2 MUST be refused with `Name a reward of 1 or 2.` A fifth step MUST be refused with `This task already has 4 logged steps.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: The engineer MUST be able to name one action for one state that appears in the log. The same state and the same action MUST NOT store another rule. A different action for that state MUST replace the stored action and MUST remove the stored score. A new logged step MUST remove the stored score. A task with no logged step MUST be refused with `Name a logged step first.` A state that is not in the log MUST be refused with `That state is not in the log.` A blank state MUST be refused with `Name the state for this rule.` A blank action MUST be refused with `Name the action for this rule.` A rolled-back rule MUST leave the logged steps and the stored score as they were.
- **FR-003**: The engineer MUST be able to evaluate the policy. The stored score MUST include a logged step only when its state has a rule and its action is the action that rule names. The score MUST store the total of those rewards and the number of those steps. A task with no logged step MUST be refused with `Name a logged step first.` A task with no rule MUST be refused with `Name a policy rule first.` A policy that matches no logged step MUST be refused with `No logged step matches this policy.` A rolled-back evaluation MUST restore the previous score.
- **FR-004**: The task page MUST show each logged step, each rule, and the score. It MUST offer Record logged step while the task is In Progress, Name policy rule only while a logged step exists, and Evaluate policy only while a rule exists. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Logged step**: The trimmed name of one past decision, its state, its action, and its reward of 1 or 2.
- **Policy rule**: The one action the policy takes in one state from the log.
- **Score**: The stored total reward and the number of logged steps that match the policy.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly recorded steps, 100% keep the state, the action, and the reward the engineer gave. A repeated name adds nothing. A fifth step is refused.
- **SC-002**: In a review of policy rules, 100% keep one action for one state. A repeated rule adds nothing. A different action replaces it.
- **SC-003**: In a review of scores, 100% count only the logged steps whose action matches the policy for that state. The score shows the total reward and the number of those steps.
- **SC-004**: An engineer can see each logged step, each rule, and the score on the task in one view.

## Assumptions

- Specifications 001 through 045 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, optimized activities, learned forecasts, and bandit choices stay as they are.
- A reward of 1 is a weak result. A reward of 2 is a strong result.
- A task holds at most 4 logged steps. One state has one rule. The score uses those rows and stores one total and one count.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
