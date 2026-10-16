# Research: Workflow Replay and Deterministic Execution

## Decision: The report is derived, not stored

**Rationale**: The current version, the step states, the file reads, and the folder changes are already stored. A report computed from those rows is the same every time those rows are the same. Storing a second copy could disagree with the rows. Replay writes nothing, so the clock and the event replay stay as they were.

**Alternatives considered**: A new table of replay runs. Rejected because a second stored copy is another record that would have to be kept identical to the steps.

## Decision: A completed step matches one stored effect

**Rationale**: A completed read matches the next stored file read of that path. A completed folder matches the change already linked to that step. If the effect is not stored, the report stops with `Stopped at {title}: the stored effect is missing.` and does not read the file or create the folder.

**Alternatives considered**: Reading the file from disk to confirm it. Rejected because that would perform the step again. Calling the model. Rejected because the model is not a workflow step, and a new reply would not be deterministic.

## Decision: The walk stops at the first unfinished step

**Rationale**: Pending, waiting, and failed steps do not have a completed effect to match. The report includes the completed prefix and the existing stop sentence. Later steps are omitted. A waiting change is not approved. A running step refuses the whole report with `Recover the interrupted step first.`

**Alternatives considered**: Skipping a pending step and continuing. Rejected because the current version is ordered, and a later step has not become the next piece of work.

## Decision: The current version is the only walk

**Rationale**: Advance already uses the current version. A pending step left on a superseded version is not part of that walk. A workflow with steps and no stored version is still version 1, matching the version already shown on the task.

**Alternatives considered**: Replaying every version. Rejected because the superseded version is the historical plan, and the current version is the one the task is on.
