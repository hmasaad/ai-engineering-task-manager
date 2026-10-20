# Tasks: Offline Reinforcement Learning and Policy Evaluation

**Input**: Design documents from `/specs/046-policy-evaluation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/commands.md

**Tests**: Test-first. The checks in T002 and T003 MUST fail before T004 through T008 are implemented.

## Phase 1: Setup

- [X] T001 Confirm `specs/046-policy-evaluation/plan.md`, `research.md`, `data-model.md`, `contracts/commands.md`, and `quickstart.md` exist.

## Phase 2: Foundational

- [X] T002 Write failing unit checks in `tests/unit/test_policy_evaluation.py` for a reward, a limit of 4 logged steps, a repeated name, one rule for one state, a replaced action, a matching score, a policy that matches nothing, a rolled-back score, and another task (FR-001, FR-002, FR-003).
- [X] T003 Write failing contract checks in `tests/contract/test_policy_evaluation_api.py` for the Policy section, Record logged step, Name policy rule, Evaluate policy, the score, the task status, and `GET /api/tasks` (FR-004).

## Phase 3: User Story 1 - Record a logged step (Priority: P1)

**Goal**: A named logged step keeps its state, action, and reward, and a task holds at most 4.

**Independent Test**: One stays rush, ada, reward 1 after a repeated name with reward 2.

- [X] T004 Add `eval_log` to `src/task_manager/storage/schema.sql` and record a logged step through `src/task_manager/domain/evaluation.py` and `src/task_manager/storage/evaluation_store.py` (FR-001).

## Phase 4: User Story 2 - Name the action a policy takes in a state (Priority: P2)

**Goal**: One state has one action, and a different action replaces it.

**Independent Test**: Rush takes ada. Naming rush takes grace replaces the action and removes the score.

- [X] T005 Add `eval_rule` and name a policy rule through the same domain and store (FR-002).

## Phase 5: User Story 3 - Score the policy on the log (Priority: P3)

**Goal**: The stored score counts only the logged steps that match the policy.

**Independent Test**: Rush takes grace and quiet takes ada. The score is a total of 4 from 2 steps.

- [X] T006 Add `eval_score` and store the matching total and count (FR-003).
- [X] T007 Expose Record logged step, Name policy rule, and Evaluate policy from `src/task_manager/workspace.py`, `src/task_manager/web/api.py`, and `src/task_manager/web/pages.py` (FR-003, FR-004).
- [X] T008 Show the Policy section in `src/task_manager/web/templates/detail.html` (FR-004).

## Phase 6: Polish

- [X] T009 Run `specs/046-policy-evaluation/quickstart.md` and confirm the existing suite stays green.

## Dependencies

T001 → T002 and T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Notes

- Each task maps to FR-001, FR-002, FR-003, or FR-004.
- A refusal rolls back the transaction.
- No new package. No column is added to an existing table.
