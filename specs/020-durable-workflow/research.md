# Research: Durable Workflow Orchestration

## Decision: One new table, no new column on task

**Rationale**: The schema is reapplied with `CREATE TABLE IF NOT EXISTS`. A new column on `task` would not appear in a workspace that already has that table. Steps are rows in `workflow_step`.

**Alternatives considered**: A JSON list on the task row. Rejected because an existing workspace would not gain the column, and one step per row keeps one state explicit.

## Decision: The step actions are `read` and `folder`

**Rationale**: Those two actions already cover an immediate result, a refusal, and a change that waits for approval. Commit, branch, pull request, test, deletion, and model proposal keep their own commands.

**Alternatives considered**: Dispatching every existing action from one step form. Rejected because that mixes unrelated command fields into this change.

## Decision: A performed step returns the task detail

**Rationale**: `call_in_transaction` rolls back when the result is a Refusal. The Failed or Waiting row must commit, so advance returns the task detail. The stop sentence is on that detail. `There is no step to run.` is a Refusal because nothing was written.

**Alternatives considered**: Returning a Refusal after saving the failure. Rejected because the failure row would be rolled back.

## Decision: A waiting step stores `change_id`

**Rationale**: The next advance reads that change. Awaiting approval leaves the step Waiting. Carried out marks it Completed without calling the folder command again. Not carried out marks it Failed and copies the decline reason. Approval and decline stay the existing commands and do not advance the workflow.

**Alternatives considered**: Treating approval as the advance. Rejected because one approval would both carry out the change and start the next step.

## Decision: The next step is the lowest position that is not Completed

**Rationale**: Positions are assigned in insertion order, starting at 1. A Failed step is retried. A Waiting step is settled. A Pending step is performed. Later steps stay as stored.

**Alternatives considered**: Skipping a Failed step. Rejected because the spec says the next advance retries that step only.

## Decision: The file and folder are checked when the step runs

**Rationale**: An earlier step may create what a later step needs. Add-time checks are the required fields only. The action's existing message is stored as the step detail and copied into the stop sentence.

**Alternatives considered**: Refusing the add when the file is missing. Rejected because the file may appear before the step runs.
