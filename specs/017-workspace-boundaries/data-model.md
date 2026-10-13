# Data Model: Workspace Boundaries and Capability-Based Permissions

No new table and no new column. Specifications 001 through 016 keep their records. This feature states which existing records form a workspace and which form a capability.

## Workspace

One start has one workspace file.

| Fact | Rule |
|---|---|
| File | The path named at start. Another path is another workspace. |
| Tasks, statuses, evidence | Stored only in that file. A second file does not receive them. |
| Engineer and assistant | The names given at start are copied onto records created after that start. Names already stored on evidence stay as they were. |
| Project folder | Not the workspace. Relative project names resolve from the folder where the task manager was started. An absolute project path is used as given. |

Closing the start and opening the same file again shows the same tasks, statuses, and evidence.

## Task record

These commands write the workspace and do not touch a project:

- Create a task, edit its goal, add or edit a criterion, verify a criterion
- Change status
- Record a decision
- Record a check
- Record a requirement, link it, name a check, or record a run
- Record an ordinary or consequential account that names no file, folder, test, or branch

A refusal stores nothing in the workspace and changes no project file.

## Capability

A capability is one existing command. It names one project and one target.

| Capability | Target | Record already stored by |
|---|---|---|
| Read one file | One file | A file read. It is not an implementation change. |
| Write one file | One file | An implementation change and its file. |
| Create one folder | One folder | An implementation change and its folder. |
| Run one test | One test | An implementation change and its test. |
| Delete one file | One file | An implementation change that waits. |
| Commit one file | One file | An implementation change that waits. |
| Create one branch | One branch | An implementation change that waits. |
| Open one pull request | One branch | An implementation change that waits. |

An approval names one change id. Only that change can be carried out. Another waiting change on the same task stays Awaiting approval.

A file read stores the text it read and does not write the file. An ordinary new file or new folder that specifications 006 and 011 already carry out on request still touches only that target.

No capability grants a later request. The assistant cannot approve a waiting change.
