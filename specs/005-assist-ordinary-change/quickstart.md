# Quickstart: Assist an Ordinary Change

Validation guide for one assistant change on an In Progress task. Behavior is defined in [spec.md](spec.md), stored shape in [data-model.md](data-model.md), and commands in [contracts/http-api.md](contracts/http-api.md) and [contracts/ui.md](contracts/ui.md).

## Prerequisites

- Python 3.12
- A shell in the repository root
- Feature 001 through feature 004 behavior already in the workspace process (create a task, mark it Ready, start it, record a change, record a check, record a decision)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Automated check

```bash
pytest
```

Expected: every test passes, including the feature 001 through feature 004 suites. The suite must include, before the corresponding behavior is considered done:

- domain tests for an ordinary assistant change, a blank project, a blank account, a bad class, and the Draft, Ready, Completed, and Cancelled refusals
- domain tests that a consequential request and an ordinary request that stopped are Awaiting approval, and that an assistant actor cannot approve or decline
- domain tests that the engineer's existing change command still stores no project and no assistant, and that a subtask's assistant change does not appear on the parent
- a replay test that runs the same assistant-change script twice from an In Progress task, using the same scripted clock and the same stored account, and compares the account, the project, the assistant, and the outcome
- contract tests that call the new HTTP command and the assistant-actor refusal, and assert the status codes and messages in the API contract

A passing suite is the verification record for this feature. A test that does not map to a spec scenario or functional requirement does not count as that requirement's evidence. The suite must not call a model or write the named project.

## Run the local app

```bash
python -m task_manager --workspace ./workspace.db --engineer "Ada" --assistant "Guide" --port 8000
```

Then open `http://127.0.0.1:8000/`. `--assistant` is the name copied onto assistant changes. Omitting it uses `Assistant`. `--engineer` remains the name copied onto the engineer's own changes and onto approvals.

## Manual scenarios

Use a fresh `workspace.db`, or delete the file first. Create an In Progress task with a goal and one acceptance criterion before scenario 1. Statuses and messages are the expected outcomes.

### 1. Record an ordinary assistant change

1. On the In Progress task, record an assistant change with project `billing`, class ordinary, and account `Rename the export label`. Confirm the change shows that account, the project, Guide, and Carried out. Confirm the status stays In Progress.
2. Submit a blank project. Confirm nothing is saved and the page says to name the project this change is for.
3. Submit a blank account. Confirm nothing is saved and the page says an account of what changed is required.
4. On a Completed task, record an assistant change. Confirm nothing is saved and the page says to reopen the task first.
5. Record an ordinary change with the existing change action and no project. Confirm it is saved as the engineer's change and shows no assistant.

### 2. A consequential request waits

1. Record an assistant change with class consequential and account `Replace the stored export name`. Confirm it shows Awaiting approval and the status stays In Progress.
2. Record an ordinary assistant change and mark that it must stop. Confirm it shows Awaiting approval and `stopped` is recorded.
3. Try to approve the waiting change as the assistant. Confirm it stays Awaiting approval and the page says the assistant cannot approve a change.
4. Approve it as the engineer with evidence `The detail page shows the new export name`. Confirm the approval names Ada and the outcome is Carried out.

### 3. The stored record is the replay

1. Record one ordinary assistant change. Read the task and confirm the account, the project, the assistant, and Carried out.
2. Run the same recorded commands again from an empty workspace. Confirm the same account, project, assistant, outcome, and order. Confirm the run did not ask an assistant to carry the work out again.
3. On a subtask, record an assistant change. Confirm it appears on the subtask and does not appear on the parent.

## Done when

- `pytest` passes, including feature 001 through feature 004 tests.
- Scenarios 1 through 3 match the outcomes above on a fresh workspace.
- A reader can open the task and state what the assistant changed or proposed, which project it was for, and whether it was carried out, without the original conversation.
