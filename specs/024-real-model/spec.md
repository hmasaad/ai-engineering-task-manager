# Feature Specification: Real Model

**Feature Branch**: `024-real-model`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Replace the model text. Add a real model that works on the task. The model receives the task and the file, and returns the revised file."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name the model service (Priority: P1)

The engineer opens Instructions and names the model, the service address, and, when the service requires one, a key. Saving keeps those values. Opening the workspace again shows the same name and address, and keeps the key. There is no field for fixed model text. A blank name is refused with `Choose the model this change uses.` A blank or unusable address is refused with `Name the model service.` A blank key is allowed. A refused save leaves the previously saved service unchanged.

**Why this priority**: Work can be sent to a real model only after the engineer has named that service.

**Independent Test**: Save model "Guide" at a local service address with no key. Open the workspace again. Instructions shows "Guide" and that address, and does not ask for model text.

**Acceptance Scenarios**:

1. **Given** no model service is saved, **When** the engineer opens Instructions, **Then** the name, address, and key are empty, and the page has no model text field.
2. **Given** the engineer saves a name and a service address, **When** the workspace is opened again, **Then** the same name and address are shown.
3. **Given** a saved service, **When** the engineer saves a blank name, **Then** the saved service stays and the engineer is told `Choose the model this change uses.`
4. **Given** a saved service, **When** the engineer saves a blank address, **Then** the saved service stays and the engineer is told `Name the model service.`

---

### User Story 2 - The model revises one file (Priority: P2)

Starting work reads the named file and asks the saved model once. The request includes the task title, the goal, the acceptance criterion, what changed, and the text of the file that was read. The model's reply is the text of the file to change. A new ordinary file is written with that reply. An existing file is left unchanged and the change waits for approval, showing the reply. Approving writes that reply and does not ask the model again. When the service cannot be reached, or the reply is empty, nothing is stored and no file is written.

**Why this priority**: The model is useful once its reply is the revised file rather than a fixed sentence.

**Independent Test**: A file contains `Attendance`. The engineer asks to change that heading to `Mark Attendance`. The model is asked once with the file text and that request. The file stays `Attendance` until approval, and the waiting change shows `Mark Attendance`.

**Acceptance Scenarios**:

1. **Given** a saved service and an existing file, **When** the engineer starts work to change that file, **Then** the model is asked once, the file on disk is unchanged, and the task shows the model's reply waiting for approval.
2. **Given** a saved service and a new ordinary file, **When** the engineer starts work, **Then** the new file contains the model's reply and the task stays In Progress.
3. **Given** the service cannot be reached, **When** the engineer starts work, **Then** nothing is stored, no file is written, and the engineer is told `The model service could not be reached.`
4. **Given** the model returns no file text, **When** the engineer starts work, **Then** nothing is stored and the engineer is told `The model did not return file text.`
5. **Given** a waiting reply, **When** the engineer approves it, **Then** the file contains that reply and the model is not asked again.

---

### User Story 3 - The page no longer asks for model text (Priority: P3)

The task list still links to Instructions. The model section shows Model name, Model address, and API key. The task section is unchanged. After a successful start, the engineer sees that task, including the model's reply.

**Why this priority**: The engineer should not be able to paste a fixed sentence where the revised file belongs.

**Independent Test**: Open Instructions from the task list. The page shows Model address and API key, and does not show Model text.

**Acceptance Scenarios**:

1. **Given** the task list, **When** the engineer opens Instructions, **Then** the page shows Model name, Model address, and API key, and does not show Model text.
2. **Given** a successful start, **When** the task opens, **Then** the task shows the model's reply.

### Edge Cases

- A service address must be an `http` or `https` address. Any other address is `Name the model service.`
- The key is sent only to the saved service with the work request. It is not part of the stored prompt.
- The model is asked once per start. A second approval does not ask again.
- A reply wrapped as a fenced code block is stored as the file text inside the fence.
- One request saves the service or starts one piece of work.
- Starting work does not complete the task and does not approve a waiting change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Instructions MUST let the engineer save a model name, a service address, and an optional key. The name and address MUST be shown again after the workspace is opened. A blank name MUST be refused with `Choose the model this change uses.` A blank or unusable address MUST be refused with `Name the model service.` The page MUST NOT ask for fixed model text.
- **FR-002**: Starting work MUST ask that model once. The request MUST include the task title, the goal, the acceptance criterion, what changed, and the text of the file that was read. The reply MUST be the text of the file to change.
- **FR-003**: A new ordinary file MUST contain the reply. An existing file MUST stay unchanged until the engineer approves. Approval MUST write the stored reply and MUST NOT ask the model again.
- **FR-004**: When the service cannot be reached, starting work MUST store nothing and MUST say `The model service could not be reached.` When the reply is empty, starting work MUST store nothing and MUST say `The model did not return file text.`
- **FR-005**: The task list MUST still link to Instructions. After work starts, the engineer MUST see that task and the model's reply.

### Key Entities

- **Model service**: The saved name, address, and optional key used for one model.
- **Model reply**: The file text returned for one start, stored with that change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An engineer can save a model service and see its name and address after the workspace is opened, in under 2 minutes.
- **SC-002**: In a review of starts that change an existing file, 100% leave the file unchanged until approval, and the waiting change shows the model's reply.
- **SC-003**: In a review of unreachable services and empty replies, 100% leave no task and no new file.
- **SC-004**: The Instructions page shows no model text field.

## Assumptions

- Specifications 001 through 023 are not rewritten. One start still reads one file and proposes one file. A replacement still waits for approval.
- The engineer chooses the model service. The key is optional because a local service may not require one.
- The page is available while the task manager is running. The engineer name and the time still come from the workspace.
- The rules are covered by automated checks.
