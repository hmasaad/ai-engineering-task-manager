# Research: Constraint Programming and Optimization for Workflow Scheduling

## Decision: An activity is a named row, separate from a schedule step

**Rationale**: Specification 042 already owns schedule steps, one predecessor, and a critical path. An activity is a named length on one In Progress task, used only by this optimizer. Another task keeps its own activities. A task holds at most 4 activities so every legal start can be checked.

**Alternatives considered**: Adding a capacity column to a schedule step would rewrite specification 042. A free number of activities would make an exact check too large for this workspace.

## Decision: A constraint is one precedence pair, and an activity may have several

**Rationale**: The constraint is that one activity cannot start until an earlier activity has finished. Several earlier activities are allowed, which a single predecessor cannot express. The same pair is stored once. A self-link and a cycle are refused and store nothing.

**Alternatives considered**: One predecessor would repeat the schedule-step rule. A free-text constraint would not be checkable.

## Decision: Capacity is 1 or 2, and the plan minimizes the finish day

**Rationale**: Capacity is how many activities may run on the same day. Two values are enough to show a packed schedule and a one-at-a-time schedule. The optimizer checks the legal start days, keeps the schedule that finishes earliest, and breaks a tie by starting the earliest-named activity sooner, then the next. The plan is stored with the optimization. A new activity, a new constraint, or a different capacity removes that plan. Opening the task later does not change it.

**Alternatives considered**: Recomputing the plan on every page view would change the starts when the rows change, without an optimization command. A wall-clock deadline would repeat the objective feature.

## Decision: These commands do not advance the workflow

**Rationale**: An activity, a constraint, a capacity, and a plan are records on this schedule. They do not read a file, name a schedule step, or change the task status.

**Alternatives considered**: Creating a workflow action for each activity would mix this feature with file reads and folder creation.
