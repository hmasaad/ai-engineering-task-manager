# Feature Specification: Adaptive Resource Allocation for Workflow and Agent Optimization

**Feature Branch**: `052-adaptive-allocation`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Adaptive Resource Allocation for Workflow and Agent Optimization"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name an agent (Priority: P1)

The engineer names an agent on an In Progress task. An agent is one worker that can receive part of the workflow budget. A task holds at most 4 agents. The same agent name does not store the agent again. A blank name is refused. A fifth agent is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A yield and an allocation can name an agent only after the agents exist.

**Independent Test**: Name " ada ", then name "ada" again. The task still has one agent, ada.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada ", **Then** ada is listed.
2. **Given** ada is already named, **When** the engineer names "ada" again, **Then** the task still has one agent.
3. **Given** four agents, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 agents.` and the fifth is not stored.
4. **Given** a blank name, **When** the engineer names an agent, **Then** the engineer is told `Name this agent.`
5. **Given** a task that is not In Progress, **When** the engineer names "ada", **Then** the engineer is told `The task must be In Progress.` and no agent is stored.
6. **Given** ada was named on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own agent.

---

### User Story 2 - Record a yield (Priority: P2)

The engineer records a yield for an agent. A yield has a name, an agent, and a value of 1 or 2. A higher value means the agent returned more from the workflow budget. A task holds at most 4 yields. An agent has at most one yield. The same yield name does not store the yield again and does not change its agent or value. A new agent or a new yield removes the stored shares. The same agent name and the same yield name do not remove them.

**Why this priority**: The shares are counted from these yields.

**Independent Test**: Record " one " for ada with value 2. Record "one" again with value 1. The task still has one yield, and that yield stays value 2.

**Acceptance Scenarios**:

1. **Given** agent ada, **When** the engineer records " one " for " ada " with value 2, **Then** the task lists one as ada, yield 2.
2. **Given** that yield, **When** the engineer records "one" again with value 1, **Then** one stays value 2.
3. **Given** an agent that is not on this task, **When** the engineer records a yield for it, **Then** the engineer is told `That agent is not on this task.`
4. **Given** ada already has a yield, **When** the engineer records another yield for ada, **Then** the engineer is told `That agent already has a yield.`
5. **Given** four yields, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 yields.`
6. **Given** a blank yield name, **When** the engineer records a yield, **Then** the engineer is told `Name this yield.` A blank agent is refused with `Name the agent.` A value other than 1 or 2 is refused with `Name a yield of 1 or 2.`
7. **Given** stored shares, **When** the engineer records another yield for an agent who already has one, **Then** the engineer is told `That agent already has a yield.` and the shares stay.
8. **Given** a yield that is rolled back, **When** the engineer opens the task, **Then** the other yields and the stored shares are unchanged.

---

### User Story 3 - Allocate the workflow budget (Priority: P3)

The engineer allocates the workflow budget. The budget is a pool of 4 units. Every agent must already have a yield. The 4 units are given one at a time. The next unit goes to the agent with the strongest claim to one more unit. An agent's claim is its yield compared with one more than the units it already holds in this allocation. The comparison is a whole-number product: each agent's yield is multiplied by one more than the other agent's current units. The larger product wins. An equal product keeps the agent stored first. Every agent is listed with the units it received, including 0. The shares are stored with that allocation. Opening the task later does not allocate again. The task shows each agent, each yield, and each share. Name agent is offered while the task is In Progress. Record yield is offered only while an agent exists. Allocate the pool is offered only while a yield exists. The task list stays the list of tasks.

**Why this priority**: The stored shares are what the engineer reads after the yields have been compared.

**Independent Test**: Ada is named before grace. Ada's yield is 2 and grace's yield is 1. Ada receives 3 units and grace receives 1.

**Acceptance Scenarios**:

