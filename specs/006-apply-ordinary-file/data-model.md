# Data Model: Apply an Ordinary File

Rules below are the stored form of `specs/006-apply-ordinary-file/spec.md`. They extend `specs/005-assist-ordinary-change/data-model.md`. The domain module is the only writer. A refused command commits nothing and leaves the project folder unchanged. Task, criterion, status-change, decision, and check rows are unchanged by recording or approving a file.

## Startup folder

Not a stored row. Captured when the workspace opens. A relative project path is resolved from this folder. An absolute project path is used as given. Tests may supply a temporary folder. Changing the process directory later does not change this folder for an already open workspace.

## Implementation Change

Unchanged columns from feature 002. `engineer_name` remains the workspace engineer. Outcome is still derived: ordinary with no resolution is Carried out; consequential with no resolution is Awaiting approval.

When this command writes a new file, class is `ordinary`. When the request is consequential, stopped, or names a file that already exists, class is `consequential`.

## Assistant Change

Unchanged columns from feature 005. `project` is the trimmed path the engineer typed, not the resolved absolute path. `stopped` is `1` only when the request class was ordinary and the request was stopped. A replacement that was not stopped stores `stopped` as `0` and class `consequential`.

An assistant change with no Applied File row is a feature 005 change. Recording it does not read or write the project.

## Applied File

Insert-only. No update and no delete. At most one row per implementation change. Written in the same command as the implementation change and the assistant change.

| Field | Required | Rules |
|---|---|---|
| change_id | yes | Exactly one implementation change. Unique. |
| file_path | yes | Non-empty after trimming. The file path the engineer named, relative to the project. Not an absolute path. |
| was_new | yes | `1` when the file did not exist at record time. `0` when it did. |
| previous_text | when the file existed | The text the file held at record time. Absent exactly when `was_new` is `1`. Present, and possibly empty, when `was_new` is `0`. |
| file_text | yes | The text written or proposed. May be empty. Not rewritten after insert. |

A saved applied file cannot be moved to another change, another path, or another project.

## Validation before insert

Considered in this order. A refusal writes no implementation-change row, no assistant row, and no applied-file row, and it does not create or modify a file.

1. The task id does not exist. The engineer is told the task was not found.
2. The task is Draft, Ready, Completed, or Cancelled. The messages match feature 002.
3. The project path is blank. `Name the project this change is for.`
4. The project path is not an existing folder, but only when a file path was sent. `The project must already exist.`
5. The account is blank. `An account of what changed is required.`
6. The class is missing or is neither ordinary nor consequential. `Choose ordinary or consequential.`
7. When no file path was sent, stop here and store the feature 005 assistant change. Do not read or write a project.
8. The file path is blank. `Name the file this change writes.`
9. The file path is absolute, escapes the project by a parent step, or resolves outside the project, including through a link. `The file must stay inside the named project.`
10. The folder that would hold the file does not exist. `The folder for that file must already exist.`
11. The file exists and cannot be read as text. Text is UTF-8 without a NUL byte. A folder at that path is not text. `The file is not text.`

## What a successful record stores

| Request | Class stored | stopped | File on disk | was_new |
|---|---|---|---|---|
| Ordinary, not stopped, file absent | ordinary | 0 | Created with the submitted text | 1 |
| Ordinary, not stopped, file already there | consequential | 0 | Unchanged | 0 |
| Ordinary, stopped | consequential | 1 | Unchanged | 1 if absent, otherwise 0 |
| Consequential | consequential | 0 | Unchanged | 1 if absent, otherwise 0 |

If exclusive create finds that a new file appeared after the absence check, the command stores the replacement row instead and does not overwrite the file.

## Approval and decline

Approval of a waiting applied file:

- The actor `assistant` is refused before any read or write, with `The assistant cannot approve a change.`
- The resolved file must still land inside the resolved project. Otherwise the proposal stays Awaiting approval and the engineer is told `The file must stay inside the named project.`
- A file that was new must still be absent. A file that existed must still contain `previous_text` and must still be text. Otherwise the proposal stays Awaiting approval and the engineer is told `The file no longer matches the text this change was proposed against.`
- When the check passes, the proposed text is written and the existing approval row is stored. The approval names the workspace engineer. The outcome becomes Carried out. The applied-file row is not updated.
- An ordinary change that is already Carried out is refused with the existing feature 002 message, and the file is not written again.
- A change that is already approved, or that was not carried out, keeps the existing feature 002 refusals and does not write.

Decline stores the existing not-carried-out resolution and does not write. The actor `assistant` is refused with `The assistant cannot decline a change.` and writes nothing.

## Reading rules

- Changes on a task stay oldest first and stay filtered to that task. A subtask's file does not appear on the parent.
- A change with no applied file reports no file. Its project and assistant fields stay the feature 005 shape.
- A change with an applied file reports the path, whether it was new, the previous text or its absence, and the proposed text.
- Replay compares those stored fields. Reading them does not write the file.
