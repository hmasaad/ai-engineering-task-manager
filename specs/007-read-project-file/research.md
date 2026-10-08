# Research: Read a Project File

## 1. Where the feature lives

**Decision**: Extend the existing local Python process with a new read command. SQLite stores each read in the same workspace file. The assistant-change command stays the feature 006 write or proposal. Omitting its file stays the feature 005 record and does not open the project. The engineer's record command does not read a file.

**Rationale**: The spec says a read is not an implementation change. Adding optional fields to the assistant-change command would collide with feature 006, where a file name and an omitted file text mean an empty write. A separate command keeps that contract and keeps a read from looking like Carried out or Awaiting approval. Principle VIII keeps this feature in the same reviewable process.

**Alternatives considered**:

- Reusing the assistant-change command when `file_text` is omitted. That command already treats an omitted `file_text` as an empty file to write or propose.
- A model that summarizes the file. Replay would no longer show the file's text, and the spec says the product does not call a model.

## 2. What is read, and what is stored

**Decision**: The command reads one existing file and stores those bytes as text. It does not call a model. It does not write, replace, or delete the file, and it does not create a folder.

The task stores the project path the engineer typed, after trimming. It does not store the resolved absolute path. A relative path is resolved from the folder captured when the workspace opened. An absolute path is used as given. A test may pass a temporary folder instead of the process directory.

The file path stored is the relative path the engineer named, in portable form. The text stored is the file's text, including spaces at either end. An empty file stores an empty text.

**Rationale**: Principle V requires the observed text to be captured, because a later read of the project could see different bytes. Principle VI requires the task, the path, the text, and the assistant to be reconstructable without the conversation. Storing the typed project path lets the task show `billing`.

**Alternatives considered**:

- Storing the resolved absolute path. The task would no longer show the path the engineer typed.
- Reading the file again whenever the task is opened. The spec says a later replay shows the stored text and does not read the file again.

## 3. How a path is judged to stay inside the project

**Decision**: Use the same inside-project check as feature 006. The file path must be relative. An absolute file path, or a path whose normalized parent steps leave the project, is refused with `The file must stay inside the named project.` and nothing is stored. The project path is then resolved, which follows links. A project path that is missing or is not a folder is `The project must already exist.` The resolved file must stay inside the resolved project folder. A link that stays inside is allowed, and the stored text is the text that link reaches. A link that lands outside is the same outside refusal, and nothing is stored.

A file that does not exist, including a file whose folder inside the project does not exist, is refused with `The file must already exist.` The command does not create that folder.

**Rationale**: The spec uses the same project boundary as the previous feature and adds a missing-file refusal instead of creating a path. Checking only the typed name would allow a link inside the project to read a file outside it.

**Alternatives considered**:

- Refusing every link. The spec allows a link that stays inside the project.
- A separate missing-folder message. The spec uses `The file must already exist.` for a missing folder inside the project.

## 4. What counts as text

**Decision**: Text is the same rule as feature 006. Text is UTF-8 without a NUL byte. A folder at the path is not text. An empty file is text. A file that is not text is refused with `The file is not text.`, nothing is stored, and the file is unchanged.

**Rationale**: The spec says text has the same meaning as the previous feature. A second definition would let a file be writable and unreadable, or the reverse.

**Alternatives considered**:

- Treating any byte sequence as text. The spec refuses a file that cannot be read as text.
- A new message for a folder. The spec includes a folder at that path in `The file is not text.`

## 5. How the read is stored

**Decision**: One append-only table, `file_read`. Each row stores the task id, the project path, the file path, the text, the assistant name, and the time. Nothing updates or deletes a row. A second read of the same file inserts another row. Rows for a task are listed oldest first. A subtask's rows are not listed on the parent. The assistant name is copied from the configured workspace assistant. A client-supplied assistant name is ignored.

A read does not insert an implementation change, an assistant change, or an applied file.

**Rationale**: The spec forbids editing or removing a saved read, and it forbids storing the read as an implementation change. A new table leaves the feature 005 and feature 006 tables unchanged, so an older workspace file gains the table when it is opened. `CREATE TABLE IF NOT EXISTS` does not add a column to a table that already exists.

**Alternatives considered**:

- A row in `applied_file` with no write. That table belongs to an implementation change, and the spec says a read is not one.
- Storing only the path and reading the file when the task is shown. The stored text would change when the file changed.

## 6. What else stays unchanged

**Decision**: Recording a read does not verify a criterion, record a check, record a decision, or change task status. Completion and cancellation do not gain a new refusal. A carried-out change still needs a passing check. Approve and decline are not called by this command, and the assistant still cannot approve or decline. An earlier assistant change is not backfilled with a read.

**Rationale**: The spec says seeing a file must not weaken the approval and check rules already in place.

**Alternatives considered**:

- Treating the read as evidence that completes a criterion. The spec says the assistant does not choose Passed or Failed, and a read does not verify a criterion.
- Blocking completion until every read is checked. The spec says completion does not gain a new refusal because of the read.

## 7. What replay does

**Decision**: Replay runs the same command script against a fresh workspace and a fresh project folder that already contains the same file text. Each folder is read once. The compared record includes the path, the text, the project, and the assistant. Opening the stored task does not read the file and does not change it. After a read is stored, changing or deleting the file leaves that row unchanged. A later read request stores a second row with the text at that later time.

**Rationale**: The spec says two passes of the same stored read produce the same text and the second pass does not read the file again. Two fresh folders keep the existing replay comparison independent. The stored row, not a second look at the project, is what the second pass shows.

**Alternatives considered**:

- Re-running the script in the same folder after editing the file and expecting the first row to change. The spec keeps the original text.
- Skipping the filesystem in the replay test. The spec's outcome includes the text that was in the file, and the file remaining unchanged.
