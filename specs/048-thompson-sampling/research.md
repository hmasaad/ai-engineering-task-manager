# Research: Multi-Armed Bandits, Thompson Sampling, and Contextual Exploration

## Decision: An arm is separate from a bandit action

An arm is a new named choice for this feature. It does not read or change the bandit actions from specification 045. A task holds at most 2 arms and at most 2 contexts.

## Decision: A pull is a win or a loss in one context

A reward of 2 adds one win. A reward of 1 adds one loss. Pulls in another context do not change the scores. A task holds at most 4 pulls. The same pull name keeps the first reward.

## Decision: Three fixed samples stand in for a random draw

Each arm starts with one imagined win and one imagined loss. The middle score is twice the wins, after the imagined win, minus the losses, after the imagined loss. The high score adds 4 with no pulls in that context, 1 with one pull, and 0 with two or more. The low score is the middle score minus 1. Draws use middle, then high, then low, and then repeat. The higher score wins. Equal scores keep the arm named first. The chosen arm and the sample name are stored. A random sample would change the result between replays, so it is not used.

## Decision: A new row removes the draw and restarts the sample

A new arm, a new context, or a new pull removes the stored draw. The next draw uses the middle score. The same names do not remove it. Opening the page does not draw again.

## Decision: The commands do not advance the workflow

Naming an arm, naming a context, recording a pull, and drawing an arm leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, or name a safe action.
