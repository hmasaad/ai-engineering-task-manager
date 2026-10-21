# Feature Specification: Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling

**Feature Branch**: `053-asha-scheduling`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Asynchronous Hyperband, ASHA, and Distributed Agent Scheduling"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Name a trial and a runner (Priority: P1)

The engineer names a trial and a runner on an In Progress task. A trial is one configuration the workflow can measure. A runner is the agent that can carry out the next trial. A task holds at most 4 trials and at most 2 runners. The same trial name does not store the trial again. The same runner name does not store the runner again. A blank name is refused. A fifth trial is refused. A third runner is refused. A task that is not In Progress is refused. The task status stays as it was.

**Why this priority**: A rung score and a schedule can name a trial or a runner only after those names exist.

**Independent Test**: Name " red ", then name "red" again. The task still has one trial, red. Name " ada ", then name "ada" again. The task still has one runner, ada.

**Acceptance Scenarios**:

1. **Given** an In Progress task, **When** the engineer names " red " as a trial and " ada " as a runner, **Then** red and ada are listed.
2. **Given** red and ada are already named, **When** the engineer names them again, **Then** the task still has one trial and one runner.
3. **Given** four trials, **When** the engineer names a fifth, **Then** the engineer is told `This task already has 4 trials.` and the fifth is not stored.
4. **Given** two runners, **When** the engineer names a third, **Then** the engineer is told `This task already has 2 runners.` and the third is not stored.
5. **Given** a blank name, **When** the engineer names a trial, **Then** the engineer is told `Name this trial.` A blank runner is refused with `Name this runner.`
6. **Given** a task that is not In Progress, **When** the engineer names "red", **Then** the engineer is told `The task must be In Progress.` and nothing is stored.
7. **Given** red was named on one task, **When** the engineer names "red" on another task, **Then** that other task has its own trial.

---

### User Story 2 - Record a rung score (Priority: P2)

The engineer records a rung score for a trial. A rung score has a name, a trial, a rung, and a score. The rung is 1 or 2. Rung 1 is the early measurement. Rung 2 is the promoted measurement. The score is 1 or 2. A higher score is a better result. A trial has at most one score at each rung. A task holds at most 6 rung scores. The same rung-score name does not store the score again and does not change its trial, rung, or score. A rung 2 score is accepted only when at least two rung 1 scores exist and the trial is in the promoted half of those scores. The promoted half is the higher rung 1 scores, keeping half of the scored trials and dropping the remainder. Equal rung 1 scores keep the trial stored first. The engineer does not wait for every named trial. A new trial, a new runner, or a new rung 1 score removes the stored schedule. A new rung 2 score removes the winner and leaves the assignments. The same names do not remove them.

**Why this priority**: The promoted trials and the assignments are counted from these scores.

**Independent Test**: Record " one " for red at rung 1 with score 1. Record "one" again at rung 1 with score 2. The task still has one rung score, and that score stays 1.

**Acceptance Scenarios**:

1. **Given** trial red, **When** the engineer records " one " for " red " at rung 1 with score 1, **Then** the task lists one as red, rung 1, score 1.
2. **Given** that score, **When** the engineer records "one" again with score 2, **Then** one stays score 1.
3. **Given** a trial that is not on this task, **When** the engineer records a rung score for it, **Then** the engineer is told `That trial is not on this task.`
4. **Given** red already has a rung 1 score, **When** the engineer records another rung 1 score for red, **Then** the engineer is told `That trial already has this rung.`
5. **Given** six rung scores, **When** the engineer records a seventh, **Then** the engineer is told `This task already has 6 rung scores.`
6. **Given** a blank rung-score name, **When** the engineer records a score, **Then** the engineer is told `Name this rung score.` A blank trial is refused with `Name the trial.` A rung other than 1 or 2 is refused with `Name a rung of 1 or 2.` A score other than 1 or 2 is refused with `Name a score of 1 or 2.`
7. **Given** fewer than two rung 1 scores, **When** the engineer records rung 2, **Then** the engineer is told `Record two rung scores first.`
8. **Given** a trial that is outside the promoted half, **When** the engineer records rung 2 for it, **Then** the engineer is told `That trial is not promoted.`
9. **Given** a stored schedule, **When** the engineer records a new rung 1 score, **Then** the promoted trials, the assignments, and the winner are removed.
10. **Given** a stored winner, **When** the engineer records rung 2 for a trial that is not promoted, **Then** the engineer is told `That trial is not promoted.` and the winner stays.
11. **Given** a rung score that is rolled back, **When** the engineer opens the task, **Then** the other scores and the stored schedule are unchanged.

---

