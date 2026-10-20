# Research: Deadline-Aware Scheduling and Service-Level Objectives (SLOs)

## Decision: An objective is a named row with a deadline on one task

**Rationale**: The workspace has one engineer and no sign-in. An objective is a named promise on one In Progress task, the same way ranked work is a named row. Another task keeps its own deadlines. This feature does not reuse the priority schedule, because that schedule has ranks and ages and no deadline.

**Alternatives considered**: Attaching a deadline to ranked work would rewrite the priority feature. A global objective list would mix two tasks.

## Decision: The deadline is a real UTC time in one written form

**Rationale**: The engineer types the deadline, and the same text must sort in time order. The accepted form is `2026-12-01T00:00:00Z`. Any other text is refused with `Name a deadline.` The deadline is stored as that text when the objective is set. A repeated name keeps the first deadline.

**Alternatives considered**: A deadline of "in two hours" would depend on the clock at a later read. A free sentence would not tell the schedule which objective is earlier.

## Decision: The service stores met or missed from the time recorded with that service

**Rationale**: Constitution Principle V says the clock must not change a choice unless that time is stored with the choice. The service records its own time. Met means that time is at or before the deadline. Missed means that time is after the deadline. Opening the task later does not recompute the result. A rolled-back service removes the row, so the objective is waiting again.

**Alternatives considered**: Comparing the deadline with the clock each time the page opens would change a missed service into a met service, or the reverse, without a new service. Leaving the result implied by the absence of a row would hide whether the deadline was kept.

## Decision: The earliest deadline is served, and the earliest objective wins a tie

**Rationale**: That is the deadline rule in the spec. The written deadline sorts in time order, so the smallest deadline is the earliest. Storage order is the tie. A served objective is not waiting and is not chosen again. When every objective has been served, the next service is refused and no row is written.

**Alternatives considered**: Serving the newest objective would ignore the deadline. Random choice among equal deadlines would break replay.

## Decision: A service does not advance the workflow or the priority schedule

**Rationale**: Specifications 001 through 040 already own workflow steps, workers, tenants, and priority ranks. A service records which objective was taken and whether the deadline was met. It does not read a file, rank work, or change the task status.

**Alternatives considered**: Serving an objective by calling workflow advance would mix this feature with the step list and could fail for a task that has no steps.
