# Feature Specification: Online Learning and Predictive Workflow Scheduling

**Feature Branch**: `044-online-learning`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "implement Online Learning and Predictive Workflow Scheduling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record how long a kind of work took (Priority: P1)

The engineer records an outcome on an In Progress task. The outcome has a name, a kind of work, and an actual length of 1 or 2. A length of 1 is one day. A length of 2 is two days. A task holds at most 4 outcomes. The same outcome name does not store the outcome again and does not change its kind or its length. A blank name is refused. A blank kind is refused. A length other than 1 or 2 is refused. A fifth outcome is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A prediction can be learned only after the engineer has recorded what actually happened.

**Independent Test**: Record " past " for kind " review " with length 2. Record "past" again with kind "export" and length 1. The task still has one outcome, and it stays "review took 2".

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer records " past " for kind " review " with length 2, **Then** the task lists past as review took 2.
2. **Given** that outcome, **When** the engineer records "past" again with kind "export" and length 1, **Then** past stays review took 2.
3. **Given** four outcomes, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 outcomes.` and the fifth is not stored.
4. **Given** a blank name, **When** the engineer records an outcome, **Then** the engineer is told `Name this outcome.`
5. **Given** a blank kind, **When** the engineer records "past" with length 1, **Then** the engineer is told `Name this kind.` and no outcome is stored.
6. **Given** the length "3", **When** the engineer records "note" for kind "review", **Then** the engineer is told `Name a length of 1 or 2.` and no outcome is stored.
7. **Given** a task that is not In Progress, **When** the engineer records "past" for kind "review" with length 1, **Then** the engineer is told `The task must be In Progress.` and no outcome is stored.
8. **Given** an outcome named "past" on one task, **When** the engineer records "past" for kind "export" with length 1 on another task, **Then** that other task has its own outcome.

---

### User Story 2 - Learn a predicted length for each kind (Priority: P2)

Each new outcome updates the predicted length of its kind. The prediction counts how many outcomes of that kind took 1 day and how many took 2 days. The kind is predicted to take 2 days only when the 2-day outcomes outnumber the 1-day outcomes. Otherwise the kind is predicted to take 1 day, including when the two counts are equal. The task lists each kind that has an outcome, oldest kind first, with that prediction. A later outcome of the same kind changes the prediction. Opening the task later does not change the prediction, because it is counted from the stored outcomes.

**Why this priority**: The engineer needs to see what the task has learned before a schedule is built from it.

**Independent Test**: Record review taking 1 day, then review taking 2 days. Review is still predicted to take 1 day. Record review taking 2 days again. Review is predicted to take 2 days.

**Acceptance Scenarios**:

1. **Given** one review outcome of 1 day, **When** the engineer opens the task, **Then** review is predicted to take 1 day.
2. **Given** one review outcome of 1 day and one of 2 days, **When** the engineer opens the task, **Then** review is still predicted to take 1 day.
3. **Given** one review outcome of 1 day and two of 2 days, **When** the engineer opens the task, **Then** review is predicted to take 2 days.
4. **Given** review was recorded before export, **When** the engineer opens the task, **Then** review is listed before export.
5. **Given** a stored prediction of the schedule, **When** the engineer records a new outcome, **Then** that schedule is removed and the kind prediction uses the new count.

---

### User Story 3 - Predict a schedule for upcoming work (Priority: P3)

The engineer names a forecast. A forecast is upcoming work of a kind that already has an outcome. The same forecast name does not store the forecast again and does not change its kind. A task holds at most 4 forecasts. The engineer then predicts the schedule. Each forecast receives the predicted length of its kind at that moment, and a start day. Forecasts run one at a time, oldest first. Day 0 is the first day. The next forecast starts on the day the previous forecast is predicted to finish. The finish day is the day the last forecast is predicted to finish. The schedule is stored with that prediction. A new outcome or a new forecast removes the stored schedule. The same forecast name does not remove it. The task shows each outcome, each learned kind, each forecast, and the finish day. Record outcome is offered while the task is In Progress. Name forecast is offered only while an outcome exists. Predict schedule is offered only while a forecast exists. The task list stays the list of tasks.

**Why this priority**: The stored schedule is what the engineer reads after the task has learned from the outcomes.

**Independent Test**: Review has two outcomes of 2 days. Export has one outcome of 1 day. Forecast "draft" is review, and forecast "ship" is export. The prediction starts draft on day 0 for 2 days and ship on day 2 for 1 day. The finish day is 3.

**Acceptance Scenarios**:

1. **Given** those outcomes and forecasts, **When** the engineer predicts the schedule, **Then** draft is predicted to take 2 days and starts on day 0, ship is predicted to take 1 day and starts on day 2, and the finish day is 3.
2. **Given** that schedule, **When** the engineer names "draft" again with kind "export", **Then** draft stays review and the schedule stays in place.
3. **Given** a stored schedule, **When** the engineer names a new forecast, **Then** the schedule is removed and can be predicted again.
4. **Given** no outcome for kind "audit", **When** the engineer names a forecast of audit, **Then** the engineer is told `Record an outcome for that kind first.`
5. **Given** no forecast, **When** the engineer predicts the schedule, **Then** the engineer is told `Name a forecast first.`
6. **Given** four forecasts, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 forecasts.`
7. **Given** a blank forecast name, **When** the engineer names a forecast, **Then** the engineer is told `Name this forecast.` A blank kind is refused with `Name the kind of work.`
8. **Given** a prediction that is rolled back, **When** the engineer opens the task, **Then** the previous schedule is unchanged.