### User Story 3 - Schedule the next promoted trial (Priority: P3)

The engineer schedules the next trial. At least two rung 1 scores must exist, and the task must have a runner. The promoted trials are the better half of the rung 1 scores recorded so far. The number promoted is half the number of rung 1 scores, dropping the remainder. A higher score is promoted first. Equal scores promote the trial stored first. The next assignment is the earliest promoted trial that has no rung 2 score and no assignment yet. It goes to the runner with the fewest assignments. An equal load keeps the runner stored first. Scheduling again, while that trial is already assigned, does not add a second assignment. When every promoted trial has a rung 2 score, the winner is the promoted trial with the higher rung 2 score. Equal rung 2 scores choose the trial stored first. The promoted trials, the assignments, and the winner are stored with that schedule. Opening the task later does not schedule again. The task shows each trial, each runner, each rung score, the promoted trials, the assignments, and the winner. Name trial and Name runner are offered while the task is In Progress. Record rung is offered only while a trial exists. Schedule the next trial is offered only while two rung 1 scores and a runner exist. The task list stays the list of tasks.

**Why this priority**: The stored assignment is what the engineer reads after the early scores have been compared.

**Independent Test**: Red, blue, gold, and teal are named in that order. Their rung 1 scores are 1, 2, 2, and 1. Ada is named before grace. After all four rung 1 scores, the first schedule assigns blue to ada, and the second assigns gold to grace. Blue then scores 1 at rung 2 and gold scores 2. The next schedule names gold as the winner.

**Acceptance Scenarios**:

1. **Given** only red at rung 1 score 1 and blue at rung 1 score 2, and runner ada, **When** the engineer schedules, **Then** blue is promoted and the assignment is blue on ada.
2. **Given** all four rung 1 scores and runners ada and grace, **When** the engineer schedules twice, **Then** blue is on ada and gold is on grace.
3. **Given** those two assignments, blue's rung 2 score of 1, and gold's rung 2 score of 2, **When** the engineer schedules again, **Then** the winner is gold.
4. **Given** blue and gold both score 2 at rung 2, **When** the engineer schedules, **Then** the winner is blue, because blue was stored first.
5. **Given** red and blue both score 1 at rung 1, **When** the engineer schedules, **Then** red is promoted, because red was stored first.
6. **Given** red and blue both score 1, and gold then scores 2 at rung 1, **When** the engineer schedules, **Then** gold is promoted and red is not.
7. **Given** no trial, **When** the engineer schedules, **Then** the engineer is told `Name a trial first.`
8. **Given** trials but no runner, **When** the engineer schedules, **Then** the engineer is told `Name a runner first.`
9. **Given** fewer than two rung 1 scores, **When** the engineer schedules, **Then** the engineer is told `Record two rung scores first.`
10. **Given** a schedule that is rolled back, **When** the engineer opens the task, **Then** the previous assignments are unchanged.

### Edge Cases

