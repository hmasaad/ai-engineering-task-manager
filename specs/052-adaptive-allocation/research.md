# Research: Adaptive Resource Allocation for Workflow and Agent Optimization

## Decision: An allocation agent is separate from a worker

An agent is a new named worker for this feature. It does not read or change the workers from specifications 037 and 038, the tenants from specification 039, or the fidelity candidates from specification 051. A task holds at most 4 agents.

## Decision: A yield is one whole-number return

The value is 1 or 2, and a higher value is a better return from the workflow budget. An agent has at most one yield. A task holds at most 4 yields.

## Decision: The pool is 4 units and the next unit uses a product

The workflow budget is always 4 units. Each unit goes to the agent with the larger product. The product is that agent's yield multiplied by one more than the other agent's units already given in this allocation. An equal product keeps the agent stored first. The comparison does not divide and does not use a random sample. The same rows always store the same shares. A share of 0 is stored.

## Decision: A new row removes the shares

A new agent or a new yield removes the stored shares. The same names do not remove them. Opening the page does not allocate again.

## Decision: The commands do not advance the workflow

Naming an agent, recording a yield, and allocating the pool leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, or name a fidelity candidate.
