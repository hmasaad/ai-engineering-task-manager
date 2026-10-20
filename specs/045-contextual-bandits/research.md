# Research: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

## Decision: An action and a context are named rows, separate from a forecast

**Rationale**: Specification 044 already owns outcomes and predicted lengths. An action is one way the work can be done. A context is the situation. Another task keeps its own rows. A task holds at most 2 actions and 4 contexts so the comparison stays small.

**Alternatives considered**: Adding a reward column to a forecast would rewrite specification 044. A free number of actions would hide the two-choice comparison this feature is for.

## Decision: A trial stores one reward, and the value is the average of those rewards

**Rationale**: Each new trial adds its reward to one action in one context. The learned value is the total reward divided by the number of trials. The comparison uses the totals and the counts, so one and a half does not need rounding. A new trial removes the stored choice, because that choice was made from the previous totals. Opening the task later does not change the totals.

**Alternatives considered**: A new learning package would add a dependency this workspace does not take. A random explore step would make the same trials produce a different choice.

## Decision: The choice tries an untried action, then takes the higher average

**Rationale**: Before every action has a trial in the context, the choice is the earliest-named action that has no trial there. After that, the choice is the higher average, and an equal average keeps the action named first. Trials in another context do not count. The choice is stored with the request.

**Alternatives considered**: Always taking the higher average would never try the second action after the first reward. Recomputing the choice on every page view would change it when a trial arrives, without a choose command.

## Decision: These commands do not advance the workflow

**Rationale**: An action, a context, a trial, and a choice are records on this task. They do not read a file, record an outcome, or change the task status.

**Alternatives considered**: Creating a workflow action for each choice would mix this feature with file reads and folder creation.