- A name or a trial with surrounding spaces is the same text as the trimmed value.
- A rung and a score are accepted only when the trimmed text is 1 or 2.
- One request names one trial, names one runner, records one rung score, or schedules once.
- A task holds at most 4 trials, 2 runners, and 6 rung scores. A trial has at most one score at each rung.
- When six rung scores already exist, another score is refused with `This task already has 6 rung scores.` even when that trial already has that rung.
- Promotion uses the rung 1 scores recorded so far. Unscored trials stay out of the half.
- A rung 2 score can be recorded for a promoted trial before that trial is assigned to a runner.
- When two rung 1 scores are equal, the trial stored first is promoted.
- When two runners have the same number of assignments, the runner stored first receives the trial.
- When two rung 2 scores are equal, the trial stored first is the winner.
- Opening the task later does not change a stored schedule. A schedule changes only when the engineer schedules again, or when a new trial, a new runner, or a new rung score removes the part that command is allowed to remove.
- Naming a trial, naming a runner, recording a rung score, or scheduling does not read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, name an allocation agent, or change the task status.
- The task list stays the list of tasks.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engineer MUST be able to name a trial and a runner on an In Progress task. The first accepted use of a name MUST store it. The same name MUST NOT store it again. A task MUST hold at most 4 trials and at most 2 runners. A blank trial MUST be refused with `Name this trial.` A blank runner MUST be refused with `Name this runner.` A fifth trial MUST be refused with `This task already has 4 trials.` A third runner MUST be refused with `This task already has 2 runners.` A task that is not In Progress MUST be refused with `The task must be In Progress.` The same names on another task MUST apply only to that other task. A new trial or a new runner MUST remove the stored schedule. The same name MUST NOT remove it.
- **FR-002**: The engineer MUST be able to record a rung score with a name, a trial, a rung of 1 or 2, and a score of 1 or 2. The same name MUST NOT store the score again and MUST NOT change its fields. A trial MUST have at most one score at each rung. A task MUST hold at most 6 rung scores. A trial that is not on this task MUST be refused with `That trial is not on this task.` A second score for the same trial at the same rung MUST be refused with `That trial already has this rung.` A blank name MUST be refused with `Name this rung score.` A blank trial MUST be refused with `Name the trial.` A rung other than 1 or 2 MUST be refused with `Name a rung of 1 or 2.` A score other than 1 or 2 MUST be refused with `Name a score of 1 or 2.` A seventh score MUST be refused with `This task already has 6 rung scores.` Rung 2 before two rung 1 scores MUST be refused with `Record two rung scores first.` Rung 2 for a trial outside the promoted half MUST be refused with `That trial is not promoted.` A new rung 1 score MUST remove the promoted trials, the assignments, and the winner. A new rung 2 score MUST remove the winner and MUST leave the assignments. A rolled-back score MUST leave the other scores and the stored schedule as they were.
- **FR-003**: The engineer MUST be able to schedule the next trial. The promoted trials MUST be the better half of the rung 1 scores recorded so far. The number promoted MUST be half the number of those scores, dropping the remainder. A higher score MUST be promoted first. Equal scores MUST promote the trial stored first. The next new assignment MUST be the earliest promoted trial that has no rung 2 score and no assignment, and it MUST go to the runner with the fewest assignments. An equal load MUST choose the runner stored first. A repeated schedule MUST NOT assign that trial again. When every promoted trial has a rung 2 score, the winner MUST be the promoted trial with the higher rung 2 score. Equal rung 2 scores MUST choose the trial stored first. A task with no trial MUST be refused with `Name a trial first.` A task with no runner MUST be refused with `Name a runner first.` Fewer than two rung 1 scores MUST be refused with `Record two rung scores first.` A rolled-back schedule MUST restore the previous assignments.
- **FR-004**: The task page MUST show each trial, each runner, each rung score, the promoted trials, the assignments, and the winner. It MUST offer Name trial and Name runner while the task is In Progress, Record rung only while a trial exists, and Schedule the next trial only while two rung 1 scores and a runner exist. These commands MUST NOT read a file, create a folder, approve a change, deliver a message, commit a file, open a pull request, advance the workflow, place a job, admit a tenant, grant a turn, rank work, set an objective, name a schedule step, name an activity, record an outcome, name a bandit action, record a logged step, name a safe action, name an exploration arm, name a model arm, name a search design, name a fidelity candidate, name an allocation agent, or change the task status. The task list MUST stay the list of tasks.

### Key Entities

- **Trial**: The trimmed name of one configuration that can be measured.
- **Runner**: The trimmed name of one agent that can carry out a promoted trial.
- **Rung score**: One named measurement of one trial, at rung 1 or 2, with a score of 1 or 2.
- **Schedule**: The stored promoted trials, the assignments of promoted trials to runners, and the winner when every promoted trial has a rung 2 score.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a review of newly named trials and runners, 100% keep the first accepted name. A repeated name adds nothing. A fifth trial and a third runner are refused.
- **SC-002**: In a review of rung scores, 100% keep the rung and the score from the first accepted name. A second score for the same trial at the same rung is refused. A rung 2 score for a trial outside the promoted half is refused.
- **SC-003**: In a review of schedules, 100% of promoted sets are the better half of the rung 1 scores recorded so far, and 100% of new assignments go to the runner with the fewest assignments. Equal scores and equal loads choose the name stored first.
- **SC-004**: An engineer can see each trial, each runner, each rung score, the promoted trials, the assignments, and the winner on the task in one view.

## Assumptions

- Specifications 001 through 052 are not rewritten. Workflow actions, workers, schedule turns, priority ranks, objectives, schedule steps, optimized activities, learned forecasts, bandit choices, policy scores, safe probes, exploration draws, model choices, search recommendations, fidelity halvings, and allocation shares stay as they are.
- One bracket is used. Rung 1 is the early measurement. Rung 2 is the promoted measurement. A higher score is better. The half is taken from the scores recorded so far, so a later score can change who is promoted the next time the engineer schedules.
- A runner is the agent that receives the next trial. The same trials, runners, and scores always promote the same names and assign the same runner.
- A task holds at most 4 trials, 2 runners, and 6 rung scores. One schedule is stored. The promoted trials, the assignments, and the winner are counted when the engineer schedules.
- One engineer and one workspace. The same names on another task are a separate record.
- The rules are covered by automated checks.
