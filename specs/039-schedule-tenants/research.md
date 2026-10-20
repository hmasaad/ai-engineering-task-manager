# Research: Multi-Tenant Workflow Scheduling, Fairness, and Resource Quotas

## Decision: A tenant is a named row, not a user account

**Rationale**: The workspace has one engineer and no sign-in. A tenant is a named participant on one In Progress task, the same way a worker is a named holder of jobs. Another task keeps its own tenants.

**Alternatives considered**: A login per tenant would add an account model this application does not have. Sharing one global tenant list would mix two tasks.

## Decision: The quota is two turns for every tenant

**Rationale**: The spec needs one checkable bound. Two turns is small enough to exhaust in a test and large enough to show fairness across two tenants. The quota is stored on the tenant row when the tenant is admitted.

**Alternatives considered**: A quota typed on each admission would need a second number and a new refusal for a bad number. A shared quota that changes later would rewrite tenants already admitted.

## Decision: Turns used are the granted turns for that tenant

**Rationale**: A rolled-back grant removes the turn row, so the used count returns with it. The count is not a separate column that can drift from the turns.

**Alternatives considered**: Storing a used counter on the tenant would need a second write and a second rollback path.

## Decision: The next turn goes to the fewest used turns, then the earliest tenant

**Rationale**: That is the fairness rule in the spec. Storage order is the tie. A tenant at two turns is skipped while another tenant is under the quota. When every tenant is at two, the grant is refused and no row is written.

**Alternatives considered**: Strict rotation by admission order would ignore a tenant who was admitted later with zero turns. Random choice would break replay.

## Decision: The schedule does not advance the workflow

**Rationale**: Specifications 001 through 038 already own workflow steps, workers, and the waiting queue. A turn is a place on this schedule. It does not read a file, place a job, or change the task status.

**Alternatives considered**: Granting a turn by calling workflow advance would mix this feature with the step list and could fail for a task that has no steps.
