# Research: Distributed Bayesian Optimization and Decentralized Scheduling

## Decision: A point is separate from a search design

A point is a new named design for this feature. It has one setting of 1 or 2. It does not read or change the search designs from specification 050, the fidelity candidates from specification 051, the allocation agents from specification 052, or the hyperband trials from specification 053. A task holds at most 4 points. A node is one peer that keeps its own reports. A task holds at most 2 nodes. Nodes do not read or change the hyperband runners.

## Decision: A report is one node's local result

A report names one node, one point, and a score of 1 or 2. A higher score is a better local result. A node has at most one report for each point. A task holds at most 4 reports. The report count is checked before a repeated node and point, so a fifth report reports the count. No Gaussian process, no float, and no random sample are used.

## Decision: Each node suggests from its own reports

A node that has reported every point suggests nothing. A node with no report suggests the point stored first. A node with reports uses its best report: the higher score, and an equal score keeps the report stored first. An unreported point is as near as that best score when the setting matches, and one less when the setting differs. The higher nearness wins. An equal nearness keeps the point stored first. The same rows always suggest the same points.

## Decision: The agreement is the point most nodes suggest

The point suggested by the most nodes is the agreement. An equal number of suggestions keeps the point stored first. The named node is the node stored first among those that suggested that point. The suggestions and the agreement are stored when the engineer asks the nodes to agree. Opening the page does not agree again. When every node has reported every point, the engineer is told that no point is left to try.

## Decision: A new row removes the stored agreement

A new point, a new node, or a new report removes the suggestions and the agreement. The same names do not remove them. A refused report does not remove them.

## Decision: The commands do not advance the workflow

Naming a point, naming a node, recording a report, and agreeing leave the task status unchanged. They do not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, name an allocation agent, name a trial, name a runner, record a rung, or schedule a trial.