### Edge Cases

- A name or a kind with surrounding spaces is the same text as the trimmed value.
- A length is accepted only when the trimmed text is 1 or 2.
- One request records one outcome, names one forecast, or predicts once.
- A task holds at most 4 outcomes and at most 4 forecasts.
- Equal counts of 1-day and 2-day outcomes predict 1 day.
- Opening the task later does not change a stored schedule. A schedule changes only when the engineer predicts again, or when a new outcome or a new forecast removes it.
- Recording an outcome, naming a forecast, or predicting a schedule does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to record an outcome on an In Progress task with a name, a kind, and a length of 1 or 2. The first accepted use of that name MUST store the outcome. The same name MUST NOT store the outcome again and MUST NOT change its kind or its length. A task MUST hold at most 4 outcomes. A blank name MUST be refused with `Name this outcome.` A blank kind MUST be refused with `Name this kind.` A length other than 1 or 2 MUST be refused with `Name a length of 1 or 2.` A fifth outcome MUST be refused with `This task already has 4 outcomes.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task.
- **FR-002**: Each kind that has an outcome MUST show a predicted length. The prediction MUST be 2 only when the 2-day outcomes of that kind outnumber the 1-day outcomes. Otherwise the prediction MUST be 1, including a tie. Kinds MUST be listed oldest first. A new outcome MUST update that count and MUST remove a stored schedule. A rolled-back outcome MUST leave the other outcomes and any stored schedule as they were.
- **FR-003**: The engineer MUST be able to name a forecast of a kind that already has an outcome, and then predict a schedule. The same forecast name MUST NOT store the forecast again and MUST NOT change its kind or remove the schedule. A task MUST hold at most 4 forecasts. Forecasts MUST run one at a time, oldest first. Each forecast MUST receive the predicted length of its kind, and the next forecast MUST start when the previous one is predicted to finish. Day 0 is the first day. A new forecast MUST remove the stored schedule. A kind with no outcome MUST be refused with `Record an outcome for that kind first.` A blank forecast name MUST be refused with `Name this forecast.` A blank kind MUST be refused with `Name the kind of work.` A fifth forecast MUST be refused with `This task already has 4 forecasts.` A prediction with no forecast MUST be refused with `Name a forecast first.` A rolled-back prediction MUST restore the previous schedule.
- **FR-004**: The task page MUST show each outcome, each learned kind, each forecast, and the finish day. It MUST offer Record outcome while the task is In Progress, Name forecast only while an outcome exists, and Predict schedule only while a forecast exists. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Outcome**: The trimmed name of one recorded result, the kind of work, and the actual length of 1 or 2 days.
- **Learned kind**: A kind that has at least one outcome, and the predicted length counted from those outcomes.
- **Forecast**: Upcoming work of one learned kind.
- **Predicted schedule**: The stored predicted length and start day of each forecast, and the finish day, produced by one prediction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly recorded outcomes, 100% keep the kind and the length the engineer gave. A repeated name adds no outcome and changes nothing. A fifth outcome is refused.
- **SC-002**: In a review of learned kinds, 100% predict 2 days only when 2-day outcomes outnumber 1-day outcomes, and predict 1 day otherwise.
- **SC-003**: In a review of predicted schedules, 100% place forecasts one at a time in the order they were named, using the predicted length of each kind. The finish day is the end of the last forecast.
- **SC-004**: An engineer can see each outcome, each learned kind, each forecast, and the finish day on the task in one view.

## Assumptions

- Specifications 001 through 043 are not rewritten. Workflow actions, schedule steps, objectives, priority ranks, tenants, workers, and optimized activities stay as they are.
- A length of 1 is one day. A length of 2 is two days. Day 0 is the first day.
- A task holds at most 4 outcomes and at most 4 forecasts. The prediction counts those outcomes and stores one schedule.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
