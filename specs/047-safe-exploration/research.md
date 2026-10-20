# Research: Safe Exploration, Causal Inference, and Counterfactual Evaluation

## Decision: An action carries a risk, separate from a bandit action

**Rationale**: Specification 045 already owns online choices. An action here is a named risk on one In Progress task. Risk 1 may be explored. Risk 2 may not. A task holds at most 2 actions. Another task keeps its own actions.

**Alternatives considered**: Adding a risk column to a bandit action would rewrite specification 045. A free number of actions would hide the one-to-one comparison this feature is for.

## Decision: A probe is allowed only for risk 1

**Rationale**: Exploration records one reward for one action in one state. The probe is refused when the action's risk is 2, and nothing is stored. The same probe name does not change the reward. A new probe removes the stored effect, because that effect was built from the previous probes.

**Alternatives considered**: Letting a risk-2 action be probed would remove the safety bound. Reusing a logged step from specification 046 would mix the fixed log with a new exploration.

## Decision: The effect is the reward difference in one state

**Rationale**: The comparison names one action and the action it replaces, in one state. The effect is the earliest reward of the named action in that state minus the earliest reward of the replaced action in that state. The state is the same, so the change comes from the action. The effect is stored with the comparison. Opening the task later does not change it.

**Alternatives considered**: Averaging every probe would hide which probe counted. A comparison across two states would mix the state change with the action change.

## Decision: These commands do not advance the workflow

**Rationale**: An action, a probe, and an effect are records on this task. They do not read a file, record a logged step, or change the task status.

**Alternatives considered**: Creating a workflow action for each probe would mix this feature with file reads and folder creation.
