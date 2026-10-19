# Research: Run One File Read

## Decision: A run has its own name

**Decision**: Store the name in `workflow_file_run`. Do not insert a `workflow_advance` row for that name.

**Rationale**: An advance name can perform a folder. A run name is allowed only for a file read. Keeping the names apart means a later advance can still perform the next folder.

**Alternatives considered**: Reuse the advance name. That would make "once" unable to advance a later folder, and it would let an advance perform a folder under a name the engineer used for a read.

## Decision: Perform the read in the same transaction as the name

**Decision**: Call the existing prepare and finish path with no advance name, then insert the run, all in one transaction.

**Rationale**: The file read, the completed step, the outbox message, and the run name then commit together. A Refusal after that work rolls the transaction back, so the step stays Pending and no file read remains. The request does not leave the step Running.

**Alternatives considered**: Call advance as two committed transactions. A crash between them would leave the step Running, which the spec does not allow for a rolled-back run.

## Decision: Save the name only after the step is performed

**Decision**: A blank name, a task that is not In Progress, no remaining step, a next step that is not a file read, and an interrupted step return before the name is inserted. A file that cannot be read still performs the step: the step becomes Failed, the name is stored, and a later step is not performed.

**Rationale**: A refusal must leave the name free. A failed read is a performed step, so the same name must not try it again. A different name can retry that failed read.

**Alternatives considered**: Leave the name free when the file is missing. The same name could then retry forever, and the task would not show that the run had been attempted.

## Decision: The next step is the first step that is not Completed

**Decision**: A Pending or Failed read may run. A folder, a waiting step, and a Running step are refused. One request performs one step.

**Rationale**: That is the same next step an advance would choose, restricted to a file read. Waiting and Running already have their own commands.

**Alternatives considered**: Skip a folder and run a later read. That would hide the folder from the engineer and perform a step that is not next.
