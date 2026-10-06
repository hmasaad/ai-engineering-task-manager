<!--
Sync Impact Report
- Version change: unratified template → 1.0.0
- Modified principles:
  - [PRINCIPLE_1_NAME] → I. Clear Requirements
  - [PRINCIPLE_2_NAME] → II. Test-First Verification
  - [PRINCIPLE_3_NAME] → III. Explicit Task State
  - [PRINCIPLE_4_NAME] → IV. Requirement-to-Verification Traceability
  - [PRINCIPLE_5_NAME] → V. Deterministic Behavior
- Added principles:
  - VI. Observable AI Actions
  - VII. Human Approval for Consequential Actions
  - VIII. Small, Independently Verifiable Changes
- Added sections:
  - Engineering Pipeline (replaces [SECTION_2_NAME])
  - Quality Gates (replaces [SECTION_3_NAME])
- Removed sections: none
- Follow-up TODOs: none
- Rationale: Initial ratification. The previous file was an unfilled scaffold,
  so this starts at 1.0.0 rather than amending a prior constitution.
-->

# AI Engineering Task Manager Constitution

## Core Principles

### I. Clear Requirements

A unit of work MUST NOT start until its requirement names the actor, the
outcome, the constraints, and the observable acceptance criteria. Wording that
cannot be checked (for example "improve", "handle", or "make it better") MUST
be rewritten into pass/fail conditions before planning or implementation. A
requirement that cannot be verified is incomplete and MUST be clarified before
tasks are created.

Rationale: Later stages can execute only what they can check. Vague
requirements produce work whose success cannot be judged from evidence.

### II. Test-First Verification

Verification MUST be defined before implementation. For each requirement, the
check, the evidence that will prove it, and the condition that counts as done
MUST exist before the corresponding implementation is written. Implementation
is complete only when those checks pass against the stated requirement. A
passing result that does not map to an acceptance criterion does not count.

Rationale: Checks written after the code let the implementation redefine
success. The requirement decides what "done" means.

### III. Explicit Task State

Every task MUST occupy exactly one named state at a time. The allowed states
and transitions MUST be defined in stored data, and every transition MUST
record what caused it and when. Hidden, implied, or overloaded states are
forbidden. A reader MUST be able to determine a task's state from stored data
without inferring it from conversation or from the absence of a field.

Rationale: Decomposition, scheduling, and later autonomy all depend on one
state machine that humans and agents read the same way.

### IV. Requirement-to-Verification Traceability

Every change MUST be traceable in both directions along requirement → task →
implementation → verification → evidence. A requirement with no task, a task
with no verification, or a verification result with no requirement is
incomplete. Evidence MUST identify the requirement and the task it closes.

Rationale: The path from intent to proof is the record later autonomous work
will reuse. A break in that chain makes the decision unauditable.

### V. Deterministic Behavior

Given the same inputs, stored state, and configuration, the system MUST
produce the same task transitions, ordering, and outputs. A step that is
inherently non-deterministic (model output, clock, or an external system)
MUST be isolated, named, and recorded with its input and output so the rest
of the pipeline can be replayed. Randomness and time MUST NOT affect a state
transition unless that input is captured with the transition.

Rationale: Replay and regression fail when the same task can take a different
path without a record of why.

### VI. Observable AI Actions

Every action taken by an AI agent MUST leave an inspectable record of the
action, the inputs it used, the output or diff it produced, the task it
served, and the result. An action that cannot be reconstructed from stored
records is forbidden. The record MUST be sufficient for a human to explain
what the agent did without the agent's hidden context.

Rationale: Agent work that cannot be inspected cannot be verified, approved,
or trusted as autonomy increases.

### VII. Human Approval for Consequential Actions

An action is consequential when it deletes or overwrites durable data, changes
permissions, spends money, contacts an external party, merges, deploys, or
cannot be undone by a later task in the same change. A consequential action
MUST stop and wait for an explicit human approval that names the action and
the evidence reviewed. The system MUST NOT treat silence, a prior unrelated
approval, or the agent's confidence as approval.

Rationale: Autonomy grows only inside a boundary a human has accepted.
Consequential effects stay outside that boundary until a recorded approval
covers them.

### VIII. Small, Independently Verifiable Changes

Each change MUST be small enough that its requirement, diff, and verification
can be reviewed on their own. A change MUST NOT mix unrelated requirements.
If a change cannot be verified without understanding an unrelated change, it
MUST be split before it is accepted.

Rationale: Independent verification is what makes tasks decomposable and safe
for an agent to execute one at a time.

## Engineering Pipeline

This constitution is the engineering contract for the AI Engineering Task
Manager and for every stage that builds on it. The system grows in this
order, and a later stage MUST NOT be treated as available until the previous
stage satisfies the principles above:

1. Structured tasks
2. Task decomposition
3. Implementation
4. Verification
5. Evidence and decisions
6. Autonomous AI developer

Work MUST be represented as structured tasks before implementation begins.
Decomposition MUST stop at tasks that satisfy Principle VIII. Implementation
MUST NOT be recorded as done until verification evidence exists (Principles II
and IV). Evidence and decisions MUST be stored with the task they belong to,
in a form a later agent can read without the original conversation.

A class of action MAY run autonomously only when that class already has
explicit state, an observable record, a verification method, deterministic
replay or a recorded non-deterministic boundary, and a written rule for which
cases still require human approval. Expanding autonomy MUST NOT skip a stage.

## Quality Gates

A change is eligible to merge only when all of the following hold:

- The requirement is clear and has acceptance criteria (Principle I).
- Verification was defined before implementation, and the recorded result
  passes (Principle II).
- The task state transition is explicit and stored (Principle III).
- The requirement, task, change, and verification link to each other
  (Principle IV).
- Non-deterministic steps are isolated and recorded (Principle V).
- Any AI action in the change is reconstructable from records (Principle VI).
- Consequential actions carry a named human approval (Principle VII).
- The change is independently reviewable (Principle VIII).

A reviewer MUST reject a change that fails any gate. An exception MUST name
the principle it relaxes, why the relaxation is required, and the condition
that removes it. An exception does not amend this constitution.

## Governance

This constitution supersedes generic template defaults and unwritten habit.
When a feature artifact conflicts with this file, the constitution wins: the
artifact is corrected, or an amendment is proposed here first.

Amendments:

- A change to a principle, the pipeline, the gates, or these rules MUST be
  written in this file before dependent work treats it as binding.
- The author MUST include a Sync Impact Report comment naming the version
  bump and what changed. That comment is review material and is removed
  before the amendment is committed.
- Version bumps follow semantic versioning:
  - MAJOR: a principle is removed or redefined so that existing work would
    be judged differently.
  - MINOR: a principle or section is added, or guidance is materially
    expanded.
  - PATCH: wording is clarified without changing what compliance means.
- The ratification date stays 2026-10-06. Last Amended updates to the date of
  the change.
- An amendment is in force when this file is updated. Specs, plans, and task
  lists MUST be checked against the new version before new implementation
  starts.

Compliance review happens when a spec is accepted, when tasks are generated,
and before implementation is marked done. Spec Kit commands carry the
day-to-day workflow. They do not override this file.

**Version**: 1.0.0 | **Ratified**: 2026-10-06 | **Last Amended**: 2026-10-06
