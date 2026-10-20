# Research: Workflow Scheduling with Dependencies, Critical Paths, and Deadline Propagation

## Decision: A schedule step is a named row, separate from a workflow action

**Rationale**: Specifications 001 through 041 already own workflow actions, objectives, and priority ranks. A schedule step is a named length on one In Progress task. Another task keeps its own steps. The critical path is computed from these steps and their links.

**Alternatives considered**: Attaching a length to a workflow action would rewrite the workflow feature and would fail for a task that has no actions. Sharing one global chain would mix two tasks.

## Decision: A length is 1 or 2 days, and a step follows one earlier step

**Rationale**: Two lengths are enough to show a longer chain and a tie. One predecessor keeps every schedule as chains, so the critical path is one chain a person can read. A second predecessor, a self-link, and a cycle are refused and store nothing.

**Alternatives considered**: A free-typed length would need an open-ended number. Several predecessors would make the critical path a graph rather than one chain.

## Decision: The critical path is the chain with the greatest total length

**Rationale**: That is the scheduling rule in the spec. The total is the sum of the lengths from the first step to the last. Equal totals choose the chain whose first step was stored first. The order on the page is that chain from first to last.

**Alternatives considered**: Choosing the chain with the most steps would ignore a length of 2. Random choice among equal lengths would break replay.

## Decision: Latest times are counted back from one stored deadline

**Rationale**: Constitution Principle V says the clock must not change a result unless that time is stored. The deadline is stored as the text the engineer gave. The last step of every chain finishes at that deadline. Each earlier step finishes earlier by one day for each day of length in the steps after it. A new deadline replaces the stored deadline, and the latest times follow it. Opening the task later does not change the deadline.

**Alternatives considered**: A separate deadline on every step would let two ends of one chain disagree. Recomputing the deadline from the wall clock would change a latest time without a new command.

## Decision: These commands do not advance the workflow

**Rationale**: A step, a link, and a deadline are records on this schedule. They do not read a file, set an objective, rank work, or change the task status.

**Alternatives considered**: Creating a workflow action for each schedule step would mix this feature with file reads and folder creation.
