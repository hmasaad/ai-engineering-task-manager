# Research: Contextual Bandits with Linear Models and Neural Contextual Bandits

## Decision: An arm is separate from a bandit action and an exploration arm

An arm is a new named choice for this feature. It does not read or change the bandit actions from specification 045 or the exploration arms from specification 048. A task holds at most 2 arms and at most 2 contexts.

## Decision: A context carries two marks

Each mark is 0 or 1. The same context name keeps the marks from the first accepted command. A mark of 0 adds nothing to the matching weight.

## Decision: Weights are counted from pulls

Each arm starts with a first weight, a second weight, and a pair weight of 0. A pull adds its reward to the first weight when the first mark is 1, to the second weight when the second mark is 1, and to the pair weight when both marks are 1. The weights are counted when the engineer chooses. They are not stored as their own rows. A task holds at most 4 pulls.

## Decision: The neural score adds the pair only when both marks are 1

The linear score is the first weight times the first mark, plus the second weight times the second mark. The neural score adds the pair weight when both marks are 1. When either mark is 0, the neural score stays the linear score. The higher score wins. Equal scores keep the arm named first. The context, the model, and the chosen arm are stored. No float weight and no random draw are used.

## Decision: A new row removes the choice

A new arm, a new context, or a new pull removes the stored choice. The same names do not remove it. Opening the page does not choose again.

## Decision: The commands do not advance the workflow

Naming an arm, naming a context, recording a pull, and choosing an arm leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, or name an exploration arm.
