# Research: Instruction Page

## Decision: The model is one saved row

**Rationale**: The page must show the same model after the workspace is opened again. `configured_model` stores one name and one text. A workspace created earlier gains the table the next time it is opened. No column is added to an existing table.

**Alternatives considered**: Keeping the model only in the running process. Rejected because opening the workspace again would forget it. Passing the model only when the process starts. Rejected because the engineer asked to manage it on the page.

## Decision: Start work is one transaction

**Rationale**: The task, the file read, and the model proposal are stored together. A refusal from any existing check rolls the transaction back, so a missing file leaves no task.

**Alternatives considered**: Creating the task first and showing a later error on the task. Rejected because a refused start must store nothing.

## Decision: The page calls the existing read and model proposal

**Rationale**: The file must already exist, a new ordinary file is written, and a replacement waits. Those rules already exist. The page does not add a second way to write a file.

**Alternatives considered**: Letting the model choose any file and write it immediately. Rejected because a replacement is consequential and still needs approval.

## Decision: One file to read and one file to change

**Rationale**: The existing model proposal uses one stored read and returns the text of one file. The instruction names those two paths.

**Alternatives considered**: A list of files changed in one start. Rejected because each change has to stay reviewable on its own.
