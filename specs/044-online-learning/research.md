# Research: Online Learning and Predictive Workflow Scheduling

## Decision: An outcome is a named row, separate from an activity or a schedule step

**Rationale**: Specifications 042 and 043 already own schedule steps and optimized activities. An outcome records what a kind of work actually took, on one In Progress task. Another task keeps its own outcomes. A task holds at most 4 outcomes so the counts stay small.

**Alternatives considered**: Adding a learned length to an activity would rewrite specification 043. A free number of outcomes would not change the rule, and the limit matches the other schedules on this task.

## Decision: The predicted length is a count of stored outcomes

**Rationale**: Each new outcome updates the count for its kind. The kind is predicted to take 2 days only when 2-day outcomes outnumber 1-day outcomes. A tie predicts 1 day. The count is read from the stored outcomes, so opening the task later does not change it and no extra model is required. A new outcome removes a stored schedule, because that schedule was built from the previous count.

**Alternatives considered**: A moving average would need a rounding rule for one and a half days. A wall-clock model would change the prediction when the page is opened later. A new learning package would add a dependency this workspace does not take.

## Decision: A forecast runs one at a time, oldest first

**Rationale**: A forecast is upcoming work of a kind that already has an outcome. The prediction stores the predicted length of that kind and a start day. Forecasts run one at a time in the order they were named. The next forecast starts when the previous one is predicted to finish. Day 0 is the first day. The same forecast name does not change the kind and does not remove the schedule. A new forecast removes the schedule.

**Alternatives considered**: Overlapping forecasts would repeat the capacity optimizer. Recomputing the schedule on every page view would change the starts when a new outcome arrives, without a prediction command.

## Decision: These commands do not advance the workflow

**Rationale**: An outcome, a forecast, and a predicted schedule are records on this task. They do not read a file, name an activity, or change the task status.

**Alternatives considered**: Creating a workflow action for each forecast would mix this feature with file reads and folder creation.
