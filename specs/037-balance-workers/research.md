# Research: Work Stealing, Backpressure, and Load Balancing

## Decision: Jobs are their own records

**Decision**: Store workers, jobs, and steals in new tables. Do not assign workflow steps or outbox messages to a worker.

**Rationale**: A workflow step is performed in order, one next step at a time. Giving a later step to another worker would skip the step the engineer is waiting on. A job is pending work the engineer names, so the queues can differ without changing an advance.

**Alternatives considered**: Steal the next workflow step. That would make an idle worker perform a step that is not next, or would block until the busy worker finished.

## Decision: The bound is three, chosen in the command

**Decision**: Refuse a placement when the least-loaded worker already holds three pending jobs. The bound is not a stored column.

**Rationale**: The spec fixes the bound at three. A column would invite a different bound per worker, which the engineer cannot set.

**Alternatives considered**: Stop at three jobs on the task. That would refuse work while another worker was still idle.

## Decision: Ties use the worker stored first

**Decision**: Workers are ordered by the time they were stored. The earliest worker gets a job when the pending counts are equal, and loses a job when the pending counts of the busiest workers are equal. The stolen job is the earliest job that worker still holds.

**Rationale**: The same workers and the same placements then always choose the same worker and the same job. The clock is not required to break the tie.

**Alternatives considered**: Choose by name. Renaming is not part of this feature, and alphabetical order would change the result when a later worker has an earlier name.

## Decision: The steal name and the move commit together

**Decision**: Update the job's worker and insert the steal in one transaction. A Refusal stores neither.

**Rationale**: A rollback must leave the job on the original worker and leave the steal name free. A crash between the two writes would show a move with no steal, or a steal whose job had not moved.

**Alternatives considered**: Record the steal first, then move the job. A failure between them would leave a steal that did not move the job.
