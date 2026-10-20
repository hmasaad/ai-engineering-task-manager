# Research: Offline Reinforcement Learning and Policy Evaluation

## Decision: A logged step is a named row, separate from a bandit trial

**Rationale**: Specification 045 already owns online choices and rewards. A logged step is a past decision that stays fixed while a policy is scored. Another task keeps its own log. A task holds at most 4 logged steps so the total stays small.

**Alternatives considered**: Scoring the bandit trials would rewrite specification 045. A free number of steps would not change the rule, and the limit matches the other schedules on this task.

## Decision: A policy rule names one action for one state in the log

**Rationale**: The policy is the action the engineer says to take in a state that already appears in a logged step. One state has one rule. The same state and the same action are stored once. A different action replaces the rule and removes the stored score, because that score was built for the previous action.

**Alternatives considered**: A rule for a state that never appears in the log could not match a step. Several actions for one state would not say which action the policy takes.

## Decision: The score counts only the logged steps that match the policy

**Rationale**: A logged step counts when its state has a rule and its action is the action that rule names. The score stores the total of those rewards and the number of those steps. A step whose state has no rule is left out. The score is stored with the evaluation. A new logged step or a changed rule removes it. Opening the task later does not change it.

**Alternatives considered**: Recomputing the score on every page view would change the numbers when a step arrives, without an evaluation command. A random policy would make the same log produce a different score.

## Decision: These commands do not advance the workflow

**Rationale**: A logged step, a rule, and a score are records on this task. They do not read a file, name a bandit action, or change the task status.

**Alternatives considered**: Creating a workflow action for each rule would mix this feature with file reads and folder creation.
