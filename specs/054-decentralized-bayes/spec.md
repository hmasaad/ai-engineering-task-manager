# Feature Specification: Distributed Bayesian Optimization and Decentralized Scheduling

**Feature Branch**: `054-decentralized-bayes`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Distributed Bayesian Optimization and Decentralized Scheduling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name a point and a node (Priority: P1)

The engineer names a point and a node on an In Progress task. A point is one design the nodes can try, and it has one setting of 1 or 2. A node is one peer that keeps its own reports. A task holds at most 4 points and at most 2 nodes. The same point name does not store the point again and does not change its setting. The same node name does not store the node again. A blank name is refused. A fifth point is refused. A third node is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A report and an agreement can name a point or a node only after those names exist.

**Independent Test**: Name " ada " with setting 1, then name "ada" again with setting 2. The task still has one point, ada, and its setting stays 1. Name " north ", then name "north" again. The task still has one node, north.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " ada " with setting 1 and " north " as a node, **Then** ada is listed with setting 1 and north is listed.
2. **Given** ada and north are already named, **When** the engineer names them again, **Then** the task still has one point and one node, and ada's setting stays 1.
3. **Given** four points, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 points.` and the fifth is not stored.
4. **Given** two nodes, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 nodes.` and the third is not stored.
5. **Given** a blank name, **When** the engineer names a point, **Then** the engineer is told `Name this point.` A blank node is refused with `Name this node.` A setting other than 1 or 2 is refused with `Name a setting of 1 or 2.`
6. **Given** a task that is not In Progress, **When** the engineer names "ada", **Then** the engineer is told `The task must be In Progress.` and nothing is stored.
7. **Given** ada was named on one task, **When** the engineer names "ada" on another task, **Then** that other task has its own point.

---

### User Story 2 - Record a local report (Priority: P2)

The engineer records a report for one node and one point. A report has a name, a node, a point, and a score of 1 or 2. A higher score is a better local result. A node has at most one report for each point. A task holds at most 4 reports. The same report name does not store the report again and does not change its node, point, or score. A new point, a new node, or a new report removes the stored agreement. The same names do not remove it. A refused report does not remove it.

**Why this priority**: Each node's suggestion is counted from the reports that node has stored.

**Independent Test**: Record " one " for north on ada with score 2. Record "one" again for north on ada with score 1. The task still has one report, and that score stays 2.

**Acceptance Scenarios**:

1. **Given** point ada and node north, **When** the engineer records " one " for " north " on " ada " with score 2, **Then** the task lists one as north, ada, score 2.
2. **Given** that report, **When** the engineer records "one" again with score 1, **Then** one stays score 2.
3. **Given** a node that is not on this task, **When** the engineer records a report for it, **Then** the engineer is told `That node is not on this task.`
4. **Given** a point that is not on this task, **When** the engineer records a report for it, **Then** the engineer is told `That point is not on this task.`
5. **Given** north already reported ada, **When** the engineer records another report for north on ada, **Then** the engineer is told `That node already reported this point.`
6. **Given** four reports, **When** the engineer records a fifth, **Then** the engineer is told `This task already has 4 reports.`
7. **Given** a blank report name, **When** the engineer records a report, **Then** the engineer is told `Name this report.` A blank node is refused with `Name the node.` A blank point is refused with `Name the point.` A score other than 1 or 2 is refused with `Name a score of 1 or 2.`
8. **Given** a stored agreement, **When** the engineer records a new report, **Then** the suggestions and the agreement are removed.
9. **Given** a report that is rolled back, **When** the engineer opens the task, **Then** the other reports and the stored agreement are unchanged.

---

### User Story 3 - Agree on the next point (Priority: P3)

