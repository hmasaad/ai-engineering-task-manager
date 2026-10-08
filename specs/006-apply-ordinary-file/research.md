# Research: Apply an Ordinary File

## 1. Where the feature lives

**Decision**: Extend the existing local Python process. The assistant-change command gains an optional file path and file text. When those are omitted, the command stays the feature 005 record and does not touch the filesystem. The engineer's record command stays as it is and does not write a file. SQLite stores the new row in the same workspace file.

**Rationale**: The spec attaches one file to an assistant change on a task that already exists. A second process would split the task record from the file it claims to have written. Principle VIII keeps this feature in the same reviewable process.

**Alternatives considered**:

- A new command that always requires a file and leaves the feature 005 command untouched at the HTTP boundary as well as in storage. The page would then have two assistant forms for one action. Optional fields keep one action and keep the existing contract tests valid.
- A model that invents the file text. Replay would no longer use the stored text, and the spec says the text is the text the assistant has already produced.

## 2. What is written, and what is only stored

**Decision**: The submitted text is the assistant's recorded output. The command does not call a model.

An ordinary request that is not stopped, whose file does not exist, and whose folder does exist, creates that file with exactly the submitted text and stores class `ordinary`. The file is created exclusively, so a file that appears in the meantime is not overwritten. If exclusive create finds the file already there, the command stores the request as class `consequential` and Awaiting approval instead, with the text now in the file, and writes nothing.

A consequential request, an ordinary request that is stopped, and a request whose file already exists are stored as class `consequential` and do not change the project. A stopped ordinary request still records `stopped` as true. A replacement records `stopped` as false. The existing outcome rule then shows Awaiting approval.

The task stores the project path the engineer typed, after trimming. It does not store the resolved absolute path. A relative path is resolved from the folder where this process was started. An absolute path is used as given. That startup folder is captured when the workspace opens. A test may pass a temporary folder instead of the process directory.

**Rationale**: Principle V requires the non-deterministic text to be captured and replay to use that record. Principle VII treats replacement of durable text as consequential, so an ordinary class remains the case where the file was actually written. Storing the typed path lets the task show `billing`, which is the path the engineer named.

**Alternatives considered**:

- Storing a replacement as class `ordinary` with outcome Awaiting approval. The existing rule would show that ordinary change as Carried out.
- Resolving a relative path from the directory of each request, which can change after startup. The spec names the folder where the task manager was started.
- Storing the resolved absolute path. The task would no longer show the path the engineer typed.

## 3. How a path is judged to stay inside the project

**Decision**: The file path must be relative. An absolute file path, or a path whose normalized parent steps leave the project, is refused with `The file must stay inside the named project.` and nothing is stored. The project path is then resolved, which follows links. The destination folder must already exist; if it does not, the refusal is `The folder for that file must already exist.` The resolved destination folder, and the resolved file when it already exists, must stay inside the resolved project folder. A link that stays inside is allowed. A link that lands outside is the same outside refusal, and nothing is stored. A project path that is missing or is not a folder is `The project must already exist.`

The same inside check runs again before an approval writes. If it fails, no resolution row is written, the file is unchanged, and the proposal stays Awaiting approval. The message is `The file must stay inside the named project.`

**Rationale**: The spec says the file must stay inside the named project and that links are followed. Checking only the typed name would allow a link inside the project to write somewhere else. Checking again at approval stops a link that was retargeted after the proposal.

**Alternatives considered**:

- Refusing every link. The spec allows a link that stays inside the project.
- Following a link wherever it points when the typed name has no parent step. That would write outside the project.

## 4. What counts as text

**Decision**: Text is UTF-8. A file is not text when it cannot be decoded as UTF-8, when it contains a NUL byte, or when the path is a folder rather than a file. An empty file is text. The submitted text for a new file is text by definition, including an empty string. An existing file that is not text is refused with `The file is not text.`, nothing is stored, and the file is unchanged.

If a waiting proposal's file can no longer be read as text at approval, the file does not match the recorded text. Approval does not write, no resolution row is written, and the engineer is told `The file no longer matches the text this change was proposed against.`

**Rationale**: The spec refuses a file that cannot be read as text and tells the engineer the file is not text. UTF-8 is the text this process can store and show. A NUL byte distinguishes a binary file that happens to decode. The approval message for a later mismatch is the one the spec already uses, not a second sentence.

**Alternatives considered**:

- Treating any byte sequence as text and showing it on the task. The spec says a file that is not text is refused.
- Using the not-text sentence again at approval. The spec says that later case is a mismatch, and the proposal stays Awaiting approval.

## 5. How the file is stored

**Decision**: One append-only table, `applied_file`. Each row stores the change id, the file path, whether the file was new, the previous text, and the proposed text. The change id is unique. Previous text is absent exactly when the file was new. Proposed text may be empty. Nothing updates or deletes a row. A change with no row is an engineer change or a feature 005 assistant change, and no file is written for it.

The project and the assistant name stay on `assistant_change`. Reading the change joins `applied_file` when the row exists.

**Rationale**: The spec forbids editing or removing a saved change. A new table leaves the feature 005 columns unchanged, so an older workspace file gains the table when it is opened. `CREATE TABLE IF NOT EXISTS` does not add a column to a table that already exists.

**Alternatives considered**:

- New columns on `assistant_change`. The schema script would not add those columns to an existing file.
- Copying the file bytes only on disk and not in the workspace. A later reader could not reconstruct the text from the task record alone.

## 6. When approval writes

**Decision**: The existing approve command writes the file only when the change is still Awaiting approval and has an applied file. It writes only after the inside check passes and the file still matches. A new file must still be absent, and it is created exclusively. An existing file must still contain the recorded previous text, and that text is then replaced with the proposed text. The approval row is written in the same command as the successful write. A failed write stores no approval.

These existing refusals write nothing and do not touch the file: the actor is `assistant`; the change is ordinary and already Carried out; the change is already approved; the change was not carried out. Decline never writes. A body that omits the actor remains the engineer's command.

**Rationale**: The spec says approval writes the proposed text only while the file still matches, and a carried-out file is not written again. Checking the actor first keeps the assistant from writing through the approve command. Writing and recording the approval together avoids a Carried out record whose file was not written.

**Alternatives considered**:

- Writing at approval time for every consequential change, including feature 005 changes that have no file. Those changes have no file to write.
- Approving first and writing later. A crash, or a mismatch found too late, would mark the change Carried out while the file stayed unchanged.

## 7. What replay does

**Decision**: Replay runs the same command script against a fresh workspace and a fresh project folder. Each folder is written once. The compared record includes the file path, whether it was new, the text, the assistant, and Carried out. Reading the stored task does not write. A second command in the same folder, after the file exists, does not overwrite it.

**Rationale**: The spec says the second pass shows the same record and does not modify the file again. Two fresh folders keep the existing replay comparison independent. The same-folder rule is what stops the second pass from writing over the first file.

**Alternatives considered**:

- Re-running the script in the same folder and expecting a second ordinary write. The file would be replaced, which the spec forbids.
- Skipping the filesystem in the replay test. The spec's ordinary outcome includes the file on disk.
