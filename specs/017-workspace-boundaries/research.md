# Research: Workspace Boundaries and Capability-Based Permissions

## Decision: Do not add a table, a command, or a permission screen

**Decision**: Keep the workspace file, the task records, and the repository commands that specifications 001 through 016 already store. Prove the boundaries with tests.

**Rationale**: The spec says this feature does not add a task status, a requirement result, or a second permission screen. The capability is the stored command. A new grant screen would be a second approval for actions that already wait.

**Alternatives considered**: A capability table granted in advance was rejected because the spec says one request does not grant a standing permission. A role checklist was rejected because there is one engineer and one assistant name, and the assistant already cannot approve.

## Decision: One start uses one workspace file

**Decision**: The workspace is the file named when the task manager starts. Commands on that start read and write only that file. A second file is a second workspace, even when both name the same project folder.

**Rationale**: The spec requires records written in one workspace to stay absent from the other. The project folder is not the workspace. Two starts can point at one repository and still keep separate task records.

**Alternatives considered**: Storing the workspace inside the project was rejected because a task record would then appear as a file in that repository. Sharing one file between two starts was rejected because that is one workspace, not two.

## Decision: A later start does not rewrite stored evidence

**Decision**: Opening the same workspace file again shows the same task titles, statuses, and evidence. The engineer name and assistant name given on that later start apply to records created after it. They do not replace names already stored on evidence.

**Rationale**: The spec says a restart preserves evidence. Evidence includes the name copied when the record was written. Changing that name would make the earlier record describe a different person.

**Alternatives considered**: Rewriting every stored engineer name on start was rejected because the evidence would no longer say who recorded it. Refusing a start whose engineer name differs was rejected because the spec does not add that refusal.

## Decision: Task records do not run a repository command

**Decision**: Creating a task, editing a goal, adding or verifying a criterion, changing status, recording a decision, recording a check, and recording a requirement do not create, delete, or modify a project file and do not run a repository command. An ordinary change that names a project and names no file, folder, test, or branch is a task record.

**Rationale**: The spec separates task records from repository capabilities. Naming a project in an account is not permission to touch that project.

**Alternatives considered**: Treating every mention of a project as a file write was rejected because specification 005 stores an account without opening the project.

## Decision: One approval carries out one change

**Decision**: Approval names one change. A waiting commit, delete, branch, or pull request on the same task stays waiting. A file read does not write the file. An ordinary new file or new folder still follows specifications 006 and 011 and touches only that target.

**Rationale**: The spec says completing one capability does not authorize another. The existing approval already names the change. The tests have to show that a second waiting change is not carried out.

**Alternatives considered**: Approving every waiting change on the task was rejected because a prior approval would cover an unrelated change. Adding a new refusal message was rejected because the spec does not ask for one.
