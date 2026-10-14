# Research: Task Dependencies

## Decision: Store each prerequisite as one row

**Rationale**: `task` is created with `CREATE TABLE IF NOT EXISTS`, so a later start cannot add a column of ids. A row in `task_dependency` names one task and one prerequisite. The pair is unique. The row checks that the two ids differ.

**Alternatives considered**: A text column of ids on `task` cannot be added to an existing workspace file. Treating a subtask link as a prerequisite would block a parent on its own children, which is already a different completion rule.

## Decision: Reject a cycle when the link is named

**Rationale**: The new prerequisite is stored only when following prerequisites from that task does not reach the task being linked. A cycle is never stored, so the execution order always includes every task. The two links that do not yet close the cycle stay.

**Alternatives considered**: Accepting the cycle and dropping a task from the order would hide work. Checking the cycle only when starting would leave a stored loop the order cannot honor.

## Decision: The order is a topological reading with the lower id first

**Rationale**: A prerequisite is an edge that must come first. Tasks with no remaining prerequisite are eligible. The eligible task with the lower id is next. Reading the order does not write a row and does not change a status.

**Alternatives considered**: Ordering by title would change when a title is edited. Ordering only the top-level tasks would hide a prerequisite that is a subtask.

## Decision: Start is the execution hold

**Rationale**: Ready remains the status from feature 001: a goal and an acceptance criterion. An unfinished prerequisite does not stop that mark. Start is refused, after the existing Ready check, while any prerequisite is not Completed. There is no Failed task status. Cancelled, Draft, Ready, and In Progress are incomplete. Unverified criteria on that prerequisite are named; otherwise the sentence says incomplete and includes the status.

**Alternatives considered**: Redefining Ready would rewrite feature 001. Blocking completion would add a new sentence to a task that has already started. A task that is already In Progress stays In Progress when a prerequisite is reopened, and the task still shows the blocked sentence.

## Decision: The engineer can remove a link

**Rationale**: A stored prerequisite that cannot be removed would block start until that other task is Completed. Removal deletes that one row and does not change either status. A task that is not linked is refused with `That prerequisite is not linked.`

**Alternatives considered**: Leaving a mistaken link permanent makes the start hold irreversible without completing the other task.
