# Research: Call the Model Once

## 1. Where the call lives

**Decision**: Add a model boundary with a name and one `complete` method. The new command calls it once, then uses the existing assistant-file command with the returned text. The existing assistant-file command does not call a model. Tests and the local app supply a scripted model that records the prompt and returns fixed text. No network client is added.

**Rationale**: Principle V requires the model output to be isolated and recorded. A scripted model makes the one call observable in tests without choosing a vendor. The existing write rules stay in one place.

**Alternatives considered**:

- Calling a hosted model API. That adds a vendor, a secret, and a failure mode this slice does not need. The stored record is the same when a later model replaces the scripted one.
- Asking the engineer to paste the model text. That would not be a model call.

## 2. What is sent and what is stored

**Decision**: The prompt is the task title, the goal, the acceptance criteria, the stored file path, the stored file text, the project, and the file to write. The product does not read the project file again to build that prompt. `model_call` stores the change id, the file read id, the model name, the prompt, and the returned text. The returned text is also the applied file text. Nothing updates or deletes the row.

**Rationale**: The task goal can change later. The stored prompt is the input that was sent. Replay shows that row and does not rebuild the prompt or call the model.

**Alternatives considered**:

- Storing only the model name and the returned text. A later reader could not see the input that produced the text.
- Reading the project file again at call time. The spec says the input is the stored read.

## 3. When the model is called

**Decision**: Call the model only after the task, status, project, account, class, file name, file read, and file placement checks have passed. A missing model is `Choose the model this change uses.` A call that raises, or that returns something other than text, is `The model did not return file text.` and stores nothing. An empty string is valid text. Approval and opening the task do not call the model.

**Rationale**: A refusal that happens before the model must not spend the call. A failed call must not leave a partial file record.

**Alternatives considered**:

- Calling the model first and then validating. A blank project would still call the model.
- Treating an empty return as a failure. An empty file is valid text in the previous feature.

## 4. How the file is written

**Decision**: After a successful call, the existing assistant-file command receives the returned text as the file text. Ordinary, stopped, consequential, and replacement behavior stay as they are. The model row is inserted for that new change. A client-supplied model name is ignored.

**Rationale**: The spec says writing follows the ordinary-file rules. Duplicating those rules would let the two commands drift.

**Alternatives considered**:

- A second write path inside the model command. The approval match check would have to be copied as well.
