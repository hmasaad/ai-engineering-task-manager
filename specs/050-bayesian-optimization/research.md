# Research: Constrained and Multi-Objective Bayesian Optimization

## Decision: A design is separate from an optimized activity

A design is a new named point for this feature. It does not read or change the activities from specification 043, the bandit actions from specification 045, the exploration arms from specification 048, or the model arms from specification 049. A task holds at most 4 designs.

## Decision: An observation carries two objectives and one constraint

Each objective is 1 or 2, and a higher score is better. A constraint of 1 is feasible. A constraint of 2 is violated. A design has at most one observation. A task holds at most 4 observations.

## Decision: The front drops violated and dominated observations

A feasible observation dominates another when both objectives are at least as high and one is higher. The front keeps the feasible observations that are not dominated, oldest observation first. Violated observations stay off the front.

## Decision: The next design uses the nearest feasible observation

An unobserved design scores the neighbor's objective total minus the number of setting differences. The neighbor is the feasible observation with the fewest differences. A higher objective total breaks a distance tie. The observation stored first breaks a total tie. Equal design scores keep the design stored first. No Gaussian process and no random sample are used. The same rows always recommend the same design.

## Decision: A new row removes the recommendation

A new design or a new observation removes the stored front and the next design. The same names do not remove them. Opening the page does not recommend again.

## Decision: The commands do not advance the workflow

Naming a design, recording an observation, and recommending a design leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, or name a model arm.
