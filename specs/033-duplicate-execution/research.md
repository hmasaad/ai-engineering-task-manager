# Research: Idempotency and Duplicate Execution Control

## Decision: Store the name only after the command is accepted

**Rationale**: A missing file, a blank folder, a task that is not In Progress, and a rolled-back command must leave the name free. The name is inserted in the same result as the file read or the folder change. A Refusal rolls that result back, so the name is not kept. The same trimmed name on the same task is one execution. The same name on another task is a different execution.

**Alternatives considered**: Saving the name before the command runs. Rejected because a refusal would use up the name. Reusing the workflow advance name. Rejected because that name already means one workflow step, and a workflow step must not record one of these executions.

## Decision: A repeated name returns the task and does not perform the command

**Rationale**: The later request may name a different path, or the file or folder may already have been removed. The stored path stays the path from the first accepted command. The file is not read again and the folder is not created again. A blank name is not looked up and is not saved, so each blank command keeps today's rules. A different name performs another command.

**Alternatives considered**: Refusing a repeated name. Rejected because the engineer asked to control the duplicate, not to turn the second request into an error. Comparing the later path with the stored path and refusing a mismatch. Rejected because the name already identifies the execution that ran.

## Decision: One new table

**Rationale**: An existing workspace file is not altered. `command_execution` stores one row per name on a task. The task detail lists those rows. Read a file and Create a folder gain an optional execution name. Other commands stay as they are.
