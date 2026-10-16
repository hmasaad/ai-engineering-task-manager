# Research: Saga Pattern and Compensation

## Decision: The current workflow is the saga

**Rationale**: The task already has one current version of ordered steps. That version is the saga. Open means no step has failed. Failed means a step has failed. Waiting means a compensation is waiting. Compensated means every completed step has been compensated or marked not carried out. The task status stays In Progress.

**Alternatives considered**: A separate saga object with its own steps. Rejected because the workflow steps are already the ordered work.

## Decision: Compensate the latest completed step first

**Rationale**: A later failure should withdraw the most recent finished step before the earlier ones. Pending steps and the failed step itself have no completed effect to withdraw. A step that already has a compensation is skipped. One request withdraws one step.

**Alternatives considered**: Compensating every completed step in one request. Rejected because a folder removal has to be able to wait without hiding the next step. Compensating the oldest step first. Rejected because the newest effect is the one closest to the failure.

## Decision: A file read is a record, and a folder waits

**Rationale**: A file read does not change the file. Compensation records the withdrawal and leaves the stored read. A created folder is durable. Compensation waits. Approval names the evidence reviewed and removes the folder only when it is empty. The original folder change stays. A folder that contains something stays. Declining the compensation leaves the folder. Another compensation is refused while one is waiting.

**Alternatives considered**: Removing the folder as soon as the engineer compensates. Rejected because removing stored work waits for an explicit approval. Deleting the stored file read. Rejected because the read is the evidence of what the step did.

## Decision: One new table

**Rationale**: An existing workspace file is not altered. `workflow_compensation` stores one row per step. A second compensation for that step does not add a row.