The engineer asks the nodes to agree on the next point. At least one report must exist, and the task must have a point and a node. Each node suggests one point it has not reported. A node that has reported every point suggests nothing. A node with no report suggests the point stored first. A node with reports suggests the unreported point nearest its best report. The best report is the higher score, and an equal score keeps the report stored first. The nearness of an unreported point is that best score when the setting matches, and one less when the setting differs. The higher nearness wins. An equal nearness keeps the point stored first. The agreement is the point suggested by the most nodes. An equal number of suggestions keeps the point stored first. The node named in the agreement is the node stored first among those that suggested that point. The suggestions and the agreement are stored with that request. Opening the task later does not agree again. The task shows each point, each node, each report, each suggestion, and the agreement. Name point and Name node are offered while the task is In Progress. Record report is offered only while a point and a node exist. Agree on a design is offered only while a report exists. The task list stays the list of tasks.

**Why this priority**: The stored agreement is what the engineer reads after the nodes have compared their own reports.

**Independent Test**: Ada with setting 1, grace with setting 2, and mina with setting 1 are named in that order. North is named before south. North reports ada with score 2, and south reports ada with score 1. The agreement is mina on north, with 2 suggestions.

**Acceptance Scenarios**:

1. **Given** ada setting 1, grace setting 2, and mina setting 1, and reports of north on ada with score 2 and south on ada with score 1, **When** the engineer asks the nodes to agree, **Then** north and south both suggest mina, and the agreement is mina on north with 2 suggestions.
2. **Given** north reports ada setting 1 with score 2 and south reports grace setting 2 with score 2, **When** the engineer asks the nodes to agree, **Then** north suggests mina, south suggests ada, and the agreement is ada on south with 1 suggestion.
3. **Given** only north has a report, on ada with score 2, **When** the engineer asks the nodes to agree, **Then** south suggests ada, north suggests mina, and the agreement is ada on south with 1 suggestion.
4. **Given** ada setting 1, grace setting 2, mina setting 1, and nora setting 2, and north reports grace with score 2 before reporting ada with score 2, **When** the engineer asks the nodes to agree, **Then** north suggests nora.
5. **Given** one point that both nodes have reported, **When** the engineer asks the nodes to agree, **Then** the engineer is told `No point is left to try.`
6. **Given** no point, **When** the engineer asks the nodes to agree, **Then** the engineer is told `Name a point first.`
7. **Given** points but no node, **When** the engineer asks the nodes to agree, **Then** the engineer is told `Name a node first.`
8. **Given** no report, **When** the engineer asks the nodes to agree, **Then** the engineer is told `Record a report first.`
9. **Given** an agreement that is rolled back, **When** the engineer opens the task, **Then** the previous agreement is unchanged.

### Edge Cases

