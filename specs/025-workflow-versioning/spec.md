# Feature Specification: Workflow Versioning and Migration

**Feature Branch**: `025-workflow-versioning`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Workflow Versioning and Migration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The running workflow keeps a version (Priority: P1)

The engineer sees the version of the workflow on the task. The first version is version 1. A workflow that already has steps is version 1 when the task is opened. Advance still performs the current version, one step at a time, and a completed step is not performed again. Adding or removing a step after the workflow has run is still refused with the existing messages.

**Why this priority**: Later versions are only meaningful once the running workflow has a version the engineer can see.

**Independent Test**: Add two steps and advance once. The task shows version 1, the first step is Completed, and the second step is still Pending. Opening the task again still shows version 1.

**Acceptance Scenarios**:

1. **Given** a task with workflow steps and no stored version, **When** the engineer opens the task, **Then** the workflow is version 1.
2. **Given** version 1 has started, **When** the engineer adds or removes a step without a draft, **Then** the workflow stays version 1 and the engineer is told `A step can be added only before the workflow runs.` or `A step cannot be removed after the workflow runs.`
3. **Given** version 1, **When** the engineer advances, **Then** one unfinished step of that version runs and a completed step is not run again.

---

### User Story 2 - Revise the remaining work (Priority: P2)

After the workflow has run, the engineer can revise it. Revise creates the next version as a draft. The draft keeps every step that has already left Pending, in the same order, including a step that is waiting for approval or has failed. Pending steps stay on the current version and are not copied. The engineer can add a new step to the draft and can remove a pending step from the draft. A step that already ran cannot be removed. Revise does not perform a step and does not change the task status. Until the engineer migrates, advance still uses the current version.

**Why this priority**: The engineer needs a place to describe the remaining work without rewriting the record of what already ran.

**Independent Test**: Complete the first of two steps, then revise. The draft is version 2 and contains the completed step only. Add a new step to the draft. The current version still has the old pending step, and advance still performs that current version.

**Acceptance Scenarios**:

1. **Given** version 1 has at least one step that is no longer Pending, **When** the engineer revises, **Then** a draft of the next version contains the steps that already left Pending and omits the Pending steps.
2. **Given** a draft, **When** the engineer adds a step, **Then** that step is Pending on the draft and the current version is unchanged.
3. **Given** a draft step that already ran, **When** the engineer removes it, **Then** it stays and the engineer is told `A step that already ran must stay in the new version.`
4. **Given** the workflow has not run, **When** the engineer revises, **Then** no draft is created and the engineer is told `The workflow has not run yet.`
5. **Given** a draft already exists, **When** the engineer revises again, **Then** the draft stays and the engineer is told `A draft version already exists.`
6. **Given** a step is interrupted, **When** the engineer revises, **Then** no draft is created and the engineer is told `Recover the interrupted step first.`

---

### User Story 3 - Migrate onto the draft (Priority: P3)

The engineer migrates by naming why the workflow is changing. The draft becomes the current version. The previous version is kept and marked superseded, with that reason. Steps that already ran stay as they are and are not performed again. Pending steps that were left on the previous version are not deleted and are not performed. The task status does not change. The replay of steps already recorded is not rewritten. A blank reason is refused, and a migration without a draft is refused.

**Why this priority**: Switching versions is the consequential record. It happens only when the engineer names the reason.

**Independent Test**: After the draft contains the completed step and one new step, migrate with the reason `Replace the remaining step`. The task shows version 2, the old pending step is not run, and the next advance performs the new step once.

**Acceptance Scenarios**:

1. **Given** a draft and the reason `Replace the remaining step`, **When** the engineer migrates, **Then** the draft is the current version, the previous version is superseded with that reason, and the task status is unchanged.
2. **Given** a superseded pending step, **When** the engineer advances, **Then** that step is not performed and the new version's next unfinished step is performed once.
3. **Given** a completed step, **When** the engineer migrates and advances, **Then** that step is not performed again.
4. **Given** a draft, **When** the reason is blank, **Then** the current version stays and the engineer is told `Name why this workflow is migrating.`
5. **Given** no draft, **When** the engineer migrates, **Then** the engineer is told `There is no draft version to migrate.`

### Edge Cases

- A workflow with no steps has no version. Revise tells the engineer `There is no workflow to revise.`
- A waiting step is kept on the draft. Migration does not approve it and does not advance the workflow.
- A failed step that stored an effect is kept and is not performed again.
- An interrupted step must be recovered before revise or migrate.
- One request revises or migrates once. Migration does not perform a step.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A workflow with steps MUST have a current version. The first version is version 1, including a workflow that already had steps before versions were shown. The task page MUST show that version.
- **FR-002**: After the current version has run, the engineer MUST be able to revise it into one draft of the next version. The draft MUST keep every step that has left Pending and MUST omit Pending steps. Revise MUST NOT perform a step or change the task status.
- **FR-003**: While a draft exists, a new step MUST be added to the draft. A pending draft step MAY be removed. A step that already ran MUST stay, and the engineer MUST be told `A step that already ran must stay in the new version.` Advance MUST keep using the current version until migration.
- **FR-004**: Migration MUST require a reason. A blank reason MUST be refused with `Name why this workflow is migrating.` No draft MUST be refused with `There is no draft version to migrate.` A second draft MUST be refused with `A draft version already exists.` Revise before the workflow has run MUST be refused with `The workflow has not run yet.` An interrupted step MUST be refused with `Recover the interrupted step first.`
- **FR-005**: Migration MUST make the draft the current version and keep the previous version as superseded, with the reason. Steps that already ran MUST NOT be performed again. Pending steps left on the superseded version MUST remain stored and MUST NOT be performed. The replay MUST NOT be rewritten. The task status MUST stay unchanged.

### Key Entities

- **Workflow version**: The numbered set of steps the task is on. One version is current. One draft may exist. A replaced version is superseded.
- **Migration**: The reason the engineer moved from one version to the next, kept with both versions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer can see the current workflow version on the task in one view.
- **SC-002**: In a review of migrations, 100% keep the steps that already ran and do not perform those steps again.
- **SC-003**: In a review of advances after migration, 100% skip pending steps that were left on the superseded version.
- **SC-004**: An engineer can revise, add one replacement step, and migrate in under 3 minutes.

## Assumptions

- Specifications 001 through 024 are not rewritten. Advance, recovery, and exactly-once effects keep their current rules on the current version.
- Adding and removing steps before the workflow runs stays as it is.
- The engineer names the migration reason. Silence is not a reason.
- The rules are covered by automated checks.
