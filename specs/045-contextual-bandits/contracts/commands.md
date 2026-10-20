# Commands: Contextual Bandits and Reinforcement Learning for Workflow Scheduling

## Name action

`POST /api/tasks/{task_id}/bandit-actions`

`POST /tasks/{task_id}/bandit-actions`

```json
{ "name": "ada" }
```

`name` may be omitted. The page field is Action name, `id="bandit-action-name"`. The button is Name action.

The trimmed name is stored once. The same name returns the task detail and does not store another action. A task stores at most 2 actions. A new action removes the stored choice.

## Name context

`POST /api/tasks/{task_id}/bandit-contexts`

`POST /tasks/{task_id}/bandit-contexts`

```json
{ "name": "rush" }
```

`name` may be omitted. The page field is Context name, `id="bandit-context-name"`. The button is Name context.

The trimmed name is stored once. The same name returns the task detail and does not store another context. A task stores at most 4 contexts. A new context removes the stored choice.

## Record trial

`POST /api/tasks/{task_id}/bandit-trials`

`POST /tasks/{task_id}/bandit-trials`

```json
{ "name": "one", "context": "rush", "action": "ada", "reward": "1" }
```

`name`, `context`, `action`, and `reward` may be omitted. The page fields are Trial name, `id="trial-name"`, Context, `id="trial-context"`, Action, `id="trial-action"`, and Reward, `id="trial-reward"`. The button is Record trial.

The trimmed name is stored once with the trimmed context, the trimmed action, and the given reward. The reward is accepted only when the trimmed text is `1` or `2`. The same name returns the task detail and does not change the trial. A task stores at most 4 trials. A new trial removes the stored choice.

## Choose action

`POST /api/tasks/{task_id}/bandit-choices`

`POST /tasks/{task_id}/bandit-choices`

```json
{ "context": "rush" }
```

`context` may be omitted. The page field is Context, `id="choice-context"`. The button is Choose action.

The command stores one choice for the trimmed context. An action with no trial in that context is chosen before the others, and the earliest-named of those actions wins. When every action has a trial in that context, the action with the higher average reward wins. An equal average keeps the action named first.

## Task detail

The task detail includes `bandit`:

```json
{
  "actions": [{ "name": "ada" }, { "name": "grace" }],
  "contexts": [{ "name": "rush" }],
  "trials": [
    { "name": "one", "context": "rush", "action": "ada", "reward": 1 },
    { "name": "two", "context": "rush", "action": "grace", "reward": 1 },
    { "name": "three", "context": "rush", "action": "grace", "reward": 2 }
  ],
  "values": [
    { "context": "rush", "action": "ada", "total": 1, "count": 1 },
    { "context": "rush", "action": "grace", "total": 3, "count": 2 }
  ],
  "choice": { "context": "rush", "action": "grace" },
  "can_name_action": true,
  "can_name_context": true,
  "can_try": true,
  "can_choose": true
}
```

`actions`, `contexts`, `trials`, and `values` are oldest first. `choice` is null when no choice is stored. `can_name_action` and `can_name_context` are true while the task is In Progress. `can_try` and `can_choose` are true while the task is In Progress and at least one action and one context exist.

## Page

The task page shows a Bandit section.

- Each action is `ada` in `id="bandit-actions"`.
- Each context is `rush` in `id="bandit-contexts"`.
- Each trial is `one: rush, ada, reward 1` in `id="bandit-trials"`.
- Each learned value is `rush, ada: total 1 from 1` in `id="bandit-values"`.
- The choice is `Choice for rush: grace` in `id="bandit-choice"`.
- Name action and Name context are offered while the task is In Progress.
- Record trial is offered only while `can_try` is true.
- Choose action is offered only while `can_choose` is true.
- When no action exists, the section says `No actions yet.`

## Refusals

| Condition | Status | Message |
|---|---|---|
| Blank action name | 400 | `Name this action.` |
| The task already has 2 actions | 409 | `This task already has 2 actions.` |
| Blank context name | 400 | `Name this context.` |
| The task already has 4 contexts | 409 | `This task already has 4 contexts.` |
| Blank trial name | 400 | `Name this trial.` |
| Blank trial context | 400 | `Name the context.` |
| Blank trial action | 400 | `Name the action.` |
| Reward is not 1 or 2 | 400 | `Name a reward of 1 or 2.` |
| The context is not on this task | 409 | `That context is not on this task.` |
| The action is not on this task | 409 | `That action is not on this task.` |
| The task already has 4 trials | 409 | `This task already has 4 trials.` |
| No action has been named | 409 | `Name an action first.` |
| No context has been named | 409 | `Name a context first.` |
| Blank choice context | 400 | `Name the context to choose.` |
| Task is not In Progress | 409 | `The task must be In Progress.` |
| Task is missing | 404 | `Task not found.` |

A repeated action name, a repeated context name, or a repeated trial name returns the task detail with status 200.
