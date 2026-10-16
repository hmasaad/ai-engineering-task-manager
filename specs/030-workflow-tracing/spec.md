# Feature Specification: Workflow Observability and Distributed Tracing

**Feature Branch**: `030-workflow-tracing`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Implement Workflow Observability and Distributed Tracing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A workflow run keeps one trace (Priority: P1)

The first time a workflow step starts, the task gains one trace. That step becomes a span: its name, the time it started, and the state Running. When the step completes, fails, or waits, the same span records that state, the detail, and the time it ended. A later step uses the same trace and follows the first span. A step that is still running has no end time. Recording the trace does not change the task status.

**Why this priority**: The engineer can explain the workflow only when each step has a start and an end on one trace.

**Independent Test**: Advance "Read the note", then "Read the extra". The task has one trace. The note span is completed and follows nothing. The extra span is completed and follows the note span. Both files were read once.

**Acceptance Scenarios**:

1. **Given** a workflow that has not run, **When** the engineer opens the task, **Then** the task says `No trace yet.`
2. **Given** "Read the note" completes, **When** the engineer opens the task, **Then** one trace has one completed span for that step, with a start and an end.
3. **Given** that trace, **When** "Read the extra" completes, **Then** the extra span uses the same trace and follows the note span.
4. **Given** a step that fails because the file is missing, **When** the engineer opens the task, **Then** that span is failed, keeps the detail, and has an end.
5. **Given** a step that has started and not finished, **When** the engineer opens the task, **Then** that span is running and has no end.
6. **Given** a start that is rolled back, **When** the engineer opens the task, **Then** the step is unchanged and there is no trace.

---

### User Story 2 - Reading the trace does not run the workflow (Priority: P2)

The engineer can read the trace on its own. A second read returns the same trace. Reading it does not start a step, does not change the task status, and does not move the clock. An unknown task is refused with `Task not found.`

**Why this priority**: A trace that changes the workflow while it is being read is not a record.

**Independent Test**: Complete one read. Read the trace twice. The spans match, the task stays In Progress, and the clock does not move.

**Acceptance Scenarios**:

1. **Given** a completed span, **When** the engineer reads the trace twice, **Then** both reads return the same spans.
2. **Given** that read, **When** the engineer looks at the task, **Then** the task is still In Progress and the file was not read again.
3. **Given** an unknown task, **When** the engineer reads its trace, **Then** the engineer is told `Task not found.`

---

### User Story 3 - The task shows the trace (Priority: P3)

The task shows the trace and each span in order: the name, the state, the span it follows, the start, and the end. The task list stays the list of tasks.

**Why this priority**: The engineer needs the trace on the task, beside the workflow.

**Independent Test**: Complete one read and open the task. The page shows the trace and the completed span. Before the workflow runs, the page says `No trace yet.`

**Acceptance Scenarios**:

1. **Given** no step has run, **When** the engineer opens the task, **Then** the page says `No trace yet.`
2. **Given** a completed step, **When** the engineer opens the task, **Then** the page shows the trace and that span as completed.
3. **Given** a later step on the same trace, **When** the engineer opens the task, **Then** the page shows that span following the first span.

### Edge Cases

- One trace belongs to one task. A second task has its own trace.
- A span is recorded only when the step starts. Closing it happens in the same result that completes, fails, or waits the step.
- Reading the trace does not deliver a message, compensate a step, or approve a change.
- One request reads the trace. It does not add a span.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The first running step on a task MUST open one trace and one span. The span MUST name the step, start as Running, and record the start time. A later step MUST use that same trace and follow the first span.
- **FR-002**: When a step becomes Completed, Failed, or Waiting, its open span MUST record that state, the detail, and the end time in that same result. A step that is still running MUST have no end time. A rolled-back start MUST leave no trace. The task status MUST stay unchanged by the trace itself.
- **FR-003**: Reading the trace MUST NOT start a step, read a file, move the clock, or change the task status. A second read MUST return the same spans. An unknown task MUST be refused with `Task not found.`
- **FR-004**: The task page MUST show the trace and its spans. Before a step runs, the page MUST say `No trace yet.` The task list MUST stay the list of tasks.

### Key Entities

- **Trace**: One record for one task's workflow run. Every span of that task belongs to it.
- **Span**: One step's place on the trace. It names the step, the state, the start, the end, and the earlier span it follows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of completed workflows, 100% show one trace and one closed span for each step that ran.
- **SC-002**: In a review of repeated trace reads, 100% return the same spans and leave the task unchanged.
- **SC-003**: An engineer can see the trace and the span it follows on the task in one view.

## Assumptions

- Specifications 001 through 029 are not rewritten. Advance, recovery, delivery, and compensation stay as they are.
- The trace follows the workflow steps. It does not add a span for a delivery, a rejection, or a compensation.
- A step that finished before this record existed has no span added when the task is opened.
- The rules are covered by automated checks.
