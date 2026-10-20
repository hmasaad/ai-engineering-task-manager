# Research: Autoscaling and Queue-Based Capacity Planning

## Decision: Waiting work is not a placed job

**Decision**: Store a queued name in `work_queue` until a scale assigns it. Direct placement still refuses when every active worker holds three jobs.

**Rationale**: Specification 037 refuses that placement and does not store the name. A waiting queue can grow past the current workers without changing that refusal. The capacity reading can then ask for another worker.

**Alternatives considered**: Treat a refused placement as waiting work. That would store a name specification 037 leaves free, and the same request would both refuse and queue.

## Decision: One scale does one thing, and spare room comes first

**Decision**: If any active worker holds fewer than three jobs and work is waiting, assign the oldest waiting item to the least-loaded worker. Otherwise, if the workers needed are more than the active workers, add one worker named by the scale and assign the oldest waiting item to that worker. Otherwise, if the workers needed are fewer, release the newest idle worker. Equal job counts choose the worker stored first.

**Rationale**: Adding a worker while another has room would grow the roster without using the capacity already recorded. One change per request keeps a rolled-back scale to a single worker or a single assignment.

**Alternatives considered**: Add every missing worker in one request. A rollback would have to undo several workers, and the engineer could not see which name added which worker.

## Decision: A released worker stays on the record

**Decision**: Store the release in `work_release`. Do not delete the worker row.

**Rationale**: A steal may already name that worker. Deleting the row would remove that history. Placement, stealing, and the active count ignore a released worker.

**Alternatives considered**: Delete the worker. The steal record would lose a worker it still names.

## Decision: Workers needed is the ceiling of the work divided by three

**Decision**: Add the waiting items and the held jobs. Zero needs zero workers. Any larger total needs one worker for every three items, rounded up.

**Rationale**: That is the same bound a direct placement already uses. The plan and the scale then agree on when the queue is past capacity.

**Alternatives considered**: Keep at least one worker whenever the task is In Progress. An empty queue would never release the last idle worker.
