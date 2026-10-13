# Research: Verification Evidence and Trace Gaps

## Decision: Store the method and the test-run identifier in a new table

**Rationale**: `acceptance_criterion` is created with `CREATE TABLE IF NOT EXISTS`, so a later start cannot add columns to an existing workspace file. A row in `criterion_evidence` can be inserted and deleted with the current verification. `clear_verification` already runs for unverify, for an edited criterion, and for a changed requirement statement or kind, so the delete belongs there.

**Alternatives considered**: Adding columns to `acceptance_criterion` leaves existing workspace files without those columns. Putting the method on a requirement run would record it for a check, not for the criterion the engineer verified.

## Decision: The engineer types both values

**Rationale**: The method is a name such as inspection or test. The test-run identifier is an identifier such as `local-1`. Neither is chosen by the product, and neither is looked up against a stored test run or a requirement run. Surrounding spaces are removed. A blank value is refused before anything is written.

**Alternatives considered**: Requiring the identifier to match a test that was already run would block an inspection, which has no test run. Copying the latest requirement run would hide the identifier the engineer meant for this criterion.

## Decision: Existing verification checks stay first

**Rationale**: Unknown task, a cancelled task, an unknown criterion, a task that is not In Progress, a blank observation, a missing pass, and a required check that has not passed already have messages. A blank method is reported only after those. A blank test-run identifier is reported only after a method is present. A refusal writes neither the verification columns nor `criterion_evidence`.

**Alternatives considered**: Checking the method first would replace `A required check has not passed.` when the method is also blank.

## Decision: A criterion verified before this feature stays Verified

**Rationale**: Verified still means the observation, the pass, the time, and the engineer are stored. Older rows have no `criterion_evidence` row. The payload shows the method and the identifier only when that row exists. A new verification refuses to succeed without both.

**Alternatives considered**: Treating a missing evidence row as Unverified would make a Completed task show an Unverified criterion after this feature is opened on an existing workspace.

## Decision: The other gap direction is a separate read

**Rationale**: `GET /api/requirements` and `list_requirements` return a list of requirements. Tests and the page depend on that list being empty when no requirement exists. Tasks without a requirement are not requirements. The new read returns `tasks_without_requirement` and `criteria_without_verification`. The requirements page shows them beside the existing gap phrases.

**Alternatives considered**: Adding the tasks to each requirement's `missing` array would invent a requirement for a task that has none. Wrapping the requirement list in an object would break readers that expect a list.

## Decision: Unverified means the existing Verified rule is not met

**Rationale**: A criterion is on the criterion list when it is not Verified. Verifying it removes it. Marking it Unverified, editing its text, or changing a linked requirement returns it. A task is on the task list when no `requirement_task` row names it, including a subtask and a cancelled task. One link is enough to remove the task.

**Alternatives considered**: Listing only In Progress tasks would hide a Draft task that has no reason recorded yet, which is the gap this list exists to show.
