# Data Model: Read a Project File

Rules below are the stored form of `specs/007-read-project-file/spec.md`. They extend `specs/006-apply-ordinary-file/data-model.md`. The domain module is the only writer. A refused command commits nothing and leaves the project folder unchanged. Task, criterion, status-change, decision, check, implementation-change, assistant-change, and applied-file rows are unchanged by recording a read.

## Startup folder

Not a stored row. Captured when the workspace opens, as feature 006 already does. A relative project path is resolved from this folder. An absolute project path is used as given. Tests may supply a temporary folder. Changing the process directory later does not change this folder for an already open workspace.

## File Read

Insert-only. No update and no delete. One row per successful read. A second read of the same file is a new row.

| Field | Required | Rules |
|---|---|---|
| id | yes | Surrogate identity. Assigned at insert. |
| task_id | yes | Exactly one task. |
| project | yes | Non-empty after trimming. The project path the engineer typed, not the resolved absolute path. |
| file_path | yes | Non-empty after trimming. The file path the engineer named, relative to the project. Not an absolute path. |
| file_text | yes | The text read. May be empty. Spaces at either end are kept. Not rewritten after insert. |
| assistant_name | yes | Copied from the configured assistant. Not a name sent by the client. |
| read_at | yes | Clock time, UTC `YYYY-MM-DDTHH:MM:SSZ`. |

A saved file read cannot be moved to another task, another path, or another project. It is not an implementation change and has no class, outcome, or approval.

## Validation before insert

Considered in this order. A refusal writes no file-read row and does not create or modify a file.

1. The task id does not exist. The engineer is told the task was not found.
2. The task is Draft, Ready, Completed, or Cancelled. The messages match feature 002.
3. The project path is blank. `Name the project this change is for.`
4. The project path is not an existing folder. `The project must already exist.`
5. The file path is blank. `Name the file this change reads.`
6. The file path is absolute, escapes the project by a parent step, or resolves outside the project, including through a link. `The file must stay inside the named project.`
7. The file does not exist, including when its folder inside the project does not exist. `The file must already exist.`
8. The path is a folder, or the file cannot be read as text. Text is UTF-8 without a NUL byte. `The file is not text.`

The inside-project check and the text check are the ones feature 006 already uses. This feature does not define a second meaning for either.

## What a successful read stores

The row holds the trimmed project path, the relative file path, the text read, the assistant, and the time. The file's bytes are unchanged. No implementation-change row is inserted. The task status stays In Progress.

A link that stays inside the project stores the path the engineer named and the text of the file the link reaches.

## Reading rules

- File reads on a task stay oldest first, by `read_at` then `id`, and stay filtered to that task. A subtask's read does not appear on the parent.
- Opening the task returns the stored rows and does not read the project.
- A later change or deletion of the file does not change a stored row.
- A task with no reads returns an empty list.
- Replay compares the stored path, text, project, and assistant. That comparison does not read the file.

## What this feature does not write

- The assistant-change command, with or without a file, does not insert a file read. Omitting its file still does not open the project.
- The engineer's record command does not insert a file read and does not modify the project.
- Approve and decline do not insert a file read. A waiting file proposal stays Awaiting approval when a read of that file is stored.
- Completion and cancellation do not gain a refusal from a file read. A carried-out change still needs a passing check.