- A name, a node, or a point with surrounding spaces is the same text as the trimmed value.
- A setting and a score are accepted only when the trimmed text is 1 or 2.
- One request names one point, names one node, records one report, or agrees once.
- A task holds at most 4 points, 2 nodes, and 4 reports. A node has at most one report for each point.
- When four reports already exist, another report is refused with `This task already has 4 reports.` even when that node already reported that point.
- A node with no report suggests the point stored first, including a point another node has already reported.
- A node that has reported every point makes no suggestion.
- When two unreported points are equally near a node's best report, the point stored first is suggested.
- When two reports have the same score, the report stored first is that node's best report.
- When two points have the same number of suggestions, the point stored first is the agreement.
- When two nodes suggest the winning point, the node stored first is named in the agreement.
- Opening the task later does not change a stored agreement. An agreement changes only when the engineer asks the nodes to agree again, or when a new point, a new node, or a new report removes it.
- Naming a point, naming a node, recording a report, or agreeing does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, name an allocation agent, name a trial, name a runner, record a rung, schedule a trial, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a point with a setting of 1 or 2, and a node, on an In Progress task. The first accepted use of a name MUST store it. The same name MUST NOT store it again and MUST NOT change a stored setting. A task MUST hold at most 4 points and at most 2 nodes. A blank point MUST be refused with `Name this point.` A blank node MUST be refused with `Name this node.` A setting other than 1 or 2 MUST be refused with `Name a setting of 1 or 2.` A fifth point MUST be refused with `This task already has 4 points.` A third node MUST be refused with `This task already has 2 nodes.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task. A new point or a new node MUST remove the stored agreement. The same name MUST NOT remove it.
- **FR-002**: The engineer MUST be able to record a report with a name, a node, a point, and a score of 1 or 2. The same name MUST NOT store the report again and MUST NOT change its fields. A node MUST have at most one report for each point. A task MUST hold at most 4 reports. A node that is not on this task MUST be refused with `That node is not on this task.` A point that is not on this task MUST be refused with `That point is not on this task.` A second report for the same node and point MUST be refused with `That node already reported this point.` A blank name MUST be refused with `Name this report.` A blank node MUST be refused with `Name the node.` A blank point MUST be refused with `Name the point.` A score other than 1 or 2 MUST be refused with `Name a score of 1 or 2.` A fifth report MUST be refused with `This task already has 4 reports.` A new report MUST remove the suggestions and the agreement. A refused report MUST leave them. A rolled-back report MUST leave the other reports and the stored agreement as they were.
- **FR-003**: The engineer MUST be able to ask the nodes to agree on the next point. Each node MUST suggest one point it has not reported. A node with no report MUST suggest the point stored first. A node with reports MUST suggest the unreported point nearest its best report. The best report MUST be the higher score, and an equal score MUST keep the report stored first. Nearness MUST be that best score when the setting matches and one less when the setting differs. The higher nearness MUST win, and an equal nearness MUST keep the point stored first. The agreement MUST be the point suggested by the most nodes. An equal number of suggestions MUST keep the point stored first. The named node MUST be the node stored first among those that suggested that point. A task with no point MUST be refused with `Name a point first.` A task with no node MUST be refused with `Name a node first.` A task with no report MUST be refused with `Record a report first.` A task where every node has reported every point MUST be refused with `No point is left to try.` A rolled-back agreement MUST restore the previous agreement.
- **FR-004**: The task page MUST show each point, each node, each report, each suggestion, and the agreement. It MUST offer Name point and Name node while the task is In Progress, Record report only while a point and a node exist, and Agree on a design only while a report exists. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, name an allocation agent, name a trial, name a runner, record a rung, schedule a trial, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Point**: The trimmed name of one design, with a setting of 1 or 2.
- **Node**: The trimmed name of one peer that keeps its own reports.
- **Report**: One named local result of one node on one point, with a score of 1 or 2.
- **Agreement**: The stored suggestions and the point chosen by the most nodes, together with the earliest node that suggested it and the number of suggestions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named points and nodes, 100% keep the first accepted name and setting. A repeated name adds nothing. A fifth point and a third node are refused.
- **SC-002**: In a review of reports, 100% keep the node, the point, and the score from the first accepted name. A second report for the same node and point is refused. A fifth report is refused.
- **SC-003**: In a review of agreements, 100% of suggestions follow each node's own reports, and 100% of agreements name the point suggested by the most nodes. Equal nearness and equal suggestion counts choose the name stored first.
- **SC-004**: An engineer can see each point, each node, each report, each suggestion, and the agreement on the task in one view.

## Assumptions

- Specifications 001 through 053 are not rewritten. Workflow actions, workers, schedule turns, priority ranks, objectives, schedule steps, optimized activities, learned forecasts, bandit choices, policy scores, safe probes, exploration draws, model choices, search recommendations, fidelity halvings, allocation shares, and hyperband schedules stay as they are.
- One setting stands in for a design. A score of 2 is a better local result than a score of 1. A node suggests from its own reports. The agreement is the point the most nodes suggest. The same points, nodes, and reports always suggest the same names.
- A node with no report suggests the point stored first. A node that has reported every point suggests nothing.
- A task holds at most 4 points, 2 nodes, and 4 reports. One agreement is stored. The suggestions and the agreement are counted when the engineer asks the nodes to agree.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
