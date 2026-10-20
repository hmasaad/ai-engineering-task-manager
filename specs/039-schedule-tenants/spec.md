# Feature Specification: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

**Feature Branch**: `039-schedule-tenants`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admit a tenant under a quota (Priority: P1)

The engineer names a tenant on an In Progress task. That tenant may take two turns of the shared workflow schedule. The same tenant name does not admit a second tenant. A blank name is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A fair schedule can be checked only after the tenants and their quota exist.

**Independent Test**: Admit " ada " and "grace". The task lists ada and grace, each at 0 of 2. Admit "ada" again. The task still has two tenants.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer admits " ada ", **Then** ada is listed at 0 of 2.
2. **Given** ada is already admitted, **When** the engineer admits "ada" again, **Then** no other tenant is stored.
3. **Given** a blank name, **When** the engineer admits a tenant, **Then** the engineer is told `Name this tenant.`
4. **Given** a task that is not In Progress, **When** the engineer admits "ada", **Then** the engineer is told `The task must be In Progress.` and no tenant is stored.
5. **Given** ada was admitted on one task, **When** the engineer admits "ada" on another task, **Then** that other task has its own tenant.

---

### User Story 2 - Grant the next turn to the least-used tenant (Priority: P2)

The engineer names a turn. The turn is granted to the admitted tenant who has used the fewest turns and is still under the quota of two. The tenant admitted first wins a tie. The same turn name does not grant another turn. A schedule with no tenant is refused. A rolled-back turn leaves the tenants as they were.

**Why this priority**: Fairness is the reason the tenants share one schedule.

**Independent Test**: Admit ada, then grace. Grant "one", "two", "three", and "four". Ada receives "one" and "three". Grace receives "two" and "four". Grant "one" again. The schedule still has those four turns.

**Acceptance Scenarios**:

1. **Given** ada and grace have used no turns, **When** the engineer grants "one", **Then** ada receives it and is at 1 of 2.
2. **Given** ada has used one turn and grace has used none, **When** the engineer grants "two", **Then** grace receives it.
3. **Given** ada and grace have each used one turn, **When** the engineer grants "three", **Then** ada receives it.
4. **Given** a turn named "one", **When** the engineer grants "one" again, **Then** no other turn is stored.
5. **Given** no tenant has been admitted, **When** the engineer grants "one", **Then** the engineer is told `Name a tenant first.`
6. **Given** a turn that is rolled back, **When** the engineer opens the task, **Then** that tenant is still at 0 of 2 and that turn name can still be used.

---

### User Story 3 - Stop a tenant who has used the quota (Priority: P3)

A tenant who has used two turns does not receive another turn while another tenant still has room. When every tenant has used two turns, the engineer is told `Every tenant is at its quota.` A blank turn name is refused with `Name this turn.` The task shows each tenant, the used count, the quota, and each granted turn. The task list stays the list of tasks.

**Why this priority**: The quota is what keeps one tenant from taking the whole schedule, and the page is where the engineer sees that.

**Independent Test**: After ada and grace have each received two turns, grant "five". The engineer is told `Every tenant is at its quota.` The page shows ada at 2 of 2, grace at 2 of 2, and the four granted turns.

**Acceptance Scenarios**:

1. **Given** ada has used two turns and grace has used one, **When** the engineer grants "next", **Then** grace receives it.
2. **Given** ada and grace have each used two turns, **When** the engineer grants "five", **Then** the engineer is told `Every tenant is at its quota.`
3. **Given** a blank turn name, **When** the engineer grants a turn, **Then** the engineer is told `Name this turn.`
4. **Given** admitted tenants and granted turns, **When** the engineer opens the task, **Then** the page shows each tenant as used of 2 and each turn as granted to that tenant. Grant turn is offered only while a tenant still has room.
5. **Given** a grant on one task, **When** the engineer opens another task, **Then** that other task does not list the first task's turns.

### Edge Cases

- A name with surrounding spaces is the same name as the trimmed text.
- One request admits one tenant or grants one turn.
- Each tenant may take two turns. Zero turns used is shown as 0 of 2.
- Equal used counts choose the tenant admitted first.
- Admitting a tenant or granting a turn does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a tenant on an In Progress task. The first accepted use of that name MUST admit the tenant with a quota of two turns and zero turns used. The same name MUST NOT admit another tenant. A blank name MUST be refused with `Name this tenant.` A task that is not In Progress MUST be refused with `The task must be In Progress.`
- **FR-002**: The engineer MUST be able to name a turn. The first accepted use of that name MUST grant that turn to the admitted tenant who has used the fewest turns and is still under the quota of two. The tenant admitted first MUST win a tie. The same name MUST NOT grant another turn. A blank name MUST be refused with `Name this turn.` A schedule with no tenant MUST be refused with `Name a tenant first.`
- **FR-003**: A tenant who has used two turns MUST NOT receive another turn while another tenant is under the quota. When every admitted tenant has used two turns, the grant MUST be refused with `Every tenant is at its quota.` A rolled-back turn MUST leave the tenants and the turns as they were. The same names on another task MUST apply only to that other task.
- **FR-004**: Admitting a tenant or granting a turn MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, or change the task status. The task page MUST show each tenant, the turns used, the quota of two, and each granted turn. It MUST offer Admit tenant while the task is In Progress, and Grant turn only while a tenant still has room. The task list MUST stay the list of tasks.

### Key Entities

- **Tenant**: The trimmed name of one participant on the task. The tenant may take two turns.
- **Turn**: The trimmed name of one granted place on the shared schedule. It records which tenant received it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of admitted tenants, 100% start at 0 of 2, and a repeated name adds no tenant.
- **SC-002**: In a review of granted turns, 100% go to a tenant who has used the fewest turns and is under the quota of two. Equal counts choose the tenant admitted first.
- **SC-003**: In a review of grants made after every tenant has used two turns, 100% are refused and leave the schedule unchanged. In a review of rolled-back turns, 100% leave the tenant at the count it had before.
- **SC-004**: An engineer can see each tenant, the turns used, the quota, and each granted turn on the task in one view.

## Assumptions

- Specifications 001 through 038 are not rewritten. Workers, the waiting queue, and the workflow steps stay as they are.
- One tenant may take two turns. That quota is the same for every tenant.
- One grant gives one turn to one tenant.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
