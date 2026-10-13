# Commands: Workspace Boundaries and Capability-Based Permissions

No new page and no new HTTP command. Pages and the HTTP API call the same workspace. The rules below are the contract for those existing commands.

## Workspace

Every command uses the workspace file named at start.

- A record created through one file is absent from a second file.
- A record created in the second file does not appear in the first.
- Opening the same file after it was closed returns the same task title, status, and evidence.
- A name supplied for the engineer or the assistant on a later start does not replace a name already stored on evidence.

## Task records

These commands must leave every project file, the current commit, and the current branch unchanged, and must not run a repository command:

- `POST /api/tasks` and the task page that creates a task
- Goal, criterion, verification, and status commands
- Decision commands
- Check commands
- Requirement commands
- `POST /api/tasks/{id}/implementation-changes` when no file, folder, test, or branch is part of that command
- `POST /api/tasks/{id}/assistant-changes` when no file is sent

Opening the task must show the stored records and must not touch the project.

## Capabilities

Each command below authorizes one target. Carrying it out must not carry out a different command or a different target.

| Command | One target | Waits |
|---|---|---|
| `POST /api/tasks/{id}/file-reads` | One existing text file | No. The file is not written. |
| `POST /api/tasks/{id}/assistant-changes` with one new file | That file | A replacement, a consequential request, or a stopped request waits. |
| `POST /api/tasks/{id}/folders` | One new folder | A consequential or stopped request waits. |
| `POST /api/tasks/{id}/test-runs` | One test | A consequential or stopped request waits. |
| `POST /api/tasks/{id}/deletes` | One text file | Always |
| `POST /api/tasks/{id}/commits` | One text file | Always |
| `POST /api/tasks/{id}/branches` | One new branch | Always |
| `POST /api/tasks/{id}/pull-requests` | One existing branch | Always |

`POST /api/tasks/{id}/implementation-changes/{change_id}/approve` names that change. Another waiting change on the task stays Awaiting approval. The assistant receives `The assistant cannot approve a change.` and nothing is carried out.

Existing messages and status codes stay as specifications 001 through 016 define them. This feature adds none.
