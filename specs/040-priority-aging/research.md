# Research: Priority Scheduling, Aging, and Starvation Prevention

## Decision: Ranked work is a named row on one task

**Rationale**: The workspace has one engineer and no sign-in. A piece of work is a named row on one In Progress task, the same way a tenant is a named participant. Another task keeps its own ranks. This feature does not reuse the worker queue, because that queue has no rank.

**Alternatives considered**: Ranking a placed job would mix this feature with the worker bound of three. A global priority list would mix two tasks.

## Decision: The rank is 1, 2, or 3, and the score is rank plus age

**Rationale**: Three ranks are enough to show that 3 beats 1, and that aging can close a gap of 2. The rank is stored on the work when it is ranked. Age starts at 0. The score is computed when a serve is chosen. Rank 3 is the highest rank.

**Alternatives considered**: A free-typed rank would need an open-ended number and a new story for how far aging must climb. Two ranks would not show a middle score.

## Decision: Age is stored on the waiting work and rises by 1 when other work is served

**Rationale**: Constitution Principle V says the clock must not change a choice unless that time is stored with the choice. Age rises by one for every other piece of work that is still waiting when a new serve is stored. The serve and those age changes commit together. A rolled-back serve restores the ages. Work that already has a serve is not waiting and does not age.

**Alternatives considered**: Aging from the wall clock would make the same stored rows serve different work at a later time. Aging every waiting row, including ones ranked together, would leave their relative scores unchanged, which is the intended priority rule until a new higher rank arrives at age 0.

## Decision: The highest score is served, and the earliest work wins a tie

**Rationale**: That is the scheduling rule in the spec. Storage order is the tie. Rank-1 work aged by 2 has score 3, the same as new rank-3 work at age 0. The earlier work is served, so a stream of new rank-3 work cannot leave that rank-1 work waiting forever.

**Alternatives considered**: Always serving the newest high rank would be the starvation this feature prevents. Random choice among equal scores would break replay.

## Decision: A serve does not advance the workflow or the tenant schedule

**Rationale**: Specifications 001 through 039 already own workflow steps, workers, and tenant turns. A serve records which ranked work was taken. It does not read a file, place a job, admit a tenant, grant a turn, or change the task status.

**Alternatives considered**: Serving by calling workflow advance would mix this feature with the step list and could fail for a task that has no steps.
