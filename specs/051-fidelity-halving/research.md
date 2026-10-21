# Research: Multi-Fidelity Bayesian Optimization and Successive Halving

## Decision: A candidate is separate from a search design

A candidate is a new named design for this feature. It does not read or change the activities from specification 043, the bandit actions from specification 045, the exploration arms from specification 048, the model arms from specification 049, or the search designs from specification 050. A task holds at most 4 candidates.

## Decision: Fidelity 1 is cheap and fidelity 2 is expensive

Each measurement has one fidelity and one score. Both are 1 or 2. A higher score is better. A candidate has at most one measurement at each fidelity. A task holds at most 6 measurements, which is four cheap measurements plus the two expensive measurements of a kept half.

## Decision: Halving keeps the better half of the cheap scores

The number kept is half the number of candidates, dropping the remainder. Four candidates keep two. Three candidates keep one. Two candidates keep one. A higher cheap score is kept first. Equal cheap scores keep the candidate stored first. Every candidate must already have a cheap measurement.

## Decision: The expensive score names the winner among the kept names

The winner is stored only when every kept candidate has a fidelity 2 measurement. The higher expensive score wins. Equal expensive scores choose the candidate stored first. A candidate who was not kept cannot be measured at fidelity 2. No Gaussian process and no random sample are used. The same rows always keep the same names and name the same winner.

## Decision: A new row removes only the part that depends on it

A new candidate or a new cheap measurement removes the kept names and the winner. A new expensive measurement removes the winner and leaves the kept names. The same names do not remove them. Opening the page does not halve again.

## Decision: The commands do not advance the workflow

Naming a candidate, recording a measurement, and halving the field leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, or name a search design.
