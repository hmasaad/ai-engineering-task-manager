# Research: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

## Decision: A trial is separate from a fidelity candidate

A trial is a new named configuration for this feature. It does not read or change the fidelity candidates from specification 051 or the allocation agents from specification 052. A task holds at most 4 trials. A runner is the agent that receives the next trial. A task holds at most 2 runners. Runners do not read or change the workers from specifications 037 and 038.

## Decision: One bracket has two rungs

Rung 1 is the early score. Rung 2 is the promoted score. Each score is 1 or 2, and a higher score is better. A trial has at most one score at each rung. A task holds at most 6 rung scores, which is four early scores plus two promoted scores.

## Decision: Promotion uses the scores recorded so far

The number promoted is half the number of rung 1 scores, dropping the remainder. A higher score is promoted first. Equal scores keep the trial stored first. The engineer does not wait until every named trial has a score. No random sample and no second bracket are used. The same rows always promote the same trials.

## Decision: The next trial goes to the least-loaded runner

The next assignment is the earliest promoted trial that has no rung 2 score and no assignment. It goes to the runner with the fewest assignments. An equal load keeps the runner stored first. Scheduling again does not assign that trial a second time. When every promoted trial has a rung 2 score, the winner is the higher of those scores, and an equal score keeps the trial stored first.

## Decision: A new row removes only the part that depends on it

A new trial, a new runner, or a new rung 1 score removes the promoted names, the assignments, and the winner. A new rung 2 score removes the winner and leaves the assignments. The same names do not remove them. Opening the page does not schedule again.

## Decision: The commands do not advance the workflow

Naming a trial, naming a runner, recording a rung score, and scheduling leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, or name an allocation agent.
