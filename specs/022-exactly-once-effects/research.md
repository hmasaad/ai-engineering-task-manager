# Research: Idempotency and Exactly-Once Effects

## Decision: A stored effect is settled before the action runs

**Rationale**: Finish already runs while a step is Running. If a file read or folder change is already past the attempt baseline, finish records that outcome and does not call the action. That is the same comparison recovery already uses.

**Alternatives considered**: A new effect table that stores the read id or change id. Rejected because the attempt baseline and `change_id` already identify the one effect, and a new column would not appear in a workspace that already created `workflow_step`.

## Decision: A Failed step with a change is not performed again

**Rationale**: A decline stores the folder change and then marks the step Failed. Another advance must leave that change as the only one. A Failed step with no change still retries, which is the existing rule for a refusal that stored nothing.

**Alternatives considered**: Retrying every Failed step. Rejected because the retry would record a second folder change.

## Decision: The advance name is a row, not a response snapshot

**Rationale**: `workflow_advance` stores the task, the trimmed name, and the step. A later request with that name settles that step when it is still Waiting, and otherwise returns the task without performing a step. The page stays current. A blank name inserts no row, so unnamed advances stay as they are.

**Alternatives considered**: Returning a frozen copy of the first response. Rejected because an approval after that response would be hidden. Making every advance idempotent without a name. Rejected because the next unnamed advance must still perform the next step.

## Decision: A refused advance does not save the name

**Rationale**: A task that is not In Progress, a workflow with nothing to run, and a step that must be recovered first store nothing. The engineer can send that name again after the refusal no longer applies. While the named step is still Running, the same name is `Recover the interrupted step first.`

**Alternatives considered**: Saving the name on every refusal. Rejected because the engineer could not use that name once the task was ready.

## Decision: The page fills in a new name each time the task is shown

**Rationale**: The advance form has one name field, filled when the page is rendered. Submitting it twice uses one name. Showing the task again fills in a different name, so the next submit can perform the next step. The engineer can replace the filled-in name.

**Alternatives considered**: Asking the engineer to invent a name with no default. Rejected because a double submit would then send a blank name and perform two steps.