1. **Given** those two yields, **When** the engineer allocates the pool, **Then** ada has 3 units and grace has 1.
2. **Given** ada and grace both have yield 2, **When** the engineer allocates the pool, **Then** ada has 2 units and grace has 2.
3. **Given** only ada, with yield 1, **When** the engineer allocates the pool, **Then** ada has 4 units.
4. **Given** ada yield 2, grace yield 1, mina yield 1, and nora yield 1, named in that order, **When** the engineer allocates the pool, **Then** ada has 2, grace has 1, mina has 1, and nora has 0.
5. **Given** no agent, **When** the engineer allocates the pool, **Then** the engineer is told `Name an agent first.`
6. **Given** an agent with no yield, **When** the engineer allocates the pool, **Then** the engineer is told `Record a yield for every agent first.`
7. **Given** an allocation that is rolled back, **When** the engineer opens the task, **Then** the previous shares are unchanged.

### Edge Cases

- A name or an agent with surrounding spaces is the same text as the trimmed value.
- A yield value is accepted only when the trimmed text is 1 or 2.
- One request names one agent, records one yield, or allocates the pool once.
- A task holds at most 4 agents and at most 4 yields. An agent has at most one yield. The pool is always 4 units.
- When four yields already exist, another yield is refused with `This task already has 4 yields.` even when that agent already has a yield.
- The four shares always add up to 4. An agent can receive 0.
- When two products are equal, the agent stored first receives the unit.
- Opening the task later does not change stored shares. Shares change only when the engineer allocates again, or when a new agent or a new yield removes them.
- Naming an agent, recording a yield, or allocating the pool does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name an agent on an In Progress task. The first accepted use of that name MUST store the agent. The same name MUST NOT store the agent again. A task MUST hold at most 4 agents. A blank name MUST be refused with `Name this agent.` A fifth agent MUST be refused with `This task already has 4 agents.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task. A new agent MUST remove the stored shares. The same agent name MUST NOT remove them.
- **FR-002**: The engineer MUST be able to record a yield with a name, an agent, and a value of 1 or 2. The same yield name MUST NOT store the yield again and MUST NOT change its fields. An agent MUST have at most one yield. A task MUST hold at most 4 yields. An agent that is not on this task MUST be refused with `That agent is not on this task.` A second yield for the same agent MUST be refused with `That agent already has a yield.` A blank yield name MUST be refused with `Name this yield.` A blank agent MUST be refused with `Name the agent.` A value other than 1 or 2 MUST be refused with `Name a yield of 1 or 2.` A fifth yield MUST be refused with `This task already has 4 yields.` A new yield MUST remove the stored shares. A rolled-back yield MUST leave the other yields and the stored shares as they were.
- **FR-003**: The engineer MUST be able to allocate a pool of 4 units. Every agent MUST already have a yield. Each unit MUST go to the agent with the larger whole-number product. That product is the agent's yield multiplied by one more than the other agent's units already given in this allocation. An equal product MUST give the unit to the agent stored first. Every agent MUST be stored with the units it received, including 0. The shares MUST add up to 4. A task with no agent MUST be refused with `Name an agent first.` An agent with no yield MUST be refused with `Record a yield for every agent first.` A rolled-back allocation MUST restore the previous shares.
- **FR-004**: The task page MUST show each agent, each yield, and each share. It MUST offer Name agent while the task is In Progress, Record yield only while an agent exists, and Allocate the pool only while a yield exists. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Agent**: The trimmed name of one worker that can receive workflow budget.
- **Yield**: One named result for one agent, with a value of 1 or 2.
- **Share**: The stored number of budget units given to one agent. The shares for one allocation add up to 4.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named agents, 100% keep the first accepted name. A repeated name adds no agent. A fifth agent is refused.
- **SC-002**: In a review of yields, 100% keep the value from the first accepted name. A second yield for the same agent is refused.
- **SC-003**: In a review of allocations, 100% of share lists add up to 4, and 100% give each unit to the agent with the larger product. Equal products choose the agent stored first.
- **SC-004**: An engineer can see each agent, each yield, and each share on the task in one view.

## Assumptions

- Specifications 001 through 051 are not rewritten. Workflow actions, workers, schedule turns, priority ranks, objectives, schedule steps, optimized activities, learned forecasts, bandit choices, policy scores, safe probes, exploration draws, model choices, search recommendations, and fidelity halvings stay as they are.
- The pool is the workflow's shared budget. It is always 4 units. A higher yield is a better return. The same agents and the same yields always produce the same shares.
- A task holds at most 4 agents and 4 yields. One allocation is stored. The shares are counted when the engineer allocates the pool.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
